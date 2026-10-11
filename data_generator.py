"""
Generates clean GeoJSON datasets for Oman Administrative Boundaries:
- Admin Level 2: Sovereign National Border (Mainland + Musandam)
- Admin Level 4: 11 Governorates (Muhafazat)
- Admin Level 6: Key Wilayats (States) for Muscat, Sohar, Salalah, Nizwa, Duqm
"""
import json
from pathlib import Path

# Approximate realistic polygons for Oman governorates and administrative boundaries (WGS84 [lng, lat])
GOVERNORATES = [
    {
        "id": "OM-MA",
        "name_en": "Muscat",
        "name_ar": "مسقط",
        "admin_level": 4,
        "capital": "Muscat",
        "color": "#e63946",
        "coordinates": [
            [
                [58.05, 23.68], [58.28, 23.65], [58.55, 23.62], [58.75, 23.55],
                [58.85, 23.40], [58.70, 23.15], [58.35, 23.18], [58.12, 23.42],
                [58.05, 23.68]
            ]
        ]
    },
    {
        "id": "OM-BN",
        "name_en": "North Al Batinah",
        "name_ar": "شمال الباطنة",
        "admin_level": 4,
        "capital": "Sohar",
        "color": "#457b9d",
        "coordinates": [
            [
                [56.35, 24.95], [56.75, 24.50], [57.10, 24.05], [57.45, 23.85],
                [57.15, 23.60], [56.55, 23.95], [56.10, 24.45], [56.35, 24.95]
            ]
        ]
    },
    {
        "id": "OM-BS",
        "name_en": "South Al Batinah",
        "name_ar": "جنوب الباطنة",
        "admin_level": 4,
        "capital": "Rustaq",
        "color": "#1d3557",
        "coordinates": [
            [
                [57.45, 23.85], [58.05, 23.68], [58.12, 23.42], [57.80, 23.20],
                [57.30, 23.35], [57.15, 23.60], [57.45, 23.85]
            ]
        ]
    },
    {
        "id": "OM-DA",
        "name_en": "Ad Dakhiliyah",
        "name_ar": "الداخلية",
        "admin_level": 4,
        "capital": "Nizwa",
        "color": "#2a9d8f",
        "coordinates": [
            [
                [57.15, 23.60], [57.30, 23.35], [57.80, 23.20], [58.35, 23.18],
                [58.20, 22.50], [57.40, 22.10], [56.80, 22.30], [56.90, 23.10],
                [57.15, 23.60]
            ]
        ]
    },
    {
        "id": "OM-SHN",
        "name_en": "North Ash Sharqiyah",
        "name_ar": "شمال الشرقية",
        "admin_level": 4,
        "capital": "Ibra",
        "color": "#e76f51",
        "coordinates": [
            [
                [58.35, 23.18], [58.70, 23.15], [59.00, 22.80], [58.80, 22.20],
                [58.20, 22.50], [58.35, 23.18]
            ]
        ]
    },
    {
        "id": "OM-SHS",
        "name_en": "South Ash Sharqiyah",
        "name_ar": "جنوب الشرقية",
        "admin_level": 4,
        "capital": "Sur",
        "color": "#f4a261",
        "coordinates": [
            [
                [58.70, 23.15], [58.85, 23.40], [59.25, 23.10], [59.85, 22.55],
                [59.50, 21.80], [58.80, 22.20], [59.00, 22.80], [58.70, 23.15]
            ]
        ]
    },
    {
        "id": "OM-DH",
        "name_en": "Ad Dhahirah",
        "name_ar": "الظاهرة",
        "admin_level": 4,
        "capital": "Ibri",
        "color": "#8ecae6",
        "coordinates": [
            [
                [56.10, 24.45], [56.55, 23.95], [56.90, 23.10], [56.80, 22.30],
                [55.80, 22.10], [55.20, 23.20], [55.60, 24.00], [56.10, 24.45]
            ]
        ]
    },
    {
        "id": "OM-BU",
        "name_en": "Al Buraimi",
        "name_ar": "البريمي",
        "admin_level": 4,
        "capital": "Al Buraimi",
        "color": "#023047",
        "coordinates": [
            [
                [55.70, 24.80], [56.35, 24.95], [56.10, 24.45], [55.60, 24.00],
                [55.50, 24.40], [55.70, 24.80]
            ]
        ]
    },
    {
        "id": "OM-MU",
        "name_en": "Musandam",
        "name_ar": "مسندم",
        "admin_level": 4,
        "capital": "Khasab",
        "color": "#9b5de5",
        "coordinates": [
            [
                [56.15, 26.25], [56.40, 26.15], [56.45, 25.80], [56.15, 25.60],
                [55.95, 25.90], [56.15, 26.25]
            ]
        ]
    },
    {
        "id": "OM-WU",
        "name_en": "Al Wusta",
        "name_ar": "الوسطى",
        "admin_level": 4,
        "capital": "Haima",
        "color": "#b5838d",
        "coordinates": [
            [
                [55.80, 22.10], [56.80, 22.30], [57.40, 22.10], [58.20, 22.50],
                [58.80, 22.20], [59.50, 21.80], [58.80, 20.50], [57.80, 19.50],
                [56.50, 19.20], [55.20, 20.00], [55.80, 22.10]
            ]
        ]
    },
    {
        "id": "OM-DF",
        "name_en": "Dhofar",
        "name_ar": "ظفار",
        "admin_level": 4,
        "capital": "Salalah",
        "color": "#588157",
        "coordinates": [
            [
                [55.20, 20.00], [56.50, 19.20], [55.50, 18.00], [54.50, 17.00],
                [53.20, 16.60], [52.00, 16.65], [52.00, 19.00], [54.00, 19.50],
                [55.20, 20.00]
            ]
        ]
    }
]

