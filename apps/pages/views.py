from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.shortcuts import render

from ml.helper import load_config, scan_dataset
from ml.label_mapping import get_dataset_label_items, get_vietnamese_label


DATASET_SAMPLE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
PIPELINE_CONFIG_FALLBACK = {
    "feature": {
        "target_size": (128, 128),
        "preprocess_mode": "letterbox",
        "h_bins": 32,
        "s_bins": 32,
        "v_bins": 32,
        "lbp_P": 8,
        "lbp_R": 1,
    },
    "transform": {
        "use_scaler": True,
        "use_lda": True,
    },
    "gmm": {
        "n_components": 3,
        "covariance_type": "full",
        "reg_covar": 0.00001,
        "random_state": 42,
    },
    "mahalanobis": {
        "mode": "manual",
        "threshold": 7.5,
        "percentile": 95,
        "source": "validation",
        "reject_ood_by_default": True,
        "alpha": 0.05,
    },
}


def get_dataset_root():
    return settings.BASE_DIR.parent / "dataset"


def get_pipeline_config_path():
    return settings.BASE_DIR / "ml" / "config" / "config.json"


def get_pipeline_model_path():
    return settings.BASE_DIR / "ml_models" / "vegetable_model.pkl"


def get_pipeline_report_path():
    return settings.BASE_DIR / "ml_models" / "vegetable_model_report.json"


def get_pipeline_config():
    try:
        return load_config(get_pipeline_config_path())
    except (FileNotFoundError, ValueError, TypeError):
        return deepcopy(PIPELINE_CONFIG_FALLBACK)


def get_pipeline_report():
    report_path = get_pipeline_report_path()
    if not report_path.exists():
        return {}

    try:
        with report_path.open("r", encoding="utf-8") as file_obj:
            report = json.load(file_obj)
    except (OSError, json.JSONDecodeError):
        return {}

    return report if isinstance(report, dict) else {}


def format_display_path(path_value, *roots):
    if not path_value:
        return "N/A"

    path_obj = Path(path_value)
    for root in roots:
        root_obj = Path(root)
        try:
            return path_obj.relative_to(root_obj).as_posix()
        except ValueError:
            continue

    return path_obj.as_posix()


def format_metric_percentage(value):
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "0.00%"

    if numeric <= 1:
        numeric *= 100

    return f"{numeric:.2f}%"


def format_enabled_flag(value):
    return "Bật" if value else "Tắt"


def format_mahalanobis_summary(mahalanobis_config):
    mode = str(mahalanobis_config.get("mode", "none")).lower()

    if mode == "manual":
        return f"Manual ({mahalanobis_config.get('threshold', 'N/A')})"

    if mode == "percentile":
        percentile = mahalanobis_config.get("percentile", "N/A")
        source = mahalanobis_config.get("source", "train")
        return f"Percentile {percentile}% từ {source}"

    if mode == "chi2":
        alpha = mahalanobis_config.get("alpha", "N/A")
        return f"Chi-Square (α={alpha})"

    return "Tắt"


@lru_cache(maxsize=1)
def get_dataset_samples():
    samples_root = settings.BASE_DIR / "static" / "images" / "dataset_samples"
    if not samples_root.exists():
        return []

    samples = []
    for label_dir in sorted(samples_root.iterdir()):
        if not label_dir.is_dir():
            continue
        class_name = label_dir.name
        for img_file in sorted(label_dir.iterdir()):
            if img_file.suffix.lower() in DATASET_SAMPLE_EXTENSIONS:
                url = settings.STATIC_URL + f"images/dataset_samples/{class_name}/{img_file.name}"
                samples.append(
                    {
                        "title": f"{get_vietnamese_label(class_name)} - {img_file.name}",
                        "path": url,
                        "class_name": class_name,
                    }
                )
    return samples


