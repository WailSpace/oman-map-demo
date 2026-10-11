"""Export network features to GeoJSON and SQLite with R*Tree spatial indexing.

Outputs:
- network/features/roundabouts.geojson
- network/features/traffic_signals.geojson
- network/features/motorway_exits.geojson
- network/features/uturns.geojson
- network/oman_network.sqlite (R*Tree indexed for sub-millisecond bbox queries)
"""
import os
import sys
import json
import sqlite3
import time
import osmium
import shapely.geometry as sg

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
OSM_GZ = os.path.join(HERE, "oman_roads.osm.gz")
FEAT_DIR = os.path.join(HERE, "features")
os.makedirs(FEAT_DIR, exist_ok=True)
SQLITE_PATH = os.path.join(HERE, "oman_network.sqlite")

# Zoom thresholds by road class
ZOOM_THRESHOLDS = {
    "motorway": 8,
    "motorway_link": 10,
    "trunk": 9,
    "trunk_link": 11,
    "primary": 10,
    "primary_link": 12,
    "secondary": 11,
    "secondary_link": 12,
    "tertiary": 12,
    "tertiary_link": 13,
    "unclassified": 13,
    "track": 13,
    "residential": 14,
    "service": 14,
    "living_street": 14,
    "road": 13
}

def main():
    t0 = time.time()
    print("=== Step 1: Initializing SQLite R*Tree Database ===", flush=True)
    if os.path.exists(SQLITE_PATH):
        os.remove(SQLITE_PATH)

    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE edges (
            id TEXT PRIMARY KEY,
            osm_id INTEGER,
            class TEXT,
            name TEXT,
            name_ar TEXT,
            name_en TEXT,
            ref TEXT,
            surface TEXT,
            lanes INTEGER,
            speed REAL,
            oneway INTEGER,
            is_roundabout INTEGER,
            min_zoom INTEGER,
            geojson TEXT
        );
    """)

    cur.execute("""
        CREATE VIRTUAL TABLE edges_rtree USING rtree(
            id_int,
            minX, maxX,
            minY, maxY
        );
    """)

    cur.execute("""
        CREATE TABLE features (
            id TEXT PRIMARY KEY,
            type TEXT,
            name TEXT,
            name_ar TEXT,
            ref TEXT,
            properties TEXT,
            geojson TEXT
        );
    """)

    cur.execute("""
        CREATE VIRTUAL TABLE features_rtree USING rtree(
            id_int,
            minX, maxX,
            minY, maxY
        );
    """)
    conn.commit()

    roundabouts = []
    traffic_signals = []
    motorway_exits = []
    uturns = []

    print("=== Step 2: Parsing oman_roads.osm.gz ===", flush=True)

    edge_rowid = 1
    feature_rowid = 1

    edges_batch = []
    rtree_batch = []
    feat_batch = []
    feat_rtree_batch = []

    class FeatureExtractor(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.nodes_scanned = 0
            self.ways_scanned = 0
            self.last_log = time.time()

        def node(self, n):
            nonlocal feature_rowid, feat_batch, feat_rtree_batch
            self.nodes_scanned += 1
            hw = n.tags.get("highway")
            lon = n.location.lon
            lat = n.location.lat

            if hw == "traffic_signals":
                name = n.tags.get("name", "Traffic Signal")
                traffic_signals.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": {"id": n.id, "type": "traffic_signals", "name": name}
                })
                geom_json = json.dumps({"type": "Point", "coordinates": [lon, lat]})
                props_json = json.dumps({"highway": hw})
                fid = f"node_{n.id}"
                feat_batch.append((fid, "traffic_signal", name, n.tags.get("name:ar", ""), "", props_json, geom_json))
                feat_rtree_batch.append((feature_rowid, lon, lon, lat, lat))
                feature_rowid += 1

            elif hw == "motorway_junction":
                name = n.tags.get("name", "")
                name_ar = n.tags.get("name:ar", "")
                ref = n.tags.get("ref", "")
                display = f"Exit {ref}: {name}" if ref and name else (f"Exit {ref}" if ref else (name or "Motorway Exit"))
                motorway_exits.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": {"id": n.id, "type": "motorway_junction", "name": display, "ref": ref}
                })
                geom_json = json.dumps({"type": "Point", "coordinates": [lon, lat]})
                props_json = json.dumps({"ref": ref, "highway": hw})
                fid = f"exit_{n.id}"
                feat_batch.append((fid, "motorway_exit", display, name_ar, ref, props_json, geom_json))
                feat_rtree_batch.append((feature_rowid, lon, lon, lat, lat))
                feature_rowid += 1

            elif hw in ("turning_circle", "turning_loop"):
                name = "U-Turn / Turning Loop"
                uturns.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "properties": {"id": n.id, "type": hw, "name": name, "detection": "osm_tag"}
                })
                geom_json = json.dumps({"type": "Point", "coordinates": [lon, lat]})
                props_json = json.dumps({"detection": "osm_tag", "highway": hw})
                fid = f"uturn_{n.id}"
                feat_batch.append((fid, "uturn", name, "", "", props_json, geom_json))
                feat_rtree_batch.append((feature_rowid, lon, lon, lat, lat))
                feature_rowid += 1

        def way(self, w):
            nonlocal edge_rowid, feature_rowid, edges_batch, rtree_batch, feat_batch, feat_rtree_batch
            self.ways_scanned += 1
            hw = w.tags.get("highway")
            if not hw:
                return

            coords = []
            try:
                for n in w.nodes:
                    if n.location.valid():
                        coords.append([round(n.location.lon, 6), round(n.location.lat, 6)])
            except Exception:
                return

            if len(coords) < 2:
                return

            # Bounding box of way
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            is_rb = 1 if w.tags.get("junction") in ("roundabout", "circular") else 0
            name = w.tags.get("name", "")
            name_ar = w.tags.get("name:ar", "")
            name_en = w.tags.get("name:en", "")
            ref = w.tags.get("ref", "")
            surf = w.tags.get("surface", "unspecified")

            try:
                lanes = int(w.tags.get("lanes", "1"))
            except ValueError:
                lanes = 1

            try:
                speed_str = w.tags.get("maxspeed", "")
                speed = float(''.join(c for c in speed_str if c.isdigit() or c == '.')) if speed_str else 0.0
            except ValueError:
                speed = 0.0

            oneway = 1 if w.tags.get("oneway") in ("yes", "1", "true") or is_rb else 0
            min_zoom = ZOOM_THRESHOLDS.get(hw, 14)
            if is_rb:
                min_zoom = min(min_zoom, 12)

            geom_dict = {"type": "LineString", "coordinates": coords}
            geom_json = json.dumps(geom_dict)

            wid = str(w.id)
            edges_batch.append((
                wid, w.id, hw, name, name_ar, name_en, ref, surf,
                lanes, speed, oneway, is_rb, min_zoom, geom_json
            ))
            rtree_batch.append((edge_rowid, min_x, max_x, min_y, max_y))
            edge_rowid += 1

            # Roundabout feature
            if is_rb:
                centroid_x = sum(xs) / len(xs)
                centroid_y = sum(ys) / len(ys)
                rb_name = name or (ref and f"Roundabout {ref}") or "Roundabout"
                roundabouts.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [round(centroid_x, 6), round(centroid_y, 6)]},
                    "properties": {"id": w.id, "type": "roundabout", "name": rb_name, "way_id": w.id}
                })
                rb_geom_json = json.dumps({"type": "Point", "coordinates": [round(centroid_x, 6), round(centroid_y, 6)]})
                rb_props = json.dumps({"way_id": w.id, "highway": hw})
                fid = f"rb_{w.id}"
                feat_batch.append((fid, "roundabout", rb_name, name_ar, ref, rb_props, rb_geom_json))
                feat_rtree_batch.append((feature_rowid, centroid_x, centroid_x, centroid_y, centroid_y))
                feature_rowid += 1

            # Detected U-turn slot (short link road connecting opposite divided carriageways)
            if hw in ("trunk_link", "primary_link", "secondary_link") and not is_rb:
                if len(coords) <= 5 and (max_x - min_x) < 0.001 and (max_y - min_y) < 0.001:
                    # Heuristic U-turn median connector
                    u_name = "U-Turn Slot"
                    mid_x = (min_x + max_x) / 2.0
                    mid_y = (min_y + max_y) / 2.0
                    uturns.append({
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [round(mid_x, 6), round(mid_y, 6)]},
                        "properties": {"id": w.id, "type": "uturn_slot", "name": u_name, "detection": "median_link_heuristic"}
                    })
                    u_geom_json = json.dumps({"type": "Point", "coordinates": [round(mid_x, 6), round(mid_y, 6)]})
                    u_props = json.dumps({"detection": "median_link_heuristic", "way_id": w.id})
                    fid = f"uturn_slot_{w.id}"
                    feat_batch.append((fid, "uturn", u_name, "", "", u_props, u_geom_json))
                    feat_rtree_batch.append((feature_rowid, mid_x, mid_x, mid_y, mid_y))
                    feature_rowid += 1

            if len(edges_batch) >= 10000:
                cur.executemany("INSERT OR REPLACE INTO edges VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", edges_batch)
                cur.executemany("INSERT INTO edges_rtree VALUES (?,?,?,?,?)", rtree_batch)
                edges_batch.clear()
                rtree_batch.clear()

            if len(feat_batch) >= 5000:
                cur.executemany("INSERT OR REPLACE INTO features VALUES (?,?,?,?,?,?,?)", feat_batch)
                cur.executemany("INSERT INTO features_rtree VALUES (?,?,?,?,?)", feat_rtree_batch)
                feat_batch.clear()
                feat_rtree_batch.clear()

            if time.time() - self.last_log > 15:
                print(f"Processed {self.ways_scanned:,} ways -> {edge_rowid:,} edges indexed ({time.time() - t0:.1f}s)", flush=True)
                self.last_log = time.time()

    ext = FeatureExtractor()
    ext.apply_file(OSM_GZ, locations=True)

    if edges_batch:
        cur.executemany("INSERT OR REPLACE INTO edges VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", edges_batch)
        cur.executemany("INSERT INTO edges_rtree VALUES (?,?,?,?,?)", rtree_batch)
    if feat_batch:
        cur.executemany("INSERT OR REPLACE INTO features VALUES (?,?,?,?,?,?,?)", feat_batch)
        cur.executemany("INSERT INTO features_rtree VALUES (?,?,?,?,?)", feat_rtree_batch)

    conn.commit()
    conn.close()

    print(f"=== Step 3: Writing GeoJSON Feature Collections ===", flush=True)
    def save_geojson(filename, feats):
        out_path = os.path.join(FEAT_DIR, filename)
        fc = {"type": "FeatureCollection", "features": feats}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fc, f, ensure_ascii=False)
        print(f"Saved {filename} ({len(feats)} features)", flush=True)

    save_geojson("roundabouts.geojson", roundabouts)
    save_geojson("traffic_signals.geojson", traffic_signals)
    save_geojson("motorway_exits.geojson", motorway_exits)
    save_geojson("uturns.geojson", uturns)

    sqlite_size = os.path.getsize(SQLITE_PATH)
    print(f"SQLite DB size: {sqlite_size / (1024*1024):.2f} MB")
    print(f"Completed feature exports and SQLite indexing in {time.time() - t0:.1f}s!", flush=True)

if __name__ == "__main__":
    main()
