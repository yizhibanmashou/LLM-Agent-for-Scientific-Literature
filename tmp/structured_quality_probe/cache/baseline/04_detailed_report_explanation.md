# Structured 质量评估详细报告说明

## 一、报告目的

本次工作的目标不是修复 structured，也不是重新跑 OCR，而是先验证一件基础问题：当前项目能否建立一套可重复、可解释、可用于优化前后对比的 structured 质量评估方案。

结论是：方案可行，但不能把 PaddleOCR 或 GLM-OCR 任意一方直接当作 ground truth。原因是二者都只是机器 OCR/结构化输出，并且本次检测已经发现两者都存在不同类型的问题。更稳妥的评价口径应当是：

| 评价层次 | 说明 |
| --- | --- |
| 自动全量审计 | 对全部 structured JSON、公式库、表格库做规则检测，得到可复跑的质量指标。 |
| OCR 源对照 | 比较 PaddleOCR 与 GLM-OCR 的覆盖、长度、公式数量和结构异常，证明二者只能作为参考源。 |
| 人工抽样验证 | 对固定抽样 ID 做人工判定，补足自动规则无法判断的语义正确性。 |

因此，本次报告建议采用“structured 可用质量通过率”，而不是传统 OCR 字符级准确率。

## 二、生成的报告文件

| 文件 | 作用 |
| --- | --- |
| `00_data_availability.md/json` | 检查数据路径是否存在、统计 structured 与 OCR 可用章节数。 |
| `01_structured_quality_audit.md/json` | 对 structured 做全量质量审计，输出问题数量、样例和核心指标。 |
| `01_structured_issue_samples.jsonl` | 全量问题样例明细，每行一个 issue，可用于后续定位与抽样。 |
| `02_ocr_source_comparison.md/json` | 比较 PaddleOCR 与 GLM-OCR 的覆盖和质量问题，证明二者都不是绝对真值。 |
| `samples/paddle_glm_disagreement_samples.jsonl` | Paddle 与 GLM 差异片段抽样。 |
| `03_feasibility_conclusion.md` | 周五汇报可用的结论版文字。 |
| `04_detailed_report_explanation.md` | 本文件，对上述报告进行解释说明。 |

所有新增脚本、缓存、样本和报告均位于 `tmp/structured_quality_probe/` 下，未修改 `data/structured/`、`data/paddle_output/`、`data/glmocr_output/`。

## 三、数据可用性说明

本次路径检查得到的关键结果如下：

| 项目 | 结果 |
| --- | ---: |
| structured JSON 文件数 | 1005 |
| structured blocks 总数 | 6138 |
| formula_library 条目数 | 2247 |
| table_library 条目数 | 146 |
| `data/structured/` | 存在 |
| `data/structured/formula_library.json` | 存在 |
| `data/structured/table_library.json` | 存在 |
| `data/paddle_output/` | 当前不存在 |
| `data/glmocr_output/` | 当前不存在 |
| 实际可用 PaddleOCR 输出 | `tmp/paddle_output/`，36 个章节/附录 |
| 实际可用 GLM-OCR 输出 | `tmp/glmocr_output/`，36 个章节/附录 |

这里需要特别说明：用户原始任务中写的是 `data/paddle_output/` 和 `data/glmocr_output/`，但当前工作树实际可读的是 `tmp/paddle_output/` 与 `tmp/glmocr_output/`。脚本没有擅自移动或复制 OCR 数据，而是在报告中如实记录了 requested path 缺失、fallback path 可用的情况。

## 四、structured 审计方法

structured 审计脚本只读扫描以下对象：

| 对象 | 检测内容 |
| --- | --- |
| 所有章节/附录 JSON | block 数量、block.type、内容质量、占位符、公式/表格引用。 |
| `formula_library.json` | 公式条目数、公式引用是否能被解析和匹配。 |
| `table_library.json` | 表格条目数、表格引用是否能被解析和匹配。 |

审计问题按严重级别分为：

| severity | 含义 | 示例 |
| --- | --- | --- |
| fatal | 会破坏下游使用或引用完整性的问题 | JSON 无法解析、必要字段缺失、公式/表格引用缺失。 |
| error | 明显结构化质量问题 | `[h]` 残留块、ghost block、数学定界符不平衡、破损占位符。 |
| warning | 需要关注但不一定直接阻断的问题 | block 很短、discussion 中占位符过多、可疑 OCR 噪声。 |
| info | 补充信息 | derivation 跨章节引用等非默认错误项。 |

