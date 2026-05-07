# 08 Candidate Optimization Manifest

本报告记录候选优化版的确定性改动。候选版只写入 tmp，不覆盖 `data/structured`。

## 输出位置

| item | path |
| --- | --- |
| candidate_structured_dir | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured |
| change_manifest | tmp/structured_quality_probe/candidates/current_plus_p0p1/change_manifest.json |
| changes_jsonl | tmp/structured_quality_probe/candidates/current_plus_p0p1/changes.jsonl |
| block_index_mapping_jsonl | tmp/structured_quality_probe/candidates/current_plus_p0p1/block_index_mapping.jsonl |
| manual_review_queue_jsonl | tmp/structured_quality_probe/candidates/current_plus_p0p1/manual_review_queue.jsonl |

## 自动改动概览

| metric | value |
| --- | --- |
| copied_structured_files | 1007 |
| removed_blocks | 249 |
| added_table_entries | 6 |
| manual_queue_items | 35 |

## 删除的确定性噪声 block

| reason | count |
| --- | --- |
| ghost_block | 7 |
| h_only_block | 242 |

## 旧库证据补入的表格

| table_id | occurrences | ocr_evidence | old_table_title |
| --- | --- | --- | --- |
| 8.1 | 4 | 12 | Table 8.1 Summary of expressions for f_s and population-genetic impacts of a hard sweep on a linked neutral site. |
| 10.2 | 1 | 2 | Table 10.2 Parameters of adaptive evolution and connections among alpha, gamma, omega, f, p0, and pb. |
| 18.7 | 2 | 4 | Table 18.7 Coefficients for pure-drift variances and covariances in response. |
| 18.8 | 2 | 4 | Table 18.8 Coefficients of variation for selection-experiment designs under the pure-drift approximation. |
| 20.1 | 1 | 2 | Table 20.1 Design issues for applying animal-model and selection-response methods to natural populations. |
| 21.3 | 5 | 10 | Table 21.3 Summary of covariances between the selection unit and one parent from the recombination unit. |

## manual queue 类型预览

| queue_type | preview_count |
| --- | --- |
| table_reference_missing | 3 |
| manual_review_issue | 32 |

## 边界

- 没有修改 `data/structured`。
- 没有把 PaddleOCR 或 GLM-OCR 当作 ground truth；它们只用于判断旧版表格是否有文本证据。
- 不确定的数学、截断、derivation 和无法证据补表的问题全部进入 manual queue。
