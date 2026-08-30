# Jetson 验收测试记录（2026-08-30）

## 最终结论

最终验收采用第二次测试结果。测试在 Jetson Orin 上使用正式 TensorRT Engine，对未参与训练和最佳权重选择的 `test` 划分进行离线检测；`val` 划分未参与选样。

| 测试 | 铅笔 | 网球 | 合计 | 正确 | 正确率 | 结论 |
|---|---:|---:|---:|---:|---:|---|
| 第一次（初步） | 10 | 10 | 20 | 19 | 95.0% | 通过 |
| 第二次（最终） | 20 | 20 | 40 | 39 | 97.5% | 通过 |

第二次测试才是最终验收：铅笔20张、网球20张，共40张。40个图片名和全局GT对象编号均不重复，测试编号连续为1–40。所有入选图片都只含一个GT对象，固定随机种子为 `20260830`，置信度阈值为0.25。

## 第二次测试逐类结果

| 类别 | 测试数 | 正确数 | 正确率 |
|---|---:|---:|---:|
| `pencil` | 20 | 19 | 95.0% |
| `tennis_ball` | 20 | 20 | 100.0% |
| 总计 | 40 | 39 | 97.5% |

总正确率高于课程要求的80%。这是留出测试集静态图片的板端离线验收，不应与摄像头端到端FPS或完整测试集mAP混为同一指标。

## 唯一错误案例

- 测试编号：3
- 图片：`pencil_red4.jpg`
- 预期类别：`pencil`
- 预测类别：`none`
- 检测数量：0
- 判定：漏检，按错误计分

错误样本完整保留在 [`attempt_02/errors/`](attempt_02/errors/)，没有删除、替换或重新抽样。

## 速度

第二次测试的静态图片预处理、TensorRT推理及后处理速度如下：

| 指标 | 数值 |
|---|---:|
| 平均离线模型速度 | 31.7906 FPS |
| 最低离线模型速度 | 30.1659 FPS |
| 课程最低要求 | 5 FPS |

离线模型速度高于5 FPS，但其计时口径不含摄像头采集和ROS 2发布。摄像头端到端部署证据见上级目录的 [`deployment_evidence.txt`](../deployment_evidence.txt)：图像话题速率最低13.369 FPS，节点发布的检测速度最低15.421 FPS。

## 完整测试集补充评估

同一批资料还包含对完整留出测试集的板端官方评估：119张图片、150个GT实例，总体 Precision 0.988、Recall 0.902、mAP@0.5 0.966、mAP@0.5:0.95 0.856。原始指标、曲线、混淆矩阵和预测JSON见 [`official_test/`](official_test/)。

这组板端评估指标与项目原有Windows独立测试结果属于不同运行环境和Ultralytics版本，应分别保留，不能相互覆盖。

## 模型与环境

- 设备：NVIDIA Jetson Orin NX Engineering Reference Developer Kit
- Jetson Linux：R36.4.3，aarch64
- Python：3.10.12
- PyTorch：2.10.0
- CUDA：12.6，可用
- TensorRT：10.3.0
- Ultralytics：8.4.135
- ROS 2：Humble
- 验收模型：`models/pencil_tennis_yolo26n_best.engine`
- Engine SHA-256：`BBFFFC6D678DDF8627B58BE11D50A2F67FED4D430DC387680D085712713DC0E3`

详细原始记录见 [`environment/`](environment/) 和 [`models/model_hashes.txt`](models/model_hashes.txt)。

## 证据目录

- [`attempt_01/`](attempt_01/)：第一次10张铅笔、10张网球的初步测试。
- [`attempt_02/`](attempt_02/)：第二次20张铅笔、20张网球的最终验收。
- [`environment/`](environment/)：Jetson、CUDA、TensorRT、ROS 2和摄像头环境。
- [`git/`](git/)：验收运行时的仓库快照信息。
- [`logs/`](logs/)：构建、检测、两次验收和完整测试集日志。
- [`models/`](models/)：模型大小与SHA-256。
- [`official_test/`](official_test/)：完整测试集官方评估产物。
- [`scripts/`](scripts/)：本次验收使用的脚本和绝对路径配置，仅作为复现实录。
- [`SHA256SUMS.txt`](SHA256SUMS.txt)：整理后全部证据文件的完整性校验。

`scripts/yolo_test_absolute.yaml` 含本次Jetson临时工作目录的绝对路径，不能直接作为其他电脑的通用配置。

## Git与视频来源

验收包生成时的仓库快照为 `c21880ce8b9207d4c22af1234b4cc0d29c391f8d`，当时本地 `main` 与 `origin/main` 一致。上级目录复用的ROS 2部署证据是在更早的板端提交 `f95c2e9` 上采集的；该代码树后来以规范提交 `2e15f0d` 保留。两个提交分别描述验收快照和早期ROS 2采集现场，不是同一个时间点。

验收包内视频与上级目录的 [`jetson_demo.mp4`](../jetson_demo.mp4) SHA-256同为 `8D004988EB5021C3C0BEACEDF09E17637402166DB50598898170D7E3178BA28C`，因此没有重复提交。

原始压缩包及其外层SHA-256文件保存在本地 `backups/jetson/2026-08-30/acceptance-package/`，该备份目录按项目规则不提交Git。原压缩包SHA-256为 `FC6CA114C25A4F99628EC69BA283E2FA49F0315E41424E1643031349621ED858`。
