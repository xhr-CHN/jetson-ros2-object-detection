# Windows YOLO26n 训练脚本设计

日期：2026-08-24

## 目标

为本项目提供一个仅面向当前 Windows 电脑的、可复现的 YOLO26n 目标检测训练入口，替代易出错的超长 PowerShell 命令。脚本同时支持短时冒烟训练和100轮正式训练。

## 运行环境

- 项目目录：`E:\机器人集成小组项目`
- Python：`D:\视觉识别一硝3\.venv\Scripts\python.exe`
- Ultralytics：复用上述虚拟环境中已经安装的版本
- GPU：NVIDIA GeForce RTX 4060 Laptop GPU
- 预训练权重：`D:\视觉识别一硝3\yolo26n.pt`
- 数据配置：`E:\机器人集成小组项目\dataset\data-windows.yaml`

## 文件与接口

新增 `src/train_yolo26n_windows.py`。

正式训练：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py
```

冒烟训练：

```powershell
& "D:\视觉识别一硝3\.venv\Scripts\python.exe" src\train_yolo26n_windows.py --smoke
```

脚本允许用命令行参数临时覆盖 `epochs` 和 `batch`，但其余路径及核心参数保持为当前电脑的明确默认值。

## 默认训练参数

| 参数 | 正式训练 | 冒烟训练 |
|---|---:|---:|
| model | `D:\视觉识别一硝3\yolo26n.pt` | 相同 |
| data | `E:\机器人集成小组项目\dataset\data-windows.yaml` | 相同 |
| epochs | 100 | 3 |
| imgsz | 640 | 640 |
| batch | 8 | 8 |
| device | 0 | 0 |
| workers | 0 | 0 |
| patience | 20 | 20 |
| plots | true | true |
| save | true | true |

正式训练输出名称为 `pencil_tennis_yolo26n`，冒烟训练输出名称为 `yolo26n_smoke`；输出根目录为项目下的 `runs`。

## 启动检查与错误处理

脚本在加载模型前检查：

1. 预训练权重文件存在；
2. Windows 数据配置文件存在；
3. PyTorch 能识别 CUDA；
4. 至少存在一个 CUDA 设备。

任一检查失败时，脚本以非零状态退出并给出明确错误。脚本不得自动退回 CPU，以免用户误以为正在进行 GPU 训练。

## 文档

README 增加“Windows 本地训练”小节，说明复用旧 `.venv` 的原因、正式训练和冒烟训练命令、结果目录以及显存不足时使用 `--batch 4` 的方法。

## 验证标准

- `python src/train_yolo26n_windows.py --help` 正常输出帮助信息；
- 脚本通过 Python 语法编译检查；
- 用模拟方式验证正式模式和冒烟模式产生预期参数，且不启动耗时训练；
- Git 仅包含设计文档、训练脚本、Windows 数据配置和 README 的相关改动；
- 完成后建立独立 commit 并推送 GitHub。

## 非目标

- 不兼容 Linux 服务器路径；
- 不创建或修复 Python 虚拟环境；
- 不自动安装依赖；
- 不自动开始100轮训练；
- 不修改原始数据集和标签。
