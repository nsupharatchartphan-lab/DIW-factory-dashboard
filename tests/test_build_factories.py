import unittest

from scripts.build_factories import parse_type_code, type_main, load_factories_from_workbook

WORKBOOK_PATH = "list of factories north thailand.xlsx"


class TestParseTypeCode(unittest.TestCase):
    def test_simple_prefix(self):
        self.assertEqual(parse_type_code("3-10(3)-2/22ชม"), "10(3)")

    def test_letter_digit_prefix(self):
        self.assertEqual(parse_type_code("จ3-10(1)-1/39ชม"), "10(1)")

    def test_letter_dot_prefix_no_dash_before_type(self):
        self.assertEqual(parse_type_code("น.53(5)-1/2540-นนน."), "53(5)")

    def test_no_sub_type(self):
        self.assertEqual(parse_type_code("3-105-112/48ชม"), "105")


class TestTypeMain(unittest.TestCase):
    def test_with_subtype(self):
        self.assertEqual(type_main("10(3)"), "10")

    def test_without_subtype(self):
        self.assertEqual(type_main("105"), "105")


class TestMalformedRowFix(unittest.TestCase):
    def test_ttd_solar_row_is_corrected(self):
        factories = {f["fid"]: f for f in load_factories_from_workbook(WORKBOOK_PATH)}
        row = factories[10600271025699]
        self.assertEqual(row["province"], "นครสวรรค์")
        self.assertEqual(row["amphoe"], "ตากฟ้า")
        self.assertIsNone(row["tambon"])
        self.assertEqual(row["postcode"], "60190")
        self.assertEqual(row["hp_registered"], 12351)  # best-effort, see Global Constraints
