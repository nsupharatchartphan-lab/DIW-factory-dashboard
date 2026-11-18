import unittest

from scripts.fetch_boundaries import filter_boundaries, round_coordinates

SAMPLE = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"pro_th": "เชียงใหม่"},
     "geometry": {"type": "Polygon", "coordinates": [[[98.123456, 18.654321]]]}},
    {"type": "Feature", "properties": {"pro_th": "สงขลา"},
     "geometry": {"type": "Polygon", "coordinates": [[[100.1, 7.2]]]}},
]}


class TestFilterBoundaries(unittest.TestCase):
    def test_keeps_only_allowed_provinces(self):
        result = filter_boundaries(SAMPLE, {"เชียงใหม่"}, "pro_th")
        self.assertEqual(len(result["features"]), 1)
        self.assertEqual(result["features"][0]["properties"]["pro_th"], "เชียงใหม่")


class TestRoundCoordinates(unittest.TestCase):
    def test_rounds_nested_polygon_coords(self):
        result = round_coordinates(SAMPLE, 2)
        self.assertEqual(
            result["features"][0]["geometry"]["coordinates"],
            [[[98.12, 18.65]]])
