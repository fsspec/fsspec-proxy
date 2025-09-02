from pyscript import sync, ffi

import fsspec
from pyscript import display, fetch, window
from pyscript.web import span, page
import pandas as pd
import pyscript_fsspec_client.client

fs = fsspec.filesystem("pyscript")
print(fs.ls("local"))

out = fs.cat("local/mdurant/code/fsspec-proxy/pyproject.toml")
print("binary:", type(out), out)

out = fs.cat("local/mdurant/code/fsspec-proxy/pyproject.toml", start=0, end=10)
print("binary:", type(out), out)

fs.pipe_file("local/mdurant/code/fsspec-proxy/OUTPUT", b"hello world")


def make_output(table):
    """put HTML on the page"""
    new_div = span()
    new_div.innerHTML = table
    page.append(new_div)

my_data = pd.read_parquet("pyscript://Conda Stats/2017/01/2017-01-07.parquet")
make_output(my_data[:100].to_html())
