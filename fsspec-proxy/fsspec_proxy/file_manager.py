from fsspec.implementations.asyn_wrapper import AsyncFileSystemWrapper
import fsspec.utils
import os
import sys
import yaml
import logging

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fsspec.utils.setup_logging(logger_name="fsspec.memoryfs")
this_dir = os.path.abspath(os.path.dirname(__file__))


class FileSystemManager:
    def __init__(self):
        self.filesystems = {}
        if "FSSPEC_PROXY_CONFIG" in os.environ:
            self.config = self.load_config(os.getenv("FSSPEC_PROXY_CONFIG"))
        else:
            self.config = self.load_config()
        self.initialize_filesystems()

    def load_config(self, config_path=os.path.join(this_dir, "config.yaml")):
        if not os.path.exists(config_path):
            return {}
        with open(config_path, "r") as file:
            config_content = yaml.safe_load(file)
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
