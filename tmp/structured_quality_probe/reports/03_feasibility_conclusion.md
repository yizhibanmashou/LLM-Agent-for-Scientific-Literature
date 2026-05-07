# 03 Feasibility Conclusion

## 1. 为什么不能直接计算传统 OCR 准确率

传统 OCR 准确率通常需要可靠的字符级或词级 ground truth，例如人工校对文本、逐页对齐文本、或可验证的原书电子文本。当前项目里的 `structured` 产物不是单纯 OCR 文本，而是经过章节切分、block 分类、公式/表格占位符替换、公式库和表格库引用绑定之后的结构化数据。

因此，直接计算“字符识别正确率”会遇到三个问题：

| 问题 | 说明 |
| --- | --- |
| 缺少绝对真值 | PaddleOCR 和 GLM-OCR 都是机器输出，不是人工校对答案。 |
| 对齐粒度不同 | Paddle 输出以 LaTeX 源为主，GLM-OCR 输出以 Markdown/JSON 为主，structured 又是 block 级结构。 |
| 评价目标不同 | 下游知识库更关心 block 是否可用、引用是否断裂、公式/表格是否可追踪，而不只是字符是否完全一致。 |

所以，本阶段更合理的目标不是传统 OCR 字符级准确率，而是 structured 可用质量通过率。

## 2. 为什么 PaddleOCR 和 GLM-OCR 都不能作为唯一真值

本次检测发现，当前工作树下用户指定的 `data/paddle_output/` 和 `data/glmocr_output/` 不存在；实际可读 OCR 输出位于 `tmp/paddle_output/` 和 `tmp/glmocr_output/`。这两个目录均覆盖 36 个章节/附录，但都存在结构或文本质量问题。

| 来源 | 可用章节数 | 发现的问题 |
| --- | ---: | --- |
| PaddleOCR | 36 | 36 个章节存在 LaTeX 命令残留；5 个章节存在 `$` 数学定界符不平衡。 |
| GLM-OCR | 36 | 34 个章节存在 LaTeX 命令残留；1 个章节存在 `$` 数学定界符不平衡。 |
| 两者对比 | 36 个共享章节 | 13 个章节文本长度差异超过 20%；32 个章节公式数量差异超过 5。 |

结论不是“谁更好”，而是：两者都不是绝对正确答案。PaddleOCR 可以作为 structured 生产源，GLM-OCR 可以作为修复参考源，但都不能直接当 ground truth。

## 3. structured 质量评估方案是否可行

可行。原因是 structured 数据本身已经具备稳定的机器可审计对象：章节 JSON、block、`block.type`、公式引用、表格引用、公式库和表格库。审计脚本可以重复运行，并输出可对比指标。

本次 baseline 审计结果：

| 指标 | 值 |
| --- | ---: |
| structured JSON 文件数 | 1005 |
| 总 block 数 | 6138 |
| formula_library 条目数 | 2247 |
| table_library 条目数 | 146 |
| fatal | 18 |
| error | 460 |
| warning | 274 |
| strict_pass_rate | 0.922939 |
| weighted_quality_score | 0.943174 |
| formula_reference_valid_rate | 1.000000 |
| table_reference_valid_rate | 0.949721 |
| derivation_reference_valid_rate | 1.000000 |
| ghost_block_rate | 0.001140 |

这说明自动审计能稳定发现引用断裂、占位符噪声、残留结构、短块和 ghost block 等问题，可以作为后续优化前后对比的统一尺子。

## 4. 建议采用的指标

| 指标 | 含义 | 当前值 |
| --- | --- | ---: |
| strict_pass_rate | 无 fatal/error 的 block 数 / 总 block 数 | 0.922939 |
| weighted_quality_score | `1 - (5*fatal + 3*error + warning) / (5*total_blocks)` | 0.943174 |
| formula_reference_valid_rate | structured 中公式占位符能在 formula_library 找到的比例 | 1.000000 |
| table_reference_valid_rate | structured 中表格占位符能在 table_library 找到的比例 | 0.949721 |
| derivation_reference_valid_rate | derivation block 中公式引用有效比例 | 1.000000 |
| ghost_block_rate | ghost block / 总 block 数 | 0.001140 |
| manual_sample_accuracy | 固定抽样 ID 的人工验收准确率 | 待人工标注 |

## 5. 优化前后如何对比

优化前后对比应采用同一套脚本和同一份抽样 ID，避免因为抽样变化导致指标不可比。

| 对比项 | 做法 |
| --- | --- |
| baseline structured | 保存当前 `01_structured_quality_audit.json` 作为 baseline。 |
| current structured | 后续优化后重新运行同一脚本。 |
| 自动指标 | 对比 strict_pass_rate、weighted_quality_score、引用有效率、ghost_block_rate。 |
| 人工指标 | 使用同一批 block ID 做人工复核，计算 manual_sample_accuracy。 |
| OCR 参考 | Paddle/GLM 只用于辅助定位差异，不作为唯一正确答案。 |

## 6. 给老师汇报时可以使用的一段表述

我们没有直接报告传统 OCR 字符级准确率，因为当前项目的目标不是单纯识别文本，而是生成可用于知识库的结构化章节、公式、表格和引用关系。PaddleOCR 和 GLM-OCR 都是机器输出，本次检测证明二者都存在不同类型的结构化或公式文本问题，因此不能把任一方作为绝对 ground truth。我们采用“全量自动质量审计 + 分层人工抽样验证”的评价方案：自动部分统计 strict_pass_rate、weighted_quality_score、公式/表格引用有效率、derivation 引用有效率和 ghost block rate；人工部分在固定抽样 ID 上复核内容正确性。这样既能全量覆盖 structured 数据，又能通过人工抽样补足自动规则无法判断的语义准确性。
