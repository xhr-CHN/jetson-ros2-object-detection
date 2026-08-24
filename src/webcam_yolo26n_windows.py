"""Run YOLO26n pencil and tennis-ball detection with a Windows webcam."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import torch
from ultralytics import YOLO


PROJECT_ROOT = Path(r"E:\机器人集成小组项目")
MODEL_PATH = PROJECT_ROOT / "models" / "pencil_tennis_yolo26n_best.pt"
WINDOW_TITLE = "YOLO26n Pencil and Tennis Ball Detection"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect pencils and tennis balls using a Windows webcam."
    )
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="Camera index (default: 0).",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Confidence threshold from 0 to 1 (default: 0.25).",
    )
    args = parser.parse_args()
    if args.camera < 0:
        parser.error("--camera must be zero or greater")
    if not 0.0 <= args.conf <= 1.0:
        parser.error("--conf must be between 0 and 1")
    return args


def check_environment() -> None:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Trained model not found: {MODEL_PATH}")
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise RuntimeError("CUDA GPU is unavailable; inference will not fall back to CPU.")


def open_camera(index: int) -> cv2.VideoCapture:
    camera = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera.release()
        camera = cv2.VideoCapture(index)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(f"Unable to open camera index {index}.")
    return camera


def main() -> None:
    args = parse_args()
    check_environment()

    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Model: {MODEL_PATH}")
    print(f"Camera: {args.camera}, confidence: {args.conf:.2f}")
    print("Press Q or Esc to exit.")

    model = YOLO(str(MODEL_PATH))
    camera = open_camera(args.camera)
    smoothed_fps = 0.0
    failed_reads = 0

    try:
        while True:
            started = time.perf_counter()
            ok, frame = camera.read()
            if not ok:
                failed_reads += 1
                if failed_reads >= 10:
                    raise RuntimeError("Camera frame read failed 10 consecutive times.")
                continue
            failed_reads = 0

            result = model.predict(
                source=frame,
                imgsz=640,
                conf=args.conf,
                device=0,
                verbose=False,
            )[0]
            display_frame = result.plot()

            elapsed = time.perf_counter() - started
            current_fps = 1.0 / elapsed if elapsed > 0 else 0.0
            smoothed_fps = (
                current_fps if smoothed_fps == 0.0 else 0.9 * smoothed_fps + 0.1 * current_fps
            )
            cv2.putText(
                display_frame,
                f"FPS: {smoothed_fps:.1f}",
                (16, 36),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(WINDOW_TITLE, display_frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
