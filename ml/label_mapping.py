from __future__ import annotations

from pathlib import Path


DATASET_TRAIN_DIR = Path(__file__).resolve().parents[2] / "dataset" / "train"

LABEL_MAPPING = {
    "Bean": "Đậu que",
    "Bitter_Gourd": "Khổ qua",
    "Bottle_Gourd": "Bầu",
    "Brinjal": "Cà tím",
    "Broccoli": "Súp lơ xanh",
    "Cabbage": "Bắp cải",
    "Capsicum": "Ớt chuông",
    "Carrot": "Cà rốt",
    "Cauliflower": "Súp lơ trắng",
    "Cucumber": "Dưa chuột",
    "Papaya": "Đu đủ",
    "Potato": "Khoai tây",
    "Pumpkin": "Bí đỏ",
    "Radish": "Củ cải",
    "Tomato": "Cà chua",
    "OOD": "Không xác định (OOD)",
}


def normalize_label(label) -> str:
    return str(label).strip().lower().replace("-", "_").replace(" ", "_")


def get_dataset_class_names(dataset_train_dir=DATASET_TRAIN_DIR):
    dataset_train_dir = Path(dataset_train_dir)

    if not dataset_train_dir.exists():
        return [label for label in LABEL_MAPPING if label != "OOD"]

    return [
        directory.name
        for directory in sorted(dataset_train_dir.iterdir())
        if directory.is_dir()
    ]


def get_dataset_label_items(dataset_train_dir=DATASET_TRAIN_DIR):
    return [
        {
            "label": class_name,
            "label_vi": get_vietnamese_label(class_name),
        }
        for class_name in get_dataset_class_names(dataset_train_dir)
    ]


def get_vietnamese_label(label: str) -> str:
    if label is None:
        return "Không xác định"

    raw_label = str(label).strip()
    if raw_label in LABEL_MAPPING:
        return LABEL_MAPPING[raw_label]

    normalized_label = normalize_label(raw_label)
    for source_label, display_label in LABEL_MAPPING.items():
        if normalize_label(source_label) == normalized_label:
            return display_label

    return raw_label.replace("_", " ")
