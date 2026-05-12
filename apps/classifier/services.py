from pathlib import Path
from time import perf_counter

from django.conf import settings
from django.core.files.storage import default_storage

from ml.predictor import predict


def classify_uploaded_image(uploaded_file):
    """Save the uploaded file and delegate prediction to the ML package."""
    start_time = perf_counter()
    saved_name = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)
    image_path = Path(settings.MEDIA_ROOT) / saved_name
    result = predict(image_path)
    elapsed_time = perf_counter() - start_time

    try:
        confidence_value = float(result.get("confidence", 0))
    except (TypeError, ValueError):
        confidence_value = 0.0

    confidence_percent = confidence_value * 100 if confidence_value <= 1 else confidence_value
    result["image_url"] = f"{settings.MEDIA_URL}{saved_name}".replace("\\", "/")
    result["stored_path"] = str(image_path)
    result["confidence_percent"] = round(confidence_percent, 2)
    result["processing_time"] = result.get("processing_time") or f"{elapsed_time:.1f}s"
    result["model_name"] = result.get("model_name") or "VegetableGMMModel"
    return result
