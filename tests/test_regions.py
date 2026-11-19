import unittest

from scripts.regions import (
    ALL_PROVINCES, PROVINCE_REGION, REGION_COLOR_SCALE_10, REGION_ORDER,
    region_for_province,
)


class TestRegions(unittest.TestCase):
    def test_covers_all_77_provinces_exactly_once(self):
        self.assertEqual(len(ALL_PROVINCES), 77)
        self.assertEqual(len(PROVINCE_REGION), 77)

    def test_known_province_assignments(self):
        self.assertEqual(region_for_province("เชียงใหม่"), "เหนือ")
        self.assertEqual(region_for_province("กรุงเทพมหานคร"), "กลาง")
        self.assertEqual(region_for_province("ชลบุรี"), "ตะวันออก")
        self.assertEqual(region_for_province("ขอนแก่น"), "ตะวันออกเฉียงเหนือ")
        self.assertEqual(region_for_province("สงขลา"), "ใต้")

    def test_every_region_has_a_10_step_color_ramp(self):
        for region in REGION_ORDER:
            self.assertIn(region, REGION_COLOR_SCALE_10)
            self.assertEqual(len(REGION_COLOR_SCALE_10[region]), 10)

    def test_unknown_province_falls_back_to_central(self):
        self.assertEqual(region_for_province("ไม่มีจังหวัดนี้"), "กลาง")


if __name__ == "__main__":
    unittest.main()
