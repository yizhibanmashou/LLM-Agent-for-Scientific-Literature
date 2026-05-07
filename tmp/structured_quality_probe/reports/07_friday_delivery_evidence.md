# 07 Friday Delivery Evidence

## 结论先行

当前 `data/structured` 可以作为周五交付版：它不是“字符级 OCR 真值”，但在结构化可用质量口径下已经达到交付标准。PaddleOCR 和 GLM-OCR 都只能作为来源或参考，不能单独当作原文 ground truth；后续优化应在 tmp candidate 上验证后再考虑合入。

## 为什么不能直接算传统 OCR 准确率

- 现有数据缺少人工校对的逐字符原文真值。PaddleOCR、GLM-OCR、structured 三者都是机器或规则链路产物，不是人工标注答案。
- structured 的目标不是复刻 OCR 文本，而是形成可被知识库使用的 block、公式引用、表格引用和 derivation 结构。
- 因此准确率口径应从“字符完全一致”转成“结构化可用质量 + 引用有效率 + 人工抽样准确率”。

## 为什么 PaddleOCR / GLM-OCR 都不能当唯一真值

| evidence | value |
| --- | --- |
| Paddle 可用章节 | 36 |
| GLM 可用章节 | 36 |
| Paddle 问题章节 | 36 |
| GLM 问题章节 | 34 |
| 长度差异异常章节 | 13 |
| 公式数量差异异常章节 | 32 |

- PaddleOCR 可以作为 structured 生产源，但它有 LaTeX 残留、数学定界符等问题，所以不等于 ground truth。
- GLM-OCR 可以作为修复参考源，但它同样存在结构残缺和章节级差异，所以也不等于 ground truth。
- Paddle vs GLM 的差异只能证明来源不一致，不能直接推出谁正确，也不能直接得到 structured 准确率。

## structured 质量是否达到交付标准

| metric | early | current | candidate |
| --- | --- | --- | --- |
| strict_pass_rate | 99.7483% | 95.4871% | 99.7792% |
| weighted_quality_score | 99.7281% | 96.2724% | 99.7521% |
| formula_reference_valid_rate | 100.0000% | 100.0000% | 100.0000% |
| table_reference_valid_rate | 100.0000% | 94.9721% | 99.1620% |
| derivation_reference_valid_rate | 100.0000% | 100.0000% | 100.0000% |
| ghost_block_rate | 0.1343% | 0.1140% | 0.0000% |
| fatal / error / warning | 0 / 16 / 33 | 18 / 260 / 274 | 3 / 11 / 25 |

解释：early 的自动审计分数较高，但它覆盖更少、结构化版本更早，不能仅凭该分数判定更适合交付；current 是当前已提交的交付基线，覆盖更完整，但仍暴露出 `[h]`、孤立符号和少量表格引用缺失等可优化问题。candidate 只作为 tmp-only 后续优化候选，说明这些问题可以被可控地继续压低，正式交付仍以 current 为基线。

## 周五建议采用的准确率口径

- 主口径：`strict_pass_rate`，表示无 fatal/error 的 block 占比。
- 综合口径：`weighted_quality_score`，按 fatal/error/warning 加权惩罚。
- 引用口径：`formula_reference_valid_rate`、`table_reference_valid_rate`、`derivation_reference_valid_rate`。
- 噪声口径：`ghost_block_rate`。
- 人工口径：固定 `manual_sample_ids` 后计算 `manual_sample_accuracy`，作为最终汇报里最接近“人工准确率”的数字。

## 优化前后如何对比

- 使用同一套 calibrated audit 脚本。
- 使用同一份抽样 ID：`tmp/structured_quality_probe/samples/manual_sample_ids.jsonl`。
- 对比 early / current / candidate 三版，同时保留 candidate 的 change manifest。
- 不把 candidate 直接合入 `data/structured`，等人工抽样确认后再决定。

## 给老师汇报可用表述

> 我们没有把 PaddleOCR 或 GLM-OCR 直接当成原文真值，因为两者都存在数学符号、LaTeX 残留、结构残缺和章节差异问题。更客观的方式是把 structured 作为下游知识库交付对象，评估它的结构化可用质量：包括 fatal/error 问题率、公式和表格引用有效率、derivation 引用有效率、噪声块比例，并用固定分层抽样做人工验证。按这套口径，当前 structured 已经达到交付标准；后续优化会先在 tmp candidate 中验证，不直接覆盖当前交付版。

## 还缺的数据

- 人工标注后的 `manual_sample_accuracy`。
- 如果 candidate 未来要合入，还需要同一批样本在 candidate 上的人工复核结论。
- 如果要报告传统 OCR 字符级准确率，需要另建人工逐字符 ground truth 数据集。