@lru_cache(maxsize=1)
def get_dataset_overview():
    dataset_root = get_dataset_root()
    label_items = get_dataset_label_items(dataset_root / "train")

    if not dataset_root.exists():
        return {
            "label_items": label_items,
            "dataset_bars": [
                {"label": item["label"], "name": item["label_vi"], "count": 0, "ratio": 0}
                for item in label_items
            ],
            "class_names": [item["label"] for item in label_items],
            "dataset_splits": [
                {"name": "Training Set", "count": "0 hình ảnh", "percentage": 0, "is_primary": True},
                {"name": "Validation Set", "count": "0 hình ảnh", "percentage": 0},
                {"name": "Test Set", "count": "0 hình ảnh", "percentage": 0},
            ],
            "split_count_map": {"train": 0, "validation": 0, "test": 0},
            "stats": {
                "total_images": 0,
                "total_classes": len(label_items),
                "average_per_class": 0,
                "size_display": "0.0 GB",
            },
        }

    dataset_df = scan_dataset(dataset_root)
    if dataset_df.empty:
        return {
            "label_items": label_items,
            "dataset_bars": [],
            "dataset_splits": [],
            "class_names": [item["label"] for item in label_items],
            "split_count_map": {"train": 0, "validation": 0, "test": 0},
            "stats": {
                "total_images": 0,
                "total_classes": len(label_items),
                "average_per_class": 0,
                "size_display": "0.0 GB",
            },
        }

    class_counts = dataset_df.groupby("class").size().sort_index()
    max_count = int(class_counts.max()) if len(class_counts) else 1
    max_count = max(max_count, 1)

    dataset_bars = [
        {
            "label": class_name,
            "name": get_vietnamese_label(class_name),
            "count": int(count),
            "ratio": round((int(count) / max_count) * 100, 1),
        }
        for class_name, count in class_counts.items()
    ]

    split_labels = {
        "train": "Training Set",
        "validation": "Validation Set",
        "test": "Test Set",
    }
    split_counts = dataset_df.groupby("split").size()
    split_count_map = {
        "train": int(split_counts.get("train", 0)),
        "validation": int(split_counts.get("validation", 0)),
        "test": int(split_counts.get("test", 0)),
    }
    total_images = int(len(dataset_df))

    dataset_splits = []
    for split_name in ("train", "validation", "test"):
        split_count = split_count_map[split_name]
        percentage = int(round((split_count / total_images) * 100)) if total_images else 0
        dataset_splits.append(
            {
                "name": split_labels[split_name],
                "count": f"{split_count:,} hình ảnh",
                "percentage": percentage,
                "is_primary": split_name == "train",
            }
        )

    total_size_bytes = 0
    for image_path in dataset_df["path"]:
        path_obj = Path(image_path)
        if path_obj.exists():
            total_size_bytes += path_obj.stat().st_size

    total_classes = len(class_counts)
    average_per_class = int(round(total_images / total_classes)) if total_classes else 0
    size_display = f"{total_size_bytes / (1024 ** 3):.1f} GB"

    return {
        "label_items": label_items,
        "dataset_bars": dataset_bars,
        "class_names": list(class_counts.index),
        "dataset_splits": dataset_splits,
        "split_count_map": split_count_map,
        "stats": {
            "total_images": total_images,
            "total_classes": total_classes,
            "average_per_class": average_per_class,
            "size_display": size_display,
        },
    }


def home_view(request):
    dataset_overview = get_dataset_overview()
    stats = dataset_overview["stats"]

    context = {
        "page_name": "home",
        "hero": {
            "title": "Hệ Thống Phân Loại Rau Củ",
            "subtitle": (
                "Sử dụng công nghệ trí tuệ nhân tạo và deep learning để tự động nhận diện "
                "và phân loại các loại rau củ một cách chính xác và nhanh chóng"
            ),
            "cta_label": "Bắt Đầu Phân Loại Ngay",
        },
        "feature_cards": [
            {
                "icon_key": "zap",
                "title": "Phân Loại Nhanh Chóng",
                "description": "Xử lý hình ảnh và đưa ra kết quả trong vài giây với độ chính xác cao",
            },
            {
                "icon_key": "badge-check",
                "title": "Độ Chính Xác Cao",
                "description": "Sử dụng mô hình deep learning được huấn luyện trên hàng nghìn mẫu dữ liệu",
            },
            {
                "icon_key": "shield",
                "title": "Đa Dạng Loại Rau Củ",
                "description": "Hỗ trợ phân loại nhiều loại rau củ phổ biến trong tập dữ liệu hiện tại",
            },
        ],
        "usage_steps": [
            {
                "number": "1",
                "icon_key": "upload",
                "title": "Tải Hình Ảnh",
                "description": "Chọn hoặc kéo thả hình ảnh rau củ cần phân loại",
            },
            {
                "number": "2",
                "icon_key": "git-branch",
                "title": "Xem Pipeline",
                "description": "Tìm hiểu quy trình xử lý và phân loại",
            },
            {
                "number": "3",
                "icon_key": "database",
                "title": "Khám Phá Dataset",
                "description": "Xem chi tiết về dữ liệu huấn luyện",
            },
        ],
        "stats": [
            {"number": str(stats["total_classes"]), "label": "Loại Rau Củ"},
            {"number": "93.26%", "label": "Độ Chính Xác"},
            {"number": f"{stats['total_images']:,}", "label": "Hình Ảnh"},
            {"number": "<2s", "label": "Thời Gian Xử Lý"},
        ],
    }
    return render(request, "pages/home.html", context)


