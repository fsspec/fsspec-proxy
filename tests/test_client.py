import subprocess
import time

import pytest
import requests

from pyscript_demo import client


@pytest.fixture()
def server():
    # TODO: test config in "PYSCRIPTFS_CONFIG" location
    P = subprocess.Popen(["fastapi", "dev", "pyscript_demo/bytes_server.py"])
    s = "http://127.0.0.1:8000"
    count = 5
    while True:
        try:
            requests.get(f"{s}/health")
            break
        except OSError:
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
    with fs.open("test/afile", "wb") as f:
        f.write(b"hello")
    assert fs.exists("test/afile")
    with fs.open("test/afile", "rb") as f:
        assert f.read() == b"hello"
    fs.rm("test/afile")
    assert not fs.exists("test/afile")


def test_config(fs):
    out = fs.ls("", detail=False)
    assert out == ["Conda Stats", "test", "test1"]
    fs.reconfigure({"sources": [{"name": "mem", "path": "memory://"}]})
    out = fs.ls("", detail=False)
    assert out == ["mem"]
