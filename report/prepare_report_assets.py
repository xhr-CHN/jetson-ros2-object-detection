"""Prepare publication-ready copies of verified experiment evidence.

Charts are converted to grayscale for the black-and-white report layout.  Real
photographs and detection screenshots retain their original colour and aspect
ratio.  Source artifacts are never modified.
"""

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "report" / "figures"

MONOCHROME_ASSETS = {
    "training_results.png": ROOT / "results" / "training" / "yolo26n_augmented" / "results.png",
    "test_pr_curve.png": ROOT / "results" / "test" / "yolo26n" / "validation" / "BoxPR_curve.png",
    "test_confusion_matrix.png": ROOT / "results" / "test" / "yolo26n" / "validation" / "confusion_matrix_normalized.png",
}

COLOUR_PHOTOS = {
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


def convert_monochrome(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    with Image.open(source) as image:
        grayscale = ImageOps.grayscale(image)
        grayscale = ImageOps.autocontrast(grayscale, cutoff=0.2)
        grayscale.convert("RGB").save(destination, optimize=True)


def copy_colour_photo(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    with Image.open(source) as image:
        # No resize or crop: Pillow preserves the source pixel dimensions and
        # therefore the original aspect ratio.
        image.convert("RGB").save(destination, optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, source in MONOCHROME_ASSETS.items():
        destination = OUT / name
        convert_monochrome(source, destination)
        print(f"{name}: {destination.stat().st_size} bytes")

    for name, source in COLOUR_PHOTOS.items():
        destination = OUT / name
        copy_colour_photo(source, destination)
        print(f"{name}: {destination.stat().st_size} bytes")

    video_frame = OUT / "jetson_realtime.png"
    if video_frame.is_file():
        print(f"jetson_realtime.png: {video_frame.stat().st_size} bytes (colour)")


if __name__ == "__main__":
    main()
