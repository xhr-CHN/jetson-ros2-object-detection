# LaTeX 实验报告

最终报告采用 XeLaTeX/Tectonic 编译，版式为 A4 单栏课程实验报告：正文小四号宋体，英文和数字使用 Times New Roman，标题使用黑体，全部表格使用 `booktabs` 三线表。表格、曲线、流程图和 GitHub 截图使用黑白样式；真实检测照片、验收样例和 Jetson 视频帧保留原始彩色与原始宽高比。

## 文件

- `main.tex`：报告正文及自定义模板。
- `references.bib`：引用来源清单（正文使用内置参考文献表，便于单文件编译）。
- `figures/`：由项目真实训练、测试、Jetson 和 GitHub 记录整理的证据图。
- `prepare_report_assets.py`：按“数据图黑白、真实照片彩色”的规则重建报告图片。
- `experiment1_object_detection_report.pdf`：最终编译并逐页检查的 PDF。

## 编译

在安装 XeLaTeX 的环境中运行：

```bash
xelatex main.tex
xelatex main.tex
```

也可使用 Tectonic：

```bash
tectonic main.tex
tectonic main.tex
```

姓名、学号和班级目前按要求保留为空白，可在 `main.tex` 封面字段中填写后重新编译。

最终PDF使用Windows宋体、黑体和Times New Roman。为避免分发系统字体，`report/fonts/`不提交Git；本地编译时可把 `simsun.ttc`、`simhei.ttf`、`times.ttf`、`timesbd.ttf`、`timesi.ttf`、`timesbi.ttf` 放入该目录。未找到这些字体文件时，源码自动退回Fandol中文字体和TeX Gyre Termes。
