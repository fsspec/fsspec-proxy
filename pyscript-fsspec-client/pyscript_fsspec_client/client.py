from json import dumps, loads
import logging
import os

from pyscript import sync, ffi
from fsspec.spec import AbstractFileSystem, AbstractBufferedFile
import fsspec.utils

logger = logging.getLogger("pyscript_fsspec_client")
fsspec.utils.setup_logging(logger=logger)
default_endpoint =  os.getenv("FSSPEC_PROXY_URL", "http://127.0.0.1:8000")


class PyscriptFileSystem(AbstractFileSystem):
    protocol = "pyscript"

    def __init__(self, base_url=default_endpoint):
        super().__init__()
        self.base_url = base_url

    def _split_path(self, path):
        key, *relpath = path.split("/", 1)
        return key, relpath[0] if relpath else ""

    def _call(self, path, method="GET", range=None, binary=False, data=0, json=0):
        logger.debug("request: %s %s %s", path, method, range)
        headers = {}
        if binary:
            outmode = "bytes"
        elif json:
            outmode = "json"
        else:
            outmode = "text"
        if range:
            headers["Range"] = f"bytes={range[0]}-{range[1]}"
        if data:
            data = memoryview(data)
            outmode = None
        out = sync.session(
            method, f"{self.base_url}/{path}", ffi.to_js(data),
            ffi.to_js(headers), outmode
        )
        if isinstance(out, str) and out == "ISawAnError":
            raise OSError(0, out)
        if out is not None and not isinstance(out, str):
            # may need a different conversion
            out = bytes(out.to_py())
        return out

    def ls(self, path, detail=True, **kwargs):
        print(path)
        path = self._strip_protocol(path)
        key, *path =  path.split("/", 1)
        if key:
            part = path[0] if path else ""
            out = loads(self._call(f"{key}/list/{part}"))["contents"]
        else:
            raise ValueError

        print(out)
        if detail:
            return out
        return sorted(_["name"] for _ in out)

    def rm_file(self, path):
        path = self._strip_protocol(path)
        key, path =  path.split("/", 1)
        self._call(f"{key}/delete/{path}", method="DELETE", binary=True)

    def _open(
        self,
        path,
        mode="rb",
        block_size=None,
        autocommit=True,
        cache_options=None,
        **kwargs,
    ):
        return JFile(self, path, mode, block_size, autocommit, cache_options, **kwargs)

    def cat_file(self, path, start=None, end=None, **kw):
        key, relpath = self._split_path(path)
        if start is not None and end is not None:
            range = (start, end + 1)
        else:
            range = None
        return self._call(f"{key}/bytes/{relpath}", binary=True, range=range)

    def pipe_file(self, path, value, mode="overwrite", **kwargs):
        key, relpath = self._split_path(path)
        self._call(f"{key}/bytes/{relpath}", method="POST", data=value)


class JFile(AbstractBufferedFile):
    def _fetch_range(self, start, end):
        return self.fs.cat_file(self.path, start, end)

    def _upload_chunk(self, final=False):
        if final:
            self.fs.pipe_file(self.path, self.buffer.getvalue())
            return True
        return False

fsspec.register_implementation("pyscript", PyscriptFileSystem)
