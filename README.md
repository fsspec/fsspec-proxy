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
  allowing even pyscript to access bytes in remote stores

Now run:
```bash
$ fsspec-proxy dev
```
to start the (unsecured) proxy server, with port 8000. Further arguments
will be passed to fastAPI to configure, for example, the port and address
to listen on.

The default config in `config.yaml` has entry "Conda Stats", 
which is available anonymously from S3. The location of the config
file to read can be set with FSSPEC_PROXY_CONFIG. Optionally, the
server can be reconfigured via an API call.

*WARNING*: the proxy server does not currently implement secure connections
or auth. It can be regarded as a prototype to base production-level 
implementations on.

Demo
----

With the server running locally, 
now navigate to: https://martindurant.pyscriptapps.com/empty-tundra/latest/

The server will show incoming byte range requests, and you can also track them
in the browser's debug console. The end result should be a table view of the
contents of the target parquet file. 

Installation with Optional Dependencies (fsspec-proxy)
-----------------------------------------------------

The following steps apply only to the `fsspec-proxy` package. The package has
several optional dependency groups:

- `s3`: Required for S3 access (needed for the "Conda Stats" example)
- `anaconda`: Required for Anaconda Cloud access
- `all`: All optional dependencies

S3 Support
~~~~~~~~~~

To use S3 functionality (including the "Conda Stats" example):

```bash
pip install .[s3]
```

Anaconda Cloud Support
~~~~~~~~~~~~~~~~~~~~~~

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

All Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

To install all optional dependencies:

```bash
# With pip config
pip install .[all]

# Or directly with extra index
pip install .[all] --extra-index-url https://pypi.anaconda.org/anaconda-cloud/simple
```

This will ensure that all required packages for `fsspec-proxy`, including those
only available on Anaconda Cloud, are installed.
>>>>>>> 4408c85bdd76295a43f0d7a20041a646e46b3f25