derivation block 被单独处理。公式占位符出现在 derivation 中不默认算错，因为推导段落天然可能由文字和公式引用共同构成。脚本只额外检查：公式引用是否存在、是否引用过多、去掉公式占位符后是否仍有可读文本、占位符是否断裂、是否出现跨章节异常引用。

## 五、structured 审计结果解释

本次审计得到的总体结果：

| 指标 | 值 |
| --- | ---: |
| 总文件数 | 1007 |
| structured JSON 文件数 | 1005 |
| 总 block 数 | 6138 |
| fatal | 18 |
| error | 460 |
| warning | 274 |
| strict_pass_rate | 0.922939 |
| weighted_quality_score | 0.943174 |

`总文件数 = 1007`，是因为审计对象包含 1005 个章节/附录 structured JSON，再加上 `formula_library.json` 和 `table_library.json`。

### block.type 分布

| block.type | 数量 |
| --- | ---: |
| discussion | 4212 |
| derivation | 1618 |
| proposition | 277 |
| definition | 31 |

这说明 structured 的主体是 discussion 和 derivation。后续抽样时也应该分层抽样，不能只随机抽 block，否则容易被 discussion 主导，忽略 derivation 的公式引用质量。

### issue_type 分布

| issue_type | 数量 | 解读 |
| --- | ---: | --- |
| very_short_block | 253 | 内容很短，可能是标题、残留、断裂片段，也可能是合法短文本，需要抽样判定。 |
| h_only_block | 242 | 内容仅为 `[h]`，基本属于 OCR/LaTeX 结构残留。 |
| tex_command_leak | 200 | 正文中残留明显 LaTeX 结构命令，说明 structured 层仍混有源格式痕迹。 |
| table_reference_missing | 18 | 表格占位符无法在 table_library 中找到，是最明确的 fatal 问题。 |
| derivation_placeholder_only_text | 12 | derivation 去掉公式占位符后可读文本不足，需要人工看是否可接受。 |
| placeholder_in_discussion | 9 | discussion 中占位符过密，可能影响问答可读性。 |
| ghost_block | 7 | 页码、符号、孤立字符等噪声块。 |
| suspicious_truncation | 6 | 疑似短文本截断或括号/引号未闭合。 |
| unbalanced_inline_math | 5 | `$` 数学定界符数量不平衡。 |

最值得优先处理的是 `table_reference_missing`、`h_only_block` 和真正的 `tex_command_leak`。其中 `table_reference_missing` 是引用完整性问题，优先级最高。

## 六、核心指标解释

### 1. strict_pass_rate

定义：

```text
strict_pass_rate = 无 fatal/error 的 block 数 / 总 block 数
```

当前值：

```text
0.922939
```

这个指标代表 structured block 在严格规则下的可用通过率。它不是 OCR 字符准确率，而是“block 是否没有明显结构化阻断问题”的比例。

优点是直观，适合给老师汇报；缺点是 fatal 和 error 只按 block 是否命中来判断，不体现同一 block 内多个问题的严重度差异。

### 2. weighted_quality_score

定义：

```text
weighted_quality_score = 1 - (5*fatal + 3*error + warning) / (5*total_blocks)
```

当前值：

```text
0.943174
```

这个指标把问题严重度纳入计算：fatal 权重 5，error 权重 3，warning 权重 1。它比 strict_pass_rate 更适合优化前后对比，因为它可以反映“问题数量和严重度是否下降”。

### 3. formula_reference_valid_rate

定义：

```text
structured 中公式占位符能在 formula_library 中找到的比例
```

当前值：

```text
1.000000
```

说明 structured 中被检测到的公式引用全部能在公式库中找到。这是当前系统的强项，说明公式引用链条总体稳定。

### 4. table_reference_valid_rate

定义：

```text
structured 中表格占位符能在 table_library 中找到的比例
```

当前值：

```text
0.949721
```

这说明表格引用链条还有明显缺口。18 个 `table_reference_missing` 就来自这里。后续如果优化，表格引用补齐应当是第一批可验证目标之一。

### 5. derivation_reference_valid_rate

定义：

```text
derivation block 中公式引用能在 formula_library 中找到的比例
```

当前值：

```text
1.000000
```

这说明 derivation 中的公式占位符本身不是主要问题。真正需要关注的是 derivation 是否仍有足够可读文本、是否占位符过密、是否保留推导上下文。

### 6. ghost_block_rate

定义：

```text
ghost_block_rate = ghost block / 总 block 数
```

当前值：

```text
0.001140
```

ghost block 比例很低，说明孤立符号、页码、纯噪声块不是当前 structured 的主要问题。但这些问题很显眼，适合作为优化前后展示样例。

