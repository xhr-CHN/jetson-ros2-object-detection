"""Evaluate the trained YOLO26n detector on the independent test split."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(r"E:\机器人集成小组项目")
MODEL_PATH = PROJECT_ROOT / "models" / "pencil_tennis_yolo26n_best.pt"
DATA_CONFIG = PROJECT_ROOT / "dataset" / "data-windows.yaml"
TEST_IMAGES = PROJECT_ROOT / "dataset" / "images" / "test"
OUTPUT_ROOT = PROJECT_ROOT / "results" / "test" / "yolo26n"
VALIDATION_DIR = OUTPUT_ROOT / "validation"
PREDICTIONS_DIR = OUTPUT_ROOT / "predictions"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the trained pencil and tennis-ball YOLO26n model."
    )
    return parser.parse_args()


def test_images() -> list[Path]:
    if not TEST_IMAGES.is_dir():
        raise FileNotFoundError(f"Test image directory not found: {TEST_IMAGES}")
    images = sorted(
        path for path in TEST_IMAGES.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not images:
        raise RuntimeError(f"No test images found in: {TEST_IMAGES}")
    return images


def check_environment() -> list[Path]:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Trained model not found: {MODEL_PATH}")
    if not DATA_CONFIG.is_file():
        raise FileNotFoundError(f"Dataset configuration not found: {DATA_CONFIG}")
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise RuntimeError("CUDA GPU is unavailable; evaluation will not fall back to CPU.")
    return test_images()


def reset_generated_outputs() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for path in (VALIDATION_DIR, PREDICTIONS_DIR):
        if path.exists():
            shutil.rmtree(path)


def serializable_class_metrics(summary: list[dict]) -> list[dict[str, object]]:
    converted = []
    for row in summary:
        converted.append(
            {
                key: value.item() if hasattr(value, "item") else value
                for key, value in row.items()
            }
        )
    return converted


def main() -> None:
    parse_args()
    images = check_environment()
    reset_generated_outputs()

    gpu_name = torch.cuda.get_device_name(0)
    print(f"GPU: {gpu_name}")
    print(f"Model: {MODEL_PATH}")
    print(f"Test images: {len(images)}")

    model = YOLO(str(MODEL_PATH))
    metrics = model.val(
        data=str(DATA_CONFIG),
        split="test",
        imgsz=640,
        batch=8,
        device=0,
        workers=0,
        project=str(OUTPUT_ROOT),
        name="validation",
        exist_ok=True,
        plots=True,
    )

    predictions = model.predict(
        source=str(TEST_IMAGES),
        imgsz=640,
        conf=0.25,
        device=0,
        project=str(OUTPUT_ROOT),
        name="predictions",
        exist_ok=True,
        save=True,
        save_txt=True,
        save_conf=True,
        verbose=False,
    )

    saved_images = [
        path
        for path in PREDICTIONS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    if len(predictions) != len(images) or len(saved_images) != len(images):
        raise RuntimeError(
            "Prediction output count mismatch: "
            f"expected {len(images)}, got {len(predictions)} results and {len(saved_images)} images."
        )

    report = {
        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": str(MODEL_PATH),
        "data": str(DATA_CONFIG),
        "test_images": len(images),
        "gpu": gpu_name,
        "parameters": {
            "split": "test",
            "imgsz": 640,
            "batch": 8,
            "device": 0,
            "workers": 0,
            "prediction_confidence": 0.25,
        },
        "overall": {key: float(value) for key, value in metrics.results_dict.items()},
        "per_class": serializable_class_metrics(metrics.summary()),
        "prediction_images": len(saved_images),
        "prediction_label_files": len(list((PREDICTIONS_DIR / "labels").glob("*.txt"))),
    }
    metrics_path = OUTPUT_ROOT / "metrics.json"
    metrics_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Metrics: {metrics_path}")
    print(f"Predictions: {PREDICTIONS_DIR}")


if __name__ == "__main__":
    main()
