"""
Comprehensive Road & Track Extractor for the Sultanate of Oman.
Extracts:
1. data/oman_roads_tracks.json (Dirt roads, wadi tracks, unpaved desert trails)
2. data/oman_roads_residential.json (Neighborhood streets and service alleys for Muscat & urban centers)
"""
import sys
import json
import os
from pathlib import Path
import shapefile
from shapely.geometry import shape, mapping

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path(__file__).parent / "data"
SHP_FILE = DATA_DIR / "hotosm_roads" / "roads_lines.shp"

def extract_tracks_and_neighborhoods():
    print("Reading HOT OSM shapefile...")
    sf = shapefile.Reader(str(SHP_FILE), encoding="utf-8")

    tracks = []
    neighborhoods = []

    for feat in sf.iterShapeRecords():
        r = feat.record
        hw = (r["highway"] or "").lower()
        surf = (r["surface"] or "").lower()

        is_track = hw in ["track", "path"] or surf in ["unpaved", "gravel", "sand", "ground", "dirt"]
        is_residential = hw in ["residential", "living_street", "service"]

        if not is_track and not is_residential:
            continue

        raw_geom = feat.shape.__geo_interface__
        geom_obj = shape(raw_geom)
        
        # Simplify slightly to preserve high resolution while maintaining fast web rendering
        # 0.0003 deg ~ 30 meters
        simp = geom_obj.simplify(0.0003, preserve_topology=True)
        if simp.is_empty or simp.length < 0.0003:
            continue

        name = (r["name"] or "").strip()
        name_ar = (r["name_ar"] or name).strip()
        name_en = (r["name_en"] or r["name_latin"] or name).strip()

        coords = mapping(simp)
        if coords["type"] == "LineString":
            coords["coordinates"] = [[round(c[0], 5), round(c[1], 5)] for c in coords["coordinates"]]
        elif coords["type"] == "MultiLineString":
            coords["coordinates"] = [[[round(c[0], 5), round(c[1], 5)] for c in line] for line in coords["coordinates"]]

        if is_track:
            display_name = name or name_en or "Wadi / Desert Dirt Track"
            display_ar = name_ar or "مدق وادي / طريق ترابي صحراوي"
            tracks.append({
                "type": "Feature",
                "properties": {
                    "id": f"TRK-{r['id']}",
                    "name": display_name,
                    "name_ar": display_ar,
                    "name_en": name_en or display_name,
                    "highway": "track",
                    "category": "Dirt / Wadi Track (طريق ترابي / صحراوي)",
                    "surface": surf if surf else "unpaved",
                    "speed_limit_kmh": 40,
                    "requires_4wd": True,
                    "governorate": r["adm1_name"] or "",
                    "wilayat": r["adm2_name"] or "",
                    "color": "#d97706",  # Amber brown
                    "weight": 1.5,
                    "dash": "4, 4"
                },
                "geometry": coords
            })
        elif is_residential:
            # We capture residential streets (prioritizing named streets or urban centers)
            # If unnamed, we give proper neighborhood context
            display_name = name or name_en or "Local Neighborhood Street"
            display_ar = name_ar or "شارع حي سكني"
            neighborhoods.append({
                "type": "Feature",
                "properties": {
                    "id": f"RES-{r['id']}",
                    "name": display_name,
                    "name_ar": display_ar,
                    "name_en": name_en or display_name,
                    "highway": hw,
                    "category": "Neighborhood Street (شارع حي سكني)",
                    "surface": surf if surf else "asphalt",
                    "speed_limit_kmh": 50,
                    "governorate": r["adm1_name"] or "",
                    "wilayat": r["adm2_name"] or "",
                    "color": "#94a3b8",  # Slate
                    "weight": 1.2,
                    "dash": None
                },
                "geometry": coords
            })

    print(f"Extracted {len(tracks):,} dirt & wadi tracks.")
    print(f"Extracted {len(neighborhoods):,} neighborhood & residential streets.")

    # Save tracks GeoJSON
    track_file = DATA_DIR / "oman_roads_tracks.json"
    with open(track_file, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": tracks}, f, ensure_ascii=False)
    print(f"Saved: {track_file} ({round(os.path.getsize(track_file)/(1024*1024), 2)} MB)")

    # For residential streets, sample/extract primary urban neighborhood networks (~15,000 top segments)
    # to maintain high-performance in Leaflet without crashing browser RAM
    res_file = DATA_DIR / "oman_roads_residential.json"
    # Prioritize named streets or high-density areas
    named_res = [f for f in neighborhoods if f["properties"]["name"] != "Local Neighborhood Street"]
    unnamed_res = [f for f in neighborhoods if f["properties"]["name"] == "Local Neighborhood Street"]
    selected_res = named_res + unnamed_res[:10000]

    with open(res_file, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": selected_res}, f, ensure_ascii=False)
    print(f"Saved: {res_file} ({len(selected_res):,} features, {round(os.path.getsize(res_file)/(1024*1024), 2)} MB)")

if __name__ == "__main__":
    extract_tracks_and_neighborhoods()
