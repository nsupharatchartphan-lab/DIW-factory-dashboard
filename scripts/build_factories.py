import json
import re

import openpyxl

TYPE_CODE_RE = re.compile(r"(\d+(?:\([0-9]+\))?)-\d+/\d+")
TYPE_MAIN_RE = re.compile(r"\d+")

MALFORMED_FID = 10600271025699
MALFORMED_FIX = {
    "tambon": None,
    "amphoe": "ตากฟ้า",
    "province": "นครสวรรค์",
    "postcode": "60190",
    "hp_registered": 12351,
}


def parse_type_code(old_reg_no: str) -> str:
    match = TYPE_CODE_RE.search(old_reg_no)
    if not match:
        raise ValueError(f"could not parse type code from {old_reg_no!r}")
    return match.group(1)


def type_main(type_code: str) -> str:
    match = TYPE_MAIN_RE.match(type_code)
    return match.group(0)


def _clean_str(value):
    if value is None:
        return None
    text = str(value).strip()
    if text in ("", "-"):
        return None
    return text


def load_factories_from_workbook(path: str) -> list:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["export1"]
    factories = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        old_reg_no = row[1]
        fid = row[3]
        type_code = parse_type_code(str(old_reg_no))
        factory = {
            "fid": fid,
            "old_reg_no": old_reg_no,
            "name": row[4],
            "operator": row[5],
            "business": row[6],
            "address_no": _clean_str(row[7]),
            "moo": _clean_str(row[8]),
            "soi": _clean_str(row[9]),
            "road": _clean_str(row[10]),
            "tambon": _clean_str(row[11]),
            "amphoe": row[12],
            "province": row[13],
            "postcode": _clean_str(row[14]),
            "phone": _clean_str(row[15]),
            "hp_registered": row[16],
            "hp_inspected": row[17],
            "type_code": type_code,
            "type_main": type_main(type_code),
            "commercial_reg": _clean_str(row[18]),
            "tax_id": _clean_str(row[19]),
        }
        if fid == MALFORMED_FID:
            factory.update(MALFORMED_FIX)
        factories.append(factory)
    return factories


def main():
    factories = load_factories_from_workbook("list of factories north thailand.xlsx")

    with open("data/processed/factories.json", "w", encoding="utf-8") as f:
        json.dump(factories, f, ensure_ascii=False)

    type_counts = {}
    province_counts = {}
    hp_registered_max = 0
    hp_inspected_max = 0
    for factory in factories:
        type_counts[factory["type_code"]] = type_counts.get(factory["type_code"], 0) + 1
        province_counts[factory["province"]] = province_counts.get(factory["province"], 0) + 1
        hp_registered_max = max(hp_registered_max, factory["hp_registered"])
        if factory["hp_inspected"] is not None:
            hp_inspected_max = max(hp_inspected_max, factory["hp_inspected"])

    meta = {
        "type_codes": [
            {"code": code, "count": count}
            for code, count in sorted(type_counts.items(), key=lambda kv: kv[1], reverse=True)
        ],
        "provinces": [
            {"name": name, "count": count}
            for name, count in sorted(province_counts.items(), key=lambda kv: kv[1], reverse=True)
        ],
        "hp_registered_max": hp_registered_max,
        "hp_inspected_max": hp_inspected_max,
    }
    with open("data/processed/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
