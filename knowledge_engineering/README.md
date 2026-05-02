# Knowledge Engineering

`knowledge_engineering/` 是教材知识生产线的核心中段。

它负责把 `paper2latex` 产出的 `main.tex` 清洗、切分、标注并落成 `data/structured/*.json`。当前目标不是做前端产品，而是让进入 memory 和知识图谱的整本书基座更可靠。

## 在总链路里的位置

```text
paper2latex -> tmp/paddle_output -> knowledge_engineering -> data/structured -> core/knowledge_graph -> core/memory
```

## 当前主要内容

- `process.py`
  结构化处理入口
- `runtime.py`
  运行时支持、LLM 审核和公共数据模型
- `structured_repair.py`
  GLM OCR 辅助的结构化修复候选生成和人工审核流程
- `latex_overlay_repair.py`
  全库 inline LaTeX overlay 修复流程，只替换正文或表格里的公式片段
- `tmp/knowledge_engineering/`
  本模块相关缓存、诊断文件和局部中间产物；正式运行时建议统一写入根目录 `tmp/`

## 最常用的运行方式

```bash
conda run -n py310 python -m knowledge_engineering.process -i tmp/paddle_output/chapter6_full/main.tex -o data/structured --chapter-name chapter6 --artifacts-dir tmp/knowledge_engineering
```

全书 fresh structured 生成示例：

```bash
python -m knowledge_engineering.process -i tmp/paddle_output -o tmp/inline_latex_overlay_fresh_structured --artifacts-dir tmp/inline_latex_overlay_artifacts --skip-llm-cleaning --llm-phase 0
```

inline LaTeX overlay dry-run 示例：

```bash
python -m knowledge_engineering.latex_overlay_repair --structured-dir data/structured --source-dir tmp/inline_latex_overlay_fresh_structured --out tmp/structured_repair/full_inline_latex_overlay_dryrun
```

## 当前优化重点

这层应该优先解决 structured 质量问题：

1. 内联数学符号丢失
2. 占位符残留
3. chunk prose 与公式库/表格库脱节
4. 公式库和表格库的 LaTeX/HTML 层细节噪声
5. 源页、chunk、公式、表格之间的可追溯关系

质量审计脚本会把问题清单写入 `tmp/structured_review/`。这些问题是修复 backlog，不是 memory 入库排除清单。

inline LaTeX 修复的当前规则更严格：不使用 GLM OCR 整段覆盖正文，只从 fresh structured 中取更可靠的 `$...$` 公式片段，且保持正文、占位符、表格行列结构不变。exact overlay 可以自动应用；中低置信项进入 review 或仅报告。

## 职责边界

`knowledge_engineering` 的职责是把教材变成高质量结构化知识。它不直接承担：

- 教学产品前端
- memory 后端实现
- 最终 agent 决策

它的输出应该尽量稳定、可追溯、可被下游长期复用。
