"""Interactive ROS 2 acceptance-test recorder."""

import csv
import json
import threading
from datetime import datetime
from pathlib import Path

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32, String

from .result_utils import (
    VALID_CLASSES,
    create_test_record,
    parse_result_message,
    summarize_records,
)


CSV_FIELDS = (
    "test_id",
    "expected_class",
    "predicted_class",
    "confidence",
    "correct",
    "fps",
    "timestamp",
)


class TestRecorderNode(Node):
    """Record one latest-frame prediction for each operator-confirmed object."""

    def __init__(self):
        super().__init__("pencil_tennis_test_recorder")
        self.declare_parameter("target_count", 20)
        self.declare_parameter("output_root", "results/jetson_test")
        self.target_count = int(self.get_parameter("target_count").value)
        if self.target_count < 1:
            raise ValueError("target_count must be at least 1")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(self.get_parameter("output_root").value) / timestamp
        self.output_dir.mkdir(parents=True, exist_ok=False)
        self.csv_path = self.output_dir / "test_records.csv"
        self.summary_path = self.output_dir / "summary.json"

        self.lock = threading.Lock()
        self.latest_payload = None
        self.latest_fps = 0.0
        self.records = []
        self.finished = False

        self.create_subscription(String, "/detection/results", self.result_callback, 10)
        self.create_subscription(Float32, "/detection/fps", self.fps_callback, 10)
        self.input_thread = threading.Thread(target=self.operator_loop, daemon=True)
        self.input_thread.start()
        self.get_logger().info(f"Results will be saved to {self.output_dir}")

    def result_callback(self, message):
        try:
            payload = parse_result_message(message.data)
        except (json.JSONDecodeError, ValueError, TypeError, KeyError) as error:
            self.get_logger().warning(f"ignored invalid result message: {error}")
            return
        with self.lock:
            self.latest_payload = payload

    def fps_callback(self, message):
        with self.lock:
            self.latest_fps = float(message.data)

    def operator_loop(self):
        prompt = "输入预期类别 pencil/tennis_ball 并回车记录，输入 q 结束："
        while rclpy.ok() and not self.finished:
            try:
                expected = input(prompt).strip().lower()
            except EOFError:
                expected = "q"

            if expected in ("q", "quit", "exit"):
                self.finish()
                return
            if expected not in VALID_CLASSES:
                print("类别无效，请输入 pencil 或 tennis_ball。")
                continue

            with self.lock:
                payload = self.latest_payload
                fps = self.latest_fps
            if payload is None:
                print("尚未收到检测结果，请等待检测节点开始发布。")
                continue

            record = create_test_record(
                len(self.records) + 1,
                expected,
                payload,
                fps,
                datetime.now().isoformat(timespec="seconds"),
            )
            self.records.append(record)
            self.write_csv()
            print(
                f"已记录 {len(self.records)}/{self.target_count}: "
                f"预测={record['predicted_class']} "
                f"置信度={record['confidence']:.3f} "
                f"FPS={record['fps']:.2f} "
                f"正确={'是' if record['correct'] else '否'}"
            )
            if len(self.records) >= self.target_count:
                self.finish()
                return

    def write_csv(self):
        with self.csv_path.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(self.records)

    def finish(self):
        if self.finished:
            return
        self.finished = True
        summary = summarize_records(self.records)
        with self.summary_path.open("w", encoding="utf-8") as stream:
            json.dump(summary, stream, ensure_ascii=False, indent=2)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        print(f"测试结果已保存到 {self.output_dir}")
        if rclpy.ok():
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = TestRecorderNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        node.finish()
    finally:
        if not node.finished:
            node.finish()
        node.destroy_node()


if __name__ == "__main__":
    main()
