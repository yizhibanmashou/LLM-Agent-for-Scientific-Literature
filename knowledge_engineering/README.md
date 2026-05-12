# Knowledge Engineering

`knowledge_engineering/` 是教材知识生产线的核心中段，负责把 `paper2latex`
产出的 LaTeX/Paddle raw layout 清洗、融合、切分、标注为 structured JSON。

```text
paper2latex -> tmp/paddle_output -> knowledge_engineering -> data/structured -> core/knowledge_graph -> core/memory
```

## 目录结构

结构按 `paper2latex/src/paper2latex/` 的方式归类，生产逻辑放到明确子包里：

- `core/`
  公共模型、排序/规范化工具、运行时能力。这里不放具体试验管线。
- `pipeline/`
  可执行的主流程编排，包括 structured 生成、可选 Example library 注入、fusion candidate 生成。
- `processors/`
  可复用处理器，包括 Example 抽取、OCR evidence、structured repair、LaTeX overlay repair。
- `reports/`
  审计、diff、质量报告等产物构建逻辑。
- `scripts/`
  trial/CLI 胶水层，只负责参数、候选复制、audit/report/diff，不承载核心抽取规则。

根目录只保留包入口和文档。生产代码使用子包内的 canonical 模块，避免旧路径和新路径并存。

## 主要模块

- `knowledge_engineering.pipeline.process`
  structured 生成主入口，包含 LaTeX 清洗、章节切分、表格/公式库落盘、chunk 输出。
- `knowledge_engineering.pipeline.example_pipeline`
  可选的 Example library 注入、`[[SEE_EXAMPLE:*]]` 处理与 `example_library.json` 生成。
- `knowledge_engineering.pipeline.structured_fusion`
  基于 Paddle raw layout、OCR evidence 和现有 structured 的 fusion candidate 生成。
- `knowledge_engineering.processors.example_extraction`
  Example 抽取、raw layout 恢复、visual stop、sequence gap 检测。
- `knowledge_engineering.processors.structured_repair`
  structured candidate 校验与修复辅助。
- `knowledge_engineering.processors.latex_overlay_repair`
  inline LaTeX overlay 修复，只替换正文或表格里的公式片段。
- `knowledge_engineering.reports.fusion_reporting`
  fusion 审核报告、对比摘要和 artifact 构建。

## 数据边界

`data/structured` 是当前交付基线。实验、候选、缓存、报告和质量对比输出默认写入：

```text
tmp/structured_quality_probe/
```

本模块可以只读参考 `data/structured` 做 ID 集合、内容结构和质量对比。探索性候选默认留在 `tmp/structured_quality_probe/`；有 PDF 渲染、Paddle raw layout 或其他强证据支撑的结构修复，可以直接写回 `data/structured`。

当前主流程可以直接写回 `data/structured`，并在开启 `--structured-fusion` 时同步执行通用后处理。
如果还需要 `example_library.json`，再显式开启 `--example-pipeline`。

## 常用运行方式

```bash
conda run -n py312 python -X utf8 -m knowledge_engineering.pipeline.process -i tmp/paddle_output -o tmp/structured_quality_probe/candidates/fullbook --artifacts-dir tmp/structured_quality_probe/artifacts --skip-llm-cleaning --llm-phase 0
```

inline LaTeX overlay dry-run：

```bash
conda run -n py312 python -X utf8 -m knowledge_engineering.processors.latex_overlay_repair --structured-dir data/structured --source-dir tmp/structured_quality_probe/candidates/fullbook --out tmp/structured_quality_probe/latex_overlay_dryrun
```

## 当前优化重点

这层优先服务 structured 质量：

1. 保留一二级标题与 chunk 的结构位置。
2. 让 Example、table、formula 与正文 chunk 保持可追溯关系。
3. 通过通用规则处理 Paddle raw layout 中的 footer、figure title、paragraph title、跨页续接和 visual stop。
4. 保持 `heading_path`、`display_heading`、`section_level_1`、`section_level_2` 等 metadata 稳定。
5. 探索性候选先进入 `tmp/structured_quality_probe/`，强证据修复可以直接覆盖正式 baseline，并保留 artifacts 便于回查。

## 职责边界

`knowledge_engineering` 的职责是把教材变成高质量结构化知识。它不直接承担教学产品前端、memory 后端实现或最终 agent 决策；它的输出应该稳定、可追溯、可被下游长期复用。
