from contextlib import asynccontextmanager
import io
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from fsspec_proxy import file_manager


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


@app.delete("/api/delete/{key}/{path:path}")
async def delete_file(key, path, response: fastapi.Response):
    fs_info = app.manager.get_filesystem(key)
    path = f"{fs_info['path'].rstrip('/')}/{path.lstrip('/')}"
    if fs_info is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    if fs_info.get("readonly"):
        raise fastapi.HTTPException(status_code=403, detail="Not Allowed")
    try:
        out = await fs_info["instance"]._rm_file(path)
    except FileNotFoundError:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    except PermissionError:
        raise fastapi.HTTPException(status_code=403, detail="Not Allowed")
    response.status_code = 204


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


@app.post("/api/bytes/{key}/{path:path}")
async def put_bytes(key, path, request: fastapi.Request, response: fastapi.Response):
    fs_info = app.manager.get_filesystem(key)
    if fs_info is None:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    if fs_info.get("readonly"):
        raise fastapi.HTTPException(status_code=403, detail="Not Allowed")
    path = f"{fs_info['path'].rstrip('/')}/{path.lstrip('/')}"
    data = await request.body()
    print("####", data)
    try:
        await fs_info["instance"]._pipe_file(path, data)
    except FileNotFoundError:
        raise fastapi.HTTPException(status_code=404, detail="Item not found")
    response.status_code = 201
    return {"contents": []}


@app.post("/api/config")
async def setup(request: fastapi.Request):
    if not app.manager.config.get("allow_reload", False):
        raise fastapi.HTTPException(status_code=403, detail="Not Allowed")
    app.manager.config = await request.json()
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


@app.get("/health")
async def ok():
    return {"status": "ok", "contents": []}
