oex export
==========

Generated:        2026-10-07 19:02:59 UTC
oex version:      0.4.15
Project:          https://github.com/osgeonepal/oex

Country (ISO3):   OMN
Boundary:         geoBoundaries gbOpen ADM0
Bounding box:     (52.0000, 16.6502, 59.8394, 26.3886)

Dataset:          roads
Format:           ESRI Shapefile (shp)
Features:         187,948

Source:           OpenStreetMap contributors
Source URL:       https://www.openstreetmap.org/
Snapshot:         2026-10-07
License:          Open Database License (ODC-ODbL)
License URL:      https://opendatacommons.org/licenses/odbl/1-0/

About the source
  OpenStreetMap is a community-edited geographic dataset of the world. Country
  features are extracted from the source PBF via quackosm with the union of
  all category tag filters; per-category exports apply tag predicates at query
  time.

Notes
  - Shapefile output is split by geometry type:
    <category>_polygons.shp, <category>_lines.shp, <category>_points.shp.
    This is a shapefile-format limitation, not a data limitation.
  - Field names are truncated to 10 characters in shp; gpkg keeps them full.

Feedback:         https://github.com/osgeonepal/oex/issues
Engine: geofabrik