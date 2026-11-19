import unittest

from scripts.label_layout import add_label_positions


def _square(cx, cy, half):
    return {
        "type": "Polygon",
        "coordinates": [[
            [cx - half, cy - half], [cx + half, cy - half],
            [cx + half, cy + half], [cx - half, cy + half],
            [cx - half, cy - half],
        ]],
    }


class TestAddLabelPositions(unittest.TestCase):
    def test_label_sits_inside_the_polygon_when_nothing_crowds_it(self):
        geojson = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"pro_th": "ก"}, "geometry": _square(0, 0, 2)},
        ]}
        result = add_label_positions(geojson)
        props = result["features"][0]["properties"]
        self.assertFalse(props["label_shifted"])
        self.assertAlmostEqual(props["label_lon"], 0, places=1)
        self.assertAlmostEqual(props["label_lat"], 0, places=1)

    def test_pushes_apart_two_tightly_packed_provinces(self):
        # Two tiny adjacent squares near Bangkok's latitude — their
        # long province names would overlap at the shared border
        # without any nudging.
        geojson = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"pro_th": "สมุทรปราการ"},
             "geometry": _square(100.5, 13.6, 0.03)},
            {"type": "Feature", "properties": {"pro_th": "สมุทรสาคร"},
             "geometry": _square(100.56, 13.6, 0.03)},
        ]}
        result = add_label_positions(geojson)
        p0 = result["features"][0]["properties"]
        p1 = result["features"][1]["properties"]
        self.assertTrue(p0["label_shifted"] or p1["label_shifted"])
        separation = ((p0["label_lon"] - p1["label_lon"]) ** 2 +
                      (p0["label_lat"] - p1["label_lat"]) ** 2) ** 0.5
        original_separation = ((p0["label_anchor_lon"] - p1["label_anchor_lon"]) ** 2 +
                                (p0["label_anchor_lat"] - p1["label_anchor_lat"]) ** 2) ** 0.5
        self.assertGreater(separation, original_separation)

    def test_never_shifts_further_than_the_cap(self):
        geojson = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"pro_th": "ก" * 30},
             "geometry": _square(0, 13, 0.001)},
            {"type": "Feature", "properties": {"pro_th": "ข" * 30},
             "geometry": _square(0.002, 13, 0.001)},
        ]}
        result = add_label_positions(geojson)
        for feature in result["features"]:
            props = feature["properties"]
            dist = ((props["label_lon"] - props["label_anchor_lon"]) ** 2 +
                    (props["label_lat"] - props["label_anchor_lat"]) ** 2) ** 0.5
            self.assertLessEqual(dist, 0.6 + 1e-6)


if __name__ == "__main__":
    unittest.main()
