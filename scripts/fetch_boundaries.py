import json

import requests

PROVINCES_URL = "https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/provinces.geojson"
DISTRICTS_URL = "https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/districts.geojson"

NORTH_PROVINCES = {
    "เชียงใหม่", "นครสวรรค์", "เชียงราย", "กำแพงเพชร", "ลำปาง", "เพชรบูรณ์",
    "ลำพูน", "ตาก", "พิษณุโลก", "พิจิตร", "สุโขทัย", "แพร่", "พะเยา",
    "อุตรดิตถ์", "น่าน", "อุทัยธานี", "แม่ฮ่องสอน",
}


def filter_boundaries(geojson: dict, allowed_provinces: set, province_key: str) -> dict:
    return {
        "type": geojson["type"],
        "features": [
            feature
            for feature in geojson["features"]
            if feature["properties"][province_key] in allowed_provinces
        ],
    }


def round_coordinates(geojson: dict, ndigits: int) -> dict:
    def round_coords(coords):
        if isinstance(coords[0], (int, float)):
            return [round(c, ndigits) for c in coords]
        return [round_coords(c) for c in coords]

    return {
        "type": geojson["type"],
        "features": [
            {
                **feature,
                "geometry": {
                    **feature["geometry"],
                    "coordinates": round_coords(feature["geometry"]["coordinates"]),
                },
            }
            for feature in geojson["features"]
        ],
    }


def main():
    provinces = requests.get(PROVINCES_URL, timeout=10)
    provinces.raise_for_status()
    districts = requests.get(DISTRICTS_URL, timeout=10)
    districts.raise_for_status()

    provinces_geojson = round_coordinates(
        filter_boundaries(provinces.json(), NORTH_PROVINCES, "pro_th"), 5
    )
    districts_geojson = round_coordinates(
        filter_boundaries(districts.json(), NORTH_PROVINCES, "pro_th"), 5
    )

    with open("data/boundaries/provinces.geojson", "w", encoding="utf-8") as f:
        json.dump(provinces_geojson, f, ensure_ascii=False)
    with open("data/boundaries/districts.geojson", "w", encoding="utf-8") as f:
        json.dump(districts_geojson, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
