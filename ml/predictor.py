from __future__ import annotations

from pathlib import Path

from .helper import load_config
from .label_mapping import get_vietnamese_label
from .model_loader import load_trained_model


def predict(image_path):
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh cần dự đoán: {image_path}")

    model = load_trained_model()

    # Cập nhật threshold linh hoạt từ config.json mà không cần train lại (nếu dùng chế độ manual)
    config_path = Path(__file__).resolve().parent / "config" / "config.json"
    try:
        current_config = load_config(config_path)
        maha_config = current_config.get("mahalanobis", {})
        if maha_config.get("mode") == "manual" and "threshold" in maha_config:
            model.threshold_maha = float(maha_config["threshold"])
            model.maha_params = maha_config
    except Exception:
        pass

    raw_result = model.predict(image_path)

    final_label = str(raw_result.get("prediction") or raw_result.get("class_prediction") or "").strip()
    if not final_label:
        raise RuntimeError("VegetableGMMModel.predict() không trả về nhãn hợp lệ.")

    result = {
        "label": final_label,
        "label_vi": get_vietnamese_label(final_label),
        "confidence": float(raw_result.get("confidence", 0.0)),
        "model_name": raw_result.get("model_name", "VegetableGMMModel"),
    }

    if "class_prediction" in raw_result:
        result["class_prediction"] = raw_result["class_prediction"]
        result["class_prediction_vi"] = get_vietnamese_label(raw_result["class_prediction"])

    for key in (
        "is_ood",
        "mahalanobis",
        "threshold_maha",
        "nearest_class_by_mahalanobis",
        "nearest_component",
        "proba",
    ):
        if key in raw_result:
            result[key] = raw_result[key]

    return result
