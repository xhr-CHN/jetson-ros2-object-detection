"""ROS 2 node that runs YOLO on an OpenCV camera."""

import json
import time

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32, String
from ultralytics import YOLO


class DetectorNode(Node):
    """Capture camera frames, run YOLO, and publish detections."""

    def __init__(self):
        super().__init__("pencil_tennis_detector")
        self.declare_parameter("model", "models/pencil_tennis_yolo26n_best.pt")
        self.declare_parameter("camera", 0)
        self.declare_parameter("confidence", 0.25)
        self.declare_parameter("image_size", 640)
        self.declare_parameter("device", "cuda:0")
        self.declare_parameter("timer_period", 0.01)

        model_path = self.get_parameter("model").value
        camera_index = int(self.get_parameter("camera").value)
        self.confidence = float(self.get_parameter("confidence").value)
        self.image_size = int(self.get_parameter("image_size").value)
        self.device = str(self.get_parameter("device").value)

        self.get_logger().info(f"Loading model: {model_path}")
        self.model = YOLO(model_path)
        self.camera = cv2.VideoCapture(camera_index)
        if not self.camera.isOpened():
            self.camera.release()
            raise RuntimeError(f"unable to open camera index {camera_index}")

        self.bridge = CvBridge()
        self.image_publisher = self.create_publisher(Image, "/detection/image", 10)
        self.results_publisher = self.create_publisher(String, "/detection/results", 10)
        self.fps_publisher = self.create_publisher(Float32, "/detection/fps", 10)
        self.frame_id = 0
        timer_period = float(self.get_parameter("timer_period").value)
        self.timer = self.create_timer(timer_period, self.process_frame)
        self.get_logger().info("Detector ready")

    def process_frame(self):
        started = time.perf_counter()
        success, frame = self.camera.read()
        if not success:
            self.get_logger().warning("camera frame read failed")
            return

        result = self.model.predict(
            source=frame,
            conf=self.confidence,
            imgsz=self.image_size,
            device=self.device,
            verbose=False,
        )[0]
        elapsed = max(time.perf_counter() - started, 1e-9)
        fps = 1.0 / elapsed
        self.frame_id += 1

        detections = []
        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls.item())
                x1, y1, x2, y2 = (float(value) for value in box.xyxy[0].tolist())
                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": str(result.names[class_id]),
                        "confidence": float(box.conf.item()),
                        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                    }
                )

        payload = {
            "timestamp": self.get_clock().now().nanoseconds / 1e9,
            "frame_id": self.frame_id,
            "image_width": int(frame.shape[1]),
            "image_height": int(frame.shape[0]),
            "detections": detections,
        }
        results_message = String()
        results_message.data = json.dumps(payload, ensure_ascii=False)
        self.results_publisher.publish(results_message)

        fps_message = Float32()
        fps_message.data = fps
        self.fps_publisher.publish(fps_message)

        annotated = result.plot()
        cv2.putText(
            annotated,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )
        image_message = self.bridge.cv2_to_imgmsg(annotated, encoding="bgr8")
        image_message.header.stamp = self.get_clock().now().to_msg()
        image_message.header.frame_id = "camera"
        self.image_publisher.publish(image_message)

    def destroy_node(self):
        if hasattr(self, "camera"):
            self.camera.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = DetectorNode()
        rclpy.spin(node)
    except (KeyboardInterrupt, RuntimeError, FileNotFoundError) as error:
        if node is not None:
            node.get_logger().error(str(error))
        else:
            print(f"Detector startup failed: {error}")
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
