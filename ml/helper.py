from __future__ import annotations

"""
Helpers for dataset scanning, config loading, and GMM utilities.

`ml/config/config.json` is expected to be strict JSON without inline comments.
Any prose explanations should live in Python docstrings or project docs instead.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from sklearn.mixture import GaussianMixture
except ImportError as exc:  # pragma: no cover - depends on environment
    GaussianMixture = None
    _GAUSSIAN_MIXTURE_IMPORT_ERROR = exc
else:  # pragma: no cover - trivial assignment
    _GAUSSIAN_MIXTURE_IMPORT_ERROR = None


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
REQUIRED_CONFIG_SECTIONS = {"feature", "transform", "gmm", "mahalanobis"}


def _require_gaussian_mixture():
    if GaussianMixture is None:
        raise RuntimeError(
            "Không thể train GMM vì thiếu scikit-learn. "
            "Hãy cài các dependency trong requirements.txt."
        ) from _GAUSSIAN_MIXTURE_IMPORT_ERROR


def _logsumexp(values, axis=1, keepdims=True):
    values = np.asarray(values, dtype=np.float64)
    max_values = np.max(values, axis=axis, keepdims=True)
    stable = np.exp(values - max_values)
    summed = np.sum(stable, axis=axis, keepdims=True)
    result = max_values + np.log(summed + 1e-12)

    if not keepdims:
        result = np.squeeze(result, axis=axis)

    return result


def scan_dataset(dataset_root, splits=("train", "validation", "test")):
    dataset_root = Path(dataset_root)
    rows = []

    for split in splits:
        split_dir = dataset_root / split
        if not split_dir.exists():
            continue

        for class_dir in sorted(split_dir.iterdir()):
            if not class_dir.is_dir():
                continue

            for img_path in class_dir.rglob("*"):
                if img_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
                    continue

                rows.append(
                    {
                        "split": split,
                        "class": class_dir.name,
                        "path": str(img_path),
                    }
                )

    return pd.DataFrame(rows, columns=["split", "class", "path"])


def load_config(config_path):
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file config: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as file_obj:
            config = json.load(file_obj)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Config {config_path} không phải JSON hợp lệ. "
            "Hãy bỏ comment hoặc dữ liệu thừa khỏi file."
        ) from exc

    missing_sections = sorted(REQUIRED_CONFIG_SECTIONS - set(config))
    if missing_sections:
        raise ValueError(
            f"Config {config_path} thiếu các section bắt buộc: {', '.join(missing_sections)}"
        )

    target_size = config["feature"].get("target_size")
    if not isinstance(target_size, (list, tuple)) or len(target_size) != 2:
        raise ValueError("feature.target_size phải là list gồm 2 số nguyên dương.")

    target_size = tuple(int(size) for size in target_size)
    if any(size <= 0 for size in target_size):
        raise ValueError("feature.target_size phải chứa giá trị dương.")

    config["feature"]["target_size"] = target_size

    mode = config["mahalanobis"].get("mode")
    if mode not in {"none", "manual", "percentile"}:
        raise ValueError("mahalanobis.mode chỉ nhận 'none', 'manual' hoặc 'percentile'.")

    return config


def fit_gmm_classifier(
    X_train,
    y_train,
    n_components=3,
    covariance_type="full",
    reg_covar=1e-5,
    random_state=42,
):
    _require_gaussian_mixture()

    X_train = np.asarray(X_train, dtype=np.float64)
    y_train = np.asarray(y_train)

    if len(X_train) == 0 or len(y_train) == 0:
        raise ValueError("Dữ liệu train trống, không thể fit GMM.")

    if len(X_train) != len(y_train):
        raise ValueError("Số mẫu và số nhãn train không khớp nhau.")

    requested_components = max(1, int(n_components))
    classes = np.array(sorted(np.unique(y_train)))
    gmms = {}
    priors = {}
    n_total = len(y_train)

    for cls in classes:
        X_cls = X_train[y_train == cls]
        if len(X_cls) == 0:
            continue

        priors[cls] = len(X_cls) / n_total
        effective_components = max(1, min(requested_components, len(X_cls)))

        gmm = GaussianMixture(
            n_components=effective_components,
            covariance_type=covariance_type,
            reg_covar=reg_covar,
            max_iter=200,
            random_state=random_state,
        )
        gmm.fit(X_cls)
        gmms[cls] = gmm

    if not gmms:
        raise ValueError("Không fit được bất kỳ GMM class nào từ dữ liệu train.")

    return classes, gmms, priors


def predict_gmm_proba(X, classes, gmms, priors):
    X = np.asarray(X, dtype=np.float64)

    if len(classes) == 0:
        raise ValueError("Classes rỗng, không thể tính xác suất GMM.")

    log_scores = []
    for cls in classes:
        gmm = gmms[cls]
        log_likelihood = gmm.score_samples(X)
        log_prior = np.log(float(priors[cls]) + 1e-12)
        log_scores.append(log_likelihood + log_prior)

    log_scores = np.vstack(log_scores).T
    log_norm = _logsumexp(log_scores, axis=1, keepdims=True)
    return np.exp(log_scores - log_norm)


def predict_gmm_class(X, classes, gmms, priors):
    proba = predict_gmm_proba(X, classes, gmms, priors)
    pred_index = np.argmax(proba, axis=1)
    pred_class = classes[pred_index]
    confidence = proba[np.arange(len(X)), pred_index]
    return pred_class, confidence, proba


def get_gmm_covariance(gmm, component_idx):
    dim = gmm.means_.shape[1]

    if gmm.covariance_type == "full":
        return gmm.covariances_[component_idx]

    if gmm.covariance_type == "diag":
        return np.diag(gmm.covariances_[component_idx])

    if gmm.covariance_type == "spherical":
        return np.eye(dim, dtype=np.float64) * gmm.covariances_[component_idx]

    if gmm.covariance_type == "tied":
        return gmm.covariances_

    raise ValueError(f"Không hỗ trợ covariance_type={gmm.covariance_type}")


def mahalanobis_distance_to_gmms(x, classes, gmms):
    x = np.asarray(x, dtype=np.float64)
    min_distance = float("inf")
    nearest_class = None
    nearest_component = None

    for cls in classes:
        gmm = gmms[cls]

        for component_idx in range(gmm.n_components):
            mean = gmm.means_[component_idx]
            covariance = get_gmm_covariance(gmm, component_idx)
            inv_covariance = np.linalg.pinv(covariance)
            diff = x - mean
            squared_distance = float(diff.T @ inv_covariance @ diff)
            distance = float(np.sqrt(max(squared_distance, 0.0)))

            if distance < min_distance:
                min_distance = distance
                nearest_class = cls
                nearest_component = component_idx

    return min_distance, nearest_class, nearest_component


def compute_mahalanobis_batch(X, classes, gmms):
    X = np.asarray(X, dtype=np.float64)
    distances = []
    nearest_classes = []
    nearest_components = []

    for sample in X:
        distance, nearest_class, nearest_component = mahalanobis_distance_to_gmms(
            sample,
            classes,
            gmms,
        )
        distances.append(distance)
        nearest_classes.append(nearest_class)
        nearest_components.append(nearest_component)

    return {
        "distance": np.asarray(distances, dtype=np.float64),
        "nearest_class": np.asarray(nearest_classes, dtype=object),
        "nearest_component": np.asarray(nearest_components, dtype=np.int64),
    }


def compute_mahalanobis_threshold(X, classes, gmms, percentile=95):
    percentile = float(percentile)
    if not 0 < percentile <= 100:
        raise ValueError("percentile phải nằm trong khoảng (0, 100].")

    maha = compute_mahalanobis_batch(X, classes, gmms)
    return float(np.percentile(maha["distance"], percentile))
