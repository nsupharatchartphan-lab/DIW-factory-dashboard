import json

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

from scripts.regions import REGION_ORDER


def dissolve_regions(provinces_geojson: dict) -> dict:
    by_region = {}
    for feature in provinces_geojson["features"]:
        region = feature["properties"]["region"]
        by_region.setdefault(region, []).append(shape(feature["geometry"]))

    features = []
    for region in REGION_ORDER:
        geometries = by_region.get(region)
        if not geometries:
            continue
        merged = unary_union(geometries)
        features.append({
            "type": "Feature",
            "properties": {"region": region},
            "geometry": mapping(merged),
        })
    return {"type": "FeatureCollection", "features": features}


def main():
    with open("data/boundaries/provinces_nationwide.geojson", encoding="utf-8") as f:
        provinces_geojson = json.load(f)
    regions_geojson = dissolve_regions(provinces_geojson)
    with open("data/boundaries/regions_nationwide.geojson", "w", encoding="utf-8") as f:
        json.dump(regions_geojson, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
