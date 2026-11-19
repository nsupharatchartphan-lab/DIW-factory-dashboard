import unittest

from scripts.regions import tag_region


class TestTagRegion(unittest.TestCase):
    def test_adds_region_property_using_province_key(self):
        geojson = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"pro_th": "เชียงใหม่"}, "geometry": {}},
            {"type": "Feature", "properties": {"pro_th": "สงขลา"}, "geometry": {}},
        ]}
        result = tag_region(geojson)
        self.assertEqual(result["features"][0]["properties"]["region"], "เหนือ")
        self.assertEqual(result["features"][1]["properties"]["region"], "ใต้")


if __name__ == "__main__":
    unittest.main()
