from pyscript import sync, ffi

import fsspec.parquet
from pyscript import display, fetch, window
from pyscript.web import span, page
import pandas as pd
import time
import pyscript_fsspec_client.client


sync.console_print(str(fsspec.__version__))
fs = fsspec.filesystem("pyscript", base_url="http://localhost:8000/local")
sync.console_print(str(fs.ls("")))

# out = fs.cat("mdurant/code/fsspec-proxy/pyproject.toml")
# sync.console_print(str(("binary:", type(out), out)))
#
# out = fs.cat("mdurant/code/fsspec-proxy/pyproject.toml", start=0, end=10)
# sync.console_print(str(("binary:", type(out), out)))
#
# out = fs.cat_ranges(
#     paths=["mdurant/code/fsspec-proxy/pyproject.toml"] * 3,
#     starts=[0, 0, 20],
#     ends=[1, 10, 30]
# )
# sync.console_print(str(("binary:", type(out), out)))
#
# fs.pipe_file("mdurant/code/fsspec-proxy/OUTPUT", b"hello world")
#

def make_output(table):
    """put HTML on the page"""
    new_div = span()
    new_div.innerHTML = table
    page.append(new_div)


cols = ["time", "pkg_name", "counts"]
t1 = time.time()
# sync version, one file
my_data = pd.read_parquet("pyscript://2025/daily_2025-10.parquet",
                           storage_options={"base_url": "http://localhost:8000/Conda Stats"},
                           columns=cols)

t2 = time.time()

filters = [["pkg_name", "==", "numpy"]]
# concurrent version, 12 files
files = fsspec.parquet.open_parquet_files("pyscript://2025/daily_2025-*.parquet",
                         storage_options={"base_url": "http://localhost:8000/Conda Stats"},
                         columns=cols, max_gap=1, footer_sample_size=64_000,
                         filters=filters)
my_data2 = []
for f in files:
    with f as f:
        my_data2.append(pd.read_parquet(f, columns=cols, filters=filters))
t3 = time.time()

df = pd.concat(my_data2)
make_output(df[df.pkg_name == "numpy"].groupby("time")[["counts"]].sum().sort_index().to_html())
sync.console_print(f"times: {t2-t1} {t3-t2}")
