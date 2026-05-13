from __future__ import annotations

from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError as exc:  # pragma: no cover - depends on environment
    cv2 = None
    _CV2_IMPORT_ERROR = exc
else:  # pragma: no cover - trivial assignment
    _CV2_IMPORT_ERROR = None


def _require_cv2():
    if cv2 is None:
        raise RuntimeError(
            "Không thể xử lý ảnh vì thiếu opencv-python. "
            "Hãy cài các dependency trong requirements.txt."
        ) from _CV2_IMPORT_ERROR


def _validate_color_image(image):
    image = np.asarray(image)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Ảnh đầu vào phải có shape (H, W, 3).")
    return image


def read_image(image_or_path):
    _require_cv2()

    if isinstance(image_or_path, (str, Path)):
        image_path = Path(image_or_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"Không đọc được ảnh: {image_path}")

        return image

    if isinstance(image_or_path, np.ndarray):
        return image_or_path.copy()

    raise TypeError("image_or_path phải là đường dẫn ảnh hoặc numpy.ndarray.")


def convert_bgr_to_rgb(img_bgr):
    _require_cv2()

    image = _validate_color_image(img_bgr)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def preprocess_image(img_rgb, target_size=(128, 128), mode="letterbox"):
    _require_cv2()

    image = _validate_color_image(img_rgb)

    if not isinstance(target_size, (list, tuple)) or len(target_size) != 2:
        raise ValueError("target_size phải là tuple/list gồm 2 số nguyên.")

    target_w, target_h = int(target_size[0]), int(target_size[1])
    if target_w <= 0 or target_h <= 0:
        raise ValueError("target_size phải chứa giá trị dương.")

    if mode == "resize":
        return cv2.resize(image, (target_w, target_h), interpolation=cv2.INTER_AREA)

    if mode == "letterbox":
        height, width = image.shape[:2]
        scale = min(target_w / width, target_h / height)
        new_w = max(1, int(round(width * scale)))
        new_h = max(1, int(round(height * scale)))

        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        canvas = np.full((target_h, target_w, 3), 255, dtype=np.uint8)

        x_offset = (target_w - new_w) // 2
        y_offset = (target_h - new_h) // 2
        canvas[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = resized
        return canvas

    raise ValueError("mode chỉ nhận 'resize' hoặc 'letterbox'.")


def prepare_image(image_or_path, target_size=(128, 128), mode="letterbox"):
    # OpenCV đọc ảnh theo BGR, nên contract nội bộ được chuẩn hóa sang RGB tại đây.
    image_bgr = read_image(image_or_path)
    image_rgb = convert_bgr_to_rgb(image_bgr)
    return preprocess_image(image_rgb, target_size=target_size, mode=mode)
