# LLM-Agent 科学教材知识库

把教材 chapter PDF 和 Paddle 解析结果加工为可追溯的结构化知识库、教材 Markdown 与离线 Study Reader。正式交付覆盖 Evolution、Genetics、PopGen 三本教材，共 68 个章节/附录。

## 数据流程

```text
data/背景资料/ 中可信 chapter PDF
  + data/paddle_output/ OCR / LaTeX
  -> knowledge_engineering
  -> data/structured/*.json
  -> textbook_exporter
  -> data/textbook/*.md + figures
  -> study_reader
```

`data/背景资料/` 中已经切分的 chapter PDF 是逐页准确性裁决的可信母版。Evolution 的统一母版按 profile 中的章节顺序确定性拼接，不依赖另一个未提供的完整 PDF。

## 可复现环境

- Python 3.12
- Node.js 24、npm 11
- Python 依赖由根目录 `pyproject.toml` 和 `uv.lock` 固定
- KaTeX 0.16.47 随项目安装，Reader 发布构建不依赖运行时 CDN

```powershell
uv sync --frozen
npm ci
python scripts/verify_project.py fast
```

发布级验证会执行三书逐页审计、全书数学检查、Reader 确定性离线重建、静态资源闭包和本地 Pack 验证：

```powershell
python scripts/verify_project.py release --build-packs
```

所有检查输出结构化 JSON；运行期间的完整报告写入 `tmp/release_check/report.json`。任一门禁失败都会返回非零退出码。

## 教材准确性审计

统一入口支持 Evolution、Genetics、PopGen 或 `all`：

```powershell
python scripts/audit_book_accuracy.py build --book all --dpi 72
python scripts/audit_book_accuracy.py verify --book all
python scripts/audit_book_accuracy.py status --book all
```

正式发布不接受 waiver。只有 `automated_valid=true`、未覆盖实质 source block 为零且证据哈希未漂移时，教材才能安装和打包。

逐页证据采用左右对照图：左侧显示原始 PDF 页及彩色 source-block bbox，右侧显示相同颜色编号的 `RAW LOCATOR` 和实际 `DELIVERY`。流程、字段说明、重建命令和示例图见[逐页准确性审计说明](docs/book-accuracy-audit.md)，强制门禁见[教材逐页准确性审计规范](BOOK_ACCURACY_AUDIT_STANDARD.md)。

![公式与 Example 映射示例](docs/assets/book-audit/genetics-formula-example.jpg)

## Study Reader

正式 Reader 数据保存在 `study_reader/data/generated/`，发布模式只复用已提交结果，不调用远程 LLM：

```powershell
python study_reader/build_study_reader.py --release --skip-llm
python scripts/build_study_reader_assets.py
python study_reader/serve_study_reader.py --port 8000
```

打开 `http://127.0.0.1:8000/study_reader/`。旧 MCP/Web 和 GROBID 自动启动属于 unsupported legacy，不是默认发布入口。

## 目录约定

| 路径 | 用途 | Git |
| --- | --- | --- |
| `data/structured/` | 正式结构化 JSON | 跟踪 |
| `data/textbook/` | 确定性教材 Markdown 与图片 | 跟踪 |
| `study_reader/data/generated/` | 68 章离线 Reader 数据 | 跟踪 |
| `book_audits/` | 三书 profile 与 correction | 跟踪 |
| `data/背景资料/` | 本地可信 chapter PDF | 忽略 |
| `data/paddle_output/` | 本地 OCR / LaTeX 输入 | 忽略 |
| `tmp/book_audits/<Book>/` | 可重建的逐页证据、台账、staging 与报告 | 忽略 |
| `Pack/` | 本地生成的交付包 | 忽略 |

`tmp/` 可以在发布完成后清空；重新审计时会从可信 chapter PDF、Paddle 输出、受版本控制的 profile/correction 和正式数据重建。不要手工修改大段 `data/textbook/`，应从 `data/structured/` 重新导出。