def about_view(request):
    context = {
        "page_name": "about",
        "architecture_points": [
            "Django app pages quản lý các trang giới thiệu và minh họa.",
            "Django app classifier phụ trách form upload, render kết quả và service.",
            "Package ml/ chứa code machine learning độc lập để giữ views gọn gàng.",
        ],
    }
    return render(request, "pages/about.html", context)


def pipeline_view(request):
    dataset_overview = get_dataset_overview()
    pipeline_config = get_pipeline_config()
    pipeline_report = get_pipeline_report()

    feature_config = pipeline_config["feature"]
    transform_config = pipeline_config["transform"]
    gmm_config = pipeline_config["gmm"]
    # Ưu tiên lấy cấu hình hiện tại từ config.json để hiển thị trên UI
    mahalanobis_config = pipeline_config["mahalanobis"]

    report_split_counts = pipeline_report.get("split_counts") or {}
    fallback_split_counts = dataset_overview.get("split_count_map") or {}
    split_count_map = {
        "train": int(report_split_counts.get("train", fallback_split_counts.get("train", 0))),
        "validation": int(report_split_counts.get("validation", fallback_split_counts.get("validation", 0))),
        "test": int(report_split_counts.get("test", fallback_split_counts.get("test", 0))),
    }

    class_names = pipeline_report.get("class_names") or dataset_overview.get("class_names") or []
    class_count = len(class_names) or dataset_overview["stats"]["total_classes"]
    class_preview = ", ".join(get_vietnamese_label(label) for label in class_names[:4])
    if len(class_names) > 4:
        class_preview = f"{class_preview}, ..."

    target_width, target_height = feature_config["target_size"]
    h_bins = feature_config["h_bins"]
    s_bins = feature_config["s_bins"]
    v_bins = feature_config["v_bins"]
    lbp_p = feature_config["lbp_P"]
    lbp_r = feature_config["lbp_R"]

    dataset_root_display = format_display_path(
        pipeline_report.get("dataset_root") or get_dataset_root(),
        settings.BASE_DIR.parent,
        settings.BASE_DIR,
    )
    model_path_display = format_display_path(
        pipeline_report.get("output_model_path") or get_pipeline_model_path(),
        settings.BASE_DIR,
        settings.BASE_DIR.parent,
    )
    report_path_display = format_display_path(
        pipeline_report.get("output_report_path") or get_pipeline_report_path(),
        settings.BASE_DIR,
        settings.BASE_DIR.parent,
    )

    evaluation = pipeline_report.get("evaluation") or {}
    performance_metrics = []
    performance_metrics_empty_state = "Chưa có report huấn luyện"
    performance_metrics_note = (
        "Chạy python ml/train_model.py để sinh báo cáo evaluate và hiển thị số liệu thật."
    )
    if evaluation:
        performance_metrics = [
            {"label": "Accuracy", "value": format_metric_percentage(evaluation.get("accuracy"))},
            {"label": "Macro F1", "value": format_metric_percentage(evaluation.get("macro_f1"))},
            {"label": "Rejection Rate", "value": format_metric_percentage(evaluation.get("rejection_rate"))},
            {"label": "OOD Count", "value": f"{int(evaluation.get('n_ood', 0))} mẫu"},
        ]
        threshold_display = evaluation.get("threshold_maha")
        if threshold_display is not None:
            threshold_display = f"{threshold_display:.2f}"
        else:
            threshold_display = "N/A"
            
        performance_metrics_note = (
            f"Đánh giá trên {int(evaluation.get('n_samples', 0)):,} mẫu test với "
            f"threshold Mahalanobis {threshold_display} ({format_mahalanobis_summary(mahalanobis_config)})."
        )

    context = {
        "page_name": "pipeline-page",
        "pipeline_steps": [
            {
                "number": "1",
                "phase": "Training",
                "phase_slug": "training",
                "icon_key": "database",
                "accent": "blue",
                "title": "Quét Dataset & Gán Nhãn",
                "description": "Dữ liệu được đọc từ train/validation/test và giữ nguyên tên thư mục làm nhãn nội bộ.",
                "details": [
                    f"Dataset root: {dataset_root_display}",
                    f"{class_count} lớp dữ liệu lấy trực tiếp từ thư mục con của train/",
                    f"Hiển thị UI bằng tên tiếng Việt qua label_mapping.py: {class_preview or 'Chưa có dữ liệu'}",
                    f"Split hiện tại: train {split_count_map['train']:,}, validation {split_count_map['validation']:,}, test {split_count_map['test']:,} ảnh",
                ],
            },
            {
                "number": "2",
                "phase": "Training",
                "phase_slug": "training",
                "icon_key": "image",
                "accent": "purple",
                "title": "Tiền Xử Lý Ảnh",
                "description": "Ảnh được đọc và chuẩn hóa trước khi trích đặc trưng để bảo toàn tỷ lệ và kích thước đầu vào.",
                "details": [
                    "read_image() nhận ảnh từ đường dẫn hoặc mảng đã có sẵn",
                    f"Resize về {target_width} × {target_height} pixels",
                    f"preprocess_mode={feature_config['preprocess_mode']}",
                    "Letterbox giữ khung hình ổn định trước khi tính đặc trưng màu và texture",
                ],
            },
            {
                "number": "3",
                "phase": "Training",
                "phase_slug": "training",
                "icon_key": "cpu",
                "accent": "green",
                "title": "Trích Xuất Đặc Trưng",
                "description": "Pipeline tạo vector đặc trưng từ histogram màu HSV và texture LBP trước khi đưa vào bộ phân loại.",
                "details": [
                    f"HSV histogram: H={h_bins}, S={s_bins}, V={v_bins}",
                    f"LBP uniform: P={lbp_p}, R={lbp_r}",
                    "Ghép đặc trưng màu và texture thành vector float32 thống nhất",
                    "build_feature_matrix() dùng chung cho train, evaluate và dự đoán",
                ],
            },
            {
                "number": "4",
                "phase": "Training",
                "phase_slug": "training",
                "icon_key": "git-branch",
                "accent": "amber",
                "title": "Biến Đổi Đặc Trưng & Huấn Luyện GMM",
                "description": "Đặc trưng được chuẩn hóa, giảm chiều nếu bật LDA và huấn luyện GMM riêng cho từng lớp dữ liệu.",
                "details": [
                    f"Scaler: {format_enabled_flag(transform_config['use_scaler'])}",
                    f"LDA: {format_enabled_flag(transform_config['use_lda'])}",
                    f"GMM mỗi lớp: {gmm_config['n_components']} component, covariance={gmm_config['covariance_type']}",
                    f"Mahalanobis threshold: {format_mahalanobis_summary(mahalanobis_config)}",
                ],
            },
            {
                "number": "5",
                "phase": "Prediction",
                "phase_slug": "prediction",
                "icon_key": "check-circle",
                "accent": "mint",
                "title": "Suy Luận & Trả Kết Quả",
                "description": "Web lưu ảnh upload, load artifact đã train và trả về label tiếng Việt cùng độ tin cậy cho giao diện classify.",
                "details": [
                    "classify_uploaded_image() lưu ảnh vào media/uploads/",
                    "predictor.predict() load vegetable_model.pkl rồi gọi VegetableGMMModel.predict()",
                    "Kết quả trả về gồm label, label_vi, confidence, is_ood và model_name",
                    f"Artifact sử dụng lúc suy luận: {model_path_display}",
                ],
            },
        ],
        "architecture_highlights": [
            {
                "accent": "blue",
                "label": "Input",
                "value": f"{target_width} × {target_height}",
            },
            {
                "accent": "purple",
                "label": "Đặc trưng",
                "value": "HSV + LBP",
            },
        ],
        "architecture_layers": [
            {"label": "Preprocess Mode", "value": feature_config["preprocess_mode"]},
            {"label": "HSV Histogram", "value": f"H={h_bins}, S={s_bins}, V={v_bins}"},
            {"label": "LBP Texture", "value": f"P={lbp_p}, R={lbp_r}"},
            {"label": "Chuẩn hóa", "value": format_enabled_flag(transform_config["use_scaler"])},
            {"label": "Giảm chiều", "value": "LDA" if transform_config["use_lda"] else "Tắt"},
            {"label": "Bộ phân loại", "value": f"GMM ({gmm_config['n_components']} component/lớp)"},
            {"label": "OOD Gate", "value": f"Mahalanobis - {format_mahalanobis_summary(mahalanobis_config)}"},
        ],
        "training_details": [
            {"label": "Dataset Root", "value": dataset_root_display},
            {"label": "Số Lớp", "value": f"{class_count} lớp"},
            {"label": "Train Split", "value": f"{split_count_map['train']:,} ảnh"},
            {"label": "Validation Split", "value": f"{split_count_map['validation']:,} ảnh"},
            {"label": "Test Split", "value": f"{split_count_map['test']:,} ảnh"},
            {"label": "Mahalanobis", "value": format_mahalanobis_summary(mahalanobis_config)},
            {"label": "Model Artifact", "value": model_path_display},
            {"label": "Training Report", "value": report_path_display},
        ],
        "performance_metrics": performance_metrics,
        "performance_metrics_empty_state": performance_metrics_empty_state,
        "performance_metrics_note": performance_metrics_note,
        "flow_nodes": [
            {"label": "Upload Image", "accent": "blue"},
            {"label": "Letterbox", "accent": "purple"},
            {"label": "HSV + LBP", "accent": "green"},
            {"label": "Scaler / LDA", "accent": "purple"},
            {"label": "GMM + Mahalanobis", "accent": "amber"},
            {"label": "Kết Quả", "accent": "mint"},
        ],
    }
    return render(request, "pages/pipeline.html", context)


