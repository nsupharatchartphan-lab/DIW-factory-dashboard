import math

from shapely.geometry import shape

# Calibrated for the map's typical whole-country view (the province
# level always fits all of Thailand in frame, which sits around this
# zoom on a normal screen) so the label-collision estimate matches
# what the viewer actually sees, rather than an arbitrary scale.
TARGET_ZOOM = 6
CHAR_WIDTH_PX = 7.2
LABEL_PADDING_PX = 8
LABEL_HEIGHT_PX = 26  # name + count, two lines
MEAN_LAT_FOR_SCALE = 13.0
ITERATIONS = 400
MAX_SHIFT_DEG = 0.6


def _meters_per_pixel(lat_deg: float, zoom: int) -> float:
    return 156543.03392 * math.cos(math.radians(lat_deg)) / (2 ** zoom)


def _half_extents_deg(name: str, lat_deg: float):
    mpp = _meters_per_pixel(lat_deg, TARGET_ZOOM)
    width_px = len(name) * CHAR_WIDTH_PX + LABEL_PADDING_PX
    half_width_m = (width_px / 2) * mpp
    half_height_m = (LABEL_HEIGHT_PX / 2) * mpp
    lon_scale = 111320 * math.cos(math.radians(lat_deg))
    half_width_deg = half_width_m / lon_scale if lon_scale else 0
    half_height_deg = half_height_m / 111320
    return half_width_deg, half_height_deg


def add_label_positions(provinces_geojson: dict) -> dict:
    features = provinces_geojson["features"]

    anchors = []
    half_extents = []
    for feature in features:
        geom = shape(feature["geometry"])
        point = geom.representative_point()
        anchors.append([point.x, point.y])
        half_extents.append(_half_extents_deg(feature["properties"]["pro_th"], point.y))

    positions = [list(a) for a in anchors]

    for _ in range(ITERATIONS):
        moved = False
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                xi, yi = positions[i]
                xj, yj = positions[j]
                hwi, hhi = half_extents[i]
                hwj, hhj = half_extents[j]
                overlap_x = (hwi + hwj) - abs(xi - xj)
                overlap_y = (hhi + hhj) - abs(yi - yj)
                if overlap_x > 0 and overlap_y > 0:
                    moved = True
                    if overlap_x < overlap_y:
                        push = overlap_x / 2 + 1e-6
                        direction = 1 if xi >= xj else -1
                        positions[i][0] += direction * push
                        positions[j][0] -= direction * push
                    else:
                        push = overlap_y / 2 + 1e-6
                        direction = 1 if yi >= yj else -1
                        positions[i][1] += direction * push
                        positions[j][1] -= direction * push
        if not moved:
            break

    new_features = []
    for feature, anchor, pos in zip(features, anchors, positions):
        dx = pos[0] - anchor[0]
        dy = pos[1] - anchor[1]
        dist = math.hypot(dx, dy)
        if dist > MAX_SHIFT_DEG:
            scale = MAX_SHIFT_DEG / dist
            pos = [anchor[0] + dx * scale, anchor[1] + dy * scale]
            dist = MAX_SHIFT_DEG
        shifted = dist > 1e-4
        new_features.append({
            **feature,
            "properties": {
                **feature["properties"],
                "label_lon": round(pos[0], 5),
                "label_lat": round(pos[1], 5),
                "label_anchor_lon": round(anchor[0], 5),
                "label_anchor_lat": round(anchor[1], 5),
                "label_shifted": shifted,
            },
        })

    return {"type": provinces_geojson["type"], "features": new_features}
