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
- [ ] 训练与评估模型
- [ ] 部署到 Jetson
- [ ] 实现 ROS 2 结果发布
- [ ] 完成 20 个物体的验收测试
- [ ] 完成 LaTeX 实验报告

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

最佳模型默认保存在 `runs/pencil_tennis_yolo26n/weights/best.pt`。脚本不会在 CUDA 不可用时自动退回 CPU。
