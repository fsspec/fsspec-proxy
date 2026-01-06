import io
import logging
import os
import yaml

from fsspec.implementations.asyn_wrapper import AsyncFileSystemWrapper
import fsspec.utils

logger = logging.getLogger("fsspec_proxy")
# TODO: this config is copied as config.yaml; de-dup and move other options
#  into the config
default_config = b"""sources:
 - name: inmemory
   path: memory://mytests
 - name: local
   path: file:///Users
   readonly: true
 - name: "Conda Stats"
   path: "s3://anaconda-package-data/conda-stats/"
   kwargs:
     anon: True
 - name: "MyAnaconda"
   path: "anaconda://my/"
allow_reload: true
"""

class FileSystemManager:
    """
    Holds configured fsspec instances
    """

    def __init__(self, config_path=None):
        """

        :param config_path: if NONE, loads config from FSSPEC_PROXY_CONFIG
        """
        self.filesystems = {}
        config_path = config_path or os.getenv("FSSPEC_PROXY_CONFIG", None)
        self.config = self.load_config(config_path)
        self.initialize_filesystems()

    def load_config(self, config_path=None):
        """Reset the config"""
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
        """Create filesystem instances"""
        new_filesystems = {}

        for fs_config in self.config.get("sources", []):
            key = fs_config["name"]
            fs_path = fs_config["path"]
            kwargs = fs_config.get("kwargs", {})

            try:
                fs, url2 = fsspec.url_to_fs(fs_path, **kwargs)
            except Exception:
                # or we could still list show their names but not the contents
                logger.exception("Instantiating filesystem %s failed, skipping", key)
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
        """Get filesystem instance by configured name"""
        return self.filesystems.get(key)
