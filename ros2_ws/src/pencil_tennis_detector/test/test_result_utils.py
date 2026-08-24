import json
import unittest

from pencil_tennis_detector.result_utils import (
    create_test_record,
    parse_result_message,
    select_highest_confidence,
    summarize_records,
)


class ResultUtilsTest(unittest.TestCase):
    def test_parse_and_select_highest_confidence(self):
        message = json.dumps(
            {
                "detections": [
                    {"class_name": "pencil", "confidence": 0.61},
                    {"class_name": "tennis_ball", "confidence": 0.92},
                ]
            }
        )
        payload = parse_result_message(message)
        selected = select_highest_confidence(payload["detections"])
        self.assertEqual(selected["class_name"], "tennis_ball")

    def test_empty_detection_creates_incorrect_none_record(self):
        record = create_test_record(
            1, "pencil", {"detections": []}, 12.5, "2026-08-24T12:00:00"
        )
        self.assertEqual(record["predicted_class"], "none")
        self.assertEqual(record["confidence"], 0.0)
        self.assertEqual(record["correct"], 0)

    def test_summary_applies_course_thresholds(self):
        records = [
            {"correct": 1 if index < 16 else 0, "fps": 5.0 + index / 10}
            for index in range(20)
        ]
        summary = summarize_records(records)
        self.assertEqual(summary["total_tests"], 20)
        self.assertAlmostEqual(summary["accuracy"], 0.8)
        self.assertTrue(summary["meets_20_tests"])
        self.assertTrue(summary["meets_accuracy_80_percent"])
        self.assertTrue(summary["meets_minimum_5_fps"])

    def test_fewer_than_twenty_does_not_pass_acceptance(self):
        summary = summarize_records([{"correct": 1, "fps": 30.0}])
        self.assertFalse(summary["meets_20_tests"])
        self.assertFalse(summary["meets_accuracy_80_percent"])
        self.assertFalse(summary["meets_minimum_5_fps"])


if __name__ == "__main__":
    unittest.main()
