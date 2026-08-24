# Pencil and Tennis Ball YOLO26n

## 模型概况

- 任务：目标检测
- 架构：YOLO26n
- 类别：`0=pencil`、`1=tennis_ball`
- 输入尺寸：640 × 640
- 预训练：是
- 最佳轮次：第87轮
- 权重：[`pencil_tennis_yolo26n_best.pt`](pencil_tennis_yolo26n_best.pt)

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

这些指标来自验证集，不等同于课程要求的独立20个物体验收结果。模型仍需在测试集、实际摄像头场景和 Jetson 上分别验证准确率与速度。

## 文件校验

```text
SHA256  DA747F4ED471BE2A4BEF0E858B3DE5CE8FF133A1FF5459CEB2B1577093A4063D
File    pencil_tennis_yolo26n_best.pt
Size    5,415,023 bytes
```

## 已知限制

- 增强训练集包含317个铅笔目标和387个网球目标，数量基本均衡。
- 两类源数据的背景风格不同。
- 训练数据缺少铅笔和网球同时出现的场景。
- Kaggle 铅笔数据集的公开元数据未声明明确许可证；公开再分发前需确认许可。
- 尚未完成 Jetson TensorRT 推理速度测试。
