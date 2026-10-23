#!/usr/bin/env python3
"""Interactive Mobile App Viewport server for Namaaz Reminder (v1.6.1).

Serves `design/mobile_viewport/index.html` together with the real Android APK
drawable assets (`app/src/main/res/drawable-xxxhdpi/ic_app_icon.png` and
`app/src/main/res/drawable-nodpi/leather_black_tile.png`) so the exact mobile UI
can be inspected interactively in Arena's Live Preview viewport.
"""

import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWPORT_DIR = os.path.join(REPO_ROOT, "design", "mobile_viewport")
RES_DIR = os.path.join(REPO_ROOT, "app", "src", "main", "res")
FONTS_DIR = os.path.join(REPO_ROOT, "docs", "assets", "fonts")

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))

ASSET_MAP = {
    "/res/ic_app_icon.png": (
        os.path.join(RES_DIR, "drawable-xxxhdpi", "ic_app_icon.png"),
        "image/png",
    ),
    "/res/leather_black_tile.png": (
        os.path.join(RES_DIR, "drawable-nodpi", "leather_black_tile.png"),
        "image/png",
    ),
    "/favicon.ico": (
        os.path.join(REPO_ROOT, "docs", "favicon.ico"),
        "image/x-icon",
    ),
}


class ViewportHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self._serve(head_only=True)

    def do_GET(self):
        self._serve(head_only=False)

    def _serve(self, head_only: bool):
        parsed = urllib.parse.urlparse(self.path).path
        if parsed in ("/", "/index.html"):
            target = os.path.join(VIEWPORT_DIR, "index.html")
            ctype = "text/html; charset=utf-8"
        elif parsed in ASSET_MAP:
            target, ctype = ASSET_MAP[parsed]
        elif parsed.startswith("/fonts/"):
            fname = os.path.basename(parsed)
            target = os.path.join(FONTS_DIR, fname)
            ctype = "font/woff2"
        else:
            target = os.path.join(VIEWPORT_DIR, "index.html")
            ctype = "text/html; charset=utf-8"

        if not os.path.isfile(target):
            self.send_response(404)
            self.end_headers()
            return

        with open(target, "rb") as fh:
            data = fh.read()

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if not head_only:
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

    def log_message(self, fmt, *args):
        sys.stdout.write("%s  %s\n" % (self.address_string(), fmt % args))
        sys.stdout.flush()


def main():
    server = ThreadingHTTPServer((HOST, PORT), ViewportHandler)
    print(f"Namaaz Reminder Mobile Viewport listening on http://{HOST}:{PORT}")
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
