# 05 Sampling Plan

本报告固定 baseline 后的人工抽样 ID。抽样只读取 structured 和已有审计报告，不修改任何原始数据。

## 抽样数量

| stratum | target | actual |
| --- | --- | --- |
| discussion_normal | 30 | 30 |
| derivation | 30 | 30 |
| proposition_definition | 20 | 20 |
| fatal_error | 30 | 30 |
| warning | 20 | 20 |
| ocr_disagreement_chapter | 20 | 20 |

## 输出文件

| 文件 | 用途 |
| --- | --- |
| samples/manual_sample_ids.jsonl | 固定抽样 ID，每行一个样本。 |
| samples/manual_sample_ids.json | 同一抽样清单的 JSON 数组版。 |
| samples/manual_sample_annotation_template.csv | 人工标注模板，UTF-8 BOM，Excel 可直接打开。 |
| cache/baseline_manifest.json | baseline 报告哈希和核心指标。 |
| cache/baseline/ | baseline 报告副本。 |

## 标注口径

- `manual_is_acceptable`：该 block 是否可用于下游知识库。
- `manual_content_accuracy`：正文语义是否正确，可填 `correct / minor_issue / major_issue / unusable`。
- `manual_structure_accuracy`：block 类型、切分、上下文是否合理。
- `manual_formula_table_accuracy`：公式/表格引用和表达是否可接受。
- `manual_issue_type` 和 `manual_notes`：人工发现的问题类别与说明。
