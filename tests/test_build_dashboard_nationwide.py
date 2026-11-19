import unittest

from scripts.build_dashboard_nationwide import inject


class TestInject(unittest.TestCase):
    def test_replaces_all_seven_placeholders(self):
        template = (
            "const FACTORIES = /*__FACTORIES__*/ [];\n"
            "const PROVINCES_GEOJSON = /*__PROVINCES_GEOJSON__*/ {};\n"
            "const DISTRICTS_GEOJSON = /*__DISTRICTS_GEOJSON__*/ {};\n"
            "const META = /*__META__*/ {};\n"
            "const SUBDISTRICT_CENTROIDS = /*__SUBDISTRICT_CENTROIDS__*/ [];\n"
            "const SUBDISTRICTS_GEOJSON = /*__SUBDISTRICTS_GEOJSON__*/ {};\n"
            "const REGIONS_GEOJSON = /*__REGIONS_GEOJSON__*/ {};\n")
        result = inject(template, {
            "FACTORIES": [{"name": "x"}],
            "PROVINCES_GEOJSON": {"type": "FeatureCollection"},
            "DISTRICTS_GEOJSON": {"type": "FeatureCollection"},
            "META": {"a": 1},
            "SUBDISTRICT_CENTROIDS": [{"tambon": "y"}],
            "SUBDISTRICTS_GEOJSON": {"type": "z"},
            "REGIONS_GEOJSON": {"type": "w"},
        })
        self.assertNotIn("/*__FACTORIES__*/ []", result)
        self.assertIn('"name": "x"', result)
        self.assertIn('"a": 1', result)
        self.assertIn('"tambon": "y"', result)
        self.assertIn('"type": "z"', result)
        self.assertIn('"type": "w"', result)


if __name__ == "__main__":
    unittest.main()
