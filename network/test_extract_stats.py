"""Test extraction logic on gcc-states-latest.osm.pbf to get counts and execution time.
"""
import json
import time
import os
import shapely.geometry as sg
from shapely.prepared import prep
import osmium

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PBF_PATH = os.path.join(HERE, "raw", "gcc-states-latest.osm.pbf")
BOUNDARIES_PATH = os.path.join(ROOT, "data", "oman_boundaries.json")

DRIVABLE_HIGHWAYS = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "unclassified", "residential", "living_street", "service", "track", "road",
    "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link"
}

print("Loading boundary...")
with open(BOUNDARIES_PATH, "r", encoding="utf-8") as f:
    bdata = json.load(f)

oman_feat = next(f for f in bdata["features"] if f["properties"].get("admin_level") == 2)
raw_poly = sg.shape(oman_feat["geometry"])
buffered_poly = raw_poly.buffer(0.003) # ~330m buffer
prep_poly = prep(buffered_poly)
bbox = buffered_poly.bounds # minx, miny, maxx, maxy
print(f"Boundary loaded. BBox: {bbox}")

class WayCollector(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.way_count = 0
        self.oman_ways = 0
        self.by_class = {}
        self.t0 = time.time()
        self.last_log = time.time()

    def way(self, w):
        self.way_count += 1
        hw = w.tags.get("highway")
        if hw not in DRIVABLE_HIGHWAYS:
            return

        # Fast rejection by way's nodes
        # If no nodes have valid locations or none in bbox, skip
        has_node_in_oman = False
        try:
            for n in w.nodes:
                if not n.location.valid():
                    continue
                lon = n.location.lon
                lat = n.location.lat
                if bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]:
                    # Check prepared geometry
                    pt = sg.Point(lon, lat)
                    if prep_poly.intersects(pt):
                        has_node_in_oman = True
                        break
        except Exception:
            return

        if has_node_in_oman:
            self.oman_ways += 1
            self.by_class[hw] = self.by_class.get(hw, 0) + 1

        if time.time() - self.last_log > 15:
            print(f"Scanned {self.way_count} ways... Oman ways found: {self.oman_ways} ({time.time() - self.t0:.1f}s)", flush=True)
            self.last_log = time.time()

collector = WayCollector()
print("Starting pass 1 scan with locations=True...")
collector.apply_file(PBF_PATH, locations=True)
print(f"Finished in {time.time() - collector.t0:.1f}s!")
print(f"Total Oman drivable ways: {collector.oman_ways}")
for k, v in sorted(collector.by_class.items(), key=lambda x: -x[1]):
    print(f"  {k:20s}: {v:,}")
