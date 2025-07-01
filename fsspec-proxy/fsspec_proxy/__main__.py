#!/usr/bin/env python

import os
import re
import sys

from fastapi_cli.cli import main

import fsspec_proxy.bytes_server
path = fsspec_proxy.bytes_server.__file__


def run_main():
    mode = "dev" if "dev" in sys.argv else "run"
    # TODO: this should be unified with the config
    os.environ["FS_PROXY_PRIVATE"] = str("private" in sys.argv)
    argv = [_ for _ in sys.argv if _ not in {"dev", "run", "private"}]
    sys.argv = [
        re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0]),
        mode,
        path
    ] + argv[1:]
    sys.exit(main())


if __name__ == "__main__":
    run_main()
