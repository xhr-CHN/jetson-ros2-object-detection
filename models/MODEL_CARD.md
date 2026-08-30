# Pencil and Tennis Ball YOLO26n

## 模型概况

- 任务：目标检测
- 架构：YOLO26n
- 类别：`0=pencil`、`1=tennis_ball`
- 输入尺寸：640 × 640
- 预训练：是
- 最佳轮次：第87轮
- PyTorch权重：[`pencil_tennis_yolo26n_best.pt`](pencil_tennis_yolo26n_best.pt)
- ONNX模型：[`pencil_tennis_yolo26n_best.onnx`](pencil_tennis_yolo26n_best.onnx)
- TensorRT Engine：[`pencil_tennis_yolo26n_best.engine`](pencil_tennis_yolo26n_best.engine)

## 训练配置

- 训练轮数：100
- 批量大小：8
- GPU：NVIDIA GeForce RTX 4060 Laptop GPU
- CUDA设备：0
- 数据配置：`dataset/data-windows.yaml`
- 训练图片：605张
- 验证图片：171张
- 测试图片：119张（未参与训练与最佳权重选择）

完整参数见 [`results/training/yolo26n_augmented/args.yaml`](../results/training/yolo26n_augmented/args.yaml)，逐轮指标见 [`results/training/yolo26n_augmented/results.csv`](../results/training/yolo26n_augmented/results.csv)。

## 最佳验证指标

| 指标 | 数值 |
|---|---:|
| Precision | 0.96338 |
| Recall | 0.97329 |
| mAP@0.5 | 0.98185 |
| mAP@0.5:0.95 | 0.88025 |

这些指标来自验证集，不等同于课程要求的独立验收结果。独立测试集评估、Jetson摄像头部署和40项板端离线验收均已完成，三者采用不同数据与计时口径，应分别解读。

## 文件校验

| 文件 | 大小 | SHA256 |
|---|---:|---|
| `pencil_tennis_yolo26n_best.pt` | 5,415,023 bytes | `DA747F4ED471BE2A4BEF0E858B3DE5CE8FF133A1FF5459CEB2B1577093A4063D` |
| `pencil_tennis_yolo26n_best.onnx` | 9,761,287 bytes | `4616C124B10E4B2C65CE9680E14E3FE41B1170F2F4E1CAD33FD79C68CE4C2401` |
| `pencil_tennis_yolo26n_best.engine` | 7,863,922 bytes | `BBFFFC6D678DDF8627B58BE11D50A2F67FED4D430DC387680D085712713DC0E3` |

## Jetson 部署验证

- 设备：Jetson Orin（aarch64）
- Jetson Linux：R36.4.3
- PyTorch：2.10.0
- CUDA：12.6，可用
- TensorRT：10.3.0
- ROS 2节点：`/pencil_tennis_detector`
- 发布话题：`/detection/image`、`/detection/results`、`/detection/fps`
- 图像话题速率：13.369–14.092 FPS，平均13.795 FPS
- 检测 FPS样本：15.421–17.971 FPS，平均16.657 FPS

原始记录和演示视频见 [`results/jetson/2026-08-30/`](../results/jetson/2026-08-30/)。TensorRT Engine 是本次 Jetson 环境生成的部署产物，不保证能在不同 JetPack、TensorRT、CUDA、GPU架构或推理配置中直接复用。

## Jetson 最终验收

- 最终测试轮次：第二次
- 数据来源：仅使用未参与训练和最佳权重选择的 `test` 划分，未使用 `val`
- 随机种子：`20260830`
- 铅笔：20张，正确19张，正确率95.0%
- 网球：20张，正确20张，正确率100.0%
- 总计：40张，正确39张，正确率97.5%
- 平均离线TensorRT模型速度：31.7906 FPS
- 最低离线TensorRT模型速度：30.1659 FPS
- 唯一错误：`pencil_red4.jpg` 漏检

完整记录见 [`results/jetson/2026-08-30/acceptance/`](../results/jetson/2026-08-30/acceptance/)。97.5%是固定40项样本的分类式验收正确率，不是mAP；离线TensorRT速度也不等于摄像头采集、绘制和ROS 2发布的端到端速度。

## 已知限制

- 增强训练集包含317个铅笔目标和387个网球目标，数量基本均衡。
- 两类源数据的背景风格不同。
- 训练数据缺少铅笔和网球同时出现的场景。
- Kaggle 铅笔数据集的公开元数据未声明明确许可证；公开再分发前需确认许可。
- 当前最终验收使用留出测试集静态图片；如果课程现场明确要求摄像头前逐个摆放实体物体，还需按现场要求补做对应形式的记录。
