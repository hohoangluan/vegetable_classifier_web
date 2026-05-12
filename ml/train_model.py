from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

try:
    import joblib
except ImportError as exc:  # pragma: no cover - depends on environment
    joblib = None
    _JOBLIB_IMPORT_ERROR = exc
else:  # pragma: no cover - trivial assignment
    _JOBLIB_IMPORT_ERROR = None

from ml.helper import load_config, scan_dataset
from ml.label_mapping import LABEL_MAPPING, get_dataset_class_names, get_vietnamese_label, normalize_label
from ml.model_loader import create_model_from_json, load_trained_model


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]
WORKSPACE_ROOT = SCRIPT_PATH.parents[2]
DEFAULT_DATASET_ROOT = WORKSPACE_ROOT / "dataset"
DEFAULT_CONFIG_PATH = SCRIPT_PATH.parent / "config" / "config.json"
DEFAULT_OUTPUT_MODEL = PROJECT_ROOT / "ml_models" / "vegetable_model.pkl"
DEFAULT_OUTPUT_REPORT = PROJECT_ROOT / "ml_models" / "vegetable_model_report.json"


def configure_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:  # pragma: no cover - depends on terminal
            pass


def console_print(message=""):
    text = str(message)

    try:
        print(text)
        return
    except UnicodeEncodeError:
        pass

    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write(text.encode("utf-8", errors="replace") + b"\n")
        sys.stdout.flush()
        return

    print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train VegetableGMMModel and save it as ml_models/vegetable_model.pkl",
    )
    parser.add_argument(
        "--dataset-root",
        default=str(DEFAULT_DATASET_ROOT),
        help="Path to dataset root containing train/validation/test directories.",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to strict JSON config used to initialize VegetableGMMModel.",
    )
    parser.add_argument(
        "--output-model",
        default=str(DEFAULT_OUTPUT_MODEL),
        help="Where to save the trained VegetableGMMModel artifact.",
    )
    parser.add_argument(
        "--output-report",
        default=str(DEFAULT_OUTPUT_REPORT),
        help="Where to save the JSON training report.",
    )
    return parser.parse_args()


def ensure_joblib_available():
    if joblib is None:
        raise RuntimeError(
            "Không thể lưu vegetable_model.pkl vì thiếu joblib. "
            "Hãy cài dependency trong requirements.txt."
        ) from _JOBLIB_IMPORT_ERROR


def safe_label_mapping_for_dataset(class_names):
    normalized_mapping_keys = {
        normalize_label(label_name)
        for label_name in LABEL_MAPPING
        if label_name != "OOD"
    }
    missing = [
        class_name
        for class_name in class_names
        if normalize_label(class_name) not in normalized_mapping_keys
    ]

    if missing:
        missing_str = ", ".join(sorted(missing))
        raise ValueError(
            "Thiếu tên hiển thị tiếng Việt cho các class trong dataset/train: "
            f"{missing_str}"
        )


def split_dataset_frame(dataset_df):
    split_frames = {}

    for split_name in ("train", "validation", "test"):
        split_frame = dataset_df[dataset_df["split"] == split_name].copy()
        split_frame = split_frame.reset_index(drop=True)
        split_frames[split_name] = split_frame

    return split_frames


def summarize_split_counts(split_frames):
    return {
        split_name: int(len(split_frame))
        for split_name, split_frame in split_frames.items()
    }


def build_label_summary(class_names):
    return [
        {
            "label": class_name,
            "label_vi": get_vietnamese_label(class_name),
        }
        for class_name in class_names
    ]


def build_report(
    dataset_root,
    config_path,
    output_model_path,
    output_report_path,
    class_names,
    split_counts,
    model,
    evaluation_metrics=None,
):
    report = {
        "dataset_root": str(dataset_root),
        "config_path": str(config_path),
        "output_model_path": str(output_model_path),
        "output_report_path": str(output_report_path),
        "class_names": list(class_names),
        "class_display_names": {
            class_name: get_vietnamese_label(class_name)
            for class_name in class_names
        },
        "split_counts": split_counts,
        "feature_config": model.feature_params,
        "mahalanobis": {
            "mode": model.maha_params.get("mode"),
            "threshold": None if model.threshold_maha is None else float(model.threshold_maha),
            "reject_ood_by_default": model.maha_params.get("reject_ood_by_default"),
        },
        "evaluation": None,
    }

    if evaluation_metrics:
        report["evaluation"] = {
            "accuracy": float(evaluation_metrics["accuracy"]),
            "macro_f1": float(evaluation_metrics["macro_f1"]),
            "rejection_rate": float(evaluation_metrics["rejection_rate"]),
            "n_samples": int(evaluation_metrics["n_samples"]),
            "n_ood": int(evaluation_metrics["n_ood"]),
            "threshold_maha": (
                None
                if evaluation_metrics["threshold_maha"] is None
                else float(evaluation_metrics["threshold_maha"])
            ),
            "classification_report": evaluation_metrics["classification_report"],
        }

    return report


