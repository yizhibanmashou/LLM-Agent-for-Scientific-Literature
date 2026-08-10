# Project Handoff

## 2026-08-09：教材逐页准确性审计规范（当前状态，覆盖下方旧 PopGen 结论）

- 用户明确要求 PopGen 先进入正式 `data/`；已使用显式自动发现项豁免完成原子安装。正式目录仅写入 PopGen 的 structured、textbook 与两套正式图片，审计证据、报告和安装前快照仍只位于 `tmp/book_audits/PopGen/`。
- 安装报告：`tmp/book_audits/PopGen/reports/installation.json`；`protected_hashes_unchanged=true`，Genetics、Evolution、其他书籍及母版 PDF 未被修改。当前豁免项为 197 个尚待自动归因的 Paddle source blocks，不等同于 197 段正文缺失。
- 项目强制规范：`BOOK_ACCURACY_AUDIT_STANDARD.md`；所有新审计统一位于 `tmp/book_audits/<Book>/`。
- 统一入口：`scripts/audit_book_accuracy.py`（`build` / `verify` / `install`）；`scripts/record_book_visual_review.py` 仅用于安装后可选抽查记录。
- PopGen 本轮仅含 Chapter 2、3、4、6，共 207 页；母版范围固定为 59–106、109–162、165–210、271–329。
- 旧 `tmp/popgen/`、`tmp/popgen_accuracy/`、`tmp/pdfs/popgen_accuracy/` 仅登记为 legacy 输入，没有删除或覆盖。
- 下方旧段落所称 “207 页已渲染、36 条队列结案、valid=true” 不再单独构成准确性验收；当前证据链要求全部范围页面、block 和资源通过自动检查并绑定来源哈希。
- 当前新审计目录：`tmp/book_audits/PopGen/`。人工台账已取消安装门禁作用；自动验证全部通过后即可原子安装到 `data/`，之后由用户抽查。
- 第一次重建已发现旧审计漏项：Table 6.2 的完整源表位于 Chapter 6 local page 8（master page 278），旧正式库却是 `body not recovered` stub；已在 staging 中按精确 block/bbox 恢复，仍须通过自动验证。
- 本轮不调用远程 LLM，不处理 Evolution，不移动正在进行的 `tmp/genetics_accuracy_audit/`。

复现命令：

```powershell
python scripts/audit_book_accuracy.py build --book PopGen
python scripts/audit_book_accuracy.py verify --book PopGen
python scripts/audit_book_accuracy.py install --book PopGen
```

## 2026-08-09：PopGen 准确性、三书展示与 Pack 导出

本节为 UTF-8 正文，是本轮任务的最终状态来源。

### PopGen 准确性审计

- 审计入口：`python scripts/audit_popgen_accuracy.py --install`
- 锁定范围：Chapter 2 = 59–106，Chapter 3 = 109–162，Chapter 4 = 165–210，Chapter 6 = 271–329。
- 207 页均已渲染；页面清单：`tmp/pdfs/popgen_accuracy/page_manifest.json`。
- 最终报告：`tmp/popgen_accuracy/accuracy_audit.json`，`valid=true`。
- 36 条人工队列全部结案：1 条幽灵字符自动删除，35 条修复或有证据保留，未决为 0。
- 安装结果：103 个 structured unit、115 个公式、28 个表格、73 个图片记录、4 个 textbook。
- 修复覆盖断词、跨页括号/公式、公式左右操作数、重复图示公式、表注误入正文、跨表中断句和 OCR 错字。
- 审计阶段远程 LLM 调用为 0：所有异常均由 PDF/Paddle 页面证据或确定性结构规则解决。
- 安装前后 4,424 个非 PopGen 文件 SHA-256 完全一致。

### 三书 Study Reader

- 配置：Evolution 36、Genetics 28、PopGen 4，共 68 个章节/附录；PopGen 默认章为 `PopGen_chapter2`。
- `textbook_exporter` 支持 `--books Evolution,Genetics,PopGen`，并保留 `--book-id`。
- 轻量目录：`study_reader/data/generated/study_dataset.json`，约 27 KB，不含内嵌章节正文。
- 章节数据：`study_reader/data/generated/chapters/*.json`，共 68 个；前端按需加载、缓存，并兼容旧版内嵌 `data`。
- Evolution/Genetics 共 59 个已有 LLM 结果从 v3 数据集保留；PopGen 定向判定共 6 个请求，全部命中 `tmp/llm_cache`，远程调用 0。
- 静态资源闭包：`.cloudflare-assets/asset_manifest.json`，68 章、454 张实际引用图片、596 个文件，构建时缺文件即失败。
- 本地浏览器验收已实际切换三本书；PopGen Chapter 2 正文、公式、表格和图片正常，控制台错误为 0。
- Cloudflare 配置恢复为 `wrangler.jsonc`，Worker 名称为 `literature`，资源目录为 `.cloudflare-assets`。
- 目标 URL：`https://literature.13260051624.workers.dev/`。
- 最终部署尚未完成：Wrangler 在非交互环境要求 `CLOUDFLARE_API_TOKEN`。当前线上仍是旧版（63 章、仅 Evolution/Genetics、8.1 MB 内嵌数据，PopGen 资源 404）。配置 token 后在项目根目录运行：

