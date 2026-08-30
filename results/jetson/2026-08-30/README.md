# Jetson 部署验证结果（2026-08-30）

## 结论

铅笔与网球 YOLO26n 检测项目已经在 Jetson Orin 上完成部署，CUDA、TensorRT、ROS 2检测节点和三个检测话题均正常。记录到的图像话题速率和检测 FPS均高于课程要求的5 FPS。

独立验收也已经完成。第一次10+10项测试作为初步记录保留；第二次才是最终验收，使用铅笔20张、网球20张，共40张互不重复的留出测试图片，正确39张，总正确率97.5%，超过80%的要求。

## 环境

| 项目 | 记录值 |
|---|---|
| 设备 | Jetson Orin，aarch64 |
| Jetson Linux | R36.4.3 |
| PyTorch | 2.10.0 |
| CUDA | 12.6，可用 |
| TensorRT | 10.3.0 |
| ROS 2节点 | `/pencil_tennis_detector` |

## 部署模型

| 文件 | 大小 | SHA256 |
|---|---:|---|
| `pencil_tennis_yolo26n_best.pt` | 5,415,023 bytes | `DA747F4ED471BE2A4BEF0E858B3DE5CE8FF133A1FF5459CEB2B1577093A4063D` |
| `pencil_tennis_yolo26n_best.onnx` | 9,761,287 bytes | `4616C124B10E4B2C65CE9680E14E3FE41B1170F2F4E1CAD33FD79C68CE4C2401` |
| `pencil_tennis_yolo26n_best.engine` | 7,863,922 bytes | `BBFFFC6D678DDF8627B58BE11D50A2F67FED4D430DC387680D085712713DC0E3` |

TensorRT Engine 是在本次 Jetson 环境中生成的部署产物。JetPack、TensorRT、CUDA、GPU架构或推理设置改变时，应从 PT 或 ONNX 重新生成，不应假设 Engine 可跨环境复用。

## ROS 2接口

- `/detection/image`：带检测框、类别、置信度和 FPS的图像。
- `/detection/results`：每帧结构化检测结果 JSON。
- `/detection/fps`：检测 FPS。

## 速度记录

| 指标 | 样本数 | 最低 | 平均 | 最高 |
|---|---:|---:|---:|---:|
| `/detection/image` 话题速率 | 5 | 13.369 FPS | 13.795 FPS | 14.092 FPS |
| `/detection/fps` 数据 | 46 | 15.421 FPS | 16.657 FPS | 17.971 FPS |

两种记录口径均高于5 FPS。图像话题速率更接近包含采集、推理、绘制和发布的实际输出吞吐量；`/detection/fps` 是节点发布的检测速度数据。

## 检测样例

原始记录包含一个明确样例：类别 `tennis_ball`，类别编号1，置信度0.958984375，输入图像大小640 × 480。

## 最终验收

| 项目 | 结果 |
|---|---:|
| 最终测试轮次 | 第二次 |
| 铅笔 | 20张，正确19张，95.0% |
| 网球 | 20张，正确20张，100.0% |
| 总计 | 40张，正确39张，97.5% |
| 最低离线TensorRT速度 | 30.1659 FPS |
| 结论 | 通过 |

唯一错误是 `pencil_red4.jpg` 漏检，模型没有给出高于0.25阈值的检测结果。错误样本未被删除、替换或重新抽样。完整CSV、JSON、40张标注结果图、环境、日志和校验文件见 [`acceptance/README.md`](acceptance/README.md)。

该验收在Jetson上对留出测试集静态图片运行，`val`划分未参与选样；它与现场摄像头逐个摆放实物的测试形式不同。摄像头部署和ROS 2实时速度由本目录的部署证据及最终视频单独证明。

## 文件

- [`deployment_evidence.txt`](deployment_evidence.txt)：从 Jetson 导出的原始系统、模型、ROS 2和速度记录。
- [`jetson_demo.mp4`](jetson_demo.mp4)：最终板端演示视频，29.76秒，1306 × 992，H.264 Main、`yuv420p`、约16 FPS，包含 AAC双声道音频。第8秒与第20秒的抽检画面均同时显示铅笔和网球检测，画面实时速度为16.9–17.2 FPS。SHA256：`8D004988EB5021C3C0BEACEDF09E17637402166DB50598898170D7E3178BA28C`。
- [`acceptance/`](acceptance/)：两次板端离线验收记录，其中第二次20+20项为最终结果。

最终视频已经完成全片音视频解码检查，没有重新转码。此前分别展示铅笔和网球的 `jetson_demo_01.mp4`、`jetson_demo_02.mp4` 已移入本地 `backups/` 目录，并可从早期 Git提交恢复；它们不再出现在当前 GitHub 文件列表中。原始 WebM 同样按原哈希保存在本地备份中。

原始证据是在旧提交 `f95c2e9` 上采集的。该提交仅因作者身份和提交消息不规范，被代码树完全相同的规范提交 `2e15f0d` 替代；检测代码内容未发生变化。

最终验收包生成时的仓库快照为 `c21880c`，与上述早期ROS 2部署证据的采集提交不是同一个时间点，二者分别保留。
