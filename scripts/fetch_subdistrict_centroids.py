import json

import requests

SUBDISTRICTS_URL = "https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/subdistricts.geojson"

NORTH_PROVINCES = {
    "เชียงใหม่", "นครสวรรค์", "เชียงราย", "กำแพงเพชร", "ลำปาง", "เพชรบูรณ์",
    "ลำพูน", "ตาก", "พิษณุโลก", "พิจิตร", "สุโขทัย", "แพร่", "พะเยา",
    "อุตรดิตถ์", "น่าน", "อุทัยธานี", "แม่ฮ่องสอน",
}


def extract_centroids(geojson: dict, allowed_provinces: set) -> list:
    result = []
    for feature in geojson["features"]:
        props = feature["properties"]
        if props["pro_th"] not in allowed_provinces:
            continue
        result.append({
            "province": props["pro_th"],
            "amphoe": props["amp_th"],
            "tambon": props["tam_th"],
            "lat": props["lat"],
            "lon": props["lon"],
        })
    return result


def main():
    response = requests.get(SUBDISTRICTS_URL, timeout=30)
    response.raise_for_status()
    centroids = extract_centroids(response.json(), NORTH_PROVINCES)
    with open("data/boundaries/subdistrict_centroids.json", "w", encoding="utf-8") as f:
        json.dump(centroids, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
