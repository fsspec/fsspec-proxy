#! /usr/bin/env python
import http.server
import os
import sys


class ExtraHeadersHandler(http.server.SimpleHTTPRequestHandler):
    directory = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()

    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", 'same-origin')
        self.send_header("Cross-Origin-Embedder-Policy", 'require-corp')
        self.send_header("Cross-Origin-Resource-Policy", 'cross-origin')
        super().end_headers()


if __name__ == '__main__':
    port = int(sys.argv[-1]) if sys.argv[-1].isnumeric() else 9988
    with http.server.HTTPServer(("localhost", port), ExtraHeadersHandler) as httpd:
        print(f"Serving HTTP on 'localhost:{port}' ")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
