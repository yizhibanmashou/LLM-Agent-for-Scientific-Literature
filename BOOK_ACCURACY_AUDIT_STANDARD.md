# 教材逐页准确性审计规范

本规范适用于本项目中所有教材的 structured、公式、表格、图片、Example 和 textbook 交付。

## 裁决原则

- `data/背景资料/` 中经人工确认并切分好的 chapter PDF 是内容与版式准确性的可信母版。自动审计必须以母版页、Paddle source block、bbox 和交付内容的可追溯对应关系作出判断。
- 当一本书没有单一完整 PDF 时，允许按 profile 固定的 chapter 顺序确定性拼接统一母版；profile 必须绑定每个 chapter PDF 的 SHA-256、页数、顺序及拼接结果 SHA-256。Evolution 采用此方式。
- 每个纳入范围的源页都必须渲染并进入自动全量审计；仅检查异常队列或抽样不能替代全量自动检查。
- 每个 structured block、公式、逻辑表格、图片和 Example 必须保存源页、源 block、bbox 与证据哈希。跨页内容保存完整 `source_pages`。
- 自动验证必须绑定母版 PDF、页面证据和交付内容 SHA-256。证据变化后必须重新执行自动审计。
- 人工状态不再是安装门禁；`pending`、未填写 `verified` 或未执行人工逐页审核不会阻止安装。
- 自动审计发现的 `needs_correction`、未覆盖实质源 block、证据漂移、缺图、乱码、占位符、计数异常或来源缺失仍会阻止正式安装。
- 人工修正必须精确限定书籍、源页、源 block、bbox、原文和修正文；不允许全书模糊替换。

## 自动审计范围

- 页面：标题层级、段落边界、跨页连接、断词、正文、标点、公式、图表引用和阅读顺序。
- 公式：LaTeX、编号、上下标、希腊字母、矩阵、左右操作数和所属单元。
- 表格：标题、表头、单元格、合并关系、脚注、续表、正文引用和所属小节。
- 图片：编号、图注、裁切、清晰度、方向、黑边、缺字和正文位置。不得用图内设计性斜线判断旋转。
- Example：起止范围、跨页延续、内嵌公式/图表和下一小节边界。没有 Example 时也必须保存空台账和自动检查结论。

人工检查改为安装后的可选抽查。`review/status.json`、`review/events.jsonl` 和逐页证据图可以继续记录抽查结论，但不参与 `valid` 计算，也不阻止安装。

表格保持“小节内沉底”策略：正文语义位置保留引用，完整逻辑表仅在所属小节末尾渲染一次。

## 统一临时目录

每本书使用 `tmp/book_audits/<Book>/`：

```text
manifest.json
source/{pages,normalized_layout}/
evidence/{page_contacts,crops,contacts,figure_pairs}/
ledgers/{pages,blocks,formulas,tables,figures,examples}.json
review/{status.json,events.jsonl}
corrections/applied_corrections.json
staging/data/
snapshots/preinstall/
reports/{verification.json,report.md,protected_hashes.json}
logs/
failures/
```

历史目录可以作为只读输入，但新审计产物不得继续散落到其他 `tmp/` 根目录。正式 `data/` 不保存页面渲染、OCR、联系图、日志、快照或失败产物。

`tmp/book_audits/` 是可删除的本地证据目录，不是正式交付内容。清理前应完成验证并迁出需要长期保留的示例；清理后可从可信 chapter PDF、Paddle 输出、受版本控制的 profile/correction、审计代码和正式交付数据完整重建。公开流程和示例见 [`docs/book-accuracy-audit.md`](docs/book-accuracy-audit.md)。

## 标准流程

```powershell
python scripts/audit_book_accuracy.py build --book <Book>
python scripts/audit_book_accuracy.py verify --book <Book>
python scripts/audit_book_accuracy.py status --book <Book>
python scripts/audit_book_accuracy.py install --book <Book>
```

`<Book>` 可取 `Evolution`、`Genetics`、`PopGen` 或 `all`；统一重建三书证据时使用 `build --book all --dpi 72`。

`build` 建立证据、台账和 staging，并立即执行自动验证；`verify` 只以自动检查结果判定 `valid`；`install` 必须重新执行同一自动验证，并采用快照、书名前缀过滤和原子替换。自动验证全部通过后即可进入正式 `data/`，人工抽查在安装后进行。

默认安装要求 `valid=true`。诊断模式可以显式记录 waiver，但 waiver 不得生成 `automated_valid=true`，也不得用于正式 release、Pack 或“准确性通过”的声明。

## 保护边界

- 只替换当前书名前缀的正式产物；共享库只更新当前书记录。
- 安装前后对其他书、母版 PDF 和共享库非当前书条目做 SHA-256 对比。
- 不调用远程 LLM 作准确性裁决。重新 OCR 时使用项目指定的本地 Paddle 环境。
- 不回退、清理或整理用户已有未提交成果。

## 页面审计证据版式（强制）

新生成的逐页证据图必须使用以下左右对照版式，供自动追溯和安装后人工抽查。旧页面不因版式升级而被要求重新检查；但已经发现且尚未修正的问题仍保持自动验证未通过状态。

- 左侧标题为 `PDF page N - ORIGINAL`，内容必须是母版 PDF 的原始渲染页。
- 左侧必须按实际 Paddle source block 的 bbox 绘制彩色框和数字编号，不得凭观察猜测框的位置。
- 右侧标题为 `PDF page N - original with source block boxes | structured delivery`。
- 右侧每条记录的数字和文字颜色必须与左侧对应 bbox 一致，并明确显示 structured unit/block ID、block type，以及 `source=pN:bM` 格式的精确来源定位。
- 每条记录必须同时展示 `RAW LOCATOR:` 原始 source block 内容和 `DELIVERY:` 实际交付内容；相似度分数不能代替原文对照。
- 跨页或多 block 合并必须列出所有 source locator，并在相关源页画出每个贡献 bbox。
- 公式、逻辑表格、图片和 Example 等资源条目也必须带 source locator，不能只显示一条没有 bbox 的资源说明。
- 自动审计记录及可选抽查事件都应绑定母版 PDF、渲染页、source block/bbox 和交付内容的 SHA-256；该版式不会放宽任何证据失效规则。
