import json

import requests

from scripts.fetch_boundaries import filter_boundaries, round_coordinates
from scripts.regions import ALL_PROVINCES, tag_region

PROVINCES_URL = "https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/provinces.geojson"
DISTRICTS_URL = "https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/districts.geojson"


def main():
    provinces = requests.get(PROVINCES_URL, timeout=30)
    provinces.raise_for_status()
    districts = requests.get(DISTRICTS_URL, timeout=30)
    districts.raise_for_status()

    provinces_geojson = tag_region(round_coordinates(
        filter_boundaries(provinces.json(), ALL_PROVINCES, "pro_th"), 5
    ))
    districts_geojson = tag_region(round_coordinates(
        filter_boundaries(districts.json(), ALL_PROVINCES, "pro_th"), 5
    ))

    with open("data/boundaries/provinces_nationwide.geojson", "w", encoding="utf-8") as f:
        json.dump(provinces_geojson, f, ensure_ascii=False)
    with open("data/boundaries/districts_nationwide.geojson", "w", encoding="utf-8") as f:
        json.dump(districts_geojson, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
