"""
Integrates:
1. geoBoundaries ADM0 (Ultra-high-res National Border: 78k vertices)
2. GADM 4.1 ADM1 (Official 11 Governorates from gadm41_OMN.gpkg)
3. geoBoundaries ADM2 (Official 61 Wilayats from Oman National Geographic Structure)
"""
import sqlite3
import json
import requests
from pathlib import Path
import shapely.wkb
from shapely.geometry import shape, mapping

OUT_PATH = Path(r"C:\Users\wail\oman-map-demo\data\oman_boundaries.json")
GPKG_PATH = Path(r"C:\Users\wail\Downloads\gadm41_OMN.gpkg")

AR_GOVS = {
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

def parse_gpkg_geom(blob: bytes):
    flags = blob[3]
    env_type = (flags >> 1) & 0x07
    env_sizes = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}
    offset = 8 + env_sizes.get(env_type, 0)
    return shapely.wkb.loads(blob[offset:])

def run_pipeline():
    features = []

    # 1. Download geoBoundaries ADM0 (National Sovereign Border)
    print("Fetching geoBoundaries ADM0 (Sovereign Border)...")
    r0 = requests.get("https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/OMN/ADM0/geoBoundaries-OMN-ADM0.geojson", timeout=30)
    data0 = r0.json()
    for f in data0["features"]:
        features.append({
            "type": "Feature",
            "properties": {
                "id": "OMN-NAT",
                "name_en": "Sultanate of Oman",
                "name_ar": "سلطنة عمان",
                "admin_level": 2,
                "type": "National Border",
                "source": "geoBoundaries Open (OSM)"
            },
            "geometry": f["geometry"]
        })

    # 2. Extract 11 Governorates from GADM 4.1
    print("Extracting 11 Governorates from GADM 4.1...")
    conn = sqlite3.connect(GPKG_PATH)
    cur = conn.cursor()
    cur.execute("SELECT GID_1, NAME_1, geom FROM ADM_ADM_1")
    for gid, name_en, blob in cur.fetchall():
        geom = parse_gpkg_geom(blob)
        features.append({
            "type": "Feature",
            "properties": {
                "id": gid,
                "name_en": name_en,
                "name_ar": AR_GOVS.get(name_en, name_en),
                "admin_level": 4,
                "type": "Governorate",
                "color": PALETTE.get(name_en, "#3b82f6"),
                "source": "GADM 4.1"
            },
            "geometry": mapping(geom)
        })

    # 3. Download geoBoundaries ADM2 (61 Wilayats from Oman National Geographic Structure)
    print("Fetching geoBoundaries ADM2 (61 Wilayats)...")
    r2 = requests.get("https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/OMN/ADM2/geoBoundaries-OMN-ADM2.geojson", timeout=30)
    data2 = r2.json()
    for f in data2["features"]:
        props = f["properties"]
        raw_name = props.get("shapeName", "Wilayat")
        clean_name = raw_name.replace("WILAYAT ", "").title()
        features.append({
            "type": "Feature",
            "properties": {
                "id": props.get("shapeID", clean_name),
                "name_en": clean_name,
                "name_ar": clean_name,
                "admin_level": 6,
                "type": "Wilayat",
                "color": "#ff758f",
                "source": "geoBoundaries (Oman National Geographic Structure)"
            },
            "geometry": f["geometry"]
        })

    print(f"Total Combined Features: {len(features)}")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False)
    print(f"Successfully generated clean master dataset -> {OUT_PATH}")

if __name__ == "__main__":
    run_pipeline()
