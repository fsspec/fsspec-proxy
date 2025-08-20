import json
import pyscript
import js
from pyodide import ffi, console


async def request(method, path, data=None, headers=None,
                  outmode="text", **kwargs):
    if data:
        resp = await js.fetch(path, method=method, body=data.buffer, headers=headers or {},
                              **kwargs)
    else:
        resp = await js.fetch(path, method=method, headers=headers or {},
                              **kwargs)
    if not resp.ok:
        return "ISawAnError"
    if resp.status >= 400:
        return "ISawAnError"
    if outmode == "text":
        return await resp.text()
    if outmode == "bytes":
        return await resp.arrayBuffer()
    if outmode is None:
        return
    return "ISawAnError"
