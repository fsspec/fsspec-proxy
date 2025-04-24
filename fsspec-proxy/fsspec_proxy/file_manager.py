from fsspec.implementations.asyn_wrapper import AsyncFileSystemWrapper
import fsspec.utils
import io
import os
import yaml
import logging

logger = logging.getLogger("fsspec_proxy")
default_config = b"""sources:
 - name: inmemory
   path: memory://mytests
 - name: local
   path: file:///Users
   readonly: true
 - name: "Conda Stats"
   path: "s3://anaconda-package-data/conda/hourly/"
   kwargs:
     anon: True
 - name: "MyAnaconda"
   path: "anaconda://my/"
allow_reload: true
"""

class FileSystemManager:
    def __init__(self, config_path=None):
        self.filesystems = {}
        config_path = config_path or os.getenv("FSSPEC_PROXY_CONFIG", None)
        self.config = self.load_config(config_path)
        self.initialize_filesystems()

    def load_config(self, config_path=None):
        if config_path is None:
            data = default_config
        elif not os.path.exists(config_path):
            return {}
        else:
            with open(config_path, "rb") as file:
                data = file.read()
        config_content = yaml.safe_load(io.BytesIO(data))
        logger.info("new config: %s", config_content)
        return config_content

    def initialize_filesystems(self):
        new_filesystems = {}

        for fs_config in self.config.get("sources", []):
            key = fs_config["name"]
            fs_path = fs_config["path"]
            kwargs = fs_config.get("kwargs", {})

            try:
                fs, url2 = fsspec.url_to_fs(fs_path, **kwargs)
            except ImportError:
                logger.error("Instantiating filesystem failed")
                continue
            if not fs.async_impl:
                fs = AsyncFileSystemWrapper(fs)

            new_filesystems[key] = {
                "instance": fs,
                "path": url2,
            }

        logger.info("new filesystems: %s", new_filesystems)
        self.filesystems = new_filesystems

    def get_filesystem(self, key):
        return self.filesystems.get(key)
