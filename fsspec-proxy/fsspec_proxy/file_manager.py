from fsspec.implementations.asyn_wrapper import AsyncFileSystemWrapper
import fsspec.utils
import io
import os
import pkgutil
import yaml
import logging

logger = logging.getLogger("fsspec_proxy")


class FileSystemManager:
    def __init__(self, config_path=None):
        self.filesystems = {}
        if config_path is None and "FSSPEC_PROXY_CONFIG" in os.environ:
            self.config = self.load_config(os.getenv("FSSPEC_PROXY_CONFIG"))
        else:
            self.config = self.load_config()
        self.initialize_filesystems()

    def load_config(self, config_path=None):
        if config_path is None:
            data = pkgutil.get_data(__name__, "config.yaml")
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

            fs, url2 = fsspec.url_to_fs(fs_path, **kwargs)
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
