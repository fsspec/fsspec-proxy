fsspec proxy and client
=======================

Allows reading/writing files via standard fsspec/python operations via a
proxy which doesn't expose any of its internal credentials. 

This is particularly useful for pyscript, which cannot call the backend
packages required to talk to remote filesystems, like botocore.

Quickstart
----------

Install the two sub-packages:
- fsspec-proxy, a fastAPI-based server which reads/writes to configured storage
  locations
- pyscript-fsspec-client, a filesystem implementation that connects to the proxy, 
  allowing even pyscript to access bytes in remote stores.

Now run:
```bash
$ fsspec-proxy dev
```
This starts the (unsecured) proxy server, with port 8000. Further arguments
will be passed to fastAPI to configure, for example, the port and address
to listen on.

The default config in `config.yaml` has entry "Conda Stats", 
which is available anonymously from S3. The location of the config
file to read can be set with FSSPEC_PROXY_CONFIG. Optionally, the
server can be reconfigured via an API call.

*WARNING*: the proxy server does not currently implement secure connections
or auth. It can be regarded as a prototype to base production-level 
implementations on.

Options
-------

- `run` (default) runs the server in production mode
- `dev` run the server in development mode
- `private` adds Access-Control-Allow-Private-Network header to allow some
 requests in some CORS situations. If you are seeing CORS issues, adding
 this might help.

Demo
----

With the server running locally, 
now navigate to: https://martindurant.pyscriptapps.com/empty-tundra/latest/

The server will show incoming byte range requests, and you can also track them
in the browser's debug console. The end result should be a table view of the
contents of the target parquet file. 

By default, the server attempts to instantiate S3 and anaconda filesystems,
but will skip these with a message if the dependencies are not available. The
demo uses the S3 backend, so you will need S3 support (below). 

S3 Support
----------

To use S3 functionality (including the "Conda Stats" example):

```bash
pip install "./fsspec-proxy[s3]"
```

Anaconda Cloud Support
----------------------

To use Anaconda Cloud functionality, you'll need to install dependencies from
the Anaconda Cloud index. You can do this in two ways:

1. Configure pip to use the Anaconda Cloud index as an extra source. Create (or
   edit) the file `~/.config/pip/pip.conf` (on macOS/Linux) or
   `%APPDATA%\pip\pip.ini` (on Windows) and add:

    [global]
    extra-index-url = https://pypi.anaconda.org/anaconda-cloud/simple

   Then install:

   ```bash
   pip install .[anaconda]
   ```

2. Or install directly using pip's `--extra-index-url` option:

   ```bash
   pip install .[anaconda] --extra-index-url https://pypi.anaconda.org/anaconda-cloud/simple
   ```
