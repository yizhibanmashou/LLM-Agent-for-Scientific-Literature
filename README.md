# LLM-Agent 科学文献系统知识库处理

把教材/论文 PDF 加工成可检索、可审核、可追溯的结构化知识库。核心产物是 `data/structured/` 下的章节 chunk、公式库、表格库，以及从结构化结果导出的 `data/textbook/` 可读教材 Markdown；配套的 review app 用于质量审核。

## 项目主线

```text
data/背景资料/*.pdf
  -> paper2latex / Paddle
  -> tmp/paddle_output/*_full/main.tex
  -> knowledge_engineering.pipeline.process
  -> data/structured/*.json              # 基础结构化产物
  -> structured_fusion                   # 通用后处理（去噪、补表、引用归一）
  -> textbook_exporter                   # 可读教材 Markdown 导出
  -> review_app                          # 人工质量审核
  -> 下游 graph / retrieval / memory / agent
```

- **主来源**：`paper2latex`/Paddle 产出的 LaTeX。
- **GLM OCR**：辅助参考，不作为结构主来源。仅在 `--fusion-enable-glm-prose-repair` 开启时用于高置信度 prose 修复，默认关闭。
- **structured_fusion**：通用后处理层，不依赖章节特例，对后续扫描书同样可复用。
- **example_pipeline**：可选的示例库注入与 `[[SEE_EXAMPLE:*]]` 折叠步骤，只有在需要生成 `example_library.json` 时才开启。

## 目录架构

