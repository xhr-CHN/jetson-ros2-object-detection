# Windows YOLO26n 测试集评估设计

日期：2026-08-24

## 目标

为已训练的铅笔与网球 YOLO26n 模型提供一个仅面向当前 Windows 电脑的可复现评估入口。在未参与训练和最佳权重选择的 `test` 数据集上计算检测指标，并保存带框预测结果供实验报告和错误分析使用。

## 输入

- Python：`D:\视觉识别一硝3\.venv\Scripts\python.exe`
- 模型：`E:\机器人集成小组项目\models\pencil_tennis_yolo26n_best.pt`
- 数据配置：`E:\机器人集成小组项目\dataset\data-windows.yaml`
- 测试图片：`E:\机器人集成小组项目\dataset\images\test`
- 类别：`0=pencil`、`1=tennis_ball`

## 评估脚本

新增 `src/evaluate_yolo26n_windows.py`，运行方式：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\evaluate_yolo26n_windows.py
```

脚本执行以下步骤：

1. 检查模型、数据配置与测试图片目录存在；
2. 检查 CUDA 可用且至少存在一个 GPU，不允许自动回退 CPU；
3. 使用 `split=test`、`imgsz=640`、`batch=8`、`device=0`、`workers=0` 运行验证；
4. 收集总体 Precision、Recall、mAP@0.5 和 mAP@0.5:0.95；
5. 收集 `pencil` 和 `tennis_ball` 的逐类指标；
6. 将指标写入 `results/test/yolo26n/metrics.json`；
7. 对测试图片运行预测并保存带框图片及含置信度的 YOLO 文本结果。

## 输出

```text
results/test/yolo26n/
├── metrics.json
├── validation/       Ultralytics 测试集验证图表和混淆矩阵
└── predictions/      带框测试图片及 labels/*.txt
```

`metrics.json` 至少包含：模型路径、数据配置、测试图片数量、GPU名称、总体指标、逐类指标以及评估参数。

## 错误处理

- 输入文件或目录缺失时，以明确错误退出；
- 测试集没有图片时退出；
- CUDA 不可用时退出，不自动使用 CPU；
- 模型类别与数据配置不一致时由 Ultralytics 错误中止，不生成伪造结果；
- 仅在评估成功后写入 `metrics.json`。

## 文档与版本控制

README 增加测试集评估命令和输出说明。评估脚本、指标 JSON、验证图表和部分必要预测结果纳入 Git；缓存和可再生成的中间文件继续忽略。评估完成后创建独立 commit 并推送 GitHub。

## 验证标准

- 脚本通过 Python 语法编译检查；
- `--help` 正常输出；
- 启动检查能识别 RTX 4060、模型、配置和83张测试图片；
- 评估成功后 `metrics.json` 包含总体及两个类别的指标；
- 预测图片数量与测试图片数量一致；
- Git 工作区不包含训练缓存、`last.pt` 或无关文件。

## 非目标

- 不测试摄像头；
- 不进行20个课堂实物的人工验收；
- 不重新训练或修改权重；
- 不导出 ONNX 或 TensorRT；
- 不处理 Jetson 部署。
