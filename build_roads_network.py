"""
Extracts, simplifies, and optimizes the Sultanate of Oman road network from HOT OSM Shapefile.
Generates:
1. data/oman_roads_highways.json (Motorways, Trunks, Primary Highways)
2. data/oman_roads_secondary.json (Secondary & Regional Arterials)
"""
import sys
import json
from pathlib import Path
import shapefile
from shapely.geometry import shape, mapping

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).parent / "data"
SHP_FILE = DATA_DIR / "hotosm_roads" / "roads_lines.shp"

def classify_road(hw_type: str, lanes_val, name: str) -> dict:
    hw = (hw_type or "").lower()
    
    # Speed limit & styling heuristics for Oman ROP highway standards
    if hw in ["motorway", "motorway_link"]:
        category = "Expressway (طريق سريع مزدوج)"
        speed = 120
        color = "#f59e0b"  # Amber gold
        weight = 3.6
        dash = None
    elif hw in ["trunk", "trunk_link"]:
        category = "National Highway (طريق وطني رئيسي)"
        speed = 100
        color = "#3b82f6"  # Royal blue
        weight = 3.0
        dash = None
    elif hw in ["primary", "primary_link"]:
        category = "Primary Arterial (طريق شرياني)"
        speed = 100
        color = "#10b981"  # Emerald
        weight = 2.6
        dash = None
    elif hw in ["secondary", "secondary_link"]:
        category = "Secondary Regional (طريق ثانوي إقليمي)"
        speed = 80
        color = "#a855f7"  # Purple
        weight = 2.0
        dash = None
    elif hw in ["tertiary", "tertiary_link"]:
        category = "Tertiary Connector (طريق فرعي رابط)"
        speed = 60
        color = "#94a3b8"  # Slate
        weight = 1.6
        dash = "4, 4"
    else:
        category = "Local Road (طريق محلي)"
        speed = 50
        color = "#64748b"
        weight = 1.2
        dash = None

    try:
        lanes = int(lanes_val) if lanes_val else (4 if speed >= 100 else 2)
    except Exception:
        lanes = 4 if speed >= 100 else 2

    return {
        "category": category,
        "speed_limit_kmh": speed,
        "lanes": lanes,
        "color": color,
        "weight": weight,
        "dash": dash
    }

def clean_str(val) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s.lower() in ["none", "null", "nan"] else s

def build_roads():
    print(f"Reading shapefile: {SHP_FILE}...")
    sf = shapefile.Reader(str(SHP_FILE), encoding="utf-8")
    
    highway_features = []
    secondary_features = []

    hw_types = {"motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link"}
    sec_types = {"secondary", "secondary_link", "tertiary"}

    total_read = 0
    skipped_small = 0

    for feat in sf.iterShapeRecords():
        total_read += 1
        r = feat.record
        hw = (r["highway"] or "").lower()

        if hw not in hw_types and hw not in sec_types:
            continue

        raw_geom = feat.shape.__geo_interface__
        geom_obj = shape(raw_geom)

        # Simplify lines to optimize web rendering performance
        # 0.0003 deg ~ 30 meters tolerance
        simp_geom = geom_obj.simplify(0.0003, preserve_topology=True)
        if simp_geom.is_empty or simp_geom.length < 0.0005:
            skipped_small += 1
            continue

        name = clean_str(r["name"])
        name_ar = clean_str(r["name_ar"])
        name_en = clean_str(r["name_en"]) or clean_str(r["name_latin"])

        # Display name logic
        display_name = name or name_en or name_ar or f"Oman {hw.capitalize()} Corridor"
        display_name_ar = name_ar or name or display_name

        classification = classify_road(hw, r["lanes"], display_name)

        # Coordinate rounding to 5 decimal places (~1m precision)
        geom_dict = mapping(simp_geom)
        if geom_dict["type"] == "LineString":
            geom_dict["coordinates"] = [[round(c[0], 5), round(c[1], 5)] for c in geom_dict["coordinates"]]
        elif geom_dict["type"] == "MultiLineString":
            geom_dict["coordinates"] = [[[round(c[0], 5), round(c[1], 5)] for c in line] for line in geom_dict["coordinates"]]

        props = {
            "id": f"OM-RD-{r['id']}",
            "name": display_name,
            "name_ar": display_name_ar,
            "name_en": name_en or display_name,
            "highway": hw,
            "category": classification["category"],
            "speed_limit_kmh": classification["speed_limit_kmh"],
            "lanes": classification["lanes"],
            "surface": clean_str(r["surface"]) or "asphalt",
            "oneway": clean_str(r["oneway"]),
            "governorate": clean_str(r["adm1_name"]),
            "wilayat": clean_str(r["adm2_name"]),
            "color": classification["color"],
            "weight": classification["weight"],
            "dash": classification["dash"]
        }

        geojson_feature = {
            "type": "Feature",
            "properties": props,
            "geometry": geom_dict
        }

        if hw in hw_types:
            highway_features.append(geojson_feature)
        else:
            secondary_features.append(geojson_feature)

        if total_read % 25000 == 0:
            print(f"Processed {total_read} features... (Highways: {len(highway_features)}, Secondary: {len(secondary_features)})")

    print(f"\nFinal Road Counts:")
    print(f"  -> Highways & Expressways: {len(highway_features)} segments")
    print(f"  -> Secondary & Regional: {len(secondary_features)} segments")

    hw_out = DATA_DIR / "oman_roads_highways.json"
    with open(hw_out, "w", encoding="utf-8") as f:
        json.dump({
            "type": "FeatureCollection",
            "features": highway_features
        }, f, ensure_ascii=False)
    print(f"Saved: {hw_out} ({round(hw_out.stat().st_size / (1024*1024), 2)} MB)")

    sec_out = DATA_DIR / "oman_roads_secondary.json"
    with open(sec_out, "w", encoding="utf-8") as f:
        json.dump({
            "type": "FeatureCollection",
            "features": secondary_features
        }, f, ensure_ascii=False)
    print(f"Saved: {sec_out} ({round(sec_out.stat().st_size / (1024*1024), 2)} MB)")

if __name__ == "__main__":
    build_roads()
