"""Prepare colour, publication-ready copies of verified experiment evidence.

Every source image retains its original colour, pixel dimensions and aspect
ratio.  Source artifacts are never modified.
"""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "figures"

ASSETS = {
    "training_results.png": ROOT / "results" / "training" / "yolo26n_augmented" / "results.png",
    "test_pr_curve.png": ROOT / "results" / "test" / "yolo26n" / "validation" / "BoxPR_curve.png",
    "test_confusion_matrix.png": ROOT / "results" / "test" / "yolo26n" / "validation" / "confusion_matrix_normalized.png",
    "detection_pencil.png": ROOT / "results" / "test" / "yolo26n" / "predictions" / "pencil_green30.jpg",
    "detection_tennis.png": ROOT
    / "results"
    / "test"
    / "yolo26n"
    / "predictions"
    / "roboflow_tennis_222_jpg.rf.a1668a8f99681895df66c4eea7b9031d.jpg",
    "acceptance_correct.png": ROOT
    / "results"
    / "jetson"
    / "2026-08-30"
    / "acceptance"
    / "attempt_02"
    / "correct"
    / "test_21_gt_0092_tennis_ball_correct.jpg",
    "acceptance_error.png": ROOT
    / "results"
    / "jetson"
    / "2026-08-30"
    / "acceptance"
    / "attempt_02"
    / "errors"
    / "test_03_gt_0070_pencil_error.jpg",
}


def copy_colour_image(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    with Image.open(source) as image:
        # No grayscale conversion, resize or crop.
        image.convert("RGB").save(destination, optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, source in ASSETS.items():
        destination = OUT / name
        copy_colour_image(source, destination)
        print(f"{name}: {destination.stat().st_size} bytes")

    video_frame = OUT / "jetson_realtime.png"
    if video_frame.is_file():
        print(f"jetson_realtime.png: {video_frame.stat().st_size} bytes (colour)")


if __name__ == "__main__":
    main()