```powershell
$env:CLOUDFLARE_API_TOKEN = '<具有 Workers Scripts Edit 权限的 token>'
npx --yes wrangler deploy
```

不要使用 `--temporary`，否则会部署到临时账户而不是指定 `literature` Worker。

### Pack

- Evolution 已从根目录无损迁移到 `Pack/EvoPack/`；迁移前后逐文件 SHA-256 完全一致，`verification.json` 为 `valid=true`。
- 通用入口：`scripts/package_book_delivery.py`。支持单章、连续范围、离散章节与附录；临时构建、完整验证后原子安装，非空目标默认拒绝覆盖。
- 已生成验收包 `Pack/GeneticsPack/`（Chapter 3–8，共 6 章），`verification.json` 为 `valid=true`。
- 总索引：`Pack/manifest.json`，当前包含 EvoPack 和 GeneticsPack。

常用命令：

```powershell
python scripts/package_book_delivery.py --book Genetics --chapters 3-8 --output Pack/GeneticsPack
python scripts/package_book_delivery.py --book PopGen --chapters 2,3,4,6 --output Pack/PopGenPack
python scripts/package_book_delivery.py --book Evolution --chapters 10-12 --appendices 1 --output Pack/EvolutionSelection
```

已有非空目标需要显式增加 `--replace`；新包仍会先在 `tmp/pack_staging/` 验证成功，再替换旧包。

### 验证

核心回归与新增验收合计 111 项通过：

```powershell
python -m pytest paper2latex/tests/unit/test_textbook_exporter.py `
  paper2latex/tests/unit/test_example_pipeline.py `
  paper2latex/tests/unit/test_structured_fusion.py `
  paper2latex/tests/unit/test_multibook_reader_pack.py -q
