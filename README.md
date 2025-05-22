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

Installation with Optional Dependencies (fsspec-proxy)
-----------------------------------------------------

The following steps apply only to the `fsspec-proxy` package. The package has
several optional dependency groups:

- `s3`: Required for S3 access (needed for the "Conda Stats" example)
- `anaconda`: Required for Anaconda Cloud access
- `all`: All optional dependencies

To install dependencies from Anaconda Cloud (like `anaconda-cloud-storage`),
configure pip to use the Anaconda Cloud index as an extra source. Create (or
edit) the file `~/.config/pip/pip.conf` (on macOS/Linux) or
`%APPDATA%\pip\pip.ini` (on Windows) and add:

    [global]
    extra-index-url = https://pypi.anaconda.org/anaconda-cloud/simple

Then install the desired optional dependencies:

```bash
# For S3 support (including the "Conda Stats" example)
pip install .[s3]

# For Anaconda Cloud support
pip install .[anaconda]

# For all optional dependencies
pip install .[all]
```

This will ensure that all required packages for `fsspec-proxy`, including those
only available on Anaconda Cloud, are installed.
