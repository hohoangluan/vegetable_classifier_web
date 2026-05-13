from __future__ import annotations

import unittest

import cv2
import numpy as np
from numpy.testing import assert_allclose
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import StandardScaler

from ml import feature_extraction as feature_module
from ml.feature_extraction import (
    NumpyLinearDiscriminantAnalysis,
    NumpyStandardScaler,
    extract_hsv_feature,
    extract_lbp_feature,
    fit_feature_transformer,
    transform_features,
)
from ml.preprocessing import convert_bgr_to_rgb, prepare_image


def _legacy_hsv_feature(img_bgr, h_bins=8, s_bins=8, v_bins=8):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    hist_h = cv2.calcHist([hsv], [0], None, [h_bins], [0, 180]).flatten()
    hist_s = cv2.calcHist([hsv], [1], None, [s_bins], [0, 256]).flatten()
    hist_v = cv2.calcHist([hsv], [2], None, [v_bins], [0, 256]).flatten()

    feature = np.concatenate([hist_h, hist_s, hist_v]).astype(np.float32)
    return feature / (feature.sum() + 1e-8)


def _legacy_lbp_feature(img_bgr, P=8, R=1):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    if feature_module.local_binary_pattern is not None:
        lbp = feature_module.local_binary_pattern(gray, P=P, R=R, method="uniform")
        n_bins = P + 2
        hist, _ = np.histogram(
            lbp.ravel(),
            bins=np.arange(0, n_bins + 1),
            range=(0, n_bins),
        )
        hist = hist.astype(np.float32)
        return hist / (hist.sum() + 1e-8)

    return feature_module._extract_uniform_lbp_histogram(gray, P=P, R=R)


class FeaturePipelineTests(unittest.TestCase):
    def test_prepare_image_converts_bgr_input_to_rgb(self):
        img_bgr = np.array([[[0, 0, 255]]], dtype=np.uint8)

        prepared = prepare_image(img_bgr, target_size=(1, 1), mode="resize")

        np.testing.assert_array_equal(prepared, np.array([[[255, 0, 0]]], dtype=np.uint8))

    def test_rgb_features_match_legacy_bgr_pipeline(self):
        img_bgr = np.array(
            [
                [[0, 0, 255], [0, 255, 0], [255, 0, 0]],
                [[25, 50, 200], [120, 80, 10], [10, 220, 180]],
                [[90, 10, 60], [255, 255, 255], [0, 0, 0]],
            ],
            dtype=np.uint8,
        )
        img_rgb = convert_bgr_to_rgb(img_bgr)

        new_hsv = extract_hsv_feature(img_rgb, h_bins=8, s_bins=8, v_bins=8)
        new_lbp = extract_lbp_feature(img_rgb, P=8, R=1)

        legacy_hsv = _legacy_hsv_feature(img_bgr, h_bins=8, s_bins=8, v_bins=8)
        legacy_lbp = _legacy_lbp_feature(img_bgr, P=8, R=1)

        assert_allclose(new_hsv, legacy_hsv, atol=1e-7)
        assert_allclose(new_lbp, legacy_lbp, atol=1e-7)

    def test_fit_feature_transformer_uses_sklearn_classes(self):
        X = np.array(
            [
                [0.0, 1.0, 2.0],
                [1.0, 1.0, 3.0],
                [8.0, 4.0, 1.0],
                [9.0, 5.0, 0.0],
            ],
            dtype=np.float32,
        )
        y = np.array(["leafy", "leafy", "root", "root"])

        X_t, scaler, lda = fit_feature_transformer(X, y, use_scaler=True, use_lda=True)

        self.assertIsInstance(scaler, StandardScaler)
        self.assertIsInstance(lda, LinearDiscriminantAnalysis)
        self.assertEqual(X_t.shape, (4, 1))

    def test_transform_features_supports_sklearn_and_legacy_transformers(self):
        X = np.array(
            [
                [0.0, 1.0, 2.0],
                [1.0, 1.0, 3.0],
                [8.0, 4.0, 1.0],
                [9.0, 5.0, 0.0],
            ],
            dtype=np.float32,
        )
        y = np.array(["leafy", "leafy", "root", "root"])

        sklearn_scaler = StandardScaler().fit(X)
        sklearn_lda = LinearDiscriminantAnalysis(n_components=1)
        sklearn_lda.fit(sklearn_scaler.transform(X), y)
        sklearn_expected = sklearn_lda.transform(sklearn_scaler.transform(X))
        sklearn_actual = transform_features(X, scaler=sklearn_scaler, lda=sklearn_lda)
        assert_allclose(sklearn_actual, sklearn_expected.astype(np.float32), atol=1e-6)

        legacy_scaler = NumpyStandardScaler().fit(X)
        legacy_lda = NumpyLinearDiscriminantAnalysis(n_components=1).fit(
            legacy_scaler.transform(X),
            y,
        )
        legacy_expected = legacy_lda.transform(legacy_scaler.transform(X))
        legacy_actual = transform_features(X, scaler=legacy_scaler, lda=legacy_lda)
        assert_allclose(legacy_actual, legacy_expected.astype(np.float32), atol=1e-5)


if __name__ == "__main__":
    unittest.main()
