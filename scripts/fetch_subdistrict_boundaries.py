import json

import requests

from scripts.fetch_boundaries import NORTH_PROVINCES, filter_boundaries, round_coordinates

SUBDISTRICTS_URL = "https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/subdistricts.geojson"


def main():
    response = requests.get(SUBDISTRICTS_URL, timeout=30)
    response.raise_for_status()
    subdistricts_geojson = round_coordinates(
        filter_boundaries(response.json(), NORTH_PROVINCES, "pro_th"), 5
    )
    with open("data/boundaries/subdistricts.geojson", "w", encoding="utf-8") as f:
        json.dump(subdistricts_geojson, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
