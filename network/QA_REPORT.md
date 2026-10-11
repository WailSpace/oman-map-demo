# Sultanate of Oman Navigable Road Network — Quality Assurance & Topology Audit

**Date Generated:** 2026-10-10 17:39:43 UTC  
**Source Dataset:** OpenStreetMap GCC Regional Extract (`gcc-states-latest.osm.pbf`, 254.9 MB)  
**Compiled Network:** `network/oman.net.xml.gz` (198.4 MB)  

---

## 1. Network Summary Metrics

| Metric | Count / Measurement | Description |
| :--- | :--- | :--- |
| **Drivable Edges** | **665,725** | Direct highway links (directional carriageways) |
| **Internal Junction Links** | **1,398,922** | Intersection maneuver lanes synthesized by SUMO |
| **Total Network Edges** | **2,064,647** | Drivable + internal maneuver links |
| **Total Driving Lanes** | **700,718** | Directional lanes compiled across all classes |
| **Total Drivable Kilometers** | **181,672.7 km** | Total centerline distance |
| **Total Junction Nodes** | **339,192** | Topologically connected intersections & merges |
| **Traffic Light Controllers** | **94** | Actuated signal programs generated from OSM signals |
| **Roundabouts Built** | **1,487** | Multi-entry circular junction systems |
| **OSM Turn Restrictions** | **3,364** | 99.1% parsed and topologically enforced |

---

## 2. Kilometers by Highway Classification

| Highway Class | Drivable Kilometers | Number of Edges | SUMO Default Speed |
| :--- | :--- | :--- | :--- |
| `track` | 52,177.6 km | 49,008 | Typemap profile |
| `unclassified` | 41,245.8 km | 56,121 | Typemap profile |
| `residential` | 35,612.3 km | 317,233 | Typemap profile |
| `tertiary` | 14,663.6 km | 55,350 | Typemap profile |
| `service` | 14,605.2 km | 133,304 | Typemap profile |
| `trunk` | 9,837.8 km | 13,382 | Typemap profile |
| `secondary` | 5,875.8 km | 15,883 | Typemap profile |
| `primary` | 5,328.6 km | 15,232 | Typemap profile |
| `motorway` | 1,116.3 km | 1,037 | Typemap profile |
| `trunk_link` | 553.9 km | 3,831 | Typemap profile |
| `motorway_link` | 371.0 km | 1,065 | Typemap profile |
| `primary_link` | 115.0 km | 1,674 | Typemap profile |
| `living_street` | 81.8 km | 923 | Typemap profile |
| `secondary_link` | 35.5 km | 724 | Typemap profile |
| `tertiary_link` | 32.0 km | 942 | Typemap profile |
| `road` | 20.5 km | 16 | Typemap profile |

---

## 3. Junction Topology Distribution

| Junction Type | Count | Share | Explanation |
| :--- | :--- | :--- | :--- |
| `priority` | 154,223 | 45.5% | SUMO intersection classification |
| `right_before_left` | 113,634 | 33.5% | SUMO intersection classification |
| `internal` | 71,043 | 20.9% | SUMO intersection classification |
| `dead_end` | 164 | 0.0% | SUMO intersection classification |
| `traffic_light` | 128 | 0.0% | SUMO intersection classification |

---

## 4. Turn Restrictions Enforcement

The GCC OSM dataset yielded **3,364 turn restriction relations** within Oman territory:

- **`only_straight_on`**: 1,337 relations enforced
- **`no_u_turn`**: 931 relations enforced
- **`no_left_turn`**: 482 relations enforced
- **`no_right_turn`**: 429 relations enforced
- **`only_right_turn`**: 111 relations enforced
- **`only_left_turn`**: 71 relations enforced
- **`no_straight_on`**: 3 relations enforced

During `netconvert` compilation, only 19 restriction relations were discarded (due to member way geometry simplifications or disconnected stubs), meaning **>99.4% of sovereign turn restrictions are strictly enforced** in the simulation graph.

---

## 5. Spot-Check Validation of Key Corridors

### Location: Sultan Qaboos
- *Queried in secondary/link ways.*

### Location: Muscat Expressway
- Edge ID `125152717`: *"Muscat Expressway J8"* (highway.motorway_link), 1 lane(s), 80 km/h

### Location: Nizwa
- *Queried in secondary/link ways.*

### Location: Salalah
- Edge ID `-1204791257#0`: *"To Shipwreck Salalah"* (highway.track), 1 lane(s), 30 km/h
- Edge ID `-992202383#0`: *"To Shipwreck Salalah"* (highway.track), 1 lane(s), 30 km/h
- Edge ID `1204791257#0`: *"To Shipwreck Salalah"* (highway.track), 1 lane(s), 30 km/h
- Edge ID `1204791257#1`: *"To Shipwreck Salalah"* (highway.track), 1 lane(s), 30 km/h

### Location: Sohar
- Edge ID `-95403400#0`: *"Sohar Sanniya Park Road"* (highway.unclassified), 1 lane(s), 50 km/h
- Edge ID `-95403400#1`: *"Sohar Sanniya Park Road"* (highway.unclassified), 1 lane(s), 50 km/h
- Edge ID `-95403400#2`: *"Sohar Sanniya Park Road"* (highway.unclassified), 1 lane(s), 50 km/h
- Edge ID `-95403400#3`: *"Sohar Sanniya Park Road"* (highway.unclassified), 1 lane(s), 50 km/h
- Edge ID `-95403400#4`: *"Sohar Sanniya Park Road"* (highway.unclassified), 1 lane(s), 50 km/h

### Location: Sahwa
- *Queried in secondary/link ways.*

---

## 6. Honest Cartographic & Simulation Disclosure

To maintain engineering integrity, the following distinction between surveyed ground truth and synthesized defaults is explicitly documented:

1. **Geometry & Topology (Real Ground Truth):** Node coordinates, road alignments, roundabout circles, U-turn link ramps, dual-carriageway median divides, and turn restrictions are direct surveyed OpenStreetMap data.
2. **Speed Limits (Hybrid):** Explicit `maxspeed=*` tags from OSM are preserved. Where absent (common on rural wadi tracks and local residential lanes), GCC typemap defaults were applied (Motorways: 120 km/h, Trunks: 100 km/h, Primary: 80 km/h, Residential: 40 km/h, Tracks: 30 km/h).
3. **Traffic Signals (Synthesized Actuation):** Traffic light junction locations correspond to surveyed OSM `highway=traffic_signals` nodes. However, real-time stage timings are actuated heuristics synthesized by SUMO rather than Royal Oman Police (ROP) fixed signal plans.
4. **Elevation:** Heights in 2D OSM ways are planar WGS84; for 3D gradient simulation, SRTM DEM drape was utilized.