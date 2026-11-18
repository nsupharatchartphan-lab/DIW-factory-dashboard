import unittest

from scripts.match_boundaries import build_excel_pairs, build_boundary_pairs, find_unmatched


class TestBuildExcelPairs(unittest.TestCase):
    def test_extracts_distinct_pairs(self):
        factories = [{"province": "เชียงใหม่", "amphoe": "เมืองเชียงใหม่"},
                     {"province": "เชียงใหม่", "amphoe": "เมืองเชียงใหม่"},
                     {"province": "ลำปาง", "amphoe": "เมืองลำปาง"}]
        self.assertEqual(build_excel_pairs(factories),
                          {("เชียงใหม่", "เมืองเชียงใหม่"), ("ลำปาง", "เมืองลำปาง")})


class TestBuildBoundaryPairs(unittest.TestCase):
    def test_extracts_distinct_pairs(self):
        geojson = {"features": [
            {"properties": {"pro_th": "เชียงใหม่", "amp_th": "เมืองเชียงใหม่"}}]}
        self.assertEqual(build_boundary_pairs(geojson), {("เชียงใหม่", "เมืองเชียงใหม่")})


class TestFindUnmatched(unittest.TestCase):
    def test_direct_match_is_not_unmatched(self):
        excel = {("เชียงใหม่", "เมืองเชียงใหม่")}
        boundary = {("เชียงใหม่", "เมืองเชียงใหม่")}
        self.assertEqual(find_unmatched(excel, boundary, {}), set())

    def test_aliased_match_is_not_unmatched(self):
        excel = {("เชียงใหม่", "เมืองฯ")}
        boundary = {("เชียงใหม่", "เมืองเชียงใหม่")}
        aliases = {("เชียงใหม่", "เมืองฯ"): ("เชียงใหม่", "เมืองเชียงใหม่")}
        self.assertEqual(find_unmatched(excel, boundary, aliases), set())

    def test_truly_unmatched_is_reported(self):
        excel = {("เชียงใหม่", "ไม่มีจริง")}
        boundary = {("เชียงใหม่", "เมืองเชียงใหม่")}
        self.assertEqual(find_unmatched(excel, boundary, {}), {("เชียงใหม่", "ไม่มีจริง")})
