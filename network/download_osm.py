"""Download the Geofabrik GCC-states extract with streaming + resume.

Usage: python network/download_osm.py [url]
Writes network/raw/gcc-states-latest.osm.pbf and network/raw/download_info.json
"""
import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
os.makedirs(RAW, exist_ok=True)

URL = sys.argv[1] if len(sys.argv) > 1 else "https://download.geofabrik.de/asia/gcc-states-latest.osm.pbf"
OUT = os.path.join(RAW, os.path.basename(URL))
PART = OUT + ".part"


def main():
    sess = requests.Session()
    sess.headers["User-Agent"] = "oman-map-demo/1.0 (research; SUMO network build)"
    total = None
    last_modified = None
    for attempt in range(1, 31):
        have = os.path.getsize(PART) if os.path.exists(PART) else 0
        headers = {"Range": f"bytes={have}-"} if have else {}
        try:
            with sess.get(URL, headers=headers, stream=True, timeout=(30, 300), allow_redirects=True) as r:
                if r.status_code == 416:
                    break
                r.raise_for_status()
                last_modified = r.headers.get("Last-Modified", last_modified)
                if r.status_code == 206:
                    cr = r.headers.get("Content-Range", "")
                    if "/" in cr:
                        total = int(cr.split("/")[-1])
                    mode = "ab"
                else:
                    total = int(r.headers.get("Content-Length", 0)) or None
                    have = 0
                    mode = "wb"
                print(f"attempt {attempt}: status {r.status_code}, resume at {have}, total {total}", flush=True)
                t0 = time.time()
                last_print = t0
                with open(PART, mode) as f:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        if chunk:
                            f.write(chunk)
                            have += len(chunk)
                            if time.time() - last_print > 15:
                                rate = have / max(time.time() - t0, 1e-3) / 1e6
                                print(f"  {have/1e6:.1f} MB / {total/1e6 if total else 0:.1f} MB", flush=True)
                                last_print = time.time()
            if total is None or os.path.getsize(PART) >= total:
                break
        except Exception as e:  # noqa
            print(f"attempt {attempt} failed: {e!r}", flush=True)
            time.sleep(min(60, 5 * attempt))
    size = os.path.getsize(PART)
    if total and size < total:
        print(f"INCOMPLETE {size}/{total}")
        sys.exit(1)
    os.replace(PART, OUT)
    info = {"url": URL, "file": OUT, "bytes": size, "http_last_modified": last_modified,
            "downloaded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(os.path.join(RAW, "download_info.json"), "w") as f:
        json.dump(info, f, indent=2)
    print("DONE", json.dumps(info))


if __name__ == "__main__":
    main()
