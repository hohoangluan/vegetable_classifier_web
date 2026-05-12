from pathlib import Path

from .feature_extraction import extract_features
from .label_mapping import get_vietnamese_label
from .model_loader import load_model_assets
from .preprocessing import prepare_image


def predict(image_path):
    """Mock predictor used to demonstrate the web-to-ML flow."""
    normalized_path = Path(image_path)

    _prepared = prepare_image(normalized_path)
    _features = extract_features(_prepared)
    _assets = load_model_assets()

    label = "carrot"
    return {
        "label": label,
        "label_vi": get_vietnamese_label(label),
        "confidence": 0.92,
    }
