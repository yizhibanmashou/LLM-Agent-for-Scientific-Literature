# LLM-Agent 科学文献系统知识库处理

把教材 PDF 加工成可追溯的结构化知识库，并导出可阅读的教材 Markdown。当前面向学习与备课的正式前端是 `study_reader/`：左侧阅读章节，右侧展示由 LLM 审查后的前置概念与可跳转来源。

## 项目主线

```text
data/背景资料/*.pdf
  -> paper2latex / Paddle
  -> data/paddle_output/*_full/main.tex
  -> knowledge_engineering.pipeline.process
  -> data/structured/*.json
  -> textbook_exporter
  -> data/textbook/*.md + data/textbook/figures/*.png
  -> study_reader
```

## 目录职责

| 路径 | 职责 |
| --- | --- |
| `data/背景资料/` | 原始 PDF，本地保留，不进 Git |
| `data/paddle_output/` | OCR / LaTeX 中间输出，本地保留 |
| `data/structured/` | 正式结构化 JSON 产物 |
| `data/textbook/` | 从 structured 导出的可读教材 Markdown 与 figures |
| `knowledge_engineering/` | 清洗、切分、修复和融合流程 |
| `textbook_exporter/` | structured -> textbook Markdown |
| `study_reader/` | 双教材章节阅读与前置概念工作台 |
| `tmp/` | 可清理的实验、缓存和审计中间产物 |

## Study Reader

Study Reader 支持两本教材：

- `Evolution and Selection of Quantitative Traits`
- `Genetics and Analysis of Quantitative Traits`

本地构建数据：

```powershell
python study_reader/build_study_reader.py --books Evolution,Genetics --chapters Evolution_chapter28,Genetics_chapter12
```

为两本书全部章节刷新 LLM 前置概念审查：

```powershell
python study_reader/build_study_reader.py --books Evolution,Genetics --all-llm
```

只构建阅读索引、不生成前置概念：

```powershell
python study_reader/build_study_reader.py --books Evolution,Genetics --skip-llm
```

启动本地服务：

```powershell
python study_reader/serve_study_reader.py --port 8000
```

打开：

```text
http://127.0.0.1:8000/study_reader/
```

旧 `/review_app/` 和 `/knowledge_engineering/review_app/` 会重定向到 `/study_reader/`。

## 数据维护

从 structured 重新导出 Markdown：

```powershell
python -m textbook_exporter --structured-dir data/structured --out-dir data/textbook
```

按章节导出：

```powershell
python -m textbook_exporter --structured-dir data/structured --out-dir data/textbook --chapters Evolution_chapter25
```

维护规则：

- `data/textbook/` 应从 `data/structured/` 重建，不手工改大段正文。
- figure 文件名必须和 `data/figure_library.json`、Markdown 引用保持同步。
- `.codegraph/`、`.understand-anything/`、`tmp/`、`data/背景资料/`、`data/paddle_output/` 都是本地工作区内容，不进入 Git。
