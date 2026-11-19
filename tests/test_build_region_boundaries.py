import unittest

from shapely.geometry import shape

from scripts.build_region_boundaries import dissolve_regions


def _square(x0, y0, x1, y1):
    return {
        "type": "Polygon",
        "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]],
    }


class TestDissolveRegions(unittest.TestCase):
    def test_merges_adjacent_same_region_provinces_into_one_feature(self):
        geojson = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"pro_th": "a", "region": "เหนือ"},
             "geometry": _square(0, 0, 1, 1)},
            {"type": "Feature", "properties": {"pro_th": "b", "region": "เหนือ"},
             "geometry": _square(1, 0, 2, 1)},
        ]}
        result = dissolve_regions(geojson)
        self.assertEqual(len(result["features"]), 1)
        feature = result["features"][0]
        self.assertEqual(feature["properties"]["region"], "เหนือ")
        merged = shape(feature["geometry"])
        self.assertAlmostEqual(merged.area, 2.0)

    def test_keeps_regions_as_separate_features(self):
        geojson = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"pro_th": "a", "region": "เหนือ"},
             "geometry": _square(0, 0, 1, 1)},
            {"type": "Feature", "properties": {"pro_th": "b", "region": "ใต้"},
             "geometry": _square(5, 5, 6, 6)},
        ]}
        result = dissolve_regions(geojson)
        regions = {f["properties"]["region"] for f in result["features"]}
        self.assertEqual(regions, {"เหนือ", "ใต้"})

    def test_output_order_follows_region_order(self):
        geojson = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"pro_th": "a", "region": "ใต้"},
             "geometry": _square(0, 0, 1, 1)},
            {"type": "Feature", "properties": {"pro_th": "b", "region": "เหนือ"},
             "geometry": _square(5, 5, 6, 6)},
        ]}
        result = dissolve_regions(geojson)
        regions_in_order = [f["properties"]["region"] for f in result["features"]]
        self.assertEqual(regions_in_order, ["เหนือ", "ใต้"])


if __name__ == "__main__":
    unittest.main()
