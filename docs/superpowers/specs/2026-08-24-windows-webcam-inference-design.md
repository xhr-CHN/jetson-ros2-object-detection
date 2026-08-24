# Windows 摄像头 YOLO26n 实时检测设计

日期：2026-08-24

## 目标

在当前 Windows 电脑上使用已训练的 YOLO26n 模型进行摄像头实时检测，只显示检测画面，不录像、不保存图片、不生成结果目录。

## 输入与环境

- Python：`D:\视觉识别一硝3\.venv\Scripts\python.exe`
- 模型：`E:\机器人集成小组项目\models\pencil_tennis_yolo26n_best.pt`
- GPU：NVIDIA GeForce RTX 4060 Laptop GPU
- 默认摄像头编号：0
- 默认置信度阈值：0.25
- 输入尺寸：640
- 类别：`pencil`、`tennis_ball`

## 脚本接口

新增 `src/webcam_yolo26n_windows.py`。

默认运行：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\webcam_yolo26n_windows.py
```

切换摄像头或置信度阈值：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\webcam_yolo26n_windows.py --camera 1 --conf 0.4
```

## 运行行为

1. 检查模型文件存在；
2. 检查 CUDA 与 GPU 可用，不允许自动回退 CPU；
3. 使用 OpenCV 打开指定摄像头；
4. 逐帧调用 YOLO26n 推理；
5. 显示检测框、类别、置信度和实时 FPS；
6. 按 `Q`、`q` 或 `Esc` 退出；
7. 无论正常退出或发生异常，均释放摄像头并关闭窗口。

FPS 使用连续帧处理耗时计算，并采用轻量指数平滑减少跳动。窗口标题为 `YOLO26n Pencil and Tennis Ball Detection`。

## 错误处理

- 模型不存在时明确报错并退出；
- CUDA 不可用时明确报错并退出；
- 摄像头编号无效或无法打开时明确报错并退出；
- 摄像头连续读取失败时退出并释放资源；
- `--conf` 必须位于0到1之间，摄像头编号不得为负数。

## 验证标准

- 脚本通过 Python 语法编译；
- `--help` 正常输出；
- 参数边界检查正常；
- 不自动启动或访问摄像头；
- 源码中不包含视频写入、图片保存或 Git 同步行为。

## 非目标

- 不录像；
- 不保存截图；
- 不发布 ROS 2 消息；
- 不进行 Jetson 部署；
- 不在本阶段提交或推送 GitHub。
