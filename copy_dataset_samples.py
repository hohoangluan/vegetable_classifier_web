"""
Chạy một lần để copy 1000 ảnh/label vào static/images/dataset_samples/.
Nguồn: dataset/train/<label>/ (900 ảnh) + dataset/test/<label>/ (100 ảnh đầu).
"""
import shutil
from pathlib import Path

DATASET_ROOT = Path(__file__).parent.parent / "dataset"
DEST_ROOT = Path(__file__).parent / "static" / "images" / "dataset_samples"
TRAIN_COUNT = 900
TEST_COUNT = 100
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def copy_samples():
    train_dir = DATASET_ROOT / "train"
    if not train_dir.exists():
        print(f"Train folder not found: {train_dir}")
        return

    labels = sorted(p.name for p in train_dir.iterdir() if p.is_dir())
    print(f"Found {len(labels)} labels: {', '.join(labels)}\n")

    for label in labels:
        dest_dir = DEST_ROOT / label
        dest_dir.mkdir(parents=True, exist_ok=True)

        train_imgs = sorted(
            p for p in (DATASET_ROOT / "train" / label).iterdir()
            if p.suffix.lower() in EXTENSIONS
        )[:TRAIN_COUNT]
        for img in train_imgs:
            shutil.copy2(img, dest_dir / img.name)

        test_imgs = sorted(
            p for p in (DATASET_ROOT / "test" / label).iterdir()
            if p.suffix.lower() in EXTENSIONS
        )[:TEST_COUNT]
        for img in test_imgs:
            dest_name = f"test_{img.name}"
            shutil.copy2(img, dest_dir / dest_name)

        print(f"  {label}: {len(train_imgs)} train + {len(test_imgs)} test = {len(train_imgs) + len(test_imgs)} imgs -> {dest_dir}")


if __name__ == "__main__":
    copy_samples()
    print("\nDone.")
