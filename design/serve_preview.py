#!/usr/bin/env python3
"""Local preview server for the Just Apps site.

Serves ``docs/`` the way Vercel does in production, so the links you test
locally are the links that ship:

  * ``/privacy`` resolves to ``docs/privacy.html``   (cleanUrls)
  * ``/`` resolves to ``docs/index.html``
  * ``/namaaz-reminder``, ``/screen-time-reminder``, ``/subscription-tracker``,
    ``/vaccine-routine`` and ``/step-reminder`` resolve to their ``.html`` files
  * a missing path returns ``docs/404.html`` with a real 404 status

The server binds 0.0.0.0 so the sandbox preview proxy can reach it, and it
sends no ``X-Frame-Options`` or CSP headers, so the page renders inside the
preview iframe.

    python3 design/serve_preview.py            # http://localhost:8000
    PORT=8080 python3 design/serve_preview.py  # another port
"""

import os
import posixpath
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))


class PreviewHandler(SimpleHTTPRequestHandler):
    """Static handler with Vercel's cleanUrls and a branded 404."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def translate_path(self, path):
        """Map an extensionless URL to its .html file, like cleanUrls does."""
        url_path = urllib.parse.urlparse(path).path
        clean = posixpath.normpath(urllib.parse.unquote(url_path)).lstrip("/")
        full = os.path.join(ROOT, clean)

        if os.path.isdir(full):
            index = os.path.join(full, "index.html")
            if os.path.exists(index):
                return index
            return full

        # /privacy -> docs/privacy.html, but only when there is no real file
        # and no file extension already in the request.
        if not os.path.exists(full) and not os.path.splitext(full)[1]:
            if os.path.exists(full + ".html"):
                return full + ".html"

        return full

    def send_error(self, code, message=None, explain=None):
        """Return the site's own 404 page instead of the stdlib one."""
        if code == 404:
            page = os.path.join(ROOT, "404.html")
            try:
                with open(page, "rb") as fh:
                    body = fh.read()
            except OSError:
                super().send_error(code, message, explain)
                return

            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return

        super().send_error(code, message, explain)

    def copyfile(self, source, outputfile):
        """A reloading browser drops connections; that is not an error."""
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, fmt, *args):
        sys.stdout.write("%s  %s\n" % (self.address_string(), fmt % args))
        sys.stdout.flush()


def main():
    if not os.path.isdir(ROOT):
        sys.exit("docs/ was not found next to this script: %s" % ROOT)

    server = ThreadingHTTPServer((HOST, PORT), PreviewHandler)
    pages = sorted(
        f[: -len(".html")] for f in os.listdir(ROOT) if f.endswith(".html")
    )
    print("Just Apps preview")
    print("  serving %s" % os.path.abspath(ROOT))
    print("  http://localhost:%d  (binds %s)" % (PORT, HOST))
    print("  pages: %s" % ", ".join("/" + p.replace("index", "") for p in pages))
    print("  press Ctrl+C to stop")
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
