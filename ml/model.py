from __future__ import annotations

import numpy as np

from .feature_extraction import (
    build_feature_matrix,
    extract_feature,
    fit_feature_transformer,
    transform_features,
)
from .helper import (
    compute_mahalanobis_batch,
    compute_mahalanobis_threshold,
    fit_gmm_classifier,
    predict_gmm_class,
)


def _accuracy_score(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(y_true == y_pred))


def _macro_f1_score(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    labels = np.unique(np.concatenate([y_true, y_pred]))
    f1_scores = []

    for label in labels:
        true_positive = np.sum((y_true == label) & (y_pred == label))
        false_positive = np.sum((y_true != label) & (y_pred == label))
        false_negative = np.sum((y_true == label) & (y_pred != label))

        precision = true_positive / (true_positive + false_positive + 1e-12)
        recall = true_positive / (true_positive + false_negative + 1e-12)

        if precision + recall == 0:
            f1_scores.append(0.0)
        else:
            f1_scores.append((2 * precision * recall) / (precision + recall))

    return float(np.mean(f1_scores)) if f1_scores else 0.0


def _classification_report_text(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    labels = np.unique(np.concatenate([y_true, y_pred]))
    lines = ["label\tprecision\trecall\tf1-score\tsupport"]

    for label in labels:
        true_positive = np.sum((y_true == label) & (y_pred == label))
        false_positive = np.sum((y_true != label) & (y_pred == label))
        false_negative = np.sum((y_true == label) & (y_pred != label))
        support = int(np.sum(y_true == label))

        precision = true_positive / (true_positive + false_positive + 1e-12)
        recall = true_positive / (true_positive + false_negative + 1e-12)
        f1_score = 0.0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)

        lines.append(
            f"{label}\t{precision:.3f}\t{recall:.3f}\t{f1_score:.3f}\t{support}"
        )

    return "\n".join(lines)


class VegetableGMMModel:
    """Pipeline train/evaluate/predict cho mô hình GMM phân loại rau củ."""

    def __init__(self, config):
        self.config = config
        self.feature_params = config["feature"]
        self.use_scaler = config["transform"]["use_scaler"]
        self.use_lda = config["transform"]["use_lda"]
        self.gmm_params = config["gmm"]
        self.maha_params = config["mahalanobis"]

        self.scaler = None
        self.lda = None
        self.classes = None
        self.gmms = None
        self.priors = None
        self.threshold_maha = None
        self.is_trained = False

    def train(self, train_df, val_df=None, path_col="path", label_col="class"):
        X_train, y_train = build_feature_matrix(
            train_df,
            path_col=path_col,
            label_col=label_col,
            feature_params=self.feature_params,
        )

        if y_train is None or len(y_train) == 0:
            raise ValueError("Train data phải có cột nhãn để fit mô hình.")

        X_train_t, self.scaler, self.lda = fit_feature_transformer(
            X_train,
            y_train,
            use_scaler=self.use_scaler,
            use_lda=self.use_lda,
        )

        self.classes, self.gmms, self.priors = fit_gmm_classifier(
            X_train_t,
            y_train,
            n_components=self.gmm_params["n_components"],
            covariance_type=self.gmm_params["covariance_type"],
            reg_covar=self.gmm_params["reg_covar"],
            random_state=self.gmm_params["random_state"],
        )

        maha_mode = self.maha_params["mode"]

        if maha_mode == "none":
            self.threshold_maha = None

        elif maha_mode == "manual":
            threshold = self.maha_params.get("threshold")
            if threshold is None:
                raise ValueError("mode='manual' yêu cầu mahalanobis.threshold trong config.")
            self.threshold_maha = float(threshold)

        elif maha_mode == "percentile":
            percentile = self.maha_params["percentile"]
            source = self.maha_params.get("source", "train")

            if source == "validation" and val_df is not None and len(val_df) > 0:
                X_val, _ = build_feature_matrix(
                    val_df,
                    path_col=path_col,
                    label_col=label_col,
                    feature_params=self.feature_params,
                )
                X_source = transform_features(X_val, scaler=self.scaler, lda=self.lda)
            else:
                X_source = X_train_t

            self.threshold_maha = compute_mahalanobis_threshold(
                X_source,
                self.classes,
                self.gmms,
                percentile=percentile,
            )

        else:
            raise ValueError("mahalanobis.mode chỉ nhận 'none', 'manual' hoặc 'percentile'.")

        self.is_trained = True
        return self

    def evaluate(self, test_df, path_col="path", label_col="class", reject_ood=None):
        if not self.is_trained:
            raise RuntimeError("Model chưa được train.")

        X_test, y_true = build_feature_matrix(
            test_df,
            path_col=path_col,
            label_col=label_col,
            feature_params=self.feature_params,
        )
        if y_true is None:
            raise ValueError("Test data phải có nhãn để evaluate.")

        if reject_ood is None:
            reject_ood = self.maha_params["reject_ood_by_default"]

        X_test_t = transform_features(X_test, scaler=self.scaler, lda=self.lda)
        pred_class, confidence, _ = predict_gmm_class(
            X_test_t,
            self.classes,
            self.gmms,
            self.priors,
        )
        maha = compute_mahalanobis_batch(X_test_t, self.classes, self.gmms)

        is_ood = np.zeros(len(X_test_t), dtype=bool)
        if reject_ood and self.threshold_maha is not None:
            is_ood = maha["distance"] > self.threshold_maha

        y_pred = pred_class.astype(object)
        y_pred[is_ood] = "OOD"

        metrics = {
            "accuracy": _accuracy_score(y_true, y_pred),
            "macro_f1": _macro_f1_score(y_true, y_pred),
            "rejection_rate": float(np.mean(is_ood)),
            "n_samples": int(len(y_true)),
            "n_ood": int(np.sum(is_ood)),
            "threshold_maha": self.threshold_maha,
            "y_true": y_true,
            "y_pred": y_pred,
            "mahalanobis": maha["distance"],
            "confidence": confidence,
            "classification_report": _classification_report_text(y_true, y_pred),
        }
        return metrics

    def predict(self, image_or_path, reject_ood=None):
        if not self.is_trained:
            raise RuntimeError("Model chưa được train.")

        if reject_ood is None:
            reject_ood = self.maha_params["reject_ood_by_default"]

        feature = extract_feature(image_or_path, **self.feature_params)
        X = np.asarray([feature], dtype=np.float32)
        X_t = transform_features(X, scaler=self.scaler, lda=self.lda)

        pred_class, confidence, proba = predict_gmm_class(
            X_t,
            self.classes,
            self.gmms,
            self.priors,
        )
        maha = compute_mahalanobis_batch(X_t, self.classes, self.gmms)
        distance = float(maha["distance"][0])

        is_ood = False
        if reject_ood and self.threshold_maha is not None:
            is_ood = distance > self.threshold_maha

        final_prediction = "OOD" if is_ood else str(pred_class[0])

        return {
            "prediction": final_prediction,
            "class_prediction": str(pred_class[0]),
            "confidence": float(confidence[0]),
            "is_ood": bool(is_ood),
            "mahalanobis": distance,
            "threshold_maha": None if self.threshold_maha is None else float(self.threshold_maha),
            "nearest_class_by_mahalanobis": str(maha["nearest_class"][0]),
            "nearest_component": int(maha["nearest_component"][0]),
            "proba": {
                str(cls): float(prob)
                for cls, prob in zip(self.classes, proba[0])
            },
            "model_name": self.__class__.__name__,
        }
