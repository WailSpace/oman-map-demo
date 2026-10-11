"""
Extracts genuine high-resolution administrative boundaries from gadm41_OMN.gpkg
and updates data/oman_boundaries.json for the live demo.
"""
import sqlite3
import json
from pathlib import Path
import shapely.wkb
from shapely.geometry import mapping

GPKG_PATH = Path(r"C:\Users\wail\Downloads\gadm41_OMN.gpkg")
OUT_JSON = Path(r"C:\Users\wail\oman-map-demo\data\oman_boundaries.json")

# Bilingual translations for GADM governorate names
AR_NAMES = {
    "Ad Dakhliyah": "الداخلية",
    "Al Batinah North": "شمال الباطنة",
    "Al Batinah South": "جنوب الباطنة",
    "Al Buraymi": "البريمي",
    "Al Dhahira": "الظاهرة",
    "Al Wusta": "الوسطى",
    "Ash Sharqiyah North": "شمال الشرقية",
    "Ash Sharqiyah South": "جنوب الشرقية",
    "Dhofar": "ظفار",
    "Musandam": "مسندم",
    "Muscat": "مسقط"
}

PALETTE = {
    "Muscat": "#e63946",
    "Al Batinah North": "#457b9d",
    "Al Batinah South": "#1d3557",
    "Ad Dakhliyah": "#2a9d8f",
    "Ash Sharqiyah North": "#e76f51",
    "Ash Sharqiyah South": "#f4a261",
    "Al Dhahira": "#8ecae6",
    "Al Buraymi": "#023047",
    "Musandam": "#9b5de5",
    "Al Wusta": "#b5838d",
    "Dhofar": "#588157"
}

def parse_gpkg_geometry(blob: bytes):
    flags = blob[3]
    env_type = (flags >> 1) & 0x07
    env_sizes = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
    offset = 8 + env_sizes.get(env_type, 0)
    return shapely.wkb.loads(blob[offset:])

def run_import():
    conn = sqlite3.connect(GPKG_PATH)
    cur = conn.cursor()
    features = []

    # 1. Level 1: 11 Governorates
    cur.execute("SELECT GID_1, NAME_1, geom FROM ADM_ADM_1")
    for gid, name_en, blob in cur.fetchall():
        geom = parse_gpkg_geometry(blob)
        name_ar = AR_NAMES.get(name_en, name_en)
        features.append({
            "type": "Feature",
            "properties": {
                "id": gid,
                "name_en": name_en,
                "name_ar": name_ar,
                "admin_level": 4,
                "type": "Governorate",
                "color": PALETTE.get(name_en, "#3b82f6")
            },
            "geometry": mapping(geom)
        })

    # 2. Level 2: Wilayats
    cur.execute("SELECT GID_2, NAME_1, NAME_2, geom FROM ADM_ADM_2")
    for gid, gov_en, name_en, blob in cur.fetchall():
        geom = parse_gpkg_geometry(blob)
        features.append({
            "type": "Feature",
            "properties": {
                "id": gid,
                "name_en": name_en,
                "name_ar": name_en,
                "governorate_en": gov_en,
                "governorate_ar": AR_NAMES.get(gov_en, gov_en),
                "admin_level": 6,
                "type": "Wilayat",
                "color": "#ff758f"
            },
            "geometry": mapping(geom)
        })

    print(f"Extracted {len(features)} total features from {GPKG_PATH}")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False)

    print(f"Updated live demo boundaries -> {OUT_JSON}")

if __name__ == "__main__":
    run_import()
