fsspec proxy and client
=======================

Allows reading/writing files via standard fsspec/python operations via a
proxy, which doesn't expose any of its internal credentials. 

This is particularly useful for pyscript, which cannot call the backend
packages required to talk to remote filesystems, like botocore.

Demo
----

This is for running the example locally. Further docs will be written when we
have agreed on a final layout of this repo and code.

With a prepared environment including `s3fs`.

```
$ git clone https://github.com/fsspec/fsspec-proxy
$ cd fsspec-proxy
$ pip install ./fsspec-proxy
$ fsspec-proxy
$ # new console, same directory
$ cd example
$ uvx pyscript run . --port 8899
```
