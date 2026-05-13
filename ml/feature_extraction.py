from __future__ import annotations

import numpy as np

try:
    import cv2
except ImportError as exc:  # pragma: no cover - depends on environment
    cv2 = None
    _CV2_IMPORT_ERROR = exc
else:  # pragma: no cover - trivial assignment
    _CV2_IMPORT_ERROR = None

try:
    from skimage.feature import local_binary_pattern
except ImportError:  # pragma: no cover - optional dependency
    local_binary_pattern = None

try:
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.preprocessing import StandardScaler
except ImportError as exc:  # pragma: no cover - depends on environment
    LinearDiscriminantAnalysis = None
    StandardScaler = None
    _SKLEARN_TRANSFORM_IMPORT_ERROR = exc
else:  # pragma: no cover - trivial assignment
    _SKLEARN_TRANSFORM_IMPORT_ERROR = None

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover - optional dependency
    tqdm = None

from .preprocessing import prepare_image


class NumpyStandardScaler:
    """Legacy scaler class kept for backward-compatible joblib loading."""

    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X):
        X = np.asarray(X, dtype=np.float64)
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0)
        self.scale_[self.scale_ == 0] = 1.0
        return self

    def transform(self, X):
        if self.mean_ is None or self.scale_ is None:
            raise RuntimeError("Scaler chưa được fit.")

        X = np.asarray(X, dtype=np.float64)
        return (X - self.mean_) / self.scale_


class NumpyLinearDiscriminantAnalysis:
    """Legacy LDA class kept for backward-compatible joblib loading."""

    def __init__(self, n_components):
        self.n_components = int(n_components)
        self.xbar_ = None
        self.scalings_ = None

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)

        classes = np.unique(y)
        if len(classes) < 2:
            raise ValueError("LDA cần ít nhất 2 lớp khác nhau.")

        overall_mean = X.mean(axis=0)
        scatter_within = np.zeros((X.shape[1], X.shape[1]), dtype=np.float64)
        scatter_between = np.zeros_like(scatter_within)

        for cls in classes:
            X_cls = X[y == cls]
            class_mean = X_cls.mean(axis=0)
            centered = X_cls - class_mean
            scatter_within += centered.T @ centered

            mean_delta = (class_mean - overall_mean).reshape(-1, 1)
            scatter_between += len(X_cls) * (mean_delta @ mean_delta.T)

        scatter_within += np.eye(scatter_within.shape[0], dtype=np.float64) * 1e-6
        matrix = np.linalg.pinv(scatter_within) @ scatter_between
        eigenvalues, eigenvectors = np.linalg.eig(matrix)

        order = np.argsort(np.real(eigenvalues))[::-1]
        selected = np.real(eigenvectors[:, order[: self.n_components]])

        self.xbar_ = overall_mean
        self.scalings_ = selected
        return self

    def transform(self, X):
        if self.xbar_ is None or self.scalings_ is None:
            raise RuntimeError("LDA chưa được fit.")

        X = np.asarray(X, dtype=np.float64)
        return (X - self.xbar_) @ self.scalings_


def _require_cv2():
    if cv2 is None:
        raise RuntimeError(
            "Không thể trích xuất đặc trưng vì thiếu opencv-python."
        ) from _CV2_IMPORT_ERROR


def _require_sklearn_transformers():
    if StandardScaler is None or LinearDiscriminantAnalysis is None:
        raise RuntimeError(
            "Không thể fit scaler/LDA vì thiếu scikit-learn."
        ) from _SKLEARN_TRANSFORM_IMPORT_ERROR


def _validate_prepared_rgb_image(image):
    image = np.asarray(image)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("Ảnh đầu vào phải có shape (H, W, 3).")
    return image


def _extract_uniform_lbp_histogram(gray, P=8, R=1):
    if P != 8 or R != 1:
        raise RuntimeError(
            "Chế độ fallback LBP hiện chỉ hỗ trợ P=8 và R=1. "
            "Hãy cài scikit-image nếu muốn dùng cấu hình khác."
        )

    padded = np.pad(gray, 1, mode="edge")
    center = padded[1:-1, 1:-1]
    offsets = [
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
        (1, 0),
        (1, -1),
        (0, -1),
    ]

    bits = []
    height, width = gray.shape
    for dy, dx in offsets:
        neighbor = padded[1 + dy : 1 + dy + height, 1 + dx : 1 + dx + width]
        bits.append((neighbor >= center).astype(np.uint8))

    bit_stack = np.stack(bits, axis=0)
    transitions = np.sum(bit_stack != np.roll(bit_stack, -1, axis=0), axis=0)
    ones = np.sum(bit_stack, axis=0)
    lbp_bins = np.where(transitions <= 2, ones, P + 1)

    hist = np.bincount(lbp_bins.ravel(), minlength=P + 2).astype(np.float32)
    return hist / (hist.sum() + 1e-8)


