LABEL_MAPPING = {
    "carrot": "Ca rot",
    "potato": "Khoai tay",
    "tomato": "Ca chua",
    "cabbage": "Bap cai",
}


def get_vietnamese_label(label: str) -> str:
    return LABEL_MAPPING.get(label, label)
