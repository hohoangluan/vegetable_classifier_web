from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage

from ml.predictor import predict


def classify_uploaded_image(uploaded_file):
    """Save the uploaded file and delegate prediction to the ML package."""
    saved_name = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)
    image_path = Path(settings.MEDIA_ROOT) / saved_name
    result = predict(image_path)
    result["image_url"] = f"{settings.MEDIA_URL}{saved_name}".replace("\\", "/")
    result["stored_path"] = str(image_path)
    return result
