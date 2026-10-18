#!/usr/bin/env python3
"""Fetches the master app icon and probes the azaan library.

The assets live in a public Supabase storage bucket. The script is meant to be
run on CI (the app's own sandbox cannot reach the bucket):

  * downloads the master app icon into ``assets/NR-icon.png``
  * probes the azaan folder and writes every file that exists into
    ``assets/azaan-index.json`` (name, url, size and content type)

Run it with:

    python3 scripts/fetch_assets.py
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request

PROJECT = "oxtqzqynhtybrgushmjp.supabase.co"
BUCKET = "Just Apps"
FOLDER = "Namaaz reminder"
PUBLIC_BASE = f"https://{PROJECT}/storage/v1/object/public/"

ICON_FILE = "NR icon.png"

# Names that may exist in the azaan folder. Every candidate is probed with a
# HEAD request, so a name that does not exist costs nothing.
AZAAN_CANDIDATES = [
    "Madinah Azaan.mp3",
    "Madina Azaan.mp3",
    "Madinah Azan.mp3",
    "Madina Azan.mp3",
    "Medina Azaan.mp3",
    "Makkah Azaan.mp3",
    "Makka Azaan.mp3",
    "Makkah Azan.mp3",
    "Makka Azan.mp3",
    "Mecca Azaan.mp3",
    "Iqama Azaan.mp3",
    "Iqamah Azaan.mp3",
    "Azaan.mp3",
    "azan.mp3",
    "Adhan.mp3",
    "Athaan.mp3",
    "Call to Prayer.mp3",
    "Namaaz Azaan.mp3",
    "Namaz Azaan.mp3",
    "Azan Makkah.mp3",
    "Azan Madinah.mp3",
    "Fajr Azaan.mp3",
    "Maghrib Azaan.mp3",
    "Isha Azaan.mp3",
    "Allah.mp3",
    "Tasbeeh.mp3",
    "Dua.mp3",
]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT, "assets")
TIMEOUT_SECONDS = 60


def public_url(file_name: str) -> str:
    return (
        PUBLIC_BASE
        + urllib.parse.quote(BUCKET, safe="")
        + "/"
        + urllib.parse.quote(FOLDER, safe="")
        + "/"
        + urllib.parse.quote(file_name, safe="")
    )


def head(url: str):
    """Returns (status, content-length, content-type) or (0, None, None)."""
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return (
                response.status,
                response.headers.get("Content-Length"),
                response.headers.get("Content-Type"),
            )
    except urllib.error.HTTPError as error:
        return error.code, None, None
    except Exception:
        return 0, None, None


def download(url: str, destination: str) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": "NamaazReminder/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            data = response.read()
    except Exception as error:  # noqa: BLE001 - the CI step reports the error
        print(f"  ! download failed: {error}")
        return False
    with open(destination, "wb") as handle:
        handle.write(data)
    print(f"  + {os.path.basename(destination)} ({len(data)} bytes)")
    return True


def main() -> None:
    os.makedirs(ASSETS_DIR, exist_ok=True)

    print(f"Probing {BUCKET}/{FOLDER} ...")
    found = []
    for candidate in AZAAN_CANDIDATES:
        url = public_url(candidate)
        status, length, content_type = head(url)
        if status == 200:
            print(f"  + {candidate} ({length} bytes, {content_type})")
            found.append(
                {
                    "file": candidate,
                    "url": url,
                    "size": int(length) if length and length.isdigit() else None,
                    "contentType": content_type,
                }
            )
        else:
            print(f"  - {candidate} (HTTP {status})")

    index = {
        "baseUrl": public_url(""),
        "sounds": found,
    }
    with open(os.path.join(ASSETS_DIR, "azaan-index.json"), "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"Wrote {len(found)} azaan file(s) to assets/azaan-index.json")

    icon_path = os.path.join(ASSETS_DIR, "NR-icon.png")
    print("Downloading the master icon ...")
    if not download(public_url(ICON_FILE), icon_path):
        raise SystemExit("Could not download the master app icon")


if __name__ == "__main__":
    main()
