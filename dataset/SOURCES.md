# 数据集来源与处理说明

访问日期：2026-08-24

## 网球数据集

- 名称：Object Detection - Tennis Ball
- 作者：Karan Jagtiani
- 平台：Mendeley Data
- 版本：Version 2（2021-12-22）
- DOI：[10.17632/ppr8rdw98w.2](https://doi.org/10.17632/ppr8rdw98w.2)
- 来源：[https://data.mendeley.com/datasets/ppr8rdw98w/2](https://data.mendeley.com/datasets/ppr8rdw98w/2)
- 许可证：[Creative Commons Attribution 4.0 International（CC BY 4.0）](https://creativecommons.org/licenses/by/4.0/)
- 原始内容：150张不同摄像机、光照、距离、角度和背景下的网球图片，使用 LabelImg 标注。
- 本项目处理：检查图片与标签配对，删除1张内容完全重复的图片，将原类别 `0` 映射为项目类别 `1=tennis_ball`，使用固定随机种子划分训练集、验证集和测试集。

引用建议：

> Jagtiani, K. (2021). Object Detection - Tennis Ball (Version 2) [Dataset]. Mendeley Data. https://doi.org/10.17632/ppr8rdw98w.2

## 铅笔数据集

- 名称：Pencil Dataset
- 作者：Farukcan Saglam（Kaggle 用户名：`greysky`）
- 平台：Kaggle
- 来源：[https://www.kaggle.com/datasets/greysky/pencil-dataset](https://www.kaggle.com/datasets/greysky/pencil-dataset)
- 页面最后更新时间：2023-04-22
- 许可证：Kaggle 公开元数据标记为 `Unknown`，未发现明确的再分发许可证。
- 原始内容：300张铅笔图片，分为训练、验证和测试目录，使用 JSON 边界框标注。
- 本项目处理：将 `green_pencil`、`red_pencil` 等原始类别统一为项目类别 `0=pencil`；将 JSON 中的 COCO 风格边界框 `[x, y, width, height]` 转换为归一化 YOLO 格式，并保留原有训练/验证/测试划分。

> 注意：许可证未知不等于允许任意再分发。当前数据仅用于本课程实验；将仓库改为公开或将数据用于其他用途前，应向数据集作者确认许可，或只公开转换脚本和来源说明而不公开铅笔图片。

## 整理后数据

类别映射：

```text
0: pencil
1: tennis_ball
```

| 数据集 | 图片数 | 铅笔目标数 | 网球目标数 |
|---|---:|---:|---:|
| train | 284 | 240 | 104 |
| val | 82 | 80 | 22 |
| test | 83 | 80 | 23 |
| 合计 | 449 | 400 | 149 |

转换脚本位于 [`tools/prepare_yolo_dataset.py`](../tools/prepare_yolo_dataset.py)，数据配置位于 [`dataset/data.yaml`](data.yaml)。
