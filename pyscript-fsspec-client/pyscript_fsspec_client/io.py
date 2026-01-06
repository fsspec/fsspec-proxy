import asyncio
import js
from pyodide import ffi, console
from pyscript import window

LOGGING = False


async def request(method, path, data=None, headers=None,
                  outmode="text", **kwargs):
    if LOGGING:
        print(method, path, outmode, kwargs, headers)
    try:
        if data:
            resp = await js.fetch(path, method=method, body=data.buffer, headers=headers or {},
                                  **kwargs)
        else:
            resp = await js.fetch(path, method=method, headers=ffi.to_js(headers) or {},
                                  **kwargs)
    except Exception as e:
        window.console.log(str(e))
        return "ISawAnError"
    if not resp.ok:
        out = "ISawAnError"
    elif resp.status >= 400:
        out = "ISawAnError"
    elif outmode == "text":
        out = await resp.text()
    elif outmode == "bytes":
        out = await resp.arrayBuffer()
    elif outmode is None:
        out = None
    else:
        out = "ISawAnError"
    if LOGGING:
        print(out)
    return out


async def batch(requests):
    requests = [r.to_py() for r in requests]
    if LOGGING:
        print("batch:", len(requests))
    out = asyncio.gather(
        *[request(*r["args"], **r["kwargs"]) for r in requests],
        return_exceptions=True
    )
    return out
