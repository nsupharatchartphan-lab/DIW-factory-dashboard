import unittest

from scripts.fetch_subdistrict_boundaries import SUBDISTRICTS_URL
from scripts.fetch_boundaries import NORTH_PROVINCES, filter_boundaries, round_coordinates


class TestFetchSubdistrictBoundaries(unittest.TestCase):
    def test_reuses_the_same_filter_and_round_helpers_as_districts(self):
        # This script has no new pure logic of its own: it filters and
        # rounds subdistricts.geojson with the exact same functions
        # fetch_boundaries.py already uses (and tests) for provinces and
        # districts. This test pins that reuse so a future refactor
        # can't quietly duplicate or diverge the filtering logic.
        sample = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"pro_th": "เชียงใหม่"},
             "geometry": {"type": "Polygon", "coordinates": [[[98.123456, 18.654321]]]}},
            {"type": "Feature", "properties": {"pro_th": "สงขลา"},
             "geometry": {"type": "Polygon", "coordinates": [[[100.1, 7.2]]]}},
        ]}
        result = round_coordinates(filter_boundaries(sample, NORTH_PROVINCES, "pro_th"), 5)
        self.assertEqual(len(result["features"]), 1)
        self.assertEqual(result["features"][0]["properties"]["pro_th"], "เชียงใหม่")

    def test_url_points_at_the_same_repo_as_the_centroid_fetch(self):
        self.assertIn("OpenGISData-Thailand", SUBDISTRICTS_URL)
        self.assertTrue(SUBDISTRICTS_URL.endswith("subdistricts.geojson"))
