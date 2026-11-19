import os
import tempfile
import unittest

import openpyxl

from scripts.build_factories_nationwide import (
    build_meta, load_factories_from_workbook, parse_type_code, type_main,
)

HEADERS = [
    "ลำดับ", "เลขทะเบียนเดิม", "ประเภทรอง", "FID", "ชื่อโรงงาน", "ผู้ประกอบการ",
    "ประกอบกิจการ", "เลขที่", "หมู่", "ซอย", "ถนน", "ตำบล", "อำเภอ", "จังหวัด",
    "ไปรษณีย์", "โทรศัพท์", "เงินทุนรวม", "ค่าอาคาร", "ค่าที่ดิน", "ค่าเครื่องจักร",
    "ทุนหมุนเวียน", "คนงานชาย", "คนงานหญิง", "คนงานรวม", "แรงม้า", "แรงม้าตรวจพบ",
    "กำลังผลิต", "หน่วย", "ทะเบียนพาณิชย์", "เลขผู้เสียภาษี", "ประเภท",
]


def _write_workbook(rows) -> str:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(HEADERS)
    for row in rows:
        ws.append(row)
    fd, path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    wb.save(path)
    return path


class TestParseTypeCode(unittest.TestCase):
    def test_parses_type_code_with_subtype(self):
        self.assertEqual(parse_type_code("3-10(1)-6/55"), "10(1)")
        self.assertEqual(type_main("10(1)"), "10")

    def test_parses_fertiliser_type_43(self):
        self.assertEqual(parse_type_code("3-43(1)-11/64"), "43(1)")
        self.assertEqual(type_main("43(1)"), "43")


class TestLoadFactoriesFromWorkbook(unittest.TestCase):
    def test_maps_columns_by_header_name_and_tags_region(self):
        row = [1, "3-10(1)-6/55", None, 999, "โรงงานทดสอบ", "-", "ทดสอบ",
               "1", "-", "-", "ถนนทดสอบ", "ตำบลทดสอบ", "ลาดกระบัง",
               "กรุงเทพมหานคร", 10520, None, 0, 0, 0, 0, 0, 0, 0, 0,
               138, 138, None, "ตัน/ปี", None, None, "-01001-"]
        path = _write_workbook([row])
        try:
            factories = load_factories_from_workbook(path)
        finally:
            os.remove(path)

        self.assertEqual(len(factories), 1)
        factory = factories[0]
        self.assertEqual(factory["province"], "กรุงเทพมหานคร")
        self.assertEqual(factory["region"], "กลาง")
        self.assertEqual(factory["type_code"], "10(1)")
        self.assertEqual(factory["type_main"], "10")
        self.assertEqual(factory["hp_registered"], 138)

    def test_tags_fertiliser_factory_with_its_own_province_region(self):
        row = [1, "3-43(1)-11/64", None, 999, "โรงปุ๋ยทดสอบ", "-", "ผลิตปุ๋ย",
               "1", "-", "-", "ถนนทดสอบ", "ตำบลทดสอบ", "เมืองเชียงใหม่",
               "เชียงใหม่", 50000, None, 0, 0, 0, 0, 0, 0, 0, 0,
               100, 100, None, "ตัน/ปี", None, None, "-01001-"]
        path = _write_workbook([row])
        try:
            factories = load_factories_from_workbook(path)
        finally:
            os.remove(path)

        factory = factories[0]
        self.assertEqual(factory["type_main"], "43")
        self.assertEqual(factory["region"], "เหนือ")

    def test_skips_rows_with_no_registration_number(self):
        row = [None] * len(HEADERS)
        path = _write_workbook([row])
        try:
            factories = load_factories_from_workbook(path)
        finally:
            os.remove(path)
        self.assertEqual(factories, [])


class TestBuildMeta(unittest.TestCase):
    def test_counts_type_codes_provinces_and_regions(self):
        factories = [
            {"type_code": "43(1)", "province": "เชียงใหม่", "region": "เหนือ",
             "hp_registered": 100, "hp_inspected": 90},
            {"type_code": "43(1)", "province": "เชียงใหม่", "region": "เหนือ",
             "hp_registered": 50, "hp_inspected": None},
            {"type_code": "10(1)", "province": "กรุงเทพมหานคร", "region": "กลาง",
             "hp_registered": 200, "hp_inspected": 200},
        ]
        meta = build_meta(factories)
        self.assertEqual(meta["hp_registered_max"], 200)
        self.assertEqual(meta["hp_inspected_max"], 200)
        type_counts = {t["code"]: t["count"] for t in meta["type_codes"]}
        self.assertEqual(type_counts["43(1)"], 2)
        province_counts = {p["name"]: p["count"] for p in meta["provinces"]}
        self.assertEqual(province_counts["เชียงใหม่"], 2)
        region_counts = {r["name"]: r["count"] for r in meta["regions"]}
        self.assertEqual(region_counts["เหนือ"], 2)
        self.assertEqual(region_counts["กลาง"], 1)


if __name__ == "__main__":
    unittest.main()
