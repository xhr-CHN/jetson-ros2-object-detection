# Jetson ROS 2 目标检测实验

## 实验目标

- 使用公开标注数据集训练不少于两类桌面物体的检测模型。
- 训练目标检测模型并部署到 Jetson。
- 实时显示目标类别、检测框和置信度。
- 通过 ROS 2 发布识别结果。
- 测试不少于 20 个物体，正确识别率不低于 80%。
- Jetson 实时检测速度不低于 5 FPS。
- 保存测试结果及典型错误案例。

## 初始检测类别

- 铅笔（pencil）
- 网球（tennis ball）

## 项目结构

```text
dataset/    公开数据集图片、标签和数据配置
models/     模型说明及部署产物
src/        训练、推理和测试程序
ros2_ws/    ROS 2 工作空间
results/    测试结果、正确案例和错误案例
report/     LaTeX 实验报告
docs/       运行说明、截图和演示材料
```

## 进度

- [x] 初始化项目及 Git 仓库
- [x] 获取公开数据集
- [x] 转换标注并划分数据集
- [x] 训练与评估模型
- [x] 部署到 Jetson
- [x] 编写 ROS 2 结果发布与验收记录程序
- [x] 完成不少于 20 个物体的验收测试
- [x] 完成 LaTeX 实验报告

## 数据来源

本项目使用 Mendeley Data 的网球数据集和 Kaggle 的铅笔数据集，并统一转换为两类 YOLO 标注。完整引用、许可证和处理说明见 [`dataset/SOURCES.md`](dataset/SOURCES.md)。

## Windows 本地训练

本项目复用 `D:\视觉识别一硝3\.venv` 中已有的 Ultralytics 和 CUDA 环境。由于该虚拟环境移动后原有的 `yolo.exe` 启动器路径已失效，应直接调用其中的 `python.exe` 运行训练脚本。

先运行3轮冒烟测试：

```powershell
cd "E:\机器人集成小组项目"
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py --smoke
```

确认冒烟测试没有数据或 CUDA 错误后，开始100轮正式训练：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py
```

如果8GB显存不足，可把批量大小改为4：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py --batch 4
```

### Roboflow 补充数据增强训练

