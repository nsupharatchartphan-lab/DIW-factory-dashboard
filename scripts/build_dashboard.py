import json
import os
import re

PLACEHOLDER_NAMES = ["FACTORIES", "PROVINCES_GEOJSON", "DISTRICTS_GEOJSON", "META"]


def inject(template: str, factories, meta, provinces_geojson, districts_geojson) -> str:
    values = {
        "FACTORIES": factories,
        "PROVINCES_GEOJSON": provinces_geojson,
        "DISTRICTS_GEOJSON": districts_geojson,
        "META": meta,
    }
    result = template
    for name in PLACEHOLDER_NAMES:
        pattern = re.compile(r"/\*__" + name + r"__\*/[^;]*;")
        replacement = f"/*__{name}__*/ {json.dumps(values[name], ensure_ascii=False)};"
        result = pattern.sub(lambda m: replacement, result, count=1)
    return result


def main():
    with open("dashboard/template.html", encoding="utf-8") as f:
        template = f.read()
    with open("data/processed/factories.json", encoding="utf-8") as f:
        factories = json.load(f)
    with open("data/processed/meta.json", encoding="utf-8") as f:
        meta = json.load(f)
    with open("data/boundaries/provinces.geojson", encoding="utf-8") as f:
        provinces_geojson = json.load(f)
    with open("data/boundaries/districts.geojson", encoding="utf-8") as f:
        districts_geojson = json.load(f)

    result = inject(template, factories, meta, provinces_geojson, districts_geojson)

    os.makedirs("dist", exist_ok=True)
    with open("dist/dashboard.html", "w", encoding="utf-8") as f:
        f.write(result)


if __name__ == "__main__":
    main()
