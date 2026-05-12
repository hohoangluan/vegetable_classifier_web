from __future__ import annotations

import pickle
from functools import lru_cache
from pathlib import Path

try:
    import joblib
except ImportError:  # pragma: no cover - optional dependency
    joblib = None

from .helper import load_config
from .model import VegetableGMMModel


MODEL_DIR = Path(__file__).resolve().parent.parent / "ml_models"
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "config.json"
DEFAULT_MODEL_PATH = MODEL_DIR / "vegetable_model.pkl"


def create_model_from_json(config_path=DEFAULT_CONFIG_PATH):
    config = load_config(config_path)
    return VegetableGMMModel(config)


def load_model_assets():
    return {
        "config_path": DEFAULT_CONFIG_PATH,
        "model_path": DEFAULT_MODEL_PATH,
        "legacy_scaler_path": MODEL_DIR / "scaler.pkl",
        "legacy_label_encoder_path": MODEL_DIR / "label_encoder.pkl",
    }


def _deserialize_model(model_path):
    errors = []

    if joblib is not None:
        try:
            return joblib.load(model_path)
        except Exception as exc:  # pragma: no cover - depends on artifact format
            errors.append(exc)

    try:
        with model_path.open("rb") as file_obj:
            return pickle.load(file_obj)
    except Exception as exc:
        errors.append(exc)

    if errors:
        last_error = errors[-1]
        raise RuntimeError(
            f"Không thể load model từ {model_path}. "
            f"Artifact có thể bị hỏng hoặc thiếu dependency phù hợp: {last_error}"
        ) from last_error

    raise RuntimeError(f"Không thể load model từ {model_path}.")


@lru_cache(maxsize=1)
def load_trained_model(model_path=DEFAULT_MODEL_PATH):
    model_path = Path(model_path)

    if not model_path.exists():
        raise FileNotFoundError(f"Không tìm thấy model artifact: {model_path}")

    if model_path.stat().st_size <= 1:
        raise RuntimeError(
            f"Model artifact {model_path} đang rỗng hoặc chỉ là placeholder. "
            "Hãy train và lưu một VegetableGMMModel hợp lệ trước khi predict."
        )

    model = _deserialize_model(model_path)

    if not isinstance(model, VegetableGMMModel):
        raise TypeError(
            f"Artifact {model_path} không chứa VegetableGMMModel hợp lệ, "
            f"nhận được {type(model).__name__}."
        )

    if not getattr(model, "is_trained", False):
        raise RuntimeError(
            f"VegetableGMMModel trong {model_path} chưa được train hoàn chỉnh."
        )

    return model
