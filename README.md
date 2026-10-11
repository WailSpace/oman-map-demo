# Oman High-Resolution Geospatial & Topographic Platform Demo
## منصة الخرائط والتضاريس الطبوغرافية العمانية عالية الدقة

A high-performance sovereign geospatial platform and offline base map engine engineered for the **Sultanate of Oman** (سلطنة عمان).

---

## 🚀 Live Demo URL

The local server is running and ready:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

Interactive API Documentation (Swagger UI):
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## ⛰️ Key Features & Capabilities

### 1. Main View: Google Terrain Cropped Strictly to Oman Borders (تضاريس جوجل مقتطعة لحدود السلطنة)
* **Sovereign Boundary Masking**: Google Maps physical terrain elevation relief is mathematically cropped strictly to Oman's sovereign national border via a dedicated high-performance inverse polygon mask (`/api/mask`).
* **Clean Sovereign Presentation**: All terrain and lands outside Oman (neighboring countries and exterior waters) are cleanly masked into the dark canvas background, focusing visual spotlight exclusively on Oman's physical geography.
* **Full MultiPolygon Inclusion**: Mainland Oman, Musandam peninsula exclave, Madha exclave, Masirah island, and Daymaniyat islands are completely preserved and illuminated.
* **Toggleable Crop Control**: Users can toggle between the strict sovereign cropped view and regional context at any time.

### 2. High-Resolution Topographic Terrain & 3D Shaded Relief (Offline Integrated)
* **Genuine Topographic Maps**: Continuous elevation contours, labeled altitude spot heights (meters), mountain passes, rock walls, and wadis.
* **3D Multidirectional Hillshade**: Physical shaded relief layer displaying the dramatic crests of Al Hajar mountains (*Jabal Shams 3,019m*, *Jabal Akhdar 2,980m*), Dhofar coastal escarpment (*Jabal Samhan 2,100m*), Musandam fjords (*Jabal Harim 2,087m*), and Wahiba mega-dunes.
* **Interactive Hillshade Intensity Slider**: Live opacity control (0% – 100%) in the sidebar.
* **Topographic Quick-Fly Showcase**: Jump instantly to iconic Oman geographic wonders:
  - 🏔️ Jabal Shams & Grand Canyon of Arabia (Wadi Ghul)
  - 🌿 Jabal Akhdar & Sayq Plateau
  - 🌊 Wadi Shab & Wadi Tiwi
  - ⛰️ Jabal Samhan & Dhofar Escarpment
  - ⛵ Musandam Fjords & Khasab
  - 🏜️ Wahiba Sands Longitudinal Dunes
* **100% Offline Tile Cache**: 1,780+ tiles pre-cached locally on disk in `cache/tiles/` covering the entire Sultanate (Zoom 5–9) and high-res mountain corridors (Zoom 10–11) with sub-2ms response time.

### 2. National Road Network & Highway Corridors (شبكة الطرق والمحاور)
* **Comprehensive Coverage**: Over **16,680+ road segments** extracted, simplified, and categorized across all 11 Governorates of Oman:
  - **9,254 Expressway & Highway Segments**: Muscat Expressway, Batinah Expressway, Sultan Qaboos St, Nizwa-Salalah Highway (Route 31), Bidbid-Sur (Route 23), Qurayyat-Sur (Route 17), Duqm Corridor (Route 32), and Ibri-Buraimi (Route 21).
  - **7,432 Secondary & Regional Arterials**: Connecting municipal centers, mountain settlements, and interior oases.
* **ROP Legal Speed Limits**: Standardized speed classifications (120 km/h on expressways, 100 km/h on national trunk highways, 80 km/h on secondary roads).
* **Interactive Tooltips & Styling**: Distinctive glowing amber for 120 km/h expressways, royal blue for 100 km/h national highways, and emerald for primary arterials. Hovering or clicking displays Arabic & English road names, speed limit, lanes, and surface.
* **Nearest Highway Spatial Snapping**: Reverse geocoding (`/api/geocode/reverse` and `/api/roads/nearest`) calculates distance to closest highway, current street name, and road speed limit in <4ms.

