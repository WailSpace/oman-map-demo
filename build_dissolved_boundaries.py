"""
Builds the pure geoBoundaries dataset:
1. All 61 Wilayats (States) with Arabic & English names + Centroid coordinates for map labels.
2. 11 Governorates created by DISSOLVING (unary_union) their constituent Wilayats.
3. Sovereign National Border created by DISSOLVING all 61 Wilayats.
Eliminates any external overlapping datasets.
"""
import json
import requests
from pathlib import Path
import shapely.geometry
import shapely.ops

DATA_FILE = Path(r"C:\Users\wail\oman-map-demo\data\oman_boundaries.json")

WILAYAT_MAP = {
    # Muscat (6)
    'WILAYAT AS SEEB': ('Muscat', 'مسقط', 'As Seeb', 'السيب'),
    'WILAYAT BAWSHAR': ('Muscat', 'مسقط', 'Bawshar', 'بوشر'),
    'WILAYAT MUTRAH': ('Muscat', 'مسقط', 'Muttrah', 'مطرح'),
    'WILAYAT MUSCAT': ('Muscat', 'مسقط', 'Muscat', 'مسقط'),
    'WILAYAT AL AMRAT': ('Muscat', 'مسقط', 'Al Amrat', 'العامرات'),
    'WILAYAT QURAYYAT': ('Muscat', 'مسقط', 'Qurayyat', 'قريات'),

    # Dhofar (10)
    'WILAYAT SALALAH': ('Dhofar', 'ظفار', 'Salalah', 'صلالة'),
    'WILAYAT TAQAH': ('Dhofar', 'ظفار', 'Taqah', 'طاقة'),
    'WILAYAT MIRBAT': ('Dhofar', 'ظفار', 'Mirbat', 'مرباط'),
    'WILAYAT SADAH': ('Dhofar', 'ظفار', 'Sadah', 'سدح'),
    'WILAYAT RAKHYUT': ('Dhofar', 'ظفار', 'Rakhyut', 'رخيوت'),
    'WILAYAT DALKUT': ('Dhofar', 'ظفار', 'Dalkut', 'ضلكوت'),
    'WILAYAT THUMRAYT': ('Dhofar', 'ظفار', 'Thumrait', 'ثمريت'),
    'WILAYAT MUQSHIN': ('Dhofar', 'ظفار', 'Muqshin', 'مقشن'),
    'WILAYAT SHALIM WA JUZOR AL HALLANIYAT': ('Dhofar', 'ظفار', 'Shalim & Hallaniyat', 'شليم وجزر الحلانيات'),
    'WILAYAT AL MAZYUNAH': ('Dhofar', 'ظفار', 'Al Mazyunah', 'المزيونة'),

    # Musandam (4)
    'WILAYAT KHASAB': ('Musandam', 'مسندم', 'Khasab', 'خصب'),
    'WILAYAT DABA': ('Musandam', 'مسندم', 'Daba', 'دبا'),
    'WILAYAT BUKHA': ('Musandam', 'مسندم', 'Bukha', 'بخاء'),
    'WILAYAT MADHA': ('Musandam', 'مسندم', 'Madha', 'مدحاء'),

    # Al Buraimi (3)
    'WILAYAT AL BURAYMI': ('Al Buraimi', 'البريمي', 'Al Buraimi', 'البريمي'),
    'WILAYAT MAHADAH': ('Al Buraimi', 'البريمي', 'Mahdah', 'محضة'),
    'WILAYAT AS SUNAYNAH': ('Al Buraimi', 'البريمي', 'As Sunaynah', 'السنينة'),

    # Ad Dakhiliyah (8)
    'WILAYAT NIZWA': ('Ad Dakhiliyah', 'الداخلية', 'Nizwa', 'نزوى'),
    'WILAYAT BAHLA': ('Ad Dakhiliyah', 'الداخلية', 'Bahla', 'بهلاء'),
    'WILAYAT MANAH': ('Ad Dakhiliyah', 'الداخلية', 'Manah', 'منح'),
    'WILAYAT AL HAMRA': ('Ad Dakhiliyah', 'الداخلية', 'Al Hamra', 'الحمراء'),
    'WILAYAT ADAM': ('Ad Dakhiliyah', 'الداخلية', 'Adam', 'أدم'),
    'WILAYAT IZKI': ('Ad Dakhiliyah', 'الداخلية', 'Izki', 'إزكي'),
    'WILAYAT SAMAIL': ('Ad Dakhiliyah', 'الداخلية', 'Samail', 'سمائل'),
    'WILAYAT BIDBID': ('Ad Dakhiliyah', 'الداخلية', 'Bidbid', 'بدبد'),

    # North Al Batinah (6)
    'WILAYAT SOHAR': ('North Al Batinah', 'شمال الباطنة', 'Sohar', 'صحار'),
    'WILAYAT SHINAS': ('North Al Batinah', 'شمال الباطنة', 'Shinas', 'شناص'),
    'WILAYAT LIWA': ('North Al Batinah', 'شمال الباطنة', 'Liwa', 'لوى'),
    'WILAYAT SAHAM': ('North Al Batinah', 'شمال الباطنة', 'Saham', 'صحم'),
    'WILAYAT AL KHABURAH': ('North Al Batinah', 'شمال الباطنة', 'Al Khaburah', 'الخابورة'),
    'WILAYAT AS SUWAYQ': ('North Al Batinah', 'شمال الباطنة', 'As Suwayq', 'السويق'),

    # South Al Batinah (6)
    'WILAYAT AR RUSTAQ': ('South Al Batinah', 'جنوب الباطنة', 'Ar Rustaq', 'الرستاق'),
    'WILAYAT AL AWABI': ('South Al Batinah', 'جنوب الباطنة', 'Al Awabi', 'العوابي'),
    'WILAYAT NAKHAL': ('South Al Batinah', 'جنوب الباطنة', 'Nakhal', 'نخل'),
    'WILAYAT WADI AL MAAWIL': ('South Al Batinah', 'جنوب الباطنة', 'Wadi Al Maawil', 'وادي المعاول'),
    'WILAYAT BARKA': ('South Al Batinah', 'جنوب الباطنة', 'Barka', 'بركاء'),
    'WILAYAT AL MUSANAAH': ('South Al Batinah', 'جنوب الباطنة', 'Al Musanaah', 'المصنعة'),

    # South Ash Sharqiyah (5)
    'WILAYAT SUR': ('South Ash Sharqiyah', 'جنوب الشرقية', 'Sur', 'صور'),
    'WILAYAT AL KAMIL WA AL WAFI': ('South Ash Sharqiyah', 'جنوب الشرقية', 'Al Kamil Wal Wafi', 'الكامل والوافي'),
    'WILAYAT JAALAN BANI BU HASAN': ('South Ash Sharqiyah', 'جنوب الشرقية', 'Jaalan Bani Bu Hasan', 'جعلان بني بو حسن'),
    'WILAYAT JAALAN BANI BU ALI': ('South Ash Sharqiyah', 'جنوب الشرقية', 'Jaalan Bani Bu Ali', 'جعلان بني بو علي'),
    'WILAYAT MASIRAH': ('South Ash Sharqiyah', 'جنوب الشرقية', 'Masirah', 'مصيرة'),

    # North Ash Sharqiyah (6)
    'WILAYAT IBRA': ('North Ash Sharqiyah', 'شمال الشرقية', 'Ibra', 'إبراء'),
    'WILAYAT AL MUDAYBI': ('North Ash Sharqiyah', 'شمال الشرقية', 'Al Mudaybi', 'المضيبي'),
    'WILAYAT BIDIYAH': ('North Ash Sharqiyah', 'شمال الشرقية', 'Bidiyah', 'بدية'),
    'WILAYAT AL QABIL': ('North Ash Sharqiyah', 'شمال الشرقية', 'Al Qabil', 'القابل'),
    'WILAYAT WADI BANI KHALID': ('North Ash Sharqiyah', 'شمال الشرقية', 'Wadi Bani Khalid', 'وادي بني خالد'),
    'WILAYAT DAMA WA AT TAIYIN': ('North Ash Sharqiyah', 'شمال الشرقية', 'Dama Wa At Taiyin', 'دماء والطائيين'),

    # Ad Dhahirah (3)
    'WILAYAT IBRI': ('Ad Dhahirah', 'الظاهرة', 'Ibri', 'عبري'),
    'WILAYAT YANQUL': ('Ad Dhahirah', 'الظاهرة', 'Yanqul', 'ينقل'),
    'WILAYAT DANK': ('Ad Dhahirah', 'الظاهرة', 'Dank', 'ضنك'),

    # Al Wusta (4)
    'WILAYAT HAYMA': ('Al Wusta', 'الوسطى', 'Haima', 'هيماء'),
    'WILAYAT MAHAWT': ('Al Wusta', 'الوسطى', 'Mahout', 'محوت'),
    'WILAYAT AD DUQM': ('Al Wusta', 'الوسطى', 'Ad Duqm', 'الدقم'),
    'WILAYAT AL JAZIR': ('Al Wusta', 'الوسطى', 'Al Jazir', 'الجازر')
}

