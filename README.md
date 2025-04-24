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
will be passed to fastAPI to configure, for example, the post and address
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
