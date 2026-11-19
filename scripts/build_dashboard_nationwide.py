import json
import os

from scripts.build_dashboard import inject


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

    result = inject(template, factories, meta, provinces_geojson, districts_geojson,
                     subdistrict_centroids, subdistricts_geojson)

    os.makedirs("dist", exist_ok=True)
    with open("dist/dashboard_nationwide.html", "w", encoding="utf-8") as f:
        f.write(result)


if __name__ == "__main__":
    main()
