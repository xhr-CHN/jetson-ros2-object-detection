from pathlib import Path
import csv
import json
import random
import shutil
import time

import cv2
from ultralytics import YOLO


SEED = 20260830
N_PER_CLASS = 10

REPO = Path("/root/jetson_acceptance_repo_20260830_205510")
ACC = Path("/root/jetson_acceptance_20260830_205633")

IMAGE_DIR = REPO / "dataset/images/test"
LABEL_DIR = REPO / "dataset/labels/test"
MODEL = REPO / "models/pencil_tennis_yolo26n_best.engine"

OUT = ACC / "acceptance/attempt_01"
CORRECT_DIR = OUT / "correct"
ERROR_DIR = OUT / "errors"

CLASS_NAMES = {
    0: "pencil",
    1: "tennis_ball",
}

random.seed(SEED)

OUT.mkdir(parents=True, exist_ok=True)
CORRECT_DIR.mkdir(parents=True, exist_ok=True)
ERROR_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 1. Build global GT object index over the ENTIRE test set
# ---------------------------------------------------------
global_object_id = 0
image_records = []

label_files = sorted(
    LABEL_DIR.glob("*.txt"),
    key=lambda p: p.name.lower()
)

for label_path in label_files:
    rows = []

    with label_path.open("r", encoding="utf-8") as f:
        for line_number, raw in enumerate(f, start=1):
            raw = raw.strip()
            if not raw:
                continue

            parts = raw.split()

            if len(parts) < 5:
                raise RuntimeError(
                    f"Invalid YOLO label: {label_path}:{line_number}"
                )

            cls_id = int(float(parts[0]))

            global_object_id += 1

            rows.append({
                "global_gt_object_id": global_object_id,
                "class_id": cls_id,
                "class_name": CLASS_NAMES.get(cls_id, f"class_{cls_id}"),
                "bbox_yolo": " ".join(parts[1:5]),
                "label_line": line_number,
            })

    stem = label_path.stem

    candidates = [
        IMAGE_DIR / f"{stem}.jpg",
        IMAGE_DIR / f"{stem}.jpeg",
        IMAGE_DIR / f"{stem}.png",
        IMAGE_DIR / f"{stem}.bmp",
        IMAGE_DIR / f"{stem}.webp",
    ]

    image_path = next((p for p in candidates if p.exists()), None)

    if image_path is None:
        continue

    image_records.append({
        "image_path": image_path,
        "label_path": label_path,
        "objects": rows,
    })


print(f"Total GT objects in test: {global_object_id}")
print(f"Test images with labels: {len(image_records)}")


# ---------------------------------------------------------
# 2. Only choose images containing EXACTLY ONE GT object
# ---------------------------------------------------------
single_pencil = [
    r for r in image_records
    if len(r["objects"]) == 1
    and r["objects"][0]["class_id"] == 0
]

single_tennis = [
    r for r in image_records
    if len(r["objects"]) == 1
    and r["objects"][0]["class_id"] == 1
]

print(f"Single-object pencil candidates: {len(single_pencil)}")
print(f"Single-object tennis_ball candidates: {len(single_tennis)}")

if len(single_pencil) < N_PER_CLASS:
    raise RuntimeError(
        f"Not enough single-pencil test images: "
        f"{len(single_pencil)} < {N_PER_CLASS}"
    )

if len(single_tennis) < N_PER_CLASS:
    raise RuntimeError(
        f"Not enough single-tennis_ball test images: "
        f"{len(single_tennis)} < {N_PER_CLASS}"
    )


selected_pencil = random.sample(single_pencil, N_PER_CLASS)
selected_tennis = random.sample(single_tennis, N_PER_CLASS)

# Keep acceptance order deterministic:
# tests 1-10 pencil, tests 11-20 tennis_ball
selected = selected_pencil + selected_tennis


# ---------------------------------------------------------
# 3. Save selection before inference
# ---------------------------------------------------------
with (OUT / "selected_images.txt").open("w", encoding="utf-8") as f:
    f.write(f"random_seed={SEED}\n")
    f.write(f"selection_rule=10 pencil + 10 tennis_ball, single-GT-object test images only\n")
    f.write(f"source_split=test only\n")
    f.write("\n")

    for i, item in enumerate(selected, start=1):
        obj = item["objects"][0]
        f.write(
            f"{i:02d}\t"
            f"global_gt_object_id={obj['global_gt_object_id']}\t"
            f"expected={obj['class_name']}\t"
            f"{item['image_path'].name}\n"
        )


