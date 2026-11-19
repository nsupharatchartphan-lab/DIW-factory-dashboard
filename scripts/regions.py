NORTH = {
    "เชียงใหม่", "นครสวรรค์", "เชียงราย", "กำแพงเพชร", "ลำปาง", "เพชรบูรณ์",
    "ลำพูน", "ตาก", "พิษณุโลก", "พิจิตร", "สุโขทัย", "แพร่", "พะเยา",
    "อุตรดิตถ์", "น่าน", "อุทัยธานี", "แม่ฮ่องสอน",
}

BANGKOK = {"กรุงเทพมหานคร"}

CENTRAL = {
    "กาญจนบุรี", "ชัยนาท", "นครนายก", "นครปฐม", "นนทบุรี",
    "ปทุมธานี", "ประจวบคีรีขันธ์", "พระนครศรีอยุธยา", "ราชบุรี", "ลพบุรี",
    "สมุทรปราการ", "สมุทรสงคราม", "สมุทรสาคร", "สระบุรี", "สิงห์บุรี",
    "สุพรรณบุรี", "เพชรบุรี", "อ่างทอง",
}

EAST = {
    "จันทบุรี", "ฉะเชิงเทรา", "ชลบุรี", "ตราด", "ปราจีนบุรี", "ระยอง", "สระแก้ว",
}

NORTHEAST = {
    "กาฬสินธุ์", "ขอนแก่น", "ชัยภูมิ", "นครพนม", "นครราชสีมา", "บึงกาฬ",
    "บุรีรัมย์", "มหาสารคาม", "มุกดาหาร", "ยโสธร", "ร้อยเอ็ด", "ศรีสะเกษ",
    "สกลนคร", "สุรินทร์", "หนองคาย", "หนองบัวลำภู", "อำนาจเจริญ", "อุดรธานี",
    "อุบลราชธานี", "เลย",
}

SOUTH = {
    "กระบี่", "ชุมพร", "ตรัง", "นครศรีธรรมราช", "นราธิวาส", "ปัตตานี",
    "พังงา", "พัทลุง", "ภูเก็ต", "ยะลา", "ระนอง", "สงขลา", "สตูล",
    "สุราษฎร์ธานี",
}

REGION_PROVINCES = {
    "เหนือ": NORTH,
    "กลาง": CENTRAL,
    "กทม.": BANGKOK,
    "ตะวันออก": EAST,
    "ตะวันออกเฉียงเหนือ": NORTHEAST,
    "ใต้": SOUTH,
}

REGION_ORDER = ["เหนือ", "กลาง", "กทม.", "ตะวันออก", "ตะวันออกเฉียงเหนือ", "ใต้"]

PROVINCE_REGION = {
    province: region
    for region, provinces in REGION_PROVINCES.items()
    for province in provinces
}

ALL_PROVINCES = set(PROVINCE_REGION.keys())

# Pastel 10-step ramps — softer, lower-saturation tones throughout
# (even the "deepest" step stays muted) so the whole country reads as
# pastel rather than the earlier saturated single-tone ramps.
REGION_COLOR_SCALE_10 = {
    "เหนือ": ["#fff6ec", "#fde9d2", "#fbdab3", "#f7c896", "#f2b67c",
              "#eba366", "#e08f57", "#cf7a4a", "#b5663d", "#8f4f30"],
    "กลาง": ["#f1f4fb", "#dfe6f6", "#c7d4ef", "#abc0e6", "#8facdb",
             "#7398cf", "#5d84c0", "#4c71ac", "#3e5e92", "#314b75"],
    "กทม.": ["#fdf1f6", "#fbdfec", "#f7c9e0", "#f1aed1", "#ea90c0",
             "#df74ad", "#cf5c98", "#b84880", "#98386a", "#763054"],
    "ตะวันออก": ["#f6f0fb", "#e9dcf5", "#dac5ee", "#c7a9e3", "#b38dd7",
                 "#9f72ca", "#8a5cb8", "#73499c", "#5c3a7d", "#462c60"],
    "ตะวันออกเฉียงเหนือ": ["#f0faf1", "#dcf3e0", "#c2e9c9", "#a3deac", "#85d190",
                           "#68c078", "#52a863", "#3f8c50", "#2f6f3e", "#22542f"],
    "ใต้": ["#fff1ee", "#ffe0d8", "#ffcabb", "#ffb29d", "#fb9982",
            "#f0806a", "#de6a56", "#c25646", "#9f4539", "#7a362c"],
}


def region_for_province(province: str) -> str:
    return PROVINCE_REGION.get(province, "กลาง")


def tag_region(geojson: dict, province_key: str = "pro_th") -> dict:
    return {
        "type": geojson["type"],
        "features": [
            {
                **feature,
                "properties": {
                    **feature["properties"],
                    "region": region_for_province(feature["properties"][province_key]),
                },
            }
            for feature in geojson["features"]
        ],
    }