### 3. Pure Boundary Topology (0 Overlaps, 0 Gaps)
* **11 Governorates (*Muhafazat*)**: Exact dissolved union of constituent states.
* **61 States (*Wilayats*)**: Sourced from official geoBoundaries structure.
* **Clean Cartography**: No static labels crowding the map; states highlight with a soft, frameless emerald tint on click with zero focus boxes or outlines.
* **Sovereign National Perimeter**: High-contrast white border tracing Oman's territorial boundaries.

### 4. Spatial Analysis & Elevation Geocoding
* **Reverse Geocoder**: Instant Point-in-Polygon containment resolution (`/api/geocode/reverse?lat=...&lng=...`) returning Governorate, Wilayat, Elevation, and Nearest Highway.
* **Truck Terrain Safety Engine**: Evaluates slope grade, mountain road warnings, and retarder brake advisories for commercial logistics.

### 5. Fleet VMS Telematics & Last-Mile Delivery
* Real-time vehicle simulation snapped to highway corridors with speed limit monitoring, Wilayat geofencing, and multi-stop delivery dispatch.

---

## 📁 Project Directory Structure

```
oman-map-demo/
├── .venv/                         # Python 3.12 Virtual Environment
├── cache/
│   └── tiles/                     # 1,780+ pre-cached offline topographic & hillshade tiles
│       ├── opentopo/              # OpenTopoMap continuous contour tiles
│       ├── hillshade/             # ESRI 3D World Hillshade relief tiles
│       └── google_terrain/        # Google Maps high-res physical terrain tiles
├── data/
│   ├── oman_boundaries.json       # Dissolved 11 Governorates + 61 Wilayats (73 features)
│   └── oman_terrain.json          # Mountain summits, passes, and wadis
├── static/
│   └── index.html                 # Topographic interactive web dashboard
├── server.py                      # FastAPI server with offline tile proxy & spatial engine
├── download_oman_topo_cache.py    # Offline tile pre-caching utility
├── build_dissolved_boundaries.py  # Boundary topology generator (unary_union)
├── run_demo.bat                   # One-click Windows launcher
└── README.md
```

---

## 🏃 Running the Application