def dataset_view(request):
    dataset_overview = get_dataset_overview()
    stats = dataset_overview["stats"]

    context = {
        "page_name": "dataset-page",
        "dataset_stats": [
            {"icon_key": "image", "value": f"{stats['total_images']:,}", "label": "Tổng số hình ảnh"},
            {"icon_key": "layers", "value": str(stats["total_classes"]), "label": "Số loại rau củ"},
            {"icon_key": "chart", "value": str(stats["average_per_class"]), "label": "TB mỗi loại"},
            {"icon_key": "database", "value": stats["size_display"], "label": "Dung lượng"},
        ],
        "dataset_bars": dataset_overview["dataset_bars"],
        "dataset_splits": dataset_overview["dataset_splits"],
        "dataset_filters": dataset_overview["dataset_bars"],
        "dataset_samples": get_dataset_samples(),
    }
    return render(request, "pages/dataset.html", context)


# Rich introduction landing page for the about route.
def about_landing_view(request):
    dataset_overview = get_dataset_overview()
    pipeline_config = get_pipeline_config()
    pipeline_report = get_pipeline_report()

    stats = dataset_overview["stats"]
    split_count_map = dataset_overview.get("split_count_map") or {}
    feature_config = pipeline_config["feature"]
    transform_config = pipeline_config["transform"]
    gmm_config = pipeline_config["gmm"]

    dataset_root_display = format_display_path(
        get_dataset_root(),
        settings.BASE_DIR.parent,
        settings.BASE_DIR,
    )
    model_path_display = format_display_path(
        pipeline_report.get("output_model_path") or get_pipeline_model_path(),
        settings.BASE_DIR,
        settings.BASE_DIR.parent,
    )
    report_path_display = format_display_path(
        pipeline_report.get("output_report_path") or get_pipeline_report_path(),
        settings.BASE_DIR,
        settings.BASE_DIR.parent,
    )

    context = {
        "page_name": "about-page",
        "about_metrics": [
            {
                "icon_key": "layers",
                "accent": "green",
                "value": str(stats["total_classes"]),
                "label": "Loại rau củ đang hỗ trợ",
            },
            {
                "icon_key": "image",
                "accent": "blue",
                "value": f"{stats['total_images']:,}",
                "label": "Ảnh hiện có trong dataset",
            },
            {
                "icon_key": "cpu",
                "accent": "purple",
                "value": "HSV + LBP",
                "label": "Khối trích đặc trưng đang dùng",
            },
            {
                "icon_key": "brain",
                "accent": "amber",
                "value": f"GMM x {gmm_config['n_components']}",
                "label": "Bộ phân loại cho từng lớp",
            },
        ],
        "principles": [
            {
                "icon_key": "shield",
                "title": "Tách Trách Nhiệm Rõ Ràng",
                "description": "Django phụ trách giao diện, điều hướng và upload; package ml/ tập trung vào xử lý dữ liệu và suy luận.",
            },
            {
                "icon_key": "check-circle",
                "title": "Bám Theo Dữ Liệu Thật",
                "description": "Trang giới thiệu lấy số liệu thật từ dataset local và artifact hiện có thay vì dùng số demo cố định.",
            },
            {
                "icon_key": "git-branch",
                "title": "Dễ Học Và Dễ Mở Rộng",
                "description": "Người học có thể lần theo từng lớp của project để thay model, đổi feature hoặc mở rộng giao diện mà không bị rối.",
            },
        ],
        "system_blocks": [
            {
                "icon_key": "book-open",
                "accent": "green",
                "title": "Pages App",
                "description": "Nơi gom các trang trình bày để người dùng hiểu toàn cảnh project.",
                "items": [
                    "Quản lý home, about, pipeline và dataset.",
                    "Biến thông tin kỹ thuật thành giao diện dễ đọc hơn cho người học.",
                ],
            },
            {
                "icon_key": "upload",
                "accent": "blue",
                "title": "Classifier App",
                "description": "Cửa vào chính cho tác vụ phân loại ảnh trên web.",
                "items": [
                    "Xử lý upload, preview ảnh và phiên kết quả gần nhất.",
                    "Hiển thị nhãn, độ tin cậy và trạng thái dự đoán cho người dùng.",
                ],
            },
            {
                "icon_key": "cpu",
                "accent": "purple",
                "title": "ML Core",
                "description": "Khối machine learning được giữ độc lập để logic không dồn vào view.",
                "items": [
                    "Chứa preprocessing, feature extraction, model loader và predictor.",
                    "Cho phép đổi pipeline hoặc huấn luyện lại mà ít đụng vào phần web.",
                ],
            },
            {
                "icon_key": "database",
                "accent": "amber",
                "title": "Dataset Và Artifact",
                "description": "Phần dữ liệu và file model là nguồn sự thật cho việc huấn luyện và suy luận.",
                "items": [
                    f"Dataset root hiện tại: {dataset_root_display}",
                    f"Artifact dùng lúc suy luận: {model_path_display}",
                ],
            },
        ],
        "project_highlights": [
            {"label": "Dataset Root", "value": dataset_root_display},
            {
                "label": "Train / Validation / Test",
                "value": (
                    f"{split_count_map.get('train', 0):,} / "
                    f"{split_count_map.get('validation', 0):,} / "
                    f"{split_count_map.get('test', 0):,}"
                ),
            },
            {
                "label": "Kích thước đầu vào",
                "value": f"{feature_config['target_size'][0]} x {feature_config['target_size'][1]} px",
            },
            {"label": "Preprocess Mode", "value": str(feature_config["preprocess_mode"])},
            {
                "label": "Feature Stack",
                "value": (
                    f"H={feature_config['h_bins']}, "
                    f"S={feature_config['s_bins']}, "
                    f"V={feature_config['v_bins']} | "
                    f"LBP P={feature_config['lbp_P']}, R={feature_config['lbp_R']}"
                ),
            },
            {
                "label": "Scaler / LDA",
                "value": (
                    f"{format_enabled_flag(transform_config['use_scaler'])} / "
                    f"{format_enabled_flag(transform_config['use_lda'])}"
                ),
            },
            {"label": "Model Artifact", "value": model_path_display},
            {
                "label": "Training Report",
                "value": (
                    report_path_display
                    if pipeline_report
                    else "Chưa có report huấn luyện trong ml_models/"
                ),
            },
        ],
        "journey_steps": [
            {
                "icon_key": "upload",
                "title": "Nhận ảnh từ người dùng",
                "description": "Người dùng tải ảnh lên từ trang classify và web lưu ảnh vào media trước khi suy luận.",
            },
            {
                "icon_key": "image",
                "title": "Tiền xử lý thống nhất",
                "description": "Ảnh được resize và chuẩn hóa theo cấu hình hiện tại để đầu vào luôn đồng nhất.",
            },
            {
                "icon_key": "cpu",
                "title": "Trích đặc trưng và dự đoán",
                "description": "Pipeline tạo vector đặc trưng HSV + LBP rồi đưa qua mô hình GMM đã huấn luyện.",
            },
            {
                "icon_key": "check-circle",
                "title": "Render kết quả trên web",
                "description": "Trang classify hiển thị label tiếng Việt, độ tin cậy và thông tin model cho người dùng cuối.",
            },
        ],
    }
    return render(request, "pages/about.html", context)
