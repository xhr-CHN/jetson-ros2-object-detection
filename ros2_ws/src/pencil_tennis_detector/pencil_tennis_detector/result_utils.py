"""Pure-Python helpers shared by ROS nodes and unit tests."""

import json
from statistics import mean


VALID_CLASSES = ("pencil", "tennis_ball")


def parse_result_message(message):
    """Parse and minimally validate one detection result JSON message."""
    payload = json.loads(message)
    detections = payload.get("detections")
    if not isinstance(detections, list):
        raise ValueError("detections must be a list")
    return payload


def select_highest_confidence(detections):
    """Return the highest-confidence detection, or None for an empty frame."""
    if not detections:
        return None
    return max(detections, key=lambda item: float(item["confidence"]))


def create_test_record(test_id, expected_class, payload, fps, timestamp):
    """Create one manually triggered acceptance-test record."""
    if expected_class not in VALID_CLASSES:
        raise ValueError(f"unsupported class: {expected_class}")

    best = select_highest_confidence(payload["detections"])
    predicted_class = "none" if best is None else str(best["class_name"])
    confidence = 0.0 if best is None else float(best["confidence"])
    return {
        "test_id": int(test_id),
        "expected_class": expected_class,
        "predicted_class": predicted_class,
        "confidence": confidence,
        "correct": int(predicted_class == expected_class),
        "fps": float(fps),
        "timestamp": timestamp,
    }


def summarize_records(records):
    """Calculate course acceptance metrics for recorded physical tests."""
    total = len(records)
    correct = sum(int(record["correct"]) for record in records)
    fps_values = [float(record["fps"]) for record in records]
    accuracy = correct / total if total else 0.0
    average_fps = mean(fps_values) if fps_values else 0.0
    minimum_fps = min(fps_values) if fps_values else 0.0
    return {
        "total_tests": total,
        "correct_tests": correct,
        "accuracy": accuracy,
        "average_fps": average_fps,
        "minimum_fps": minimum_fps,
        "meets_20_tests": total >= 20,
        "meets_accuracy_80_percent": total >= 20 and accuracy >= 0.8,
        "meets_minimum_5_fps": total >= 20 and minimum_fps >= 5.0,
    }