```text
.
├── data/
│   ├── 背景资料/              # 原始 PDF 和参考资料
│   ├── structured/            # 正式结构化知识产物
│   ├── textbook/              # 从 structured 导出的可读教材 Markdown
│   └── knowledge_graph/        # 后续图谱数据位置
├── textbook_exporter/          # structured -> textbook Markdown 独立导出器
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
| `data/textbook/` | 从 structured 导出的可读教材 Markdown | 通过 `textbook_exporter` 重建 |
| `knowledge_engineering/` | 主处理流程、结构化修复、fusion 后处理 | 是核心代码 |
| `textbook_exporter/` | 将结构化 chunk/公式/表格/example 展开为教材 Markdown | 是核心代码 |
| `review_app/` | 审核 chunks/formulas/tables 的本地前端和数据生成器 | 可以改 |
| `paper2latex/` | 上游 PDF 到 LaTeX 工具和相关测试 | 谨慎改 |
| `glmocr/` | GLM OCR 辅助通道 | 谨慎改 |
| `tmp/` | 可复现/可清理的中间产物和缓存 | 不当作源码维护 |

### 核心模块

| 文件 | 职责 |
| --- | --- |
| `knowledge_engineering/pipeline/process.py` | 主入口：解析 LaTeX、清洗噪声、切分章节、构建公式/表格库，并可选接入 fusion / example pipeline |
| `knowledge_engineering/pipeline/structured_fusion.py` | 通用后处理：去噪、补表、引用归一、OCR 表格绑定审计、公式 LaTeX 规范化 |
| `knowledge_engineering/pipeline/example_pipeline.py` | 可选的 Example library 注入、占位符折叠与 `example_library.json` 生成 |
| `knowledge_engineering/processors/ocr_evidence.py` | Paddle raw layout / GLM OCR 跨通道证据索引，用于表格绑定与修复候选 |
| `knowledge_engineering/processors/structured_repair.py` | 底层工具：GLM 审计、候选修复构建、排序去重 |
| `textbook_exporter/exporter.py` | 从 `data/structured` 导出 `data/textbook/chapterX_textbook.md` |
| `review_app/build_review_app.py` | 审核数据生成器，支持 `--chapters` 按章节过滤 |

## 关键数据产物

`data/structured/` 是当前最重要的结果目录：

- `chapter*_*.json` / `appendix*_*.json`：按章节切分后的知识单元（987 个）。
- `formula_library.json`：全书公式库（2248 条）。
- `table_library.json`：全书表格库（164 条）。
- `example_library.json`：全书示例库（322 条），只有在 example pipeline 开启时才会生成。

`data/textbook/` 是面向阅读和人工核查的 Markdown 产物：

- `chapterX_textbook.md`：按 chunk 顺序串接正文，并展开公式、表格、example 占位符。
- `[[TABLE:*]]` 展开表格本体，`[[SEE_TABLE:*]]` 保持短引用文本。
- inline table 使用章节内优先匹配，避免跨章节 `inline_1` / `inline_2` 混淆。

当前基线状态：structured / textbook 占位符与引用审查为 0 个已知阻断问题；全书导出 36 个 `chapter*_textbook.md` / `appendix*_textbook.md` 文件。

结构化产物要保持这些约束：

- chunk 数量、block 顺序和章节编号可追溯。
- `[[SEE_FORMULA:*]]` / `[[SEE_TABLE:*]]` 等占位符不能被随意删除。
- 表格行列结构不能被修复脚本改坏。
- inline LaTeX 修复只替换 `$...$` 内的公式片段，不替换 `$...$` 外正文。

## 常用流程

### 1. 生成 structured（含 fusion 后处理）

从 `tmp/paddle_output/*_full/main.tex` 生成结构化 JSON 并自动跑 fusion：

```powershell
python -m knowledge_engineering.pipeline.process `
  -i tmp\paddle_output `
  -o data\structured `
  --artifacts-dir tmp\knowledge_engineering `
  --skip-llm-cleaning `
  --llm-phase 0 `
  --structured-fusion `
  --glmocr-dir tmp\glmocr_output `
  --reference-structured-dir tmp\structured_quality_probe\old_structured
```

单章节调试：

```powershell
python -m knowledge_engineering.pipeline.process `
  -i tmp\paddle_output\chapter6_full\main.tex `
  -o data\structured `
  --chapter-name chapter6 `
  --artifacts-dir tmp\knowledge_engineering
```

如果还需要生成 `example_library.json`，再显式加上 `--example-pipeline`。

### 2. 单独跑 fusion（对比/调试用）

不走主流程，直接对已有 structured 目录做 fusion 后处理：

```powershell
python -m knowledge_engineering.pipeline.structured_fusion `
  --structured-dir data/structured `
  --out tmp/fusion_test/structured `
  --glmocr-dir tmp/glmocr_output `
  --paddle-output-dir tmp/paddle_output `
  --reference-structured-dir tmp/structured_quality_probe/old_structured `
  --artifacts-dir tmp/fusion_test/artifacts
```

### 3. 导出 textbook Markdown

从当前 `data/structured` 生成正式可读教材 Markdown：

```powershell
python -m textbook_exporter --structured-dir data/structured --out-dir data/textbook
```

按章节导出：

```powershell
python -m textbook_exporter --structured-dir data/structured --out-dir data/textbook --chapters chapter25
```

### 4. 刷新 review app 数据

全章节审核：

```powershell
python review_app/build_review_app.py --structured-dir data/structured
python review_app/serve_review_app.py --port 8000
```

按章节审核：

```powershell
python review_app/build_review_app.py --structured-dir data/structured --chapters chapter5,chapter13
python review_app/serve_review_app.py --port 8000
```

打开：

```text
http://127.0.0.1:8000/review_app/
```

## LLM 全流程耗时估算

全书当前规模：

- PDF 输入：37 个 PDF，约 1318 页。
- structured baseline：987 个 unit。
- textbook 输出：36 个 Markdown 文件。

在 DeepSeek `deepseek-v4-flash`、`KE_LLM_REVIEW_WORKERS=16`、缓存未命中的条件下，开启 LLM phase 3、structured fusion、GLM prose repair、OCR table repair 和 example pipeline 后，全书 structured 处理预计约 65 分钟，token 用量预计约 8.07M。`textbook_exporter` 相比 LLM review 很快，通常可以视为秒级到分钟内的尾部步骤。

并发 16 不是理论极限，只是当前实测中表现稳定的并发点。DeepSeek 实际不限并发，可以继续试 24、32 或更高；是否继续接近线性提速取决于远程限流、网络稳定性、失败重试和本地写入开销。

## tmp 边界

`tmp/` 里有两类内容：

1. **重要输入**：`tmp/paddle_output/`（Paddle LaTeX 源）、`tmp/glmocr_output/`（GLM OCR 输出）。不要删除。
2. **中间产物**：`tmp/structured_quality_probe/`（审计报告、candidates、old_structured 参考）、`tmp/knowledge_engineering/`（流程 artifacts）。这些目录可重跑，经验沉淀到本地 docs 后可以清理。

不要把 `tmp/` 当作统一源码目录；真正稳定的代码入口在 `knowledge_engineering/`、`review_app/`、`glmocr/`、`paper2latex/`。

这些条目虽然也在 `tmp/` 下，但属于上游输入或轻量文字记录，上传前建议先保留：

- `tmp/paddle_output`
- `tmp/glmocr_output`
- `tmp/structured_quality_probe/*.md`

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
