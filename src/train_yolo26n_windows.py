"""Train the pencil and tennis-ball detector on the current Windows PC."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(r"E:\机器人集成小组项目")
DATA_CONFIG = PROJECT_ROOT / "dataset" / "data-windows.yaml"
MODEL_WEIGHTS = Path(r"D:\视觉识别一硝3\yolo26n.pt")
RUNS_DIR = PROJECT_ROOT / "runs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train YOLO26n to detect pencils and tennis balls on Windows."
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run a 3-epoch smoke test instead of the 100-epoch formal training.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Override the number of epochs.",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=8,
        help="Batch size (default: 8; use 4 if GPU memory is insufficient).",
    )
    args = parser.parse_args()
    if args.epochs is not None and args.epochs < 1:
        parser.error("--epochs must be at least 1")
    if args.batch < 1:
        parser.error("--batch must be at least 1")
    return args


def check_environment() -> None:
    if not MODEL_WEIGHTS.is_file():
        raise FileNotFoundError(f"YOLO26n weights not found: {MODEL_WEIGHTS}")
    if not DATA_CONFIG.is_file():
        raise FileNotFoundError(f"Dataset configuration not found: {DATA_CONFIG}")
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise RuntimeError("CUDA GPU is unavailable; training will not fall back to CPU.")


def build_training_args(args: argparse.Namespace) -> dict[str, object]:
    epochs = args.epochs if args.epochs is not None else (3 if args.smoke else 100)
    return {
        "data": str(DATA_CONFIG),
        "epochs": epochs,
        "imgsz": 640,
        "batch": args.batch,
        "device": 0,
        "workers": 0,
        "patience": 20,
        "project": str(RUNS_DIR),
        "name": "yolo26n_smoke" if args.smoke else "pencil_tennis_yolo26n",
        "plots": True,
        "save": True,
    }


def main() -> None:
    args = parse_args()
    check_environment()
    training_args = build_training_args(args)

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Model: {MODEL_WEIGHTS}")
    print(f"Data: {DATA_CONFIG}")
    print(f"Mode: {'smoke test' if args.smoke else 'formal training'}")
    print(f"Epochs: {training_args['epochs']}, batch: {training_args['batch']}")

    model = YOLO(str(MODEL_WEIGHTS))
    model.train(**training_args)


if __name__ == "__main__":
    main()
