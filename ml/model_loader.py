from functools import lru_cache
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent.parent / "ml_models"


@lru_cache(maxsize=1)
def load_model_assets():
    """Return placeholder paths for serialized ML artifacts."""
    return {
        "model_path": MODEL_DIR / "vegetable_model.pkl",
        "scaler_path": MODEL_DIR / "scaler.pkl",
        "label_encoder_path": MODEL_DIR / "label_encoder.pkl",
    }