```

唯一警告是 pytest cache 的 Windows `WinError 5`，不影响测试或交付文件。

本文档用于让新的 Codex 对话直接接管当前知识库处理工作。它记录本次连续工作中已完成的 Evolution 打包、PopGen 处理、Genetics 全章审计，以及 Genetics 全书重建与结构化修复的设计、入口、数据边界和验证方式。

## 1. 工作区约束

- 项目根目录：`D:\大学资料\大二\LLM-Agent科学文献系统知识库处理`
- 用户已有大量 Genetics structured、textbook、脚本修改和新增文件。这些属于用户工作，不得回退、覆盖无关内容或使用 destructive git 命令。
- 所有 OCR、切章副本、日志、页面证据、重建 staging、安装前快照和失败产物都必须留在 `tmp/`。
- `data/` 只放最终验证通过的交付物。
- Evolution、PopGen 和 Genetics 的正式资源按书名前缀隔离；更新 Genetics 时不得改变其他书的数据或共享库中的非 Genetics 条目。
- 本轮规则流程不调用远程 LLM。PaddleOCR 使用 conda 环境 `py312`。

## 2. Evolution 打包

正式交付目录为 `EvoPack/`，由 `scripts/package_evolution_delivery.py` 生成。

- 30 个章节目录：`chapter01` 至 `chapter30`
- 6 个附录目录：`appendix01` 至 `appendix06`
- 每个目录包含 structured JSON、四类 library、figures、`textbook.md` 和 `manifest.json`
- 根目录包含 `README.md`、`manifest.json` 和 `verification.json`
- 未复制 PDF、OCR 中间文件或绝对路径

最终验证结果：

- structured：907
- formulas：64
- tables：164
- figures：229
- examples：323
- sections：36
- `EvoPack/verification.json`：`valid=true`

常用命令：

```powershell
python scripts/package_evolution_delivery.py
python scripts/package_evolution_delivery.py --verify-only
```

## 3. PopGen 第 2、3、4、6 章

来源为 `data/背景资料/Principle of population genetics 4th ed - Hartl and Clark.pdf`，书名前缀固定为 `PopGen`。

实际使用的无章节间空白页范围：

```text
chapter2 59-106  48 pages
chapter3 109-162 54 pages
chapter4 165-210 46 pages
chapter6 271-329  59 pages
```

处理入口：

- `scripts/split_popgen_chapters.py`
- `scripts/finalize_popgen_delivery.py`
- Paddle 批处理入口：`scripts/run_paddleocr_batch.py`

最终结果：

- structured units：103
- numbered formulas：115，全部由 Paddle layout 中的 formula label 恢复
- tables：28
- figures：73
- formal examples：0；原 OCR 中也未检测到 Example headings
- textbook：4 个，直接 placeholder、图片链接和公式 tag 验证均通过
- 远程 LLM 调用：0
- 报告：`tmp/popgen/final_report.json`，`valid=true`

正式文件位于：

- `data/structured/PopGen_chapter*_*.json`
- `data/structured/PopGen_*_library.json`
- `data/figures/PopGen_*.png`
- `data/textbook/PopGen_chapter*_textbook.md`
- `data/textbook/figures/PopGen_*.png`

## 4. Genetics 旧数据全面审计

唯一页码基准为 `data/背景资料/Genetics.pdf`，共 992 页。审计脚本和报告：

- `scripts/audit_genetics_chapter_splits.py`
- `scripts/audit_genetics_structured_issues.py`
- `tmp/genetics_full_audit/genetics_chapter_split_audit.md`
- `tmp/genetics_full_audit/genetics_chapter_split_audit.csv`
- `tmp/genetics_full_audit/evidence/`
- `tmp/genetics_full_audit/structured_diagnosis/report.md`

审计结论：

- 旧切章仅第 1、2、9 章准确。
- 第 10 章正文范围正确，但多了前置空白页 266。
- 其余 23 章边界错误。
- 旧 chapter 27 错误包含 791-992；正确正文只到 818。
- 96、266、306、698 是章节间空白页，不属于相邻章节。
- Chapter 14 正确标题：`Principles of Marker-based Analysis`
- Chapter 22 正确标题：`Genotype × Environment Interaction`

正确范围：

```text
01 21-35   02 36-50   03 51-66   04 67-95   05 97-122
06 123-146 07 147-192 08 193-220 09 221-265 10 267-305
11 307-334 12 335-366 13 367-392 14 393-444 15 445-504
16 505-550 17 551-566 18 567-593 19 594-608 20 609-640
21 641-668 22 669-697 23 699-726 24 727-738 25 739-756
26 757-790 27 791-818
appendix1 819-992
```

旧结构化问题根因：

- Table 2.1 星号说明被错误保存成普通 discussion；旧 exporter 的 rows 分支也会提前 return。
- 旧 Paddle 中有 104 次 Example 标题，但旧 Genetics 重建把所有内容写成 discussion，导致共享 example library 中 Genetics 为 0。
- Paddle 已保留同页段落边界，旧 LaTeX section 重建将整节压平；相反，跨页连续句又被错误断开。
- 扫描 PDF 没有字体 metadata，Paddle 几乎不输出 bold/italic；旧通用解析还会移除部分样式命令。
- 第 3、4 章 12 张图存在约 0.845-1.892 度系统倾斜，OpenCV expanded rotation 试验可纠正。
- schema/exporter 原来不能表达无正文父标题。
- `Genetics_chapter4_004 · Introduction` 是错误切章从 Figure 4.1 中段开始后产生的伪节点。

## 5. Genetics 全书重建实现

核心入口：

- `scripts/rebuild_genetics_book.py`
  - 正确切割 27 章和一个 `Genetics_appendix1`
  - 编排 `py312` PaddleOCR
  - `--verify-only` 检查切章和 OCR 完整性
  - `--install` 仅在 staging verification 有效时执行前缀过滤原子安装
- `scripts/build_genetics_staging.py`
  - 直接读取 Paddle `paddle_raw_response.json` 的逐页 layout blocks
  - 保留 source page、printed page、bbox 和 source block IDs
  - 生成段落级 structured、四类资源、textbook、deskew 审计和 verification

Paddle 单任务对 174 页附录只返回前 100 页；一次 74 页 supplement 还退化成无分页字典，因此 OCR 层最终采用三个任务：

```text
Genetics_appendix1.pdf       source 819-992，Paddle 读取前 100 页，即 819-918
Genetics_appendix1_part2.pdf source 919-955，仅作为 tmp OCR supplement
Genetics_appendix1_part3.pdf source 956-992，仅作为 tmp OCR supplement
```

三个 OCR 响应在 staging builder 中按源页合并，正式数据仍只有一个 `Genetics_appendix1`。补充分片不会进入 `data/`。

合并附录内部边界：

```text
819-834 Appendix 1
835-846 Appendix 2
847-864 Appendix 3: Further Topics in Matrix Algebra and Linear Models
865-880 Appendix 4: Maximum Likelihood Estimation and Likelihood-ratio Tests
881-902 Appendix 5: Computing the Power of Statistical Tests
903-960 Literature Cited
961-972 Author Index
973-982 Organism and Trait Index
983-992 Subject Index
```

结构化行为：

- 每个 Paddle text block 默认成为独立 paragraph block。
- 只在跨页且满足“上一块没有句末标点、下一块小写延续、没有标题/图表边界”时合并，并保留多个 source block IDs。
- Example 使用章节作用域；合并附录内额外使用 `A1` 至 `A5` 作用域，避免局部编号冲突。
- 表格使用 `notes` 数组保存脚注；Table 2.1 的星号说明从 Paddle `vision_footnote` 绑定到表格。
- 空父标题使用 `node_kind: heading`、`allow_empty: true`、`blocks: []`。
- Chapter 4 的 OCR `Introduction` 伪标题被拒绝，正文归入正确层级。
- Subject Index 解析结果只用于定位候选词，不能直接决定 `[[term]]` 样式；黑体、斜体一律回看原 PDF 字形，最终产物不存在自动猜测或嵌套样式标记。
- figure 从正确切章 PDF 和 Paddle bbox 重裁；deskew 同时比较正负旋转候选，使用扩展白色画布，并以原页正文基线、表格线或坐标框判断方向；设计性斜线不触发旋转。

Exporter 修改：

- `textbook_exporter/exporter.py` 支持 heading-only chunk。
- rows、HTML 和无数据表格路径都能渲染 `notes`。
- legacy `markdown_body` 若是整张表的重复 Markdown 副本则不重复输出；否则展开内部资源引用后渲染。

安全安装：

- staging：`tmp/genetics_rebuild/staging/`
- 安装前快照：`tmp/genetics_rebuild/preinstall_snapshots/<timestamp>/`，每次安装都创建独立快照。
- 正式替换范围：Genetics structured、专用 libraries、shared examples 中 Genetics 条目、Genetics figures、textbooks、textbook figures、两侧 `figures/examples/` 中的 Genetics 无编号图片，以及 `data/背景资料/Genetics_*.pdf`
- 母本 `data/背景资料/Genetics.pdf` 不匹配 `Genetics_*.pdf`，不会被修改。
- Evolution、PopGen 和共享 example library 中非 Genetics 条目必须保留。

## 6. Genetics 全量准确性审计与最终结果

以 `data/背景资料/Genetics.pdf` 为唯一判断依据，已完成 PDF 1-992 页原页视觉审计。自动匹配只用于定位，最终状态均由原页视觉确认。事实来源：

- 全量审计：`tmp/genetics_accuracy_audit/report.json`，`valid=true`
- staging 验证：`tmp/genetics_rebuild/verification.json`，`valid=true`
- 关键问题验收：`tmp/genetics_rebuild/key_acceptance.json`
- 安装后验证：`tmp/genetics_rebuild/postinstall_verification.json`，`valid=true`
- 最终安装前快照：`tmp/genetics_rebuild/preinstall_snapshots/20260809T200021.916456Z/`

审计覆盖和最终数量：

- 原 PDF：992/992 页已判定；前置内容 1-20，正文 21-818，合并附录 819-992
- structured：456 个单元、9178 个 block，全部有原页证据，无待判定项
- formulas：1813 条，全部逐项核对
- tables：75 个逻辑表格，全部逐页核对；Table 6.1 和 Table 15.6 的续表已合并并保留 parts/source_pages
- figures：152 张，全部比较原页、原裁图和修复图；正式 figures 与 textbook figures 名称和 SHA256 逐文件一致
- Examples：157 个，全部核对起止范围并合入共享 `example_library.json`
- textbook：28 个，即 27 章加 `Genetics_appendix1`；无缺字、孤立断词、缺图、缺续表、重复表格或未解析占位符
- 无编号 Example 图片：24 张，均安装到资源库和 textbook 的 `figures/examples/`
- deskew：75 张接受修正、77 张保持原样；接受项最大残余倾斜 0.475°，无裁字，设计性斜线不会触发旋转
- 远程 LLM 调用：0

关键修复：

- 修复 `lethal equiv-alents`、`1nus`→`Thus`、`funda-/mental`、`heri-/tability`、`interactions`→`iterations`、PDF 890 页重复前缀等跨页断词和 OCR 错误。
- 修复 Table 6.1、Table 15.6 跨页续表丢失；所有表格继续执行“小节内沉底”，正文保留语义引用，每个逻辑表只在所属小节末尾完整渲染一次。
- Table 2.1 星号说明仅作为表格 `notes` 渲染，不再成为普通 discussion。
- 修复非空单元误标 `node_kind: heading`；只有真正无正文的父标题允许 heading-only。
- Subject Index 只提供样式候选定位，`[[...]]` 不由索引自动决定；所有样式以原页字形为准，最终无嵌套或交叉样式标记。
- deskew 修复 OpenCV `-90°` 归一化、旋转符号、实际写入角度复测、扩边裁切和无改善拒绝替换。
- 修复 `$…$` / `$$…$$` 混排和残缺定界符：表格单元格一律使用行内数学，块公式定界符独占一行；同时按原 PDF 修复8条损坏块公式和 PDF 282、557、840、861、877页的行内公式。严格 KaTeX 校验覆盖28个 textbook、4167个结构化 block、1813条公式和1225个 Study Reader 公式资产，错误数为0。

安装后检查 3892 个受保护的非 Genetics 文件及源 `Genetics.pdf`，均无变化或缺失。共享 Examples 中 323 条非 Genetics 记录数量与规范化内容哈希均保持不变。安装只替换 Genetics 产物，不处理工作区其余未提交修改。

## 7. 测试与复现命令

Genetics 专项测试 `paper2latex/tests/unit/test_genetics_rebuild.py` 共34项；与 exporter 回归合计63 passed。覆盖跨页表合并、小节沉底、Table 2.1 脚注、断词/OCR 修正、样式不嵌套、非空节点语义、KaTeX 定界符/公式修复、deskew 角度与裁切、安装保护和 stage/install 一致性。

除一个无关且缺少 `tmp/structured_boundary_audit/audit_boundaries.py` 临时 fixture 的旧测试文件外，全套测试结果为240 passed、7 skipped。直接运行未排除的全套测试时，该缺失 fixture 导致19项失败；这些失败不涉及 Genetics 代码或产物。pytest cache 另有一个 Windows `WinError 5` warning，不影响结果。

完整复现：

```powershell
$env:TEMP=(Resolve-Path tmp).Path
$env:TMP=$env:TEMP
python scripts/build_genetics_staging.py
python scripts/audit_genetics_accuracy.py
python scripts/rebuild_genetics_book.py --install
python scripts/audit_genetics_accuracy.py --stage . --skip-render
node scripts/validate_textbook_math.js --books Genetics
python -m pytest paper2latex/tests/unit/test_genetics_rebuild.py -q
python -m pytest paper2latex/tests -q --ignore=paper2latex/tests/unit/test_structured_boundary_audit.py
```

## 8. 后续接管状态与清单

截至 2026-08-10，本轮 Genetics 全量审计、修复、隔离重建、正式安装和安装后验证均已完成，无待核对项或待安装 staging。新对话接管时：

1. 先读取 `tmp/genetics_accuracy_audit/report.json` 和 `tmp/genetics_rebuild/postinstall_verification.json`，两者应均为 `valid=true`。
2. 所有页面渲染、联系表、角度报告、审计台账、日志、快照和失败产物只能保留在 `tmp/genetics_accuracy_audit/` 或 `tmp/genetics_rebuild/`。
3. 再次安装会在 `tmp/genetics_rebuild/preinstall_snapshots/` 创建新的时间戳快照，并复核受保护文件、323 条非 Genetics Examples 及 stage/install 哈希。
4. 不要删除时间戳快照，除非用户明确确认不再需要回溯。
5. staging 中的通用别名 `formula_library.json` 和 `table_library.json` 只用于 dry-run pipeline 审计，不会进入 `data/`。
6. 不得用自动化结果替代原 PDF 视觉判断；任何新增修正都必须记录源页和 bbox，并重新完成相应视觉验收。

## 9. GitHub 发布状态

用户最终指定直接提交并推送 `main`，不创建功能分支或 PR；提交信息使用一个词：`Genetics修复`。远程为 `origin = https://github.com/yizhibanmashou/LLM-Agent-for-Scientific-Literature.git`。

发布范围仅包括 Genetics 正式产物、共享 Examples 中的 Genetics 合入结果、Genetics 审计/重建脚本、相关 exporter/KaTeX 校验器、Study Reader Genetics 修正、回归测试和本交接文档。README、Evolution、PopGen、Pack、`node_modules/` 及其他工作区未提交成果不属于该提交。

发布验收以 `main` 上提交信息为 `Genetics修复` 的 commit 为准；推送前后均应确认 `origin/main` 与本地 `main` 无 ahead/behind，并保留本节所列验证结果。