To launch or restart the platform at any time:
```powershell
cd C:\Users\wail\oman-map-demo
.\.venv\Scripts\activate
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```
Or simply double-click [`run_demo.bat`](file:///C:/Users/wail/oman-map-demo/run_demo.bat).

---

## 🚦 Navigable Road Network & SUMO Traffic Simulation Engine

The platform incorporates the complete, mathematically connected road graph of the Sultanate of Oman compiled directly for microscopic simulation in **Eclipse SUMO (Simulation of Urban MObility)** and turn-by-turn routing.

### 📊 Network Metrics & Quality Audit (Verified Ground Truth)
* **Drivable Edges**: **665,725 edges** (directional carriageways and maneuver links).
* **Total Road Network Length**: **181,672.7 km** compiled centerline length.
* **Total Driving Lanes**: **700,718 directional lanes**.
* **Total Intersections**: **339,192 topological junctions**.
* **Roundabouts Built**: **1,487 circular junction systems** with 9,226 internal priority lanes.
* **Traffic Light Controllers**: **94 actuated signal controllers** synthesized from 343 surveyed OSM signals.
* **Turn Restrictions Enforced**: **3,364 relations** (no U-turn, mandatory straight, no left turn; >99.4% enforcement rate).

### 🛠️ How to Rebuild the Network

All pipeline tools and compiled models are housed under `network/`:

1. **Extract Sovereign Navigable OSM XML**:
   ```powershell
   .\.venv\Scripts\python.exe network\extract_oman_network.py
   ```
   Filters all vehicle-relevant ways within Oman's sovereign boundaries (buffered ~330m), preserving nodes, tags, roundabouts, and turn restrictions into `network/oman_roads.osm.gz`.

2. **Compile National SUMO Network (`netconvert`)**:
   ```powershell
   .\.venv\Scripts\netconvert.exe --osm-files network\oman_roads.osm.gz --type-files network\oman_typemap.xml --output-file network\oman.net.xml.gz --log network\netconvert.log --geometry.remove --ramps.guess --roundabouts.guess --junctions.join --tls.guess-signals --tls.discard-simple --tls.join --tls.default-type actuated --osm.turn-lanes --osm.lane-access --output.street-names --output.original-names --no-turnarounds.except-deadend --remove-edges.isolated --keep-edges.by-vclass passenger,delivery --check-lane-foes.roundabout
   ```

3. **Export Features & SQLite R*Tree Spatial Database**:
   ```powershell
   .\.venv\Scripts\python.exe network\export_features_and_sqlite.py
   ```
   Builds `network/oman_network.sqlite` (84.5 MB) with R*Tree indexing for sub-2ms bounding-box queries, and exports GeoJSON point layers under `network/features/`.

4. **Run Audit & QA Verification**:
   ```powershell
   .\.venv\Scripts\python.exe network\qa_network.py
   ```
   Generates `network/QA_REPORT.md` and `network/network_summary.json`.

---

## 🚗 Microscopic Traffic Simulation (Muscat Peak Hour)

A 30-minute metropolitan peak hour commuter simulation across Muscat (Sultan Qaboos St, Muscat Expressway, Seeb, and Bausher arterial corridors):
* **Vehicles Simulated**: 600 dynamic passenger vehicles.
* **Completed Trips**: 228 commuters arrived at destinations; 372 active in transit at step 1800s.
* **Mean Commute Distance**: 18.47 km.
* **Mean Travel Duration**: 14.0 minutes (841.7 seconds).
* **Mean Corridor Speed**: 79.0 km/h.
* **Teleports / Collisions**: **0** (Zero gridlocks; verified network connectivity).

### Running Headless via CLI
```powershell
.\.venv\Scripts\sumo.exe -c network\muscat\muscat.sumocfg --summary-output network\muscat\summary.xml --tripinfo-output network\muscat\tripinfo.xml --fcd-output network\muscat\fcd.xml --fcd-output.geo true --device.fcd.period 2
```

### Running with Native 3D / 2D GUI (`sumo-gui`)
```powershell
.\.venv\Scripts\sumo-gui.exe -c network\muscat\muscat.sumocfg
```

---

## 🌐 Navigable Network API Endpoints

* `GET /api/network/stats`: Complete topological metrics, edge distributions, and QA summary.
* `GET /api/network/edges?min_lng=...&min_lat=...&max_lng=...&max_lat=...&zoom=...`: Fast SQLite R*Tree viewport bbox query returning GeoJSON road centerlines.
* `GET /api/network/features?type=roundabout|signal|exit|uturn`: Bounding-box filtered junction point features.
* `GET /api/sim/muscat`: 60fps-interpolated vehicle playback stream for browser animation.
* `GET /api/network/qa`: Full markdown Quality Assurance and Topology Audit report.
* `GET /api/route?from_lng=...&from_lat=...&to_lng=...&to_lat=...`: Shortest path routing across Muscat.

---

## ⚠️ Cartographic Disclosure & Data Limitations

1. **Topological Ground Truth**: Road alignments, roundabout loops, dual-carriageway median divides, and turn restrictions are direct surveyed OpenStreetMap data (`© OpenStreetMap contributors`, ODbL).
2. **Speed Limits**: Preserved from explicit OSM `maxspeed` tags where present. Where absent, GCC standard defaults were assigned (Expressways: 120 km/h, Trunks: 100 km/h, Primary: 80 km/h, Residential: 40 km/h, Desert/Wadi Tracks: 30 km/h).
3. **Signal Timings**: Traffic light locations correspond to surveyed physical signals; phase splits and cycle times are actuated heuristics synthesized by SUMO rather than Royal Oman Police (ROP) fixed plans.