## 七、为什么 PaddleOCR 和 GLM-OCR 都不能当 ground truth

OCR 对照脚本比较的是可用 OCR 输出根目录：

| 来源 | 实际读取目录 | 可用章节数 |
| --- | --- | ---: |
| PaddleOCR | `tmp/paddle_output/` | 36 |
| GLM-OCR | `tmp/glmocr_output/` | 36 |

检测结果：

| 来源 | 问题章节数 | 主要问题 |
| --- | ---: | --- |
| PaddleOCR | 36 | LaTeX 命令残留覆盖全部章节；5 个章节存在数学定界符不平衡。 |
| GLM-OCR | 34 | LaTeX 命令残留覆盖大部分章节；1 个章节存在数学定界符不平衡。 |

两者之间也存在显著差异：

| 对比项 | 数量 |
| --- | ---: |
| 文本长度差异超过 20% 的章节 | 13 |
| 公式数量差异超过 5 的章节 | 32 |
| 共享章节数 | 36 |

典型差异包括：

| chapter | length_gap_ratio | formula_gap | Paddle 公式数 | GLM 公式数 |
| --- | ---: | ---: | ---: | ---: |
| chapter11 | 0.186 | 113 | 531 | 644 |
| chapter19 | 0.298 | 95 | 744 | 649 |
| chapter22 | 0.071 | 91 | 963 | 872 |
| chapter2 | 0.192 | 87 | 551 | 464 |
| appendix3 | 0.116 | 85 | 463 | 378 |

这些差异证明：如果把 PaddleOCR 当真值，GLM-OCR 会显得“不准”；如果把 GLM-OCR 当真值，PaddleOCR 又会显得“不准”。但这只能说明两者输出不一致，不能说明哪一方绝对正确。

因此，PaddleOCR 与 GLM-OCR 的合理角色是：

| 来源 | 合理定位 | 不应承担的角色 |
| --- | --- | --- |
| PaddleOCR | structured 生产源、LaTeX/公式提取参考 | 不能作为绝对 ground truth |
| GLM-OCR | 修复参考源、差异定位参考 | 不能作为绝对 ground truth |

## 八、为什么不能用 Paddle vs GLM 直接算准确率

直接做 Paddle 与 GLM 的互相比对，只能得到“一致率”或“差异率”，不能得到准确率。

原因如下：

| 原因 | 说明 |
| --- | --- |
| 二者都可能错 | 两个机器 OCR 输出都可能遗漏、改写、误识别公式。 |
| 格式不同 | Paddle 主要是 LaTeX，GLM 主要是 Markdown/JSON，格式差异会被误算成内容差异。 |
| 章节内结构不同 | 同一段内容可能被切分成不同块，无法直接逐字符对齐。 |
| 目标不同 | structured 质量关注的是知识库可用性，不是纯文本字符一致性。 |

所以本次报告的核心表述应是：Paddle 与 GLM 可以互相提供证据，但都不是标准答案；准确率口径必须引入人工抽样或可信人工标注。

## 九、建议周五报告采用的准确率口径

建议把“准确率”拆成两层：

### 自动质量通过率

用于全量覆盖，回答“structured 数据整体是否可用”。

| 指标 | 当前值 | 汇报含义 |
| --- | ---: | --- |
| strict_pass_rate | 92.29% | 约 92.29% 的 block 没有 fatal/error 级结构化问题。 |
| weighted_quality_score | 94.32% | 按 fatal/error/warning 加权后的整体质量分。 |
| formula_reference_valid_rate | 100.00% | 公式引用链条完整。 |
| table_reference_valid_rate | 94.97% | 表格引用链条仍有缺口。 |
| derivation_reference_valid_rate | 100.00% | 推导段落中的公式引用有效。 |
| ghost_block_rate | 0.11% | 纯噪声块比例很低。 |

### 人工抽样准确率

用于回答“内容语义是否真的正确”。

建议定义：

```text
manual_sample_accuracy = 人工判定正确的抽样 block 数 / 人工抽样 block 总数
```

抽样建议：

| 分层 | 建议抽样 |
| --- | ---: |
| discussion 正常块 | 30 |
| derivation 块 | 30 |
| proposition/definition | 20 |
| fatal/error 命中块 | 30 |
| warning 命中块 | 20 |
| OCR 差异较大章节中的块 | 20 |

这样人工样本既覆盖正常数据，也覆盖高风险区域，避免只抽到“看起来干净”的 block。

## 十、优化前后对比方法

后续如果要证明优化有效，建议固定三样东西：

