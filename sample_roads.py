import shapefile

sf = shapefile.Reader('data/hotosm_roads/roads_lines.shp', encoding='utf-8')
target_types = {'motorway', 'trunk', 'primary'}
seen = set()
for r in sf.iterRecords():
    hw = r['highway']
    name = r['name'] or r['name_en'] or r['name_ar']
    if hw in target_types and name and name not in seen:
        seen.add(name)
        print(f"[{hw:8}] {name} | ar: {r['name_ar']} | en: {r['name_en']} | lanes: {r['lanes']}")
        if len(seen) >= 25:
            break
