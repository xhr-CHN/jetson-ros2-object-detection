[English](README_EN.md) | [中文](README.md)

# Jetson ROS 2 Object Detection Experiment

## Experiment Objectives

- Train an object-detection model for at least two classes of desktop objects using publicly available annotated datasets.
- Train and deploy the object-detection model on a Jetson device.
- Display object classes, bounding boxes, and confidence scores in real time.
- Publish detection results through ROS 2.
- Test at least 20 objects and achieve an accuracy of at least 80%.
- Achieve a real-time detection speed of at least 5 FPS on Jetson.
- Preserve test results and representative error cases.

## Detection Classes

- Pencil (`pencil`)
- Tennis ball (`tennis_ball`)

## Project Structure

```text
dataset/    Public dataset images, labels, and data configuration
models/     Model documentation and deployment artifacts
src/        Training, inference, and evaluation programs
ros2_ws/    ROS 2 workspace
results/    Test results, correct cases, and error cases
report/     LaTeX experiment report
docs/       Operating instructions, screenshots, and demonstration materials
```

## Progress

- [x] Initialize the project and Git repository
- [x] Obtain public datasets
- [x] Convert annotations and split the dataset
- [x] Train and evaluate the model
- [x] Deploy the model on Jetson
- [x] Implement ROS 2 result publishing and acceptance-test recording
- [x] Complete an acceptance test with at least 20 objects
- [x] Complete the LaTeX experiment report

## Data Sources

This project uses the tennis-ball dataset from Mendeley Data and the pencil dataset from Kaggle, with all annotations converted into a unified two-class YOLO format. Complete citations, licenses, and processing details are provided in [`dataset/SOURCES.md`](dataset/SOURCES.md).

## Local Training on Windows

The project reuses the existing Ultralytics and CUDA environment at `D:\视觉识别一硝3\.venv`. Because the original `yolo.exe` launcher path became invalid after the virtual environment was moved, invoke its `python.exe` directly to run the training script.

Run a three-epoch smoke test first:

```powershell
cd "E:\机器人集成小组项目"
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py --smoke
```

After confirming that the smoke test reports no dataset or CUDA errors, start the formal 100-epoch training run:

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py
```

If 8 GB of GPU memory is insufficient, reduce the batch size to 4:

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py --batch 4
```

### Augmented Training with Additional Roboflow Data

