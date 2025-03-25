from contextlib import asynccontextmanager
import io
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from pyscript_demo import file_manager


# docs: https://www.python-httpx.org/async/
# from starlette.requests import Request
# from starlette.background import BackgroundTask
# import httpx
#
# this is the target API; default base is optional
# client = httpx.AsyncClient(base_url="http://containername:7800/")
#
# async def _reverse_proxy(request: Request):
#     url = httpx.URL(path=request.url.path,  # setup any URL here
#                     query=request.url.query.encode("utf-8"))  # encode path, since it was decoded for us
#     rp_req = client.build_request(request.method, url,
#                                   headers=request.headers.raw,
#                                   content=request.stream()) # streams incoming request to target
#     rp_resp = await client.send(rp_req, stream=True)
#     return StreamingResponse(
#         rp_resp.aiter_raw(),  # streams response back to caller in chunks
#         status_code=rp_resp.status_code,
#         headers=rp_resp.headers,  # might need to edit headers, but include encoding
#         background=BackgroundTask(rp_resp.aclose),  # what to do when finished
#     )


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    # start instances in async context
    app.manager = file_manager.FileSystemManager()
    yield


app = fastapi.FastAPI(lifespan=lifespan)
#app.add_route("/api/{key}/{path:path}",  # passes through all matching calls
#              _reverse_proxy, ["GET", "POST", "PUT", "DELETE"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://martindurant.pyscriptapps.com'],
    allow_methods=["GET", "POST", "DELETE", "OPTION", "PUT"],
    allow_credentials=True,
    allow_headers=["*"]
)


@app.get("/api/list")
async def list_root():
    keys = list(app.manager.filesystems)
    return {
        "status": "ok",
        "contents": [
            {"name": k, "size": 0, "type": "directory"} for k in keys
        ]
    }


@app.get("/api/list/{key}/{path:path}")
async def list_dir(key, path):
    fs_info = app.manager.get_filesystem(key)
    if fs_info is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    path = f"{fs_info['path'].rstrip('/')}/{path.lstrip('/')}"
    try:
        out = await fs_info["instance"]._ls(path, detail=True)
    except FileNotFoundError:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    out = [
        {"name": f"{key}/{o['name'].replace(fs_info['path'], '', 1).lstrip('/')}",
         "size": o["size"], "type": o["type"]}
        for o in out
    ]
    return {"status": "ok", "contents": out}


@app.get("/api/bytes/{key}/{path:path}")
async def get_bytes(key, path, request: fastapi.Request):
    start, end = _process_range(request.headers.get("Range"))
    fs_info = app.manager.get_filesystem(key)
    if fs_info is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    path = f"{fs_info['path'].rstrip('/')}/{path.lstrip('/')}"
    try:
        out = await fs_info["instance"]._cat_file(path, start=start, end=end)
    except FileNotFoundError:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    return StreamingResponse(io.BytesIO(out), media_type="application/octet-stream")


@app.post("/api/config")
async def setup(request: fastapi.Request):
    app.manager.config = request.json()
    app.manager.initialize_filesystems()


def _process_range(range):
    if range and range.startswith("bytes=") and range.count("-") == 1:
        sstart, sstop = range.split("=")[1].split("-")
        if sstart == "":
            start = int(sstop)
            end = None
        elif sstop == "":
            start = int(sstart)
            end = None
        else:
            start = int(sstart)
            end = int(sstop) - 1
    else:
        start = end = None
    return start, end



@app.options("/api/{path:path}")
async def make_cors(path, response: fastapi.Response):
    # TODO: check key is in config
    response.headers["Access-Control-Allow-Origin"] = "*"  # or set to
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response.status_code = 204


@app.get("/health")
async def ok():
    return {"status": "ok"}