项目另外使用 Roboflow Universe 的 [Pencil v2](https://universe.roboflow.com/workspace1-1gbmx/pencil-tvhes/dataset/2) 和 [Tennis ball v1](https://universe.roboflow.com/tennis-3ll0a/tennis-ball-icifx/dataset/1) 补充数据。五种铅笔子类统一为 `pencil`，网球统一为 `tennis_ball`。完整来源、许可证、类别映射和最终统计见 [`dataset/SOURCES.md`](dataset/SOURCES.md)。

从本地 ZIP 可重复整理补充数据：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" tools\merge_roboflow_yolo_datasets.py
```

先执行增强数据冒烟训练：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py --augmented --smoke
```

确认无误后执行正式增强训练：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py --augmented
```

增强训练输出单独保存在 `runs/pencil_tennis_yolo26n_augmented/`，不会直接覆盖当前正式模型。

最佳模型默认保存在 `runs/pencil_tennis_yolo26n/weights/best.pt`。脚本不会在 CUDA 不可用时自动退回 CPU。

### 独立测试集评估

使用未参与训练与最佳权重选择的测试集评估模型：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\evaluate_yolo26n_windows.py
```

总体及逐类指标保存到 `results/test/yolo26n/metrics.json`，验证图表保存到 `results/test/yolo26n/validation/`，119张带检测框的预测图片保存到 `results/test/yolo26n/predictions/`。

### Windows 摄像头实时检测

打开默认摄像头并实时显示类别、检测框、置信度和 FPS：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\webcam_yolo26n_windows.py
```

按 `Q` 或 `Esc` 退出。可使用 `--camera 1` 切换摄像头，或使用 `--conf 0.4` 调整置信度阈值。该脚本只实时显示，不录像或保存图片。

使用增强训练目录中的当前最佳模型进行摄像头测试：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\webcam_yolo26n_augmented_windows.py
```

USB 摄像头通常使用编号1；如果编号1不可用，可继续尝试2：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\webcam_yolo26n_augmented_windows.py --camera 1 --conf 0.25
```

也可以用 `--model` 指定任意待比较权重。该程序默认读取 `models/pencil_tennis_yolo26n_best.pt`，即完整训练100轮、最佳轮次为第87轮的正式增强模型。

## 已训练与部署模型

YOLO26n 正式训练已完成，筛选后的最佳权重保存在 [`models/pencil_tennis_yolo26n_best.pt`](models/pencil_tennis_yolo26n_best.pt)。用于跨框架部署的 ONNX 模型和在本次 Jetson 环境中生成的 TensorRT Engine 分别为 [`models/pencil_tennis_yolo26n_best.onnx`](models/pencil_tennis_yolo26n_best.onnx) 与 [`models/pencil_tennis_yolo26n_best.engine`](models/pencil_tennis_yolo26n_best.engine)。TensorRT Engine 与 JetPack、TensorRT、CUDA、GPU架构及推理设置相关，环境变化时应由 PT 或 ONNX 重新生成。

训练曲线、混淆矩阵和完整模型说明见 [`results/training/yolo26n_augmented/`](results/training/yolo26n_augmented/) 与 [`models/MODEL_CARD.md`](models/MODEL_CARD.md)。

独立测试集评估结果见 [`results/test/yolo26n/README.md`](results/test/yolo26n/README.md)。最终增强模型在119张测试图片上的总体 Precision 为0.9888、Recall 为0.9019、mAP@0.5 为0.9715、mAP@0.5:0.95 为0.8776。

## ROS 2 检测与验收记录

ROS 2 Python 包位于 `ros2_ws/src/pencil_tennis_detector`，以 ROS 2 Humble 为目标版本。实际运行需要 Ubuntu/Jetson 上已安装 ROS 2、`cv_bridge`、OpenCV、Ultralytics 和匹配 CUDA 的 PyTorch。

在仓库根目录构建：

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

回到仓库根目录启动摄像头检测节点：

```bash
cd ..
ros2 launch pencil_tennis_detector detector.launch.py \
  model:=$(pwd)/models/pencil_tennis_yolo26n_best.pt \
  camera:=0 confidence:=0.25 device:=cuda:0
```

节点发布以下话题：

- `/detection/image`：`sensor_msgs/Image`，包含检测框、类别、置信度和 FPS。
- `/detection/results`：`std_msgs/String`，包含每帧检测结果 JSON。
- `/detection/fps`：`std_msgs/Float32`，包含端到端实时速度。

## Jetson 部署结果

2026年8月30日已在 Jetson Orin 上完成部署验证。板端系统为 Jetson Linux R36.4.3（aarch64），CUDA 12.6 可用，TensorRT 版本为10.3.0。ROS 2 节点 `/pencil_tennis_detector` 正常发布检测图像、结构化结果和实时 FPS。

部署记录中的5次图像话题测速为13.369–14.092 FPS，平均13.795 FPS；46个检测 FPS 样本为15.421–17.971 FPS，平均16.657 FPS，超过课程要求的5 FPS。记录中的一个样例以0.958984375置信度识别出 `tennis_ball`。

- 完整结果说明：[`results/jetson/2026-08-30/README.md`](results/jetson/2026-08-30/README.md)
- 原始部署证据：[`results/jetson/2026-08-30/deployment_evidence.txt`](results/jetson/2026-08-30/deployment_evidence.txt)
- 最终演示视频：[`jetson_demo.mp4`](results/jetson/2026-08-30/jetson_demo.mp4)

除摄像头部署记录外，2026年8月30日还在Jetson上使用正式TensorRT Engine完成了两次留出测试集离线验收。第一次为铅笔10张、网球10张的初步测试；第二次才是最终验收，包含铅笔20张、网球20张，共40张互不重复的测试图片。最终正确39张，总正确率97.5%；铅笔正确率95%，网球正确率100%。第二次测试最低离线模型速度为30.1659 FPS。

最终验收的CSV、JSON、全部正确/错误案例、运行日志、环境记录及完整性校验见 [`results/jetson/2026-08-30/acceptance/README.md`](results/jetson/2026-08-30/acceptance/README.md)。该验收使用未参与训练和最佳权重选择的静态测试图片，不能与摄像头端到端FPS或完整测试集mAP混为同一指标。

## 实验报告

最终LaTeX实验报告位于 [`report/experiment1_object_detection_report.pdf`](report/experiment1_object_detection_report.pdf)，源码位于 [`report/main.tex`](report/main.tex)。报告采用A4单栏排版，正文小四号宋体，英文和数字使用Times New Roman；全部图片均保留彩色版本及原始宽高比，正文、标题、流程图线条和三线表保持黑白。报告包含训练曲线、独立测试PR曲线与混淆矩阵、Jetson实时画面、40项验收、唯一错误案例以及真实GitHub提交截图。

可在另一个已经 source 工作空间的终端检查：

```bash
ros2 topic echo /detection/results
ros2 topic echo /detection/fps
ros2 run rqt_image_view rqt_image_view /detection/image
```

如果课程现场还要求逐个摆放实物进行摄像头人工验收，可在另一个终端运行：

```bash
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
ros2 run pencil_tennis_detector test_recorder_node \
  --ros-args -p target_count:=20 -p output_root:=$(pwd)/results/jetson_test
```

每次把一个待测物体放到摄像头前，输入其预期类别 `pencil` 或 `tennis_ball` 并回车。程序取最近一帧中置信度最高的检测作为该次结果。完成20项后自动生成 `test_records.csv` 和 `summary.json`，统计正确率、平均/最低 FPS，并判断是否达到20项、80%正确率和最低5 FPS要求。输入 `q` 可提前结束。
