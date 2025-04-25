import subprocess
import time

import pytest
import requests

from pyscript_fsspec_client import client


@pytest.fixture(scope="session")
def server():
    # TODO: test config in "FSSPEC_PROXY_CONFIG" location
    P = subprocess.Popen(["fsspec-proxy"])
    s = "http://localhost:8000"
    count = 5
    while True:
        try:
            requests.get(f"{s}/health")
            break
        except BaseException:
            if count < 0:
                raise
        count -= 1
        time.sleep(0.1)
    yield f"{s}/api"
    P.terminate()
    P.wait()


@pytest.fixture()
def fs(server):
    return client.PyscriptFileSystem(server)


def test_file(fs):
    with fs.open("inmemory/afile", "wb") as f:
        f.write(b"hello")
    assert fs.exists("inmemory/afile")
    with fs.open("inmemory/afile", "rb") as f:
        assert f.read() == b"hello"
    fs.rm("inmemory/afile")
    assert not fs.exists("inmemory/afile")


def test_config(fs):
    out = fs.ls("", detail=False)
    assert out == ["Conda Stats", "MyAnaconda", "inmemory", "local"]
    fs.reconfigure({"sources": [{"name": "mem", "path": "memory://"}]})
    out = fs.ls("", detail=False)
    assert out == ["mem"]