def save_report(report, output_report_path):
    output_report_path.parent.mkdir(parents=True, exist_ok=True)
    with output_report_path.open("w", encoding="utf-8") as file_obj:
        json.dump(report, file_obj, ensure_ascii=False, indent=2)


def print_run_summary(dataset_root, config_path, output_model_path, output_report_path, label_summary, split_counts):
    console_print("=== Training configuration ===")
    console_print(f"Dataset root: {dataset_root}")
    console_print(f"Config path : {config_path}")
    console_print(f"Model path  : {output_model_path}")
    console_print(f"Report path : {output_report_path}")
    console_print()
    console_print("=== Labels ===")
    for item in label_summary:
        console_print(f"- {item['label']} -> {item['label_vi']}")
    console_print()
    console_print("=== Split counts ===")
    for split_name, count in split_counts.items():
        console_print(f"- {split_name}: {count}")
    console_print()


def print_evaluation_summary(evaluation_metrics):
    if not evaluation_metrics:
        console_print("Không có test split hoặc test split rỗng, bỏ qua evaluate.")
        return

    console_print("=== Evaluation ===")
    console_print(f"Accuracy        : {evaluation_metrics['accuracy']:.4f}")
    console_print(f"Macro F1        : {evaluation_metrics['macro_f1']:.4f}")
    console_print(f"Rejection rate  : {evaluation_metrics['rejection_rate']:.4f}")
    console_print(f"Mahalanobis thr : {evaluation_metrics['threshold_maha']}")
    console_print()
    console_print(evaluation_metrics["classification_report"])
    console_print()


def train_and_save_model(dataset_root, config_path, output_model_path, output_report_path):
    ensure_joblib_available()

    dataset_root = Path(dataset_root)
    config_path = Path(config_path)
    output_model_path = Path(output_model_path)
    output_report_path = Path(output_report_path)

    if not dataset_root.exists():
        raise FileNotFoundError(f"Không tìm thấy dataset root: {dataset_root}")

    load_config(config_path)
    class_names = get_dataset_class_names(dataset_root / "train")
    if not class_names:
        raise ValueError("dataset/train không có class directory nào để train.")

    safe_label_mapping_for_dataset(class_names)
    label_summary = build_label_summary(class_names)

    dataset_df = scan_dataset(dataset_root)
    split_frames = split_dataset_frame(dataset_df)
    split_counts = summarize_split_counts(split_frames)

    train_df = split_frames["train"]
    validation_df = split_frames["validation"] if len(split_frames["validation"]) > 0 else None
    test_df = split_frames["test"] if len(split_frames["test"]) > 0 else None

    if len(train_df) == 0:
        raise ValueError("Train split rỗng, không thể train mô hình.")

    print_run_summary(
        dataset_root,
        config_path,
        output_model_path,
        output_report_path,
        label_summary,
        split_counts,
    )

    model = create_model_from_json(config_path)
    model.train(train_df, val_df=validation_df)

    evaluation_metrics = None
    if test_df is not None:
        evaluation_metrics = model.evaluate(test_df)
        print_evaluation_summary(evaluation_metrics)
    else:
        print_evaluation_summary(None)

    output_model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_model_path)

    load_trained_model.cache_clear()
    reloaded_model = load_trained_model(output_model_path)
    if not getattr(reloaded_model, "is_trained", False):
        raise RuntimeError("Model vừa lưu không load lại được ở trạng thái trained.")

    report = build_report(
        dataset_root=dataset_root,
        config_path=config_path,
        output_model_path=output_model_path,
        output_report_path=output_report_path,
        class_names=class_names,
        split_counts=split_counts,
        model=model,
        evaluation_metrics=evaluation_metrics,
    )
    save_report(report, output_report_path)

    console_print("Train hoàn tất.")
    console_print(f"Đã lưu model : {output_model_path}")
    console_print(f"Đã lưu report: {output_report_path}")

    return {
        "model_path": output_model_path,
        "report_path": output_report_path,
        "split_counts": split_counts,
        "class_names": class_names,
        "evaluation": evaluation_metrics,
    }


def main():
    configure_stdout()
    args = parse_args()
    train_and_save_model(
        dataset_root=args.dataset_root,
        config_path=args.config,
        output_model_path=args.output_model,
        output_report_path=args.output_report,
    )


if __name__ == "__main__":
    main()
