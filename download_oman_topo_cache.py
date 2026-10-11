"""
Pre-caches High-Resolution Topographic & Hillshade Tiles for Oman.
Enables 100% offline topographic elevation terrain viewing with high resolution:
- Country-wide coverage: Zoom 5 to 9
- High-res mountain coverage (Al Hajar, Dhofar, Musandam): Zoom 10 to 11
"""
import os
import math
import time
from pathlib import Path
import requests

CACHE_ROOT = Path(__file__).parent / "cache" / "tiles"

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def download_tile(source: str, z: int, x: int, y: int, session: requests.Session) -> bool:
    target_path = CACHE_ROOT / source / str(z) / str(x) / f"{y}.png"
    if target_path.exists() and target_path.stat().st_size > 1000:
        return True

    if source == "opentopo":
        sub = ["a", "b", "c"][(x + y) % 3]
        url = f"https://{sub}.tile.opentopomap.org/{z}/{x}/{y}.png"
    elif source == "hillshade":
        url = f"https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}"
    elif source == "google_terrain":
        url = f"https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"
    elif source == "esri_topo":
        url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
    else:
        return False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) OmanTopoOffline/1.0"
    }

    try:
        resp = session.get(url, headers=headers, timeout=6)
        if resp.status_code == 200 and len(resp.content) > 500:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(resp.content)
            return True
        return False
    except Exception:
        return False

def cache_bbox(name: str, min_lat: float, min_lon: float, max_lat: float, max_lon: float, zooms, sources):
    session = requests.Session()
    print(f"\n--- Caching {name} ---")
    for z in zooms:
        x1, y2 = deg2num(min_lat, min_lon, z)
        x2, y1 = deg2num(max_lat, max_lon, z)
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        num_tiles = (max_x - min_x + 1) * (max_y - min_y + 1)
        print(f"Zoom {z} ({num_tiles} tiles/source): x=[{min_x}..{max_x}], y=[{min_y}..{max_y}]")

        for source in sources:
            cnt = 0
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    if download_tile(source, z, x, y, session):
                        cnt += 1
                    time.sleep(0.015)
            print(f"  [{source}] {cnt}/{num_tiles} cached")

if __name__ == "__main__":
    srcs = ["opentopo", "hillshade", "google_terrain"]
    # 1. Country-wide Zoom 9
    cache_bbox("Oman Nationwide (Zoom 9)", 16.5, 52.0, 26.5, 60.0, [9], srcs)
    # 2. Al Hajar Mountain Range (Jabal Shams, Jabal Akhdar, Wadi Ghul) Zoom 10-11
    cache_bbox("Al Hajar High Mountains (Shams & Akhdar)", 22.8, 56.8, 23.6, 58.0, [10, 11], srcs)
    # 3. Dhofar Escarpment & Jabal Samhan Zoom 10-11
    cache_bbox("Dhofar Mountain Escarpment (Samhan & Qara)", 16.9, 53.8, 17.5, 55.2, [10, 11], srcs)
    # 4. Musandam Peninsula (Fjords & Jabal Harim) Zoom 10-11
    cache_bbox("Musandam Fjords & Jabal Harim", 25.6, 56.1, 26.4, 56.5, [10, 11], srcs)
    print("\nAll target Oman topographic terrain tiles cached successfully!")
