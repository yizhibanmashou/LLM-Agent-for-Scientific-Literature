# LLM-Agent 科学文献系统知识库处理

这个仓库用于把教材/论文 PDF 加工成可检索、可审核、可追溯的结构化知识库。当前重点不是做最终教学产品，而是把原始文献稳定转换成 `data/structured/` 下的章节 chunk、公式库、表格库，并提供 review app 反复抽查质量。

## 项目主线

```text
data/背景资料/*.pdf
  -> paper2latex / Paddle
  -> tmp/paddle_output/*_full/main.tex
  -> knowledge_engineering.process
  -> data/structured/*.json
  -> review_app
  -> 下游 graph / retrieval / memory / agent
```

当前结构化结果以 `paper2latex`/Paddle 产物为主来源。GLM OCR 是辅助参考，不是结构主来源；尤其在 inline LaTeX 修复里，不允许用 GLM OCR 整段替换正文，只能作为低优先级公式片段参考且必须进入人工 review。

## 目录架构

```text
.
├── data/
│   ├── 背景资料/              # 原始 PDF 和参考资料
│   ├── structured/            # 正式结构化知识产物
│   └── knowledge_graph/        # 后续图谱数据位置
├── knowledge_engineering/      # 清洗、切分、修复、落库的核心流程
├── review_app/                 # 本地结构化结果审核工作台
├── paper2latex/                # PDF -> LaTeX 的上游转换模块及其测试
├── glmocr/                     # GLM OCR 调用与批处理脚本
├── tmp/                        # 中间产物、缓存、审计报告、patch，不是源码入口
├── docs/                       # 预留的长文档目录
└── scripts/                    # 预留脚本目录
```

### 目录职责

| 目录 | 职责 | 是否应手工改 |
| --- | --- | --- |
| `data/背景资料/` | 原始 PDF/背景资料 | 通常不改 |
| `data/structured/` | 下游系统读取的正式 JSON 产物 | 只通过脚本/修复流程更新 |
| `knowledge_engineering/` | 主处理流程、结构化修复、overlay repair | 是核心代码 |
| `review_app/` | 审核 chunks/formulas/tables 的本地前端和数据生成器 | 可以改 |
| `paper2latex/` | 上游 PDF 到 LaTeX 工具和相关测试 | 谨慎改 |
| `glmocr/` | GLM OCR 辅助通道 | 谨慎改 |
| `tmp/` | 可复现/可清理的中间产物和缓存 | 不当作源码维护 |

## 关键数据产物

`data/structured/` 是当前最重要的结果目录：

- `chapter*_*.json` / `appendix*_*.json`：按章节切分后的知识单元。
- `formula_library.json`：全书公式库。
- `table_library.json`：全书表格库。

结构化产物要保持这些约束：

- chunk 数量、block 顺序和章节编号可追溯。
- `[[SEE_FORMULA:*]]` / `[[SEE_TABLE:*]]` 等占位符不能被随意删除。
- 表格行列结构不能被修复脚本改坏。
- inline LaTeX 修复只替换 `$...$` 内的公式片段，不替换 `$...$` 外正文。

## 常用流程

### 1. 生成 structured

从 `tmp/paddle_output/*_full/main.tex` 生成结构化 JSON：

```powershell
python -m knowledge_engineering.process `
  -i tmp\paddle_output `
  -o data\structured `
  --artifacts-dir tmp\knowledge_engineering `
  --skip-llm-cleaning `
  --llm-phase 0
```

单章节调试：

```powershell
python -m knowledge_engineering.process `
  -i tmp\paddle_output\chapter6_full\main.tex `
  -o data\structured `
  --chapter-name chapter6 `
  --artifacts-dir tmp\knowledge_engineering
```

### 2. 修复 inline LaTeX overlay

推荐先生成一份 fresh structured 到 `tmp/`，再 dry-run overlay patch：

```powershell
python -m knowledge_engineering.process `
  -i tmp\paddle_output `
  -o tmp\inline_latex_overlay_fresh_structured `
  --artifacts-dir tmp\inline_latex_overlay_artifacts `
  --skip-llm-cleaning `
  --llm-phase 0

python -m knowledge_engineering.latex_overlay_repair `
  --structured-dir data\structured `
  --source-dir tmp\inline_latex_overlay_fresh_structured `
  --out tmp\structured_repair\full_inline_latex_overlay_dryrun
```

确认 patch 安全后只应用 `auto_apply`：

```powershell
python -m knowledge_engineering.latex_overlay_repair `
  --structured-dir data\structured `
  --source-dir tmp\inline_latex_overlay_fresh_structured `
  --out tmp\structured_repair\full_inline_latex_overlay_apply `
  --apply
```

### 3. 刷新 review app 数据

```powershell
python -m review_app.build_review_app
python -m review_app.serve_review_app --port 8000
```

打开：

```text
http://127.0.0.1:8000/review_app/
```

`review_app/source_config.json` 里可以配置默认打开章节，例如当前默认是 `chapter6`。

## tmp 边界

`tmp/` 里有两类内容：

1. 重要但可复现的输入/缓存，例如 `tmp/paddle_output/`、`tmp/glmocr_output/`、`tmp/llm_cache/`。
2. 本地运行生成物，例如 overlay patch、fresh structured、pytest cache、server log。

被 `.gitignore` 忽略的本地生成物可以清理：

```powershell
git clean -fdX tmp data/structured/probe.txt paper2latex
```

不要把 `tmp/` 当作统一源码目录；真正稳定的代码入口在 `knowledge_engineering/`、`review_app/`、`glmocr/`、`paper2latex/`。

## 环境配置

API 密钥和服务地址放在根目录 `.env`，不要提交真实密钥。可以从 `.env.example` 复制：

```powershell
Copy-Item .env.example .env
```

常用变量：

- `ZHIPU_API_KEY`：GLM OCR 调用凭证。
- `GLMOCR_INPUT_DIR` / `GLMOCR_OUTPUT_DIR`：覆盖 GLM OCR 输入输出目录。
- `PAPER2LATEX_PADDLE_API_URL`、`PAPER2LATEX_PADDLE_API_TOKEN`、`PAPER2LATEX_PADDLE_PIPELINE`：Paddle 服务配置。
- `KE_LLM_*`：结构化流程中可选的 LLM 审核配置。
