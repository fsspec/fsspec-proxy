import os
import logging

import fsspec.utils
from fsspec.spec import AbstractFileSystem, AbstractBufferedFile
from fsspec.implementations.http_sync import RequestsSessionShim

logger = logging.getLogger("pyscript_client")
fsspec.utils.setup_logging(logger=logger)
default_endpoint =  os.getenv("FSSPEC_PROXY_URL", "http://127.0.0.1:8000/api")


class PyscriptFileSystem(AbstractFileSystem):
    protocol = "pyscript"

    def __init__(self, base_url=default_endpoint):
        super().__init__()
        self.base_url = base_url
        self._session = None

    def _split_path(self, path):
        key, *relpath = path.split("/", 1)
        return key, relpath[0] if relpath else ""

    @property
    def session(self):
        if self._session is None:
            try:
                import js  # noqa: F401
                self._session = RequestsSessionShim()
            except (ImportError, ModuleNotFoundError):
                import requests
                self._session = requests.Session()
        return self._session

    def _call(self, path, method="GET", range=None, binary=False, data=None, json=None, **kw):
        logger.debug("request: %s %s %s %s", path, method, kw, range)
        headers = {}
        if range:
            headers["Range"] = f"bytes={range[0]}-{range[1]}"
        r = self.session.request(
            method, f"{self.base_url}/{path}", params=kw, headers=headers,
            data=data, json=json
        )
        if r.status_code == 404:
            raise FileNotFoundError(path)
        if r.status_code == 403:
            raise PermissionError
        r.raise_for_status()
        if binary:
            return r.content
        j = r.json() if callable(r.json) else r.json  # inconsistency in shim - to fix!
        return j["contents"]

    def ls(self, path, detail=True, **kwargs):
        path = self._strip_protocol(path)
        key, *path =  path.split("/", 1)
        if key:
            part = path[0] if path else ""
            out = self._call(f"list/{key}/{part}")
        else:
            out = self._call(f"list")

        if detail:
            return out
        return sorted(_["name"] for _ in out)

    def rm_file(self, path):
        path = self._strip_protocol(path)
        key, path =  path.split("/", 1)
        self._call(f"delete/{key}/{path}", method="DELETE", binary=True)

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
        return self._call(f"bytes/{key}/{relpath}", binary=True, range=range)

    def pipe_file(self, path, value, mode="overwrite", **kwargs):
        key, relpath = self._split_path(path)
        self._call(f"bytes/{key}/{relpath}", method="POST", data=value)

    def reconfigure(self, config):
        # only privileged identities can do this
        if not "sources" in config:
            raise ValueError("Bad config")
        if not ["name" in _ and "path" in _ for _ in config["sources"]]:
            raise ValueError("Bad config")
        self._call(f"config", method="POST", json=config, binary=True)


class JFile(AbstractBufferedFile):
    def _fetch_range(self, start, end):
        return self.fs.cat_file(self.path, start, end)

    def _upload_chunk(self, final=False):
        if final:
            self.fs.pipe_file(self.path, self.buffer.getvalue())
            return True
        return False

fsspec.register_implementation("pyscript", PyscriptFileSystem)