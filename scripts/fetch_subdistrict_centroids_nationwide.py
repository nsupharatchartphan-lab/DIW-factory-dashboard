import json

import requests

from scripts.fetch_subdistrict_centroids import extract_centroids
from scripts.regions import ALL_PROVINCES

SUBDISTRICTS_URL = "https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/subdistricts.geojson"


def main():
    response = requests.get(SUBDISTRICTS_URL, timeout=30)
    response.raise_for_status()
    centroids = extract_centroids(response.json(), ALL_PROVINCES)
    with open("data/boundaries/subdistrict_centroids_nationwide.json", "w", encoding="utf-8") as f:
        json.dump(centroids, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
