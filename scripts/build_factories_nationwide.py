import json
import re

import openpyxl

from scripts.regions import REGION_ORDER, region_for_province

TYPE_CODE_RE = re.compile(r"(\d+(?:\([0-9]+\))?)-\d+/\d+")
TYPE_MAIN_RE = re.compile(r"\d+")

HEADER_MAP = {
    "old_reg_no": "เลขทะเบียนเดิม",
    "fid": "FID",
    "name": "ชื่อโรงงาน",
    "operator": "ผู้ประกอบการ",
    "business": "ประกอบกิจการ",
    "address_no": "เลขที่",
    "moo": "หมู่",
    "soi": "ซอย",
    "road": "ถนน",
    "tambon": "ตำบล",
    "amphoe": "อำเภอ",
    "province": "จังหวัด",
    "postcode": "ไปรษณีย์",
    "phone": "โทรศัพท์",
    "hp_registered": "แรงม้า",
    "hp_inspected": "แรงม้าตรวจพบ",
    "commercial_reg": "ทะเบียนพาณิชย์",
    "tax_id": "เลขผู้เสียภาษี",
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


def build_column_index(header_row) -> dict:
    index_by_header = {}
    for idx, header in enumerate(header_row):
        if header is not None:
            index_by_header[str(header).strip()] = idx
    return {key: index_by_header[header] for key, header in HEADER_MAP.items()}


def load_factories_from_workbook(path: str) -> list:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    header_row = next(rows)
    columns = build_column_index(header_row)

    factories = []
    for row in rows:
        old_reg_no = row[columns["old_reg_no"]]
        if old_reg_no is None:
            continue
        type_code = parse_type_code(str(old_reg_no))
        province = row[columns["province"]]
        factory = {
            "fid": row[columns["fid"]],
            "old_reg_no": old_reg_no,
            "name": row[columns["name"]],
            "operator": row[columns["operator"]],
            "business": row[columns["business"]],
            "address_no": _clean_str(row[columns["address_no"]]),
            "moo": _clean_str(row[columns["moo"]]),
            "soi": _clean_str(row[columns["soi"]]),
            "road": _clean_str(row[columns["road"]]),
            "tambon": _clean_str(row[columns["tambon"]]),
            "amphoe": row[columns["amphoe"]],
            "province": province,
            "region": region_for_province(province),
            "postcode": _clean_str(row[columns["postcode"]]),
            "phone": _clean_str(row[columns["phone"]]),
            "hp_registered": row[columns["hp_registered"]],
            "hp_inspected": row[columns["hp_inspected"]],
            "type_code": type_code,
            "type_main": type_main(type_code),
            "commercial_reg": _clean_str(row[columns["commercial_reg"]]),
            "tax_id": _clean_str(row[columns["tax_id"]]),
        }
        factories.append(factory)
    wb.close()
    return factories


def build_meta(factories: list) -> dict:
    type_counts = {}
    province_counts = {}
    region_counts = {}
    hp_registered_max = 0
    hp_inspected_max = 0
    for factory in factories:
        type_counts[factory["type_code"]] = type_counts.get(factory["type_code"], 0) + 1
        province_counts[factory["province"]] = province_counts.get(factory["province"], 0) + 1
        region_counts[factory["region"]] = region_counts.get(factory["region"], 0) + 1
        if factory["hp_registered"] is not None:
            hp_registered_max = max(hp_registered_max, factory["hp_registered"])
        if factory["hp_inspected"] is not None:
            hp_inspected_max = max(hp_inspected_max, factory["hp_inspected"])

    return {
        "type_codes": [
            {"code": code, "count": count}
            for code, count in sorted(type_counts.items(), key=lambda kv: kv[1], reverse=True)
        ],
        "provinces": [
            {"name": name, "count": count, "region": region_for_province(name)}
            for name, count in sorted(province_counts.items(), key=lambda kv: kv[1], reverse=True)
        ],
        "regions": [
            {"name": region, "count": region_counts.get(region, 0)}
            for region in REGION_ORDER
        ],
        "hp_registered_max": hp_registered_max,
        "hp_inspected_max": hp_inspected_max,
    }


def main():
    factories = load_factories_from_workbook("Responsible factories section6.xlsx")

    with open("data/processed/factories_nationwide.json", "w", encoding="utf-8") as f:
        json.dump(factories, f, ensure_ascii=False)

    meta = build_meta(factories)
    with open("data/processed/meta_nationwide.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
