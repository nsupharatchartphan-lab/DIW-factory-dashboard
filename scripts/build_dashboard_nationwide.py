import json
import os
import re

PLACEHOLDER_NAMES = [
    "FACTORIES", "PROVINCES_GEOJSON", "DISTRICTS_GEOJSON", "META",
    "SUBDISTRICT_CENTROIDS", "SUBDISTRICTS_GEOJSON", "REGIONS_GEOJSON",
]


def inject(template: str, values: dict) -> str:
    result = template
    for name in PLACEHOLDER_NAMES:
        pattern = re.compile(r"/\*__" + name + r"__\*/[^;]*;")
        replacement = f"/*__{name}__*/ {json.dumps(values[name], ensure_ascii=False)};"
        result = pattern.sub(lambda m: replacement, result, count=1)
    return result


def main():
    with open("dashboard/template_nationwide.html", encoding="utf-8") as f:
        template = f.read()
    with open("data/processed/factories_nationwide.json", encoding="utf-8") as f:
        factories = json.load(f)
    with open("data/processed/meta_nationwide.json", encoding="utf-8") as f:
        meta = json.load(f)
    with open("data/boundaries/provinces_nationwide.geojson", encoding="utf-8") as f:
        provinces_geojson = json.load(f)
    with open("data/boundaries/districts_nationwide.geojson", encoding="utf-8") as f:
        districts_geojson = json.load(f)
    with open("data/boundaries/subdistrict_centroids_nationwide.json", encoding="utf-8") as f:
        subdistrict_centroids = json.load(f)
    with open("data/boundaries/subdistricts_nationwide.geojson", encoding="utf-8") as f:
        subdistricts_geojson = json.load(f)
    with open("data/boundaries/regions_nationwide.geojson", encoding="utf-8") as f:
        regions_geojson = json.load(f)

    result = inject(template, {
        "FACTORIES": factories,
        "PROVINCES_GEOJSON": provinces_geojson,
        "DISTRICTS_GEOJSON": districts_geojson,
        "META": meta,
        "SUBDISTRICT_CENTROIDS": subdistrict_centroids,
        "SUBDISTRICTS_GEOJSON": subdistricts_geojson,
        "REGIONS_GEOJSON": regions_geojson,
    })

    os.makedirs("dist", exist_ok=True)
    with open("dist/dashboard_nationwide.html", "w", encoding="utf-8") as f:
        f.write(result)


if __name__ == "__main__":
    main()