# ---------------------------------------------------------
# 4. Load the actual Jetson TensorRT Engine
# ---------------------------------------------------------
print(f"Loading TensorRT model: {MODEL}")
model = YOLO(str(MODEL))


# Warmup with first selected image
print("Running warm-up inference...")
_ = model.predict(
    source=str(selected[0]["image_path"]),
    imgsz=640,
    conf=0.25,
    device=0,
    verbose=False,
)


records = []
error_entries = []


# ---------------------------------------------------------
# 5. Run 20 deterministic acceptance cases
# ---------------------------------------------------------
for test_id, item in enumerate(selected, start=1):
    image_path = item["image_path"]
    gt = item["objects"][0]

    expected_class = gt["class_name"]

    start = time.perf_counter()

    results = model.predict(
        source=str(image_path),
        imgsz=640,
        conf=0.25,
        device=0,
        verbose=False,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    result = results[0]

    preprocess_ms = float(result.speed.get("preprocess", 0.0))
    inference_ms = float(result.speed.get("inference", 0.0))
    postprocess_ms = float(result.speed.get("postprocess", 0.0))

    pipeline_ms = preprocess_ms + inference_ms + postprocess_ms
    model_fps = 1000.0 / pipeline_ms if pipeline_ms > 0 else 0.0

    detections = []

    if result.boxes is not None:
        for box in result.boxes:
            cls_id = int(box.cls.item())
            conf = float(box.conf.item())

            xyxy = box.xyxy[0].tolist()

            detections.append({
                "class_id": cls_id,
                "class_name": CLASS_NAMES.get(
                    cls_id,
                    str(result.names.get(cls_id, cls_id))
                ),
                "confidence": conf,
                "bbox_xyxy": xyxy,
            })

    if detections:
        best = max(detections, key=lambda x: x["confidence"])
        predicted_class = best["class_name"]
        confidence = best["confidence"]
        pred_bbox = best["bbox_xyxy"]
    else:
        predicted_class = "none"
        confidence = 0.0
        pred_bbox = []

    correct = int(predicted_class == expected_class)

    annotated = result.plot()

    overlay = [
        f"Acceptance #{test_id:02d}",
        f"Global GT object #{gt['global_gt_object_id']}",
        f"Expected: {expected_class}",
        f"Predicted: {predicted_class}",
        f"Confidence: {confidence:.4f}",
        f"Model FPS: {model_fps:.2f}",
        f"Result: {'CORRECT' if correct else 'ERROR'}",
    ]

    y = 30
    for text in overlay:
        cv2.putText(
            annotated,
            text,
            (15, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            4,
            cv2.LINE_AA,
        )
        cv2.putText(
            annotated,
            text,
            (15, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )
        y += 28

    out_name = (
        f"test_{test_id:02d}"
        f"_gt_{gt['global_gt_object_id']:04d}"
        f"_{expected_class}"
        f"_{'correct' if correct else 'error'}.jpg"
    )

    target_dir = CORRECT_DIR if correct else ERROR_DIR
    annotated_path = target_dir / out_name

    cv2.imwrite(str(annotated_path), annotated)

    record = {
        "acceptance_id": test_id,
        "global_gt_object_id": gt["global_gt_object_id"],
        "image_name": image_path.name,
        "expected_class": expected_class,
        "predicted_class": predicted_class,
        "confidence": round(confidence, 6),
        "correct": correct,
        "gt_yolo_bbox": gt["bbox_yolo"],
        "prediction_count": len(detections),
        "predicted_bbox_xyxy": json.dumps(pred_bbox),
        "preprocess_ms": round(preprocess_ms, 4),
        "inference_ms": round(inference_ms, 4),
        "postprocess_ms": round(postprocess_ms, 4),
        "pipeline_ms": round(pipeline_ms, 4),
        "offline_model_fps": round(model_fps, 4),
        "wall_time_ms": round(elapsed_ms, 4),
        "annotated_image": str(annotated_path.relative_to(ACC)),
    }

    records.append(record)

    print(
        f"[{test_id:02d}/20] "
        f"GT#{gt['global_gt_object_id']} "
        f"{image_path.name} "
        f"expected={expected_class} "
        f"predicted={predicted_class} "
        f"conf={confidence:.4f} "
        f"FPS={model_fps:.2f} "
        f"{'CORRECT' if correct else 'ERROR'}"
    )

    if not correct:
        error_entries.append(record)


# ---------------------------------------------------------
# 6. CSV
# ---------------------------------------------------------
csv_path = OUT / "test_records.csv"

with csv_path.open(
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=list(records[0].keys())
    )

    writer.writeheader()
    writer.writerows(records)


# ---------------------------------------------------------
# 7. Summary
# ---------------------------------------------------------
total = len(records)
correct_n = sum(r["correct"] for r in records)
errors_n = total - correct_n

pencil_records = [
    r for r in records
    if r["expected_class"] == "pencil"
]

tennis_records = [
    r for r in records
    if r["expected_class"] == "tennis_ball"
]

fps_values = [r["offline_model_fps"] for r in records]

summary = {
    "evaluation_type": "offline held-out test-set acceptance",
    "source_split": "test",
    "val_used": False,
    "random_seed": SEED,

    "model": str(MODEL),
    "model_format": "TensorRT Engine",

    "total_tests": total,
    "correct_tests": correct_n,
    "error_tests": errors_n,
    "accuracy": correct_n / total if total else 0.0,

    "pencil_tests": len(pencil_records),
    "pencil_correct": sum(r["correct"] for r in pencil_records),
    "pencil_accuracy": (
        sum(r["correct"] for r in pencil_records)
        / len(pencil_records)
        if pencil_records else 0.0
    ),

    "tennis_ball_tests": len(tennis_records),
    "tennis_ball_correct": sum(
        r["correct"] for r in tennis_records
    ),
    "tennis_ball_accuracy": (
        sum(r["correct"] for r in tennis_records)
        / len(tennis_records)
        if tennis_records else 0.0
    ),

    "average_offline_model_fps": (
        sum(fps_values) / len(fps_values)
        if fps_values else 0.0
    ),

    "minimum_offline_model_fps": (
        min(fps_values)
        if fps_values else 0.0
    ),

    "meets_20_tests": total == 20,
    "meets_accuracy_80_percent": (
        total == 20 and correct_n / total >= 0.80
    ),

    "notes": [
        "20 cases were selected only from dataset/images/test.",
        "dataset/images/val was not used.",
        "Each selected image contains exactly one ground-truth object.",
        "Tests 1-10 are pencil and tests 11-20 are tennis_ball.",
        "The highest-confidence detection determines the predicted class.",
        "An empty detection is scored as incorrect.",
        "offline_model_fps is derived from Ultralytics preprocess + inference + postprocess time and is not the ROS camera end-to-end FPS."
    ]
}

with (OUT / "summary.json").open(
    "w",
    encoding="utf-8"
) as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------
# 8. Errors report
# ---------------------------------------------------------
with (OUT / "errors.md").open(
    "w",
    encoding="utf-8"
) as f:

    f.write("# Acceptance Errors\n\n")

    if not error_entries:
        f.write("No failed cases were observed in this 20-case sample.\n")
    else:
        for r in error_entries:
            f.write(
                f"## Test {r['acceptance_id']:02d}\n\n"
                f"- Global GT object ID: {r['global_gt_object_id']}\n"
                f"- Image: `{r['image_name']}`\n"
                f"- Expected class: `{r['expected_class']}`\n"
                f"- Predicted class: `{r['predicted_class']}`\n"
                f"- Confidence: {r['confidence']:.6f}\n"
                f"- Offline model FPS: {r['offline_model_fps']:.2f}\n"
                f"- Prediction count: {r['prediction_count']}\n"
                f"- Possible cause: requires manual review of the saved annotated image.\n\n"
            )


# ---------------------------------------------------------
# 9. Test plan
# ---------------------------------------------------------
with (OUT / "test_plan.md").open(
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "# 20-Case Test-Set Acceptance Plan\n\n"
        f"- Random seed: `{SEED}`\n"
        f"- Dataset split: `test`\n"
        f"- Validation split used: `No`\n"
        f"- Pencil cases: `10`\n"
        f"- Tennis-ball cases: `10`\n"
        f"- Selection rule: exactly one GT object per image\n"
        f"- Model: `{MODEL.name}`\n"
        f"- Model runtime: TensorRT\n"
        f"- Image size: `640`\n"
        f"- Confidence threshold: `0.25`\n"
        f"- Scoring: highest-confidence prediction must match expected class\n"
        f"- No detection: incorrect\n"
    )


print("\n========== SUMMARY ==========")
print(json.dumps(summary, indent=2, ensure_ascii=False))
print(f"\nSaved to: {OUT}")
