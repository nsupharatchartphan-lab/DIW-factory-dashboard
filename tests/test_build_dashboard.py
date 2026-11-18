import unittest

from scripts.build_dashboard import inject


class TestInject(unittest.TestCase):
    def test_replaces_all_five_placeholders(self):
        template = (
            "const FACTORIES = /*__FACTORIES__*/ [];\n"
            "const PROVINCES_GEOJSON = /*__PROVINCES_GEOJSON__*/ {};\n"
            "const DISTRICTS_GEOJSON = /*__DISTRICTS_GEOJSON__*/ {};\n"
            "const META = /*__META__*/ {};\n"
            "const SUBDISTRICT_CENTROIDS = /*__SUBDISTRICT_CENTROIDS__*/ [];\n")
        result = inject(
            template, [{"name": "x"}], {"a": 1}, {"type": "FeatureCollection"},
            {"type": "FeatureCollection"}, [{"tambon": "y"}])
        self.assertNotIn("/*__FACTORIES__*/ []", result)
        self.assertIn('"name": "x"', result)
        self.assertIn('"a": 1', result)
        self.assertIn('"tambon": "y"', result)
