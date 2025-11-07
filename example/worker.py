from pyscript import sync, ffi

import fsspec
from pyscript import display, fetch, window
from pyscript.web import span, page
import pandas as pd
import pyscript_fsspec_client.client

fs = fsspec.filesystem("pyscript")
sync.console_print(str(fs.ls("local")))

out = fs.cat("local/mdurant/code/fsspec-proxy/pyproject.toml")
sync.console_print(str(("binary:", type(out), out)))

out = fs.cat("local/mdurant/code/fsspec-proxy/pyproject.toml", start=0, end=10)
sync.console_print(str(("binary:", type(out), out)))

out = fs.cat_ranges(
    paths=["local/mdurant/code/fsspec-proxy/pyproject.toml"] * 3,
    starts=[0, 0, 20], ends=[1, 10, 30])
sync.console_print(str(("binary:", type(out), out)))

fs.pipe_file("local/mdurant/code/fsspec-proxy/OUTPUT", b"hello world")


def make_output(table):
    """put HTML on the page"""
    new_div = span()
    new_div.innerHTML = table
    page.append(new_div)

my_data = pd.read_parquet("pyscript://Conda Stats/2017/01/2017-01-07.parquet")
make_output(my_data[:100].to_html())
