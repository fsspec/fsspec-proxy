import json
import pyscript


async def request(method, path, data=None, headers=None,
                  outmode="json", **kwargs):
    print("main", method, path)
    if headers:
        print(headers)
        headers = json.loads(headers)
    resp = await pyscript.fetch(path, method=method, budy=data, headers=headers or {},
                                **kwargs)
    print("fetched", resp, resp.status)
    if resp.status >= 400:
        return ("error", resp.status, await resp.text())
    if outmode == "json":
        d = (await resp.json()).copy()
        print(d)
        return d
    if outmode == "text":
        return await resp.text()
    if outmode == "bytes":
        return await resp.bytearray()
    if outmode is None:
        return
    raise ValueError
