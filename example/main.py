from pyscript_fsspec_client import io
from pyscript import PyWorker

config = {
    "packages": ["fsspec==2025.12.0", "fastparquet", "pandas"],
    "files": {
        "./pyscript_fsspec_client/__init__.py": "./pyscript_fsspec_client/__init__.py",
        "./pyscript_fsspec_client/client.py": "./pyscript_fsspec_client/client.py",
        "./pyscript_fsspec_client/io.py": "./pyscript_fsspec_client/io.py"
    }
}
pw = PyWorker("./worker.py", type="pyodide", config=config)

def console_print(x):
    print(x)

pw.sync.session = io.request
pw.sync.batch = io.batch
pw.sync.console_print = console_print