def extract_features(prepared_image, **feature_params):
    return extract_feature(prepared_image, skip_preprocess=True, **feature_params)


def extract_hsv_feature(img_rgb, h_bins=32, s_bins=32, v_bins=32):
    _require_cv2()

    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    hist_h = cv2.calcHist([hsv], [0], None, [h_bins], [0, 180]).flatten()
    hist_s = cv2.calcHist([hsv], [1], None, [s_bins], [0, 256]).flatten()
    hist_v = cv2.calcHist([hsv], [2], None, [v_bins], [0, 256]).flatten()

    feature = np.concatenate([hist_h, hist_s, hist_v]).astype(np.float32)
    return feature / (feature.sum() + 1e-8)


def extract_lbp_feature(img_rgb, P=8, R=1):
    _require_cv2()

    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

    if local_binary_pattern is not None:
        lbp = local_binary_pattern(gray, P=P, R=R, method="uniform")
        n_bins = P + 2
        hist, _ = np.histogram(
            lbp.ravel(),
            bins=np.arange(0, n_bins + 1),
            range=(0, n_bins),
        )
        hist = hist.astype(np.float32)
        return hist / (hist.sum() + 1e-8)

    return _extract_uniform_lbp_histogram(gray, P=P, R=R)


def extract_feature(
    image_or_path,
    target_size=(128, 128),
    preprocess_mode="letterbox",
    h_bins=32,
    s_bins=32,
    v_bins=32,
    lbp_P=8,
    lbp_R=1,
    skip_preprocess=False,
):
    if skip_preprocess and isinstance(image_or_path, np.ndarray):
        image = _validate_prepared_rgb_image(image_or_path).copy()
    else:
        # Train/predict path chuẩn hóa toàn bộ ảnh đầu vào sang RGB trước khi lấy feature.
        image = prepare_image(
            image_or_path,
            target_size=target_size,
            mode=preprocess_mode,
        )

    hsv_feature = extract_hsv_feature(
        image,
        h_bins=h_bins,
        s_bins=s_bins,
        v_bins=v_bins,
    )
    lbp_feature = extract_lbp_feature(image, P=lbp_P, R=lbp_R)
    return np.concatenate([hsv_feature, lbp_feature]).astype(np.float32)


def build_feature_matrix(
    df,
    path_col="path",
    label_col="class",
    feature_params=None,
    show_progress=True,
):
    if df is None or len(df) == 0:
        raise ValueError("DataFrame đầu vào trống, không thể build feature matrix.")

    feature_params = feature_params or {}
    iterator = df.iterrows()
    if show_progress and tqdm is not None:
        iterator = tqdm(iterator, total=len(df), desc="Extract features")

    X = []
    y = []

    for _, row in iterator:
        X.append(extract_feature(row[path_col], **feature_params))

        if label_col is not None and label_col in df.columns:
            y.append(row[label_col])

    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(y) if label_col is not None and label_col in df.columns else None
    return X, y


def fit_feature_transformer(X_train, y_train, use_scaler=True, use_lda=True):
    X_train = np.asarray(X_train, dtype=np.float64)
    y_train = None if y_train is None else np.asarray(y_train)

    scaler = None
    lda = None
    X_train_t = X_train

    if use_scaler or use_lda:
        _require_sklearn_transformers()

    if use_scaler:
        scaler = StandardScaler().fit(X_train_t)
        X_train_t = scaler.transform(X_train_t)

    if use_lda:
        if y_train is None:
            raise ValueError("Không thể dùng LDA nếu thiếu nhãn train.")

        n_classes = len(np.unique(y_train))
        n_components = min(n_classes - 1, X_train_t.shape[1])
        if n_components > 0:
            lda = LinearDiscriminantAnalysis(n_components=n_components)
            X_train_t = lda.fit_transform(X_train_t, y_train)

    return np.asarray(X_train_t, dtype=np.float32), scaler, lda


def transform_features(X, scaler=None, lda=None):
    X_t = np.asarray(X, dtype=np.float64)

    if scaler is not None:
        X_t = scaler.transform(X_t)

    if lda is not None:
        X_t = lda.transform(X_t)

    return np.asarray(X_t, dtype=np.float32)
