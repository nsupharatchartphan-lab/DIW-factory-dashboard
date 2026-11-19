import unittest

from scripts.fetch_boundaries_nationwide import DISTRICTS_URL, PROVINCES_URL
from scripts.fetch_boundaries import filter_boundaries
from scripts.regions import ALL_PROVINCES, tag_region


class TestFetchBoundariesNationwide(unittest.TestCase):
    def test_urls_point_at_the_same_repo_as_the_north_fetch(self):
        self.assertTrue(PROVINCES_URL.endswith("provinces.geojson"))
        self.assertTrue(DISTRICTS_URL.endswith("districts.geojson"))

    def test_keeps_every_province_and_tags_its_region(self):
        sample = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"pro_th": "เชียงใหม่"}, "geometry": {}},
            {"type": "Feature", "properties": {"pro_th": "สงขลา"}, "geometry": {}},
            {"type": "Feature", "properties": {"pro_th": "ไม่มีจริง"}, "geometry": {}},
        ]}
        filtered = tag_region(filter_boundaries(sample, ALL_PROVINCES, "pro_th"))
        self.assertEqual(len(filtered["features"]), 2)
        regions = {f["properties"]["pro_th"]: f["properties"]["region"] for f in filtered["features"]}
        self.assertEqual(regions["เชียงใหม่"], "เหนือ")
        self.assertEqual(regions["สงขลา"], "ใต้")


if __name__ == "__main__":
    unittest.main()
