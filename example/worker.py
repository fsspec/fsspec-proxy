from pyscript import sync, document, window

import fsspec
import pyscript_fsspec_client.client

fs = fsspec.filesystem("pyscript")
print(fs.ls("local"))
