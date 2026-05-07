# 09 Three Version Structured Comparison

三版对比使用同一个 calibrated structured audit 口径。旧版额外排除了 `*_nav_*.json` 和 `*_toc_tree.json`，只比较真正包含 `blocks` 的 unit。

## 版本路径

| version | path |
| --- | --- |
| early | tmp/structured_quality_probe/old_structured |
| current | data/structured |
| candidate | tmp/structured_quality_probe/candidates/current_plus_p0p1/structured |

## 核心指标对比

| metric | early | current | candidate |
| --- | --- | --- | --- |
| structured_json_files | 981 | 1005 | 1005 |
| total_blocks | 5959 | 6138 | 5889 |
| formula_library_entries | 2263 | 2247 | 2247 |
| table_library_entries | 152 | 146 | 152 |
| fatal | 0 | 18 | 3 |
| error | 16 | 260 | 11 |
| warning | 33 | 274 | 25 |
| strict_pass_rate | 99.7483% | 95.4871% | 99.7792% |
| weighted_quality_score | 99.7281% | 96.2724% | 99.7521% |
| formula_reference_valid_rate | 100.0000% | 100.0000% | 100.0000% |
| table_reference_valid_rate | 100.0000% | 94.9721% | 99.1620% |
| derivation_reference_valid_rate | 100.0000% | 100.0000% | 100.0000% |
| ghost_block_rate | 0.1343% | 0.1140% | 0.0000% |
| h_only_block | 0 | 242 | 0 |
| ghost_block | 8 | 7 | 0 |
| tex_command_leak | 0 | 0 | 0 |
| unbalanced_inline_math | 5 | 5 | 5 |
| table_reference_missing | 0 | 18 | 3 |
| very_short_block | 13 | 253 | 4 |

## 指标变化

| metric | current - early | candidate - current |
| --- | --- | --- |
| fatal | 18 | -15 |
| error | 244 | -249 |
| warning | 241 | -249 |
| strict_pass_rate | -4.2612% | 4.2921% |
| weighted_quality_score | -3.4557% | 3.4797% |
| table_reference_valid_rate | -5.0279% | 4.1899% |
| ghost_block_rate | -0.0202% | -0.1140% |
| h_only_block | 242 | -242 |
| ghost_block | -1 | -7 |
| table_reference_missing | 18 | -15 |

## candidate gate

| gate | passed |
| --- | --- |
| candidate_fatal_not_increased | True |
| candidate_strict_pass_rate_not_lower | True |
| candidate_weighted_quality_score_not_lower | True |

## 各版本高频问题

### early

| issue_type | count |
| --- | --- |
| very_short_block | 13 |
| derivation_placeholder_only_text | 12 |
| ghost_block | 8 |
| placeholder_in_discussion | 8 |
| unbalanced_inline_math | 5 |
| suspicious_truncation | 3 |

### current

| issue_type | count |
| --- | --- |
| very_short_block | 253 |
| h_only_block | 242 |
| table_reference_missing | 18 |
| derivation_placeholder_only_text | 12 |
| placeholder_in_discussion | 9 |
| ghost_block | 7 |
| suspicious_truncation | 6 |
| unbalanced_inline_math | 5 |

### candidate

| issue_type | count |
| --- | --- |
| derivation_placeholder_only_text | 12 |
| placeholder_in_discussion | 9 |
| suspicious_truncation | 6 |
| unbalanced_inline_math | 5 |
| very_short_block | 4 |
| table_reference_missing | 3 |

## 固定抽样 ID 对比

| metric | value |
| --- | --- |
| sample_count | 150 |
| candidate_removed_samples | 35 |
| early_missing_samples | 25 |
| candidate_missing_samples | 0 |

完整抽样对比写入 `tmp/structured_quality_probe/samples/three_version_sample_comparison.jsonl`。

## 解释

- current 是当前交付基线，不在本轮直接修改。
- candidate 是 tmp-only 优化候选，用于证明后续仍有增量空间。
- candidate gate 只表示自动审计指标未回退；是否合入正式 structured 仍需人工抽样确认。
