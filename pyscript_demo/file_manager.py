from fsspec.core import strip_protocol
from fsspec.implementations.asyn_wrapper import AsyncFileSystemWrapper
import fsspec
import os
import sys
import yaml
import logging

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FileSystemManager:
    def __init__(self):
        self.filesystems = {}
        self.name_to_prefix = {}
        if "PYSCRIPTFS_CONFIG" in os.environ:
            self.config = self.load_config(os.getenv("PYSCRIPTFS_CONFIG"))
        else:
            self.config = self.load_config()
        self.initialize_filesystems()

    def load_config(self, config_path="config.yaml"):
        if not os.path.exists(config_path):
            return {}
        with open(config_path, "r") as file:
            config_content = yaml.safe_load(file)
        logger.info("new config: %s", config_content)
        return config_content

    def initialize_filesystems(self):
        new_filesystems = {}

        # Init filesystem
        for fs_config in self.config.get("sources", []):
            key = fs_config["name"]
            fs_path = fs_config["path"]
            kwargs = fs_config.get("kwargs", {})

            logger.debug("filesystem %s: %s %s", key, fs_path, kwargs)

            fs, url2 = fsspec.url_to_fs(fs_path, **kwargs)
            if not fs.async_impl:
                fs = AsyncFileSystemWrapper(fs)

            # split_path includes just prefix (no protocol)
            split_path_list = fs_path.split("//", 1)

            # Store the filesystem instance
            new_filesystems[key] = {
                "instance": fs,
                "path": url2,
            }

        logger.info("new filesystems: %s", new_filesystems)
        self.filesystems = new_filesystems

    def get_filesystem(self, key):
        return self.filesystems.get(key)

    def get_filesystem_protocol(self, key):
        filesystem_rep = self.filesystems.get(key)
        return filesystem_rep["protocol"] + "://"
