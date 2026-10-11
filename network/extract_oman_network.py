"""Extract complete navigable Oman road network from GCC OSM PBF.

Filters vehicle-drivable highway ways within Oman's sovereign boundaries (buffered ~330m),
preserves all junction nodes, turn restrictions (type=restriction), motorway exits,
signals, and speed attributes.

Outputs:
- network/oman_roads.osm.gz (OSM XML compressed, ready for SUMO netconvert)
- network/extracted_stats.json (detailed statistics)
"""
import os
import sys
import json
import time
import math
import shapely.geometry as sg
from shapely.prepared import prep
import osmium

# Configure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PBF_PATH = os.path.join(HERE, "raw", "gcc-states-latest.osm.pbf")
BOUNDARIES_PATH = os.path.join(ROOT, "data", "oman_boundaries.json")
OUT_OSM_GZ = os.path.join(HERE, "oman_roads.osm.gz")
STATS_PATH = os.path.join(HERE, "extracted_stats.json")

DRIVABLE_HIGHWAYS = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "unclassified", "residential", "living_street", "service", "track", "road",
    "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link"
}

def haversine_km(lon1, lat1, lon2, lat2):
    R = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

def main():
    t_start = time.time()
    print("=== Step 1: Loading Sovereign Boundary ===", flush=True)
    with open(BOUNDARIES_PATH, "r", encoding="utf-8") as f:
        bdata = json.load(f)

    oman_feat = next(f for f in bdata["features"] if f["properties"].get("admin_level") == 2)
    raw_poly = sg.shape(oman_feat["geometry"])
    # 0.003 deg buffer (~330m) to preserve border posts and connecting highways
    buffered_poly = raw_poly.buffer(0.003)
    prep_poly = prep(buffered_poly)
    bbox = buffered_poly.bounds
    print(f"Loaded boundary MultiPolygon. BBox: {bbox}", flush=True)

    kept_way_ids = osmium.index.IdSet()
    needed_node_ids = osmium.index.IdSet()
    kept_relation_ids = osmium.index.IdSet()

    class Pass1WayCollector(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.total_ways_scanned = 0
            self.way_stats = {}
            self.surface_stats = {}
            self.total_km = 0.0
            self.km_by_class = {}
            self.km_by_surface = {}
            self.roundabout_ways = 0
            self.t0 = time.time()
            self.last_log = time.time()

        def way(self, w):
            self.total_ways_scanned += 1
            hw = w.tags.get("highway")
            if hw not in DRIVABLE_HIGHWAYS:
                return

            # Check if any valid node falls inside Oman boundary
            in_oman = False
            way_coords = []
            try:
                for n in w.nodes:
                    if not n.location.valid():
                        continue
                    lon = n.location.lon
                    lat = n.location.lat
                    way_coords.append((lon, lat, n.ref))
                    if not in_oman and bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]:
                        if prep_poly.intersects(sg.Point(lon, lat)):
                            in_oman = True
            except Exception:
                return

            if not in_oman:
                return

            kept_way_ids.set(w.id)
            for lon, lat, nid in way_coords:
                needed_node_ids.set(nid)

            # Compute length
            length_km = 0.0
            for i in range(len(way_coords) - 1):
                length_km += haversine_km(way_coords[i][0], way_coords[i][1],
                                         way_coords[i+1][0], way_coords[i+1][1])

            self.total_km += length_km
            self.way_stats[hw] = self.way_stats.get(hw, 0) + 1
            self.km_by_class[hw] = self.km_by_class.get(hw, 0.0) + length_km

            surf = w.tags.get("surface", "unspecified").lower()
            if surf in ("asphalt", "paved", "concrete", "paving_stones"):
                s_cat = "paved_asphalt"
            elif surf in ("unpaved", "dirt", "ground", "sand", "gravel", "earth", "rock"):
                s_cat = "unpaved_track"
            else:
                s_cat = "unspecified"
            self.surface_stats[s_cat] = self.surface_stats.get(s_cat, 0) + 1
            self.km_by_surface[s_cat] = self.km_by_surface.get(s_cat, 0.0) + length_km

            if w.tags.get("junction") in ("roundabout", "circular"):
                self.roundabout_ways += 1

            if time.time() - self.last_log > 15:
                print(f"[Pass 1] Scanned {self.total_ways_scanned:,} ways -> Kept {len(kept_way_ids):,} Oman ways ({time.time() - self.t0:.1f}s)", flush=True)
                self.last_log = time.time()

    print("=== Step 2: Pass 1 - Identifying Oman Ways and Nodes ===", flush=True)
    p1 = Pass1WayCollector()
    p1.apply_file(PBF_PATH, locations=True)
    print(f"[Pass 1 Complete] Kept {len(kept_way_ids):,} ways, {len(needed_node_ids):,} nodes in {time.time() - p1.t0:.1f}s", flush=True)

    print("=== Step 3: Pass 1.5 - Collecting Turn Restrictions ===", flush=True)
    restriction_stats = {}
    class RestrictionCollector(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.count = 0

        def relation(self, r):
            if r.tags.get("type") != "restriction":
                return
            restr_type = r.tags.get("restriction", "unknown")
            # Check members
            has_from = False
            has_to = False
            via_nodes = []
            for m in r.members:
                if m.role == "from" and m.type == "w" and m.ref in kept_way_ids:
                    has_from = True
                elif m.role == "to" and m.type == "w" and m.ref in kept_way_ids:
                    has_to = True
                elif m.role == "via" and m.type == "n":
                    via_nodes.append(m.ref)

            if has_from and has_to:
                kept_relation_ids.set(r.id)
                self.count += 1
                restriction_stats[restr_type] = restriction_stats.get(restr_type, 0) + 1
                for vn in via_nodes:
                    needed_node_ids.set(vn)

    r_col = RestrictionCollector()
    r_col.apply_file(PBF_PATH)
    print(f"Kept {r_col.count} turn restriction relations.", flush=True)

    print("=== Step 4: Pass 2 - Writing Oman OSM XML (Compressed) ===", flush=True)
    t_write = time.time()
    writer = osmium.SimpleWriter(OUT_OSM_GZ)

    written_nodes = 0
    written_ways = 0
    written_relations = 0
    node_tag_stats = {"traffic_signals": 0, "motorway_junction": 0, "crossing": 0, "turning_circle": 0, "stop": 0, "give_way": 0}

    class WriterHandler(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.last_log = time.time()

        def node(self, n):
            nonlocal written_nodes
            if n.id in needed_node_ids:
                writer.add_node(n)
                written_nodes += 1
                hw = n.tags.get("highway")
                if hw in node_tag_stats:
                    node_tag_stats[hw] += 1
                if time.time() - self.last_log > 15:
                    print(f"[Pass 2 Nodes] Written {written_nodes:,} nodes ({time.time() - t_write:.1f}s)", flush=True)
                    self.last_log = time.time()

        def way(self, w):
            nonlocal written_ways
            if w.id in kept_way_ids:
                writer.add_way(w)
                written_ways += 1
                if time.time() - self.last_log > 15:
                    print(f"[Pass 2 Ways] Written {written_ways:,} ways ({time.time() - t_write:.1f}s)", flush=True)
                    self.last_log = time.time()

        def relation(self, r):
            nonlocal written_relations
            if r.id in kept_relation_ids:
                writer.add_relation(r)
                written_relations += 1

    wh = WriterHandler()
    wh.apply_file(PBF_PATH)
    writer.close()
    out_size = os.path.getsize(OUT_OSM_GZ)
    print(f"[Pass 2 Complete] Written to {OUT_OSM_GZ} ({out_size / (1024*1024):.2f} MB) in {time.time() - t_write:.1f}s", flush=True)
    print(f"Summary: {written_nodes:,} nodes, {written_ways:,} ways, {written_relations:,} relations.", flush=True)

    stats = {
        "source_pbf": PBF_PATH,
        "output_file": OUT_OSM_GZ,
        "output_size_bytes": out_size,
        "total_nodes": written_nodes,
        "total_ways": written_ways,
        "total_relations": written_relations,
        "total_road_km": round(p1.total_km, 2),
        "ways_by_class": p1.way_stats,
        "km_by_class": {k: round(v, 2) for k, v in sorted(p1.km_by_class.items(), key=lambda x: -x[1])},
        "ways_by_surface": p1.surface_stats,
        "km_by_surface": {k: round(v, 2) for k, v in sorted(p1.km_by_surface.items(), key=lambda x: -x[1])},
        "roundabout_ways": p1.roundabout_ways,
        "node_features": node_tag_stats,
        "turn_restrictions": restriction_stats,
        "elapsed_seconds": round(time.time() - t_start, 2)
    }

    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Stats written to {STATS_PATH}. Total pipeline time: {stats['elapsed_seconds']}s")

if __name__ == "__main__":
    main()
