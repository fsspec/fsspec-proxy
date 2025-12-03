"""An fsspec filesystem that proxies via pyscriptapps.com."""

from json import loads
import logging

from pyscript import sync, ffi
from fsspec.spec import AbstractFileSystem, AbstractBufferedFile
import fsspec.utils

logger = logging.getLogger("pyscript_fsspec_client")
fsspec.utils.setup_logging(logger=logger)


class PyscriptFileSystem(AbstractFileSystem):
    """An fsspec filesystem that proxies via pyscriptapps.com."""

    protocol = "pyscript"

    def __init__(self, base_url="http://0.0.0.0:8000/local"):
        super().__init__()
        self.base_url = base_url

    # `AbstractFileSystem` protocol ############################################

    def cat_file(self, path, start=None, end=None, **kw):
        if start is not None and end is not None:
            range = (start, end + 1)
        else:
            range = None
        return self._call(f"bytes/{path}", binary=True, range=range)

    def ls(self, path, detail=True, **kwargs):
        path = self._strip_protocol(path)
        out = loads(self._call(f"list/{path}"))["contents"]

        if detail:
            return out
        return sorted(_["name"] for _ in out)

    def pipe_file(self, path, value, mode="overwrite", **kwargs):
        self._call(f"bytes/{path}", method="POST", data=value)

    def rm_file(self, path):
        path = self._strip_protocol(path)
        self._call(f"delete/{path}", method="DELETE", binary=True)

    def cat_ranges(
        self, paths, starts, ends, max_gap=None, on_error="return", **kwargs
    ):
        logger.debug("cat_ranges: %s paths", len(paths))
        out = sync.batch(
            [{
                "args": ("GET", f"{self.base_url}/bytes/{path}"),
                "kwargs": {"headers": ffi.to_js({"Range": f"bytes={s}-{e + 1}"}), "outmode": "bytes"}
             }
            for path, s, e in zip(paths, starts, ends)],
        )
        return [(OSError(0, o) if isinstance(o, str) and o == "ISawAnError"
                 else bytes(o.to_py()))
                for o in out]

    def _open(
            self,
            path,
            mode="rb",
            block_size=None,
            autocommit=True,
            cache_options=None,
            **kwargs,
    ):
        return JFile(
            self, path, mode, block_size, autocommit, cache_options, **kwargs
        )

    # Internal #################################################################

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

    def _split_path(self, path):
        key, *relpath = path.split("/", 1)
        return key, relpath[0] if relpath else ""


class JFile(AbstractBufferedFile):
    """An fsspec buffered file implementation for the `pyscript` protocol."""

    # `AbstractBufferedFile` protocol ##########################################

    def _fetch_range(self, start, end):
        return self.fs.cat_file(self.path, start, end)

    def _upload_chunk(self, final=False):
        if final:
            self.fs.pipe_file(self.path, self.buffer.getvalue())
            return True
        return False


fsspec.register_implementation("pyscript", PyscriptFileSystem)
