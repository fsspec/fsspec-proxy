from pyscript_fsspec_client import io
from pyscript import PyWorker, ffi

config = {
    "packages": ["fsspec", "fastparquet"],
    "files": {
        "./pyscript_fsspec_client/__init__.py": "./pyscript_fsspec_client/__init__.py",
        "./pyscript_fsspec_client/client.py": "./pyscript_fsspec_client/client.py",
        "./pyscript_fsspec_client/io.py": "./pyscript_fsspec_client/io.py"
    }
}
pw = PyWorker("./worker.py", type="pyodide", config=config)
pw.sync.session = io.request
