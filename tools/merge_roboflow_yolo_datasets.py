"""Merge the supplied Roboflow YOLO26 archives into the project dataset."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = ROOT / "dataset"
REPORT_PATH = DATASET_ROOT / "augmentation-report.json"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
OUTPUT_SPLITS = ("train", "val", "test")
SPLIT_PRIORITY = ("test", "val", "train")
GENERATED_PREFIXES = ("roboflow_pencil_", "roboflow_tennis_")


@dataclass(frozen=True)
class Source:
    name: str
    archive: Path
    prefix: str
    class_ids: frozenset[int]
    output_class: int


SOURCES = (
    Source(
        name="pencil-v2",
        archive=Path(r"E:\Downloads\pencil.v2i.yolo26.zip"),
        prefix="roboflow_pencil_",
        class_ids=frozenset(range(5)),
        output_class=0,
    ),
    Source(
        name="tennis-ball-v1",
        archive=Path(r"E:\Downloads\tennis ball.v1i.yolo26.zip"),
        prefix="roboflow_tennis_",
        class_ids=frozenset({0}),
        output_class=1,
    ),
)


@dataclass
class Candidate:
    source: Source
    split: str
    image_name: str
    image_bytes: bytes
    label_rows: list[tuple[int, float, float, float, float]]
    file_hash: str
    pixel_hash: str


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_pixel_hash(data: bytes, name: str) -> str:
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            rgb = image.convert("RGB")
            payload = f"{rgb.width}x{rgb.height}:RGB:".encode() + rgb.tobytes()
    except Exception as error:
        raise ValueError(f"invalid image {name}: {error}") from error
    return sha256(payload)


def parse_label(data: bytes, source: Source, name: str):
    rows = []
    text = data.decode("utf-8-sig")
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 5:
            raise ValueError(f"invalid YOLO row at {name}:{line_number}")
        source_class = int(fields[0])
        values = tuple(float(value) for value in fields[1:])
        if source_class not in source.class_ids:
            raise ValueError(f"unexpected class {source_class} at {name}:{line_number}")
        if any(value < 0 or value > 1 for value in values):
            raise ValueError(f"coordinate outside [0, 1] at {name}:{line_number}")
        if values[2] <= 0 or values[3] <= 0:
            raise ValueError(f"non-positive box at {name}:{line_number}")
        rows.append((source.output_class, *values))
    if not rows:
        raise ValueError(f"empty label: {name}")
    return rows


def clean_previous_outputs() -> int:
    removed = 0
    for split in OUTPUT_SPLITS:
        for kind in ("images", "labels"):
            directory = DATASET_ROOT / kind / split
            for prefix in GENERATED_PREFIXES:
                for path in directory.glob(f"{prefix}*"):
                    if path.is_file():
                        path.unlink()
                        removed += 1
    if REPORT_PATH.exists():
        REPORT_PATH.unlink()
    return removed


def validate_existing_dataset():
    file_hashes = {}
    pixel_hashes = {}
    for split in OUTPUT_SPLITS:
        image_dir = DATASET_ROOT / "images" / split
        label_dir = DATASET_ROOT / "labels" / split
        images = {
            path.stem: path
            for path in image_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        }
        labels = {path.stem: path for path in label_dir.glob("*.txt")}
        if images.keys() != labels.keys():
            missing = sorted(images.keys() - labels.keys())
            orphan = sorted(labels.keys() - images.keys())
            raise ValueError(
                f"existing {split} image/label mismatch: missing={missing}, orphan={orphan}"
            )
        for stem, image_path in images.items():
            image_data = image_path.read_bytes()
            file_digest = sha256(image_data)
            pixel_digest = image_pixel_hash(image_data, str(image_path))
            for digest, owners, kind in (
                (file_digest, file_hashes, "file"),
                (pixel_digest, pixel_hashes, "pixel"),
            ):
                previous = owners.get(digest)
                if previous is not None:
                    raise ValueError(
                        f"duplicate existing image ({kind} hash): "
                        f"{previous} and {image_path}"
                    )
                owners[digest] = image_path
            parse_existing_label(labels[stem])
    return set(file_hashes), set(pixel_hashes)


def parse_existing_label(path: Path) -> None:
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split()
        if len(fields) != 5 or int(fields[0]) not in (0, 1):
            raise ValueError(f"invalid existing label at {path}:{line_number}")
        values = tuple(float(value) for value in fields[1:])
        if any(value < 0 or value > 1 for value in values):
            raise ValueError(f"invalid existing coordinates at {path}:{line_number}")
        if values[2] <= 0 or values[3] <= 0:
            raise ValueError(f"invalid existing box at {path}:{line_number}")


def load_candidates(source: Source) -> list[Candidate]:
    if not source.archive.is_file():
        raise FileNotFoundError(f"archive not found: {source.archive}")
    candidates = []
    with zipfile.ZipFile(source.archive) as archive:
        names = set(archive.namelist())
        for zip_split in ("train", "valid", "test"):
            output_split = "val" if zip_split == "valid" else zip_split
            image_names = sorted(
                name
                for name in names
                if name.startswith(f"{zip_split}/images/")
                and PurePosixPath(name).suffix.lower() in IMAGE_SUFFIXES
            )
            for image_name in image_names:
                stem = PurePosixPath(image_name).stem
                label_name = f"{zip_split}/labels/{stem}.txt"
                if label_name not in names:
                    raise ValueError(f"missing label for {image_name}")
                image_data = archive.read(image_name)
                rows = parse_label(archive.read(label_name), source, label_name)
                candidates.append(
                    Candidate(
                        source=source,
                        split=output_split,
                        image_name=PurePosixPath(image_name).name,
                        image_bytes=image_data,
                        label_rows=rows,
                        file_hash=sha256(image_data),
                        pixel_hash=image_pixel_hash(image_data, image_name),
                    )
                )
    return candidates


def output_stem(candidate: Candidate) -> str:
    original = PurePosixPath(candidate.image_name).stem
    return f"{candidate.source.prefix}{original}"


def write_candidate(candidate: Candidate) -> None:
    stem = output_stem(candidate)
    suffix = PurePosixPath(candidate.image_name).suffix.lower()
    image_path = DATASET_ROOT / "images" / candidate.split / f"{stem}{suffix}"
    label_path = DATASET_ROOT / "labels" / candidate.split / f"{stem}.txt"
    if image_path.exists() or label_path.exists():
        raise FileExistsError(f"output collision: {stem}")
    image_path.write_bytes(candidate.image_bytes)
    label_text = "".join(
        f"{class_id} {x:.6f} {y:.6f} {width:.6f} {height:.6f}\n"
        for class_id, x, y, width, height in candidate.label_rows
    )
    label_path.write_text(label_text, encoding="utf-8")


def final_statistics():
    result = {}
    for split in OUTPUT_SPLITS:
        image_dir = DATASET_ROOT / "images" / split
        label_dir = DATASET_ROOT / "labels" / split
        images = [
            path
            for path in image_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        ]
        labels = list(label_dir.glob("*.txt"))
        classes = Counter()
        for path in labels:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    classes[int(line.split()[0])] += 1
        result[split] = {
            "images": len(images),
            "labels": len(labels),
            "objects": {"pencil": classes[0], "tennis_ball": classes[1]},
        }
    return result


def main() -> None:
    removed = clean_previous_outputs()
    existing_file_hashes, existing_pixel_hashes = validate_existing_dataset()
    candidates = [candidate for source in SOURCES for candidate in load_candidates(source)]
    priority = {split: index for index, split in enumerate(SPLIT_PRIORITY)}
    candidates.sort(key=lambda item: (priority[item.split], item.source.name, item.image_name))

    seen_file_hashes = set(existing_file_hashes)
    seen_pixel_hashes = set(existing_pixel_hashes)
    source_stats = {
        source.name: {
            split: {"input": 0, "added": 0, "duplicates_skipped": 0, "objects_added": 0}
            for split in OUTPUT_SPLITS
        }
        for source in SOURCES
    }

    for candidate in candidates:
        stats = source_stats[candidate.source.name][candidate.split]
        stats["input"] += 1
        if (
            candidate.file_hash in seen_file_hashes
            or candidate.pixel_hash in seen_pixel_hashes
        ):
            stats["duplicates_skipped"] += 1
            continue
        write_candidate(candidate)
        seen_file_hashes.add(candidate.file_hash)
        seen_pixel_hashes.add(candidate.pixel_hash)
        stats["added"] += 1
        stats["objects_added"] += len(candidate.label_rows)

    report = {
        "sources": source_stats,
        "duplicate_policy": "SHA-256 of file bytes or decoded RGB pixels",
        "class_mapping": {"0": "pencil", "1": "tennis_ball"},
        "final": final_statistics(),
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Previous generated files removed: {removed}")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