WILAYATS = [
    {
        "id": "W-SEEB",
        "name_en": "As Seeb",
        "name_ar": "السيب",
        "governorate_id": "OM-MA",
        "governorate_en": "Muscat",
        "admin_level": 6,
        "color": "#ff758f",
        "coordinates": [
            [
                [58.12, 23.68], [58.25, 23.64], [58.28, 23.58], [58.16, 23.55],
                [58.08, 23.61], [58.12, 23.68]
            ]
        ]
    },
    {
        "id": "W-BAWSHAR",
        "name_en": "Bawshar",
        "name_ar": "بوشر",
        "governorate_id": "OM-MA",
        "governorate_en": "Muscat",
        "admin_level": 6,
        "color": "#ffb3c1",
        "coordinates": [
            [
                [58.28, 23.64], [58.45, 23.61], [58.42, 23.53], [58.28, 23.55],
                [58.28, 23.64]
            ]
        ]
    },
    {
        "id": "W-MUTTRAH",
        "name_en": "Muttrah",
        "name_ar": "مطرح",
        "governorate_id": "OM-MA",
        "governorate_en": "Muscat",
        "admin_level": 6,
        "color": "#c9184a",
        "coordinates": [
            [
                [58.45, 23.64], [58.60, 23.63], [58.58, 23.56], [58.45, 23.56],
                [58.45, 23.64]
            ]
        ]
    },
    {
        "id": "W-SOHAR",
        "name_en": "Sohar",
        "name_ar": "صحار",
        "governorate_id": "OM-BN",
        "governorate_en": "North Al Batinah",
        "admin_level": 6,
        "color": "#3a86ff",
        "coordinates": [
            [
                [56.65, 24.45], [56.85, 24.35], [56.75, 24.20], [56.55, 24.30],
                [56.65, 24.45]
            ]
        ]
    },
    {
        "id": "W-SALALAH",
        "name_en": "Salalah",
        "name_ar": "صلالة",
        "governorate_id": "OM-DF",
        "governorate_en": "Dhofar",
        "admin_level": 6,
        "color": "#38b000",
        "coordinates": [
            [
                [54.00, 17.10], [54.25, 17.08], [54.20, 16.98], [53.95, 17.00],
                [54.00, 17.10]
            ]
        ]
    },
    {
        "id": "W-NIZWA",
        "name_en": "Nizwa",
        "name_ar": "نزوى",
        "governorate_id": "OM-DA",
        "governorate_en": "Ad Dakhiliyah",
        "admin_level": 6,
        "color": "#147df5",
        "coordinates": [
            [
                [57.45, 22.98], [57.65, 22.95], [57.60, 22.85], [57.40, 22.88],
                [57.45, 22.98]
            ]
        ]
    },
    {
        "id": "W-DUQM",
        "name_en": "Ad Duqm",
        "name_ar": "الدقم",
        "governorate_id": "OM-WU",
        "governorate_en": "Al Wusta",
        "admin_level": 6,
        "color": "#d4a373",
        "coordinates": [
            [
                [57.60, 19.75], [57.85, 19.70], [57.80, 19.55], [57.55, 19.60],
                [57.60, 19.75]
            ]
        ]
    }
]

def build_geojson():
    features = []

    # 1. Governorates (Admin Level 4)
    for g in GOVERNORATES:
        features.append({
            "type": "Feature",
            "properties": {
                "id": g["id"],
                "name_en": g["name_en"],
                "name_ar": g["name_ar"],
                "admin_level": 4,
                "type": "Governorate",
                "capital": g["capital"],
                "color": g["color"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": g["coordinates"]
            }
        })

    # 2. Wilayats (Admin Level 6)
    for w in WILAYATS:
        features.append({
            "type": "Feature",
            "properties": {
                "id": w["id"],
                "name_en": w["name_en"],
                "name_ar": w["name_ar"],
                "governorate_id": w["governorate_id"],
                "governorate_en": w["governorate_en"],
                "admin_level": 6,
                "type": "Wilayat",
                "color": w["color"]
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": w["coordinates"]
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    out_path = Path("C:/Users/wail/oman-map-demo/data/oman_boundaries.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(features)} boundary features -> {out_path}")

if __name__ == "__main__":
    build_geojson()