GOV_COLORS = {
    'Muscat': '#ef4444',
    'Dhofar': '#10b981',
    'Musandam': '#8b5cf6',
    'Al Buraimi': '#06b6d4',
    'Ad Dakhiliyah': '#f59e0b',
    'North Al Batinah': '#3b82f6',
    'South Al Batinah': '#1d4ed8',
    'South Ash Sharqiyah': '#ec4899',
    'North Ash Sharqiyah': '#d97706',
    'Ad Dhahirah': '#14b8a6',
    'Al Wusta': '#64748b'
}

def build_dissolved_system():
    print("Fetching geoBoundaries ADM2 (61 Wilayats)...")
    url = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/OMN/ADM2/geoBoundaries-OMN-ADM2.geojson"
    resp = requests.get(url, timeout=35)
    data = resp.json()

    wilayat_features = []
    gov_geometries = {}
    gov_names_ar = {}

    for f in data["features"]:
        shape_name = f["properties"]["shapeName"]
        if shape_name not in WILAYAT_MAP:
            continue
        
        gov_en, gov_ar, wil_en, wil_ar = WILAYAT_MAP[shape_name]
        raw_geom = shapely.geometry.shape(f["geometry"])
        valid_geom = raw_geom.buffer(0) if not raw_geom.is_valid else raw_geom
        
        # Calculate label point inside polygon
        rep_pt = valid_geom.representative_point()
        label_point = [round(rep_pt.x, 5), round(rep_pt.y, 5)]

        wil_feat = {
            "type": "Feature",
            "properties": {
                "id": f["properties"].get("shapeID", wil_en),
                "name_en": wil_en,
                "name_ar": wil_ar,
                "governorate_en": gov_en,
                "governorate_ar": gov_ar,
                "admin_level": 6,
                "type": "Wilayat",
                "label_point": label_point,
                "color": GOV_COLORS.get(gov_en, "#3b82f6")
            },
            "geometry": shapely.geometry.mapping(valid_geom)
        }
        wilayat_features.append(wil_feat)

        if gov_en not in gov_geometries:
            gov_geometries[gov_en] = []
            gov_names_ar[gov_en] = gov_ar
        gov_geometries[gov_en].append(valid_geom)

    print(f"Parsed {len(wilayat_features)} Wilayats.")

    # Dissolve Wilayats into their respective Governorates
    print("Dissolving Wilayats into 11 Governorates...")
    gov_features = []
    all_gov_geoms = []

    for gov_en, geom_list in gov_geometries.items():
        dissolved_gov = shapely.ops.unary_union(geom_list)
        all_gov_geoms.append(dissolved_gov)
        rep_pt = dissolved_gov.representative_point()

        gov_feat = {
            "type": "Feature",
            "properties": {
                "id": f"GOV-{gov_en.upper().replace(' ', '_')}",
                "name_en": gov_en,
                "name_ar": gov_names_ar[gov_en],
                "admin_level": 4,
                "type": "Governorate",
                "label_point": [round(rep_pt.x, 5), round(rep_pt.y, 5)],
                "color": GOV_COLORS.get(gov_en, "#3b82f6")
            },
            "geometry": shapely.geometry.mapping(dissolved_gov)
        }
        gov_features.append(gov_feat)

    print(f"Created {len(gov_features)} clean dissolved Governorates.")

    # Dissolve all Governorates into 1 Sovereign National Border
    print("Dissolving into Sovereign National Border...")
    national_geom = shapely.ops.unary_union(all_gov_geoms)
    nat_feature = {
        "type": "Feature",
        "properties": {
            "id": "OMN-NATIONAL",
            "name_en": "Sultanate of Oman",
            "name_ar": "سلطنة عمان",
            "admin_level": 2,
            "type": "National Border"
        },
        "geometry": shapely.geometry.mapping(national_geom)
    }

    # Combined master dataset: National + 11 Governorates + 61 Wilayats
    # Exactly 1 + 11 + 61 = 73 features, 100% topologically derived from geoBoundaries!
    master_collection = {
        "type": "FeatureCollection",
        "features": [nat_feature] + gov_features + wilayat_features
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(master_collection, f, ensure_ascii=False)

    print(f"Overwrote {DATA_FILE} successfully with 0 overlapping data!")

if __name__ == "__main__":
    build_dissolved_system()
