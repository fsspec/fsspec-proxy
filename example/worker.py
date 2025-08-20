from pyscript import sync, ffi

import fsspec
import pyscript_fsspec_client.client

fs = fsspec.filesystem("pyscript")
print(fs.ls("local"))

out = fs.cat("local/mdurant/code/fsspec-proxy/pyproject.toml")
print("binary:", type(out), out)

out = fs.cat("local/mdurant/code/fsspec-proxy/pyproject.toml", start=0, end=10)
print("binary:", type(out), out)

fs.pipe_file("local/mdurant/code/fsspec-proxy/OUTPUT", b"hello world")
