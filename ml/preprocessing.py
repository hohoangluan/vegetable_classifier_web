from pathlib import Path


def prepare_image(image_path: Path):
    """Placeholder for resize, normalization and validation steps."""
    return {
        "image_path": str(image_path),
        "status": "prepared",
    }
