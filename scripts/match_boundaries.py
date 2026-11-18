import json
import os


def build_excel_pairs(factories: list) -> set:
    return {(f["province"], f["amphoe"]) for f in factories}


def build_boundary_pairs(districts_geojson: dict) -> set:
    return {
        (feature["properties"]["pro_th"], feature["properties"]["amp_th"])
        for feature in districts_geojson["features"]
    }


def find_unmatched(excel_pairs: set, boundary_pairs: set, aliases: dict) -> set:
    unmatched = set()
    for pair in excel_pairs:
        aliased = aliases.get(pair, pair)
        if aliased not in boundary_pairs:
            unmatched.add(pair)
    return unmatched


def _load_aliases(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if not raw:
        return {}
    return {tuple(json.loads(k)): tuple(v) for k, v in raw.items()}


def main():
    with open("data/processed/factories.json", encoding="utf-8") as f:
        factories = json.load(f)
    with open("data/boundaries/districts.geojson", encoding="utf-8") as f:
        districts_geojson = json.load(f)
    aliases = _load_aliases("data/boundaries/name_aliases.json")

    excel_pairs = build_excel_pairs(factories)
    boundary_pairs = build_boundary_pairs(districts_geojson)
    unmatched = find_unmatched(excel_pairs, boundary_pairs, aliases)

    report = {
        "total_excel_pairs": len(excel_pairs),
        "unmatched": sorted([list(pair) for pair in unmatched]),
    }
    with open("data/boundaries/match_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"total_excel_pairs={report['total_excel_pairs']}")
    print(f"unmatched={report['unmatched']}")


if __name__ == "__main__":
    main()
