LABEL_MAPPING = {
    "carrot": "Cà rốt",
    "potato": "Khoai tây",
    "tomato": "Cà chua",
    "cabbage": "Bắp cải",
}


def get_vietnamese_label(label: str) -> str:
    return LABEL_MAPPING.get(label, label)
