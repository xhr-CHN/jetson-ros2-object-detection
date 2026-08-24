"""Use the augmented YOLO26n model for real-time webcam detection."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(r"E:\机器人集成小组项目")
DEFAULT_MODEL = (
    PROJECT_ROOT
    / "runs"
    / "pencil_tennis_yolo26n_augmented"
    / "weights"
    / "best.pt"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Real-time pencil and tennis-ball detection."
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL,
        help="Path to the trained YOLO model.",
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera index, normally 0.",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold.",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Inference image size.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_path = args.model.resolve()

    if not model_path.is_file():
        raise FileNotFoundError(f"Model not found: {model_path}")

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is unavailable.")

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Model: {model_path}")
    print(f"Confidence: {args.conf}")
    print("Press Q or Esc to exit.")

    model = YOLO(str(model_path))

    camera = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(f"Unable to open camera index {args.camera}")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                print("Unable to read camera frame.")
                break

            started = time.perf_counter()

            result = model.predict(
                source=frame,
                imgsz=args.imgsz,
                conf=args.conf,
                device=0,
                verbose=False,
            )[0]

            elapsed = max(time.perf_counter() - started, 1e-9)
            fps = 1.0 / elapsed

            annotated = result.plot(
                labels=True,
                conf=True,
                boxes=True,
            )

            cv2.putText(
                annotated,
                f"FPS: {fps:.1f}",
                (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "Augmented YOLO26n - Pencil and Tennis Ball",
                annotated,
            )

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()