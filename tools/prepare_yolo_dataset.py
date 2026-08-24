"""Convert the supplied pencil and tennis-ball datasets to YOLO format."""

from __future__ import annotations

import json
import hashlib
import random
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PENCIL_ROOT = ROOT / "pencil_dataset"
TENNIS_ROOT = ROOT / "tennis"
OUTPUT_ROOT = ROOT / "dataset"
SPLITS = ("train", "val", "test")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def validate_image(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return image.size


def write_label(path: Path, rows: list[tuple[int, float, float, float, float]]) -> None:
    text = "".join(
        f"{class_id} {x:.6f} {y:.6f} {width:.6f} {height:.6f}\n"
        for class_id, x, y, width, height in rows
    )
    path.write_text(text, encoding="utf-8")


def prepare_output() -> None:
    for split in SPLITS:
        image_dir = OUTPUT_ROOT / "images" / split
        label_dir = OUTPUT_ROOT / "labels" / split
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)
        for prefix in ("pencil_", "tennis_"):
            for path in image_dir.glob(f"{prefix}*"):
                path.unlink()
            for path in label_dir.glob(f"{prefix}*.txt"):
                path.unlink()


def convert_pencils() -> dict[str, int]:
    counts: dict[str, int] = {}
    source_names = {"train": "train", "val": "valid", "test": "test"}

    for output_split, source_split in source_names.items():
        source_dir = PENCIL_ROOT / source_split
        images = sorted(
            path for path in source_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES
        )
        counts[output_split] = len(images)

        for image_path in images:
            json_path = image_path.with_suffix(".json")
            if not json_path.exists():
                raise ValueError(f"Missing pencil annotation: {json_path}")

            data = json.loads(json_path.read_text(encoding="utf-8"))
            actual_width, actual_height = validate_image(image_path)
            image_width = int(data["image_width"])
            image_height = int(data["image_height"])
            if (actual_width, actual_height) != (image_width, image_height):
                raise ValueError(f"Image size mismatch: {image_path}")

            rows = []
            for obj in data.get("objects", []):
                category = str(obj.get("category", ""))
                if not category.endswith("pencil"):
                    raise ValueError(f"Unexpected pencil category {category!r}: {json_path}")
                x, y, width, height = map(float, obj["bounding_box"])
                if width <= 0 or height <= 0 or x < 0 or y < 0:
                    raise ValueError(f"Invalid pencil box: {json_path}")
                if x + width > image_width + 1 or y + height > image_height + 1:
                    raise ValueError(f"Pencil box outside image: {json_path}")

                row = (
                    0,
                    (x + width / 2) / image_width,
                    (y + height / 2) / image_height,
                    width / image_width,
                    height / image_height,
                )
                rows.append(row)

            if not rows:
                raise ValueError(f"No pencil objects: {json_path}")

            stem = f"pencil_{image_path.stem}"
            shutil.copy2(image_path, OUTPUT_ROOT / "images" / output_split / f"{stem}{image_path.suffix.lower()}")
            write_label(OUTPUT_ROOT / "labels" / output_split / f"{stem}.txt", rows)

    return counts


def parse_tennis_label(path: Path) -> list[tuple[int, float, float, float, float]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 5:
            raise ValueError(f"Invalid YOLO row at {path}:{line_number}")
        source_class = int(fields[0])
        values = tuple(map(float, fields[1:]))
        if source_class != 0:
            raise ValueError(f"Unexpected tennis class {source_class}: {path}")
        if any(value < 0 or value > 1 for value in values) or values[2] <= 0 or values[3] <= 0:
            raise ValueError(f"Invalid tennis coordinates: {path}:{line_number}")
        rows.append((1, *values))
    if not rows:
        raise ValueError(f"No tennis objects: {path}")
    return rows


def convert_tennis() -> dict[str, int]:
    images = sorted(
        path for path in TENNIS_ROOT.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES
    )
    unique_images = []
    seen_hashes = set()
    for image_path in images:
        digest = hashlib.sha256(image_path.read_bytes()).digest()
        if digest not in seen_hashes:
            seen_hashes.add(digest)
            unique_images.append(image_path)
    images = unique_images
    random.Random(42).shuffle(images)
    train_end = round(len(images) * 0.70)
    val_end = train_end + round(len(images) * 0.15)
    split_images = {
        "train": images[:train_end],
        "val": images[train_end:val_end],
        "test": images[val_end:],
    }

    for split, paths in split_images.items():
        for image_path in paths:
            label_path = image_path.with_suffix(".txt")
            if not label_path.exists():
                raise ValueError(f"Missing tennis annotation: {label_path}")
            validate_image(image_path)
            rows = parse_tennis_label(label_path)
            stem = f"tennis_{image_path.stem}"
            shutil.copy2(image_path, OUTPUT_ROOT / "images" / split / f"{stem}{image_path.suffix.lower()}")
            write_label(OUTPUT_ROOT / "labels" / split / f"{stem}.txt", rows)

    return {split: len(paths) for split, paths in split_images.items()}


def write_yaml() -> None:
    content = """path: .
train: images/train
val: images/val
test: images/test

names:
  0: pencil
  1: tennis_ball
"""
    (OUTPUT_ROOT / "data.yaml").write_text(content, encoding="utf-8")


def main() -> None:
    prepare_output()
    pencil_counts = convert_pencils()
    tennis_counts = convert_tennis()
    write_yaml()
    print(f"pencil: {pencil_counts}")
    print(f"tennis_ball: {tennis_counts}")
    print("classes: 0=pencil, 1=tennis_ball")


if __name__ == "__main__":
    main()