The project additionally uses [Pencil v2](https://universe.roboflow.com/workspace1-1gbmx/pencil-tvhes/dataset/2) and [Tennis ball v1](https://universe.roboflow.com/tennis-3ll0a/tennis-ball-icifx/dataset/1) from Roboflow Universe. The five pencil subclasses are merged into `pencil`, and all tennis-ball labels are mapped to `tennis_ball`. Complete sources, licenses, class mappings, and final statistics are documented in [`dataset/SOURCES.md`](dataset/SOURCES.md).

The additional data can be reproducibly merged from the local ZIP files:

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" tools\merge_roboflow_yolo_datasets.py
```

Run a smoke test on the augmented dataset:

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py --augmented --smoke
```

After confirming that it runs correctly, start formal augmented training:

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py --augmented
```

Augmented-training outputs are stored separately in `runs/pencil_tennis_yolo26n_augmented/` and do not directly overwrite the current formal model.

By default, the best model is stored at `runs/pencil_tennis_yolo26n/weights/best.pt`. The script does not silently fall back to the CPU when CUDA is unavailable.

### Independent Test-Set Evaluation

Evaluate the model on the test set that was not used for training or best-weight selection:

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\evaluate_yolo26n_windows.py
```

Overall and per-class metrics are saved to `results/test/yolo26n/metrics.json`, validation plots are saved to `results/test/yolo26n/validation/`, and 119 prediction images with bounding boxes are saved to `results/test/yolo26n/predictions/`.

### Real-Time Webcam Detection on Windows

Open the default camera and display classes, bounding boxes, confidence scores, and FPS in real time:

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\webcam_yolo26n_windows.py
```

Press `Q` or `Esc` to exit. Use `--camera 1` to select another camera or `--conf 0.4` to change the confidence threshold. This script only displays the live result; it does not record video or save images.

Test the current best model from the augmented-training directory:

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\webcam_yolo26n_augmented_windows.py
```

A USB camera commonly uses index 1. If index 1 is unavailable, try index 2:

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\webcam_yolo26n_augmented_windows.py --camera 1 --conf 0.25
```

The `--model` option can also specify any weights to compare. By default, the program loads `models/pencil_tennis_yolo26n_best.pt`, the formal augmented model trained for the full 100 epochs, with the best result at epoch 87.

## Trained and Deployed Models

Formal YOLO26n training is complete. The selected best weights are stored in [`models/pencil_tennis_yolo26n_best.pt`](models/pencil_tennis_yolo26n_best.pt). The ONNX model for cross-framework deployment and the TensorRT Engine generated in the Jetson environment are [`models/pencil_tennis_yolo26n_best.onnx`](models/pencil_tennis_yolo26n_best.onnx) and [`models/pencil_tennis_yolo26n_best.engine`](models/pencil_tennis_yolo26n_best.engine), respectively. A TensorRT Engine depends on JetPack, TensorRT, CUDA, GPU architecture, and inference settings; regenerate it from PT or ONNX if the environment changes.

Training curves, confusion matrices, and complete model documentation are available in [`results/training/yolo26n_augmented/`](results/training/yolo26n_augmented/) and [`models/MODEL_CARD.md`](models/MODEL_CARD.md).

Independent test-set results are documented in [`results/test/yolo26n/README.md`](results/test/yolo26n/README.md). On 119 test images, the final augmented model achieved an overall Precision of 0.9888, Recall of 0.9019, mAP@0.5 of 0.9715, and mAP@0.5:0.95 of 0.8776.

## ROS 2 Detection and Acceptance-Test Recording

The ROS 2 Python package is located at `ros2_ws/src/pencil_tennis_detector` and targets ROS 2 Humble. Running it on Ubuntu or Jetson requires ROS 2, `cv_bridge`, OpenCV, Ultralytics, and a CUDA-compatible PyTorch installation.

Build from the repository root:

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

Return to the repository root and launch the camera detection node:

```bash
cd ..
ros2 launch pencil_tennis_detector detector.launch.py \
  model:=$(pwd)/models/pencil_tennis_yolo26n_best.pt \
  camera:=0 confidence:=0.25 device:=cuda:0
```

The node publishes these topics:

- `/detection/image`: `sensor_msgs/Image`, containing bounding boxes, classes, confidence scores, and FPS.
- `/detection/results`: `std_msgs/String`, containing per-frame detection results in JSON.
- `/detection/fps`: `std_msgs/Float32`, containing the end-to-end real-time speed.

## Jetson Deployment Results

Deployment was verified on a Jetson Orin on August 30, 2026. The device ran Jetson Linux R36.4.3 on aarch64 with CUDA 12.6 and TensorRT 10.3.0. The ROS 2 node `/pencil_tennis_detector` correctly published the annotated image, structured results, and real-time FPS.

Five image-topic rate measurements ranged from 13.369 to 14.092 FPS, with an average of 13.795 FPS. Forty-six detection-FPS samples ranged from 15.421 to 17.971 FPS, with an average of 16.657 FPS. Both exceeded the course requirement of 5 FPS. One recorded example detected `tennis_ball` with a confidence of 0.958984375.

- Complete result description: [`results/jetson/2026-08-30/README.md`](results/jetson/2026-08-30/README.md)
- Raw deployment evidence: [`results/jetson/2026-08-30/deployment_evidence.txt`](results/jetson/2026-08-30/deployment_evidence.txt)
- Final demonstration video: [`jetson_demo.mp4`](results/jetson/2026-08-30/jetson_demo.mp4)

In addition to the camera deployment record, two offline acceptance tests using the formal TensorRT Engine were performed on the Jetson on August 30, 2026. The first was a preliminary test with 10 pencil and 10 tennis-ball images. Only the second attempt is the final acceptance test: it contains 20 pencil and 20 tennis-ball images, for 40 mutually distinct test images. It correctly recognized 39 images for an overall accuracy of 97.5%; pencil accuracy was 95%, and tennis-ball accuracy was 100%. The minimum offline model speed during the second test was 30.1659 FPS.

The CSV, JSON, all correct and error cases, execution log, environment record, and integrity checks for the final acceptance test are documented in [`results/jetson/2026-08-30/acceptance/README.md`](results/jetson/2026-08-30/acceptance/README.md). This acceptance test uses static test images that were not used for training or best-weight selection. Its results must not be conflated with camera end-to-end FPS or full-test-set mAP.

## Experiment Report

The final LaTeX report is available at [`report/experiment1_object_detection_report.pdf`](report/experiment1_object_detection_report.pdf), and its source is [`report/main.tex`](report/main.tex). The report uses an A4 single-column layout with 12 pt body text. English text and numbers use Times New Roman. All images retain their original colors and aspect ratios, while body text, headings, flowchart lines, and three-line tables remain black and white. The report includes the training curves, independent-test PR curve and confusion matrix, Jetson real-time output, the 40-item acceptance test, the sole error case, and genuine GitHub screenshots.

In another terminal where the workspace has been sourced, inspect the topics with:

```bash
ros2 topic echo /detection/results
ros2 topic echo /detection/fps
ros2 run rqt_image_view rqt_image_view /detection/image
```

If the course demonstration additionally requires placing physical objects in front of the camera one by one, run the interactive acceptance recorder in another terminal:

```bash
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
ros2 run pencil_tennis_detector test_recorder_node \
  --ros-args -p target_count:=20 -p output_root:=$(pwd)/results/jetson_test
```

Place one test object in front of the camera, enter its expected class, `pencil` or `tennis_ball`, and press Enter. The program uses the highest-confidence detection in the most recent frame as the result for that item. After 20 items, it automatically generates `test_records.csv` and `summary.json`, calculates accuracy and average/minimum FPS, and checks the requirements of 20 items, 80% accuracy, and a minimum of 5 FPS. Enter `q` to stop early.
