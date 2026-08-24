# ROS 2 检测与测试记录设计

## 目标

在不依赖 Jetson 硬件的情况下，先完成可迁移到 ROS 2 Humble 的 Python 包。系统加载现有 YOLO26n 铅笔/网球模型，从摄像头获取图像，发布带标注图像、结构化检测结果和实时 FPS，并能记录不少于 20 次人工验收测试。

## 范围

本阶段包含 ROS 2 检测节点、话题接口、启动文件和交互式测试记录节点。不包含 TensorRT 导出、Jetson 摄像头驱动适配、ROS 2 安装和最终验收数据；这些工作需要取得目标板后完成。

## 技术选择

- 目标版本：ROS 2 Humble，Python 包使用 `ament_python`。
- 推理引擎：Ultralytics YOLO，默认加载仓库中的 `models/pencil_tennis_yolo26n_best.pt`。
- 图像输入：检测节点直接通过 OpenCV 打开摄像头。这样可在没有相机 ROS 驱动时运行，后续如需订阅 `/camera/image_raw` 再单独扩展。
- 消息类型：使用 ROS 2 标准消息，避免维护自定义消息包。
- 检测结果：使用 `std_msgs/String` 承载 JSON；字段固定、方便终端检查和测试记录。

## 包结构

```text
ros2_ws/src/pencil_tennis_detector/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/pencil_tennis_detector
├── launch/detector.launch.py
└── pencil_tennis_detector/
    ├── __init__.py
    ├── detector_node.py
    └── test_recorder_node.py
```

## 检测节点

`detector_node` 启动时读取 ROS 参数：模型路径、摄像头编号、置信度阈值、图像尺寸和推理设备。节点打开摄像头并加载模型；定时读取帧并执行推理，随后发布：

- `/detection/image` (`sensor_msgs/msg/Image`)：绘制检测框、类别、置信度和 FPS 的图像。
- `/detection/results` (`std_msgs/msg/String`)：每帧一个 JSON 对象。
- `/detection/fps` (`std_msgs/msg/Float32`)：该帧的端到端处理速度。

检测结果 JSON 固定包含时间戳、帧编号、图像尺寸和 `detections` 数组。每个检测项包含 `class_id`、`class_name`、`confidence` 以及 `x1/y1/x2/y2` 像素坐标。没有目标时仍发布空数组，使下游能够区分“没有目标”和“节点停止”。

节点无法加载模型或打开摄像头时输出明确错误并停止；单帧读取失败时记录警告并继续尝试。节点退出时释放摄像头。

## 测试记录节点

`test_recorder_node` 订阅 `/detection/results` 和 `/detection/fps`。测试人员在终端输入当前目标的预期类别，然后按回车记录最近一帧结果。记录规则为：最近一帧中置信度最高的检测作为该次预测；没有检测则记为 `none`。这样每件实物只产生一条可人工核验的记录，避免把视频帧数误当测试样本数。

每次记录写入 CSV：测试编号、预期类别、预测类别、置信度、是否正确、FPS 和时间戳。达到指定测试数量（默认 20）或用户提前结束后，生成 JSON 摘要，包括正确率、平均 FPS、最低 FPS，以及是否达到 80% 正确率和 5 FPS 两项要求。

输出默认放在 `results/jetson_test/<timestamp>/`。本阶段只保存表格和摘要；典型错误截图由检测画面或后续板端扩展取得，避免未经选择持续保存大量摄像头内容。

## 启动与配置

启动文件同时支持只运行检测节点，以及通过另一个命令单独启动记录节点。所有机器相关路径都通过参数传入，不把 Windows 路径写入 ROS 包。README 给出构建、source、启动、话题检查和记录 20 项测试的完整命令。

## 验证标准

- Python 源文件通过语法检查。
- ROS 2 包清单、入口点和启动文件相互一致。
- 纯 Python 单元测试验证 JSON 解析、最高置信度选择和统计逻辑，不需要摄像头或 GPU。
- 在 ROS 2 Humble 环境中可用 `colcon build` 构建，并能通过 `ros2 topic echo` 看到结果和 FPS。
- 最终 Jetson 实测时完成至少 20 条人工记录，正确率不低于 80%，实时速度不低于 5 FPS。

## 后续工作

取得 Jetson 后确认 JetPack、CUDA、ROS 2 和摄像头接口，安装匹配版本依赖，运行节点并采集最终记录。若 PyTorch 推理速度不足，再将模型导出为 TensorRT Engine；话题协议和测试记录格式保持不变。
