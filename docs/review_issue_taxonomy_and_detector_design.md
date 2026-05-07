# 审核备注分类化与 Damage Detector 联动功能设计

## 1. 新功能目标

当前审核工具已经支持在页面中为每个审核条目添加自由文本形式的“审核备注”。这个能力适合记录临时观察，但不利于后续统计、复用和自动化检测。新功能的目标是把人工审核过程中发现的问题沉淀为结构化、可复用的错误类型库，并进一步让这些错误类型能够反哺 Damage Detector。

具体目标包括：

1. 将自由文本备注升级为半结构化问题记录。
2. 支持审核者为问题选择已有分类，或快速创建新分类。
3. 记录问题发生的范围、错误片段、上下文和可选修正结果。
4. 将人工审核样例自动沉淀为 detector 候选规则的数据来源。
5. 让 Damage Detector 能读取配置化错误类型和检测规则，而不是只依赖硬编码函数。
6. 尽量减少人工负担，使人工主要负责发现问题、选择分类、确认候选结果，而不是编写复杂规则。

该功能的核心价值是把审核行为从“一次性备注”转化为“可复用质量信号”。随着审核样例增加，系统可以逐步形成面向 PDF/OCR/LaTeX/结构化 JSON 转换流程的错误类型库。

## 2. 设计细节

### 2.1 备注从自由文本变为半结构化记录

现有备注只包含 `text` 和 `created_at`。新功能建议将备注扩展为 issue record，例如：

```json
{
  "id": "note_20260506_xxxxxx",
  "issue_code": "inline_math_spaced_script",
  "issue_label": "inline 公式上下标断裂",
  "scope": "inline_math",
  "bad_span": "$ \\sigma _ A^2 $",
  "expected": "$\\sigma_A^2$",
  "note": "这里 sigma 的下标被 OCR 断开了",
  "context": "place of $ \\sigma _ A^2 $, which results...",
  "created_at": "2026-05-06T10:30:00Z"
}
```

页面上不要求用户手写 JSON，而是提供表单化操作：

- 问题分类：下拉选择已有分类，支持新建分类。
- 问题范围：正文、inline 公式、display 公式、表格、公式引用、结构切分等。
- 错误片段：用户在页面中划选，系统自动填入。
- 正确结果：可选输入；如果暂时不确定，可以留空。
- 审核备注：自由文本，可选。

这样可以把人工输入控制在很轻的范围内：选择分类、划选错误片段、必要时补一句说明。

### 2.2 问题分类库

新增一个配置文件保存问题分类，例如：

```json
{
  "version": 1,
  "categories": [
    {
      "issue_code": "inline_math_spaced_script",
      "label": "inline 公式上下标断裂",
      "scope": "inline_math",
      "description": "inline LaTeX 中下标或上标与主体之间出现异常空格或断裂。",
      "status": "active",
      "examples": [
        {
          "bad_span": "$ \\sigma _ A^2 $",
          "expected": "$\\sigma_A^2$"
        }
      ],
      "detector": {
        "mode": "regex",
        "patterns": [
          "\\$[^$]*\\s[_^]\\s+[A-Za-z0-9]"
        ]
      }
    }
  ]
}
```

建议状态分为：

- `manual_only`：只用于人工分类和统计，不参与自动检测。
- `candidate`：系统已生成候选检测规则，但需要审核命中效果。
- `active`：规则已通过审核，可以被 Damage Detector 正式使用。

新建分类默认进入 `manual_only` 或 `candidate`，不建议直接进入 `active`，避免误报扩散。

### 2.3 Damage Detector 配置化

现有 Damage Detector 逻辑主要写在 Python 函数中，例如 inline LaTeX damage 检测和结构化文本 issue 检测。新功能建议保留已有硬编码规则，同时增加一个配置化规则入口。

运行时流程：

1. 加载已有内置规则。
2. 读取问题分类配置文件。
3. 将 `status=active` 且带有 detector 配置的分类加入检测逻辑。
4. 对每个命中结果输出统一 issue code、label、matched span 和来源。

检测结果可以统一成：

```json
{
  "issue_code": "inline_math_spaced_script",
  "label": "inline 公式上下标断裂",
  "scope": "inline_math",
  "severity": "error",
  "matched_value": "$ \\sigma _ A^2 $",
  "detector_source": "configured_rule"
}
```

这样人工新增分类后，不需要直接修改 Python 函数；系统可以通过配置文件扩展检测能力。

### 2.4 自动化生成候选规则

为了尽量减少人工编写检测条件，可以引入自动归纳机制：

1. 用户在审核页面标注若干同类错误样例。
2. 系统收集 `bad_span`、上下文、scope 和可选 expected。
3. 后台使用规则归纳或 LLM 生成候选 detector 规则。
4. 将规则标记为 `candidate`。
5. 全量扫描结构化数据，展示该候选规则命中的样例。
6. 用户只需要审核命中样例是否合理。
7. 通过率足够高后，规则变为 `active`。

这个流程将人工工作从“编写规则”变成“确认规则是否可靠”。

### 2.5 页面交互建议

审核页面可以增加以下控件：

1. 分类选择器：显示已有 issue category。
2. 新建分类按钮：输入分类名称、问题范围和简短说明。
3. 错误片段采集：支持用户选中文本后点击“记录为错误片段”。
4. 正确结果输入框：可选。
5. 分类统计面板：显示当前分类出现次数、最近样例和 detector 状态。
6. 候选规则审核页：展示某个 candidate detector 的命中结果，供用户批量通过或拒绝。

### 2.6 数据流

推荐数据流如下：

```text
人工审核页面
  -> 选择/新建问题分类
  -> 标注错误片段
  -> 保存结构化 issue record
  -> 汇总到 issue category examples
  -> 自动生成 detector candidate
  -> 全量扫描并展示候选命中
  -> 人工确认候选规则
  -> active detector
  -> 后续自动检测同类问题
```

这个流程保证人工参与仍然存在，但主要集中在审核和确认环节，不需要承担大量规则输入工作。

## 3. Use Cases

### Use Case 1：inline LaTeX 下标断裂

审核者在页面中看到如下内容：

```text
place of $ \sigma _ A^2 $, which results in a two-fold lower estimate
```

审核者发现 `$ \sigma _ A^2 $` 中 `_` 前后出现异常空格，属于 inline 公式 OCR 损坏。

操作流程：

1. 选中 `$ \sigma _ A^2 $`。
2. 在问题分类中选择“inline 公式上下标断裂”。
3. 可选填写正确结果 `$\\sigma_A^2$`。
4. 保存备注。

系统自动记录该样例，并将它归入 `inline_math_spaced_script`。当同类样例积累后，系统生成候选正则：

```regex
\$[^$]*\s[_^]\s+[A-Za-z0-9]
```

该规则通过审核后，Damage Detector 后续可以自动扫描同类问题。

### Use Case 2：正文中残留 LaTeX/table placeholder

审核者在 chunk 中看到：

```text
The results are summarized in [h], followed by Cell 1 & Cell 2 ...
```

这说明表格浮动参数或 dummy table 内容泄漏到了正文块里。

操作流程：

1. 选中 `[h]` 或 `Cell 1 & Cell 2`。
2. 新建或选择分类“表格占位符泄漏”。
3. 设置问题范围为“结构化正文”。
4. 保存备注。

系统将该问题记录到分类库，并在后续扫描中统计同类泄漏。如果多个样例都具有 `[h]`、`[t]`、`Cell 1 & Cell 2` 等模式，系统可以生成 candidate detector。通过审核后，它可以进入 Damage Detector，自动标出类似结构化噪声。
