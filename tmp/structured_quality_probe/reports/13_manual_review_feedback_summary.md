# 手工审核反馈汇总

本报告读取 `review_app/data/local/review_records.json` 与 `review_app/data/local/issue_taxonomy.json`，用于把人工审核备注反哺到后续 detector 设计。

## 总览

| 指标 | 数值 |
| --- | --- |
| structured 源版本 | candidate_current_plus_p0p1 |
| 总条目数 | 3404 |
| 本次已读记录数 | 93 |
| 跨源旧记录数 | 122 |
| 结构化问题记录数 | 3 |
| 备注记录数 | 2 |

## Taxonomy 状态

| 状态 | 数量 |
| --- | --- |
| active | 0 |
| candidate | 0 |
| manual_only | 17 |

## 目标章节覆盖

| 章节 | chunks | formulas | tables | 已审核条目 | issue 数 | 备注数 | pending | pass | fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chapter5 | 27 | 74 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| chapter13 | 24 | 63 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| chapter16 | 17 | 54 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| chapter25 | 29 | 47 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| chapter26 | 26 | 75 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| chapter27 | 14 | 23 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| chapter28 | 46 | 163 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |

## issue 分类分布

| issue_code | 数量 |
| --- | --- |
| formula_reference_error | 1 |
| inline_math_damage | 1 |
| issue_c141804b | 1 |

## 严重级别分布

| severity | 数量 |
| --- | --- |
| error | 2 |
| info | 1 |

## detector 入口建议

- 只让 `status=active` 且 `detector.patterns` 非空的分类进入正式 detector。
- `candidate` 与 `manual_only` 先只统计、不自动判错。
- 人工审核新增的 `issue_rows` 先沉淀为样例与统计，再决定是否升格为 active。

## 典型问题样例

- IR0001 | chapter6 | chunks | formula_reference_error | info | - | 目标: -
- IR0002 | chapter6 | chunks | inline_math_damage | error | - | 目标: -
- IR0003 | chapter6 | tables | issue_c141804b | error | - | 目标: -
