import unittest

from scripts.fetch_subdistrict_centroids import extract_centroids

SAMPLE = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {
        "pro_th": "เชียงใหม่", "amp_th": "เมืองเชียงใหม่", "tam_th": "ศรีภูมิ",
        "lat": 18.79, "lon": 98.98}},
    {"type": "Feature", "properties": {
        "pro_th": "สงขลา", "amp_th": "เมืองสงขลา", "tam_th": "บ่อยาง",
        "lat": 7.2, "lon": 100.6}},
]}


class TestExtractCentroids(unittest.TestCase):
    def test_keeps_only_allowed_provinces_and_needed_fields(self):
        result = extract_centroids(SAMPLE, {"เชียงใหม่"})
        self.assertEqual(result, [
            {"province": "เชียงใหม่", "amphoe": "เมืองเชียงใหม่", "tambon": "ศรีภูมิ",
             "lat": 18.79, "lon": 98.98},
        ])