| 固定项 | 作用 |
| --- | --- |
| 同一套 audit 脚本 | 保证规则一致。 |
| 同一份 baseline audit JSON | 保证优化前指标可追溯。 |
| 同一批人工抽样 ID | 保证人工准确率可比较。 |

对比时建议输出：

| 指标 | baseline | current | delta |
| --- | ---: | ---: | ---: |
| strict_pass_rate | 当前值 | 优化后值 | current - baseline |
| weighted_quality_score | 当前值 | 优化后值 | current - baseline |
| table_reference_valid_rate | 当前值 | 优化后值 | current - baseline |
| h_only_block 数量 | 当前值 | 优化后值 | baseline - current |
| tex_command_leak 数量 | 当前值 | 优化后值 | baseline - current |
| manual_sample_accuracy | 当前人工标注 | 优化后人工标注 | current - baseline |

特别注意：不要只报告总分上升，还要报告 fatal/error 是否下降。对于老师来说，“高风险问题减少”比“均分提高一点”更有说服力。

## 十一、当前结论边界

本次报告能证明：

| 能证明 | 说明 |
| --- | --- |
| structured 评估方案可行 | 脚本已经全量扫描 1005 个 structured JSON 和两个库文件。 |
| 当前 structured 有可量化 baseline | 已得到 strict_pass_rate、weighted_quality_score 等指标。 |
| PaddleOCR 不能作为绝对真值 | Paddle 输出自身存在 LaTeX 残留和数学定界符问题。 |
| GLM-OCR 不能作为绝对真值 | GLM 输出自身也存在结构残留和数学定界符问题。 |
| Paddle vs GLM 不能直接得到准确率 | 两者差异只能说明不一致，不能说明谁正确。 |

本次报告还不能证明：

| 不能证明 | 还缺什么 |
| --- | --- |
| 字符级 OCR 准确率 | 缺少人工校对或权威文本 ground truth。 |
| 语义级内容完全正确率 | 缺少人工抽样标注。 |
| 优化后效果 | 还没有优化后的 current structured 与同批抽样复核。 |
| 表格/公式渲染视觉准确率 | 还缺 PDF 页面或原书页面级人工对照。 |

## 十二、建议汇报用表述

建议对老师这样讲：

> 我们先没有直接计算传统 OCR 字符级准确率，因为当前项目目标不是单纯识别文本，而是生成可进入知识库的结构化章节、公式、表格和引用关系。传统 OCR 准确率需要人工校对文本或权威电子文本作为 ground truth，而当前可用的 PaddleOCR 和 GLM-OCR 都是机器输出。本次检测证明，PaddleOCR 和 GLM-OCR 都存在结构残留、数学定界符异常、公式数量差异等问题，因此不能把任一方当作唯一真值。
>
> 因此我们采用 structured 可用质量评估方案：先做全量自动审计，统计 strict_pass_rate、weighted_quality_score、公式/表格引用有效率、derivation 引用有效率和 ghost_block_rate；再用固定抽样 ID 做人工复核，得到 manual_sample_accuracy。这样既能全量覆盖 1005 个 structured JSON 和 6138 个 block，又能通过人工抽样验证自动规则无法判断的语义正确性。
>
> 当前 baseline 的 strict_pass_rate 是 92.29%，weighted_quality_score 是 94.32%；公式引用有效率为 100%，表格引用有效率为 94.97%。这说明当前 structured 已经具备较高可用性，但仍存在表格引用缺失、`[h]` 残留块和 LaTeX 命令残留等可优化问题。后续优化可以用同一套脚本和同一批抽样 ID 做前后对比，证明质量提升是否真实发生。

## 十三、下一步建议

| 优先级 | 任务 | 目的 |
| --- | --- | --- |
| P0 | 固定 baseline audit JSON 和抽样 ID | 建立优化前基线。 |
| P0 | 建立人工抽样标注表 | 得到 manual_sample_accuracy。 |
| P1 | 优先修复 table_reference_missing | 提升表格引用完整性。 |
| P1 | 清理 `[h]` 残留块 | 降低明显结构噪声。 |
| P1 | 处理真实 LaTeX 命令残留 | 提升正文可读性和下游检索质量。 |
| P2 | 对 OCR 差异大章节做人工复核 | 判断差异来自 Paddle、GLM 还是 structured 处理。 |

本次最重要的结论是：structured 质量评估已经可以进入可重复的工程化阶段，但“准确率”必须谨慎表述为 structured 可用质量通过率，并辅以人工抽样准确率，而不是把任一 OCR 输出当作绝对答案。
