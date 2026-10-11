import requests

query = """[out:json][timeout:25];
(
  way["highway"~"motorway|trunk|primary"](23.0,57.5,24.0,59.0);
);
out geom;
"""

endpoints = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

for ep in endpoints:
    try:
        r = requests.post(ep, data={"data": query}, timeout=15, headers={"User-Agent": "OmanRoadsCollector/1.0"})
        print(ep, "-> status:", r.status_code, "len:", len(r.content))
        if r.status_code == 200:
            data = r.json()
            print("Elements:", len(data.get("elements", [])))
            break
    except Exception as e:
        print(ep, "-> error:", e)
