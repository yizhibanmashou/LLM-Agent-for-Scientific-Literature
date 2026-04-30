# LLM-Agent 科学文献系统知识库处理

本仓库用于把教材或论文 PDF 转换成后续知识图谱、检索、记忆和 Agent 可以使用的结构化知识。当前主线不是做前端展示，而是把原始资料稳定地加工成 `data/structured/` 下的章节 JSON、公式库和表格库。

## 主流程

```text
PDF
  -> paper2latex
  -> tmp/paddle_output/*_full/main.tex
  -> knowledge_engineering
  -> data/structured/*.json
```

GLM OCR 是补充通道：

```text
PDF
  -> glmocr
  -> tmp/glmocr_output/*.json / *.md
  -> knowledge_engineering.structured_repair
  -> tmp/structured_repair/*
```

核心原则是：`paper2latex` 决定结构，GLM OCR 只补正文质量。章节边界、公式库、表格库、编号系统、`[[FORMULA:x]]` 和 `[[TABLE:x]]` 占位符都以 `paper2latex` / `knowledge_engineering` 的结构化结果为准；GLM OCR 只作为 prose block 和少量 inline math OCR 问题的参考文本，不直接覆盖结构信息。

## 目录说明

- `paper2latex/`：上游 PDF 到 LaTeX 的转换模块，已按 `rudaoshi/paper2latex` 当前 main 恢复，并清理了临时对照副本。
- `glmocr/`：GLM OCR 调用与批处理脚本，默认读取 `data/背景资料/`，输出到 `tmp/glmocr_output/`。
- `knowledge_engineering/`：把 `main.tex` 清洗、切分、标注并写入 `data/structured/`，同时包含 GLM OCR 辅助修复入口。
- `data/背景资料/`：原始教材 PDF 和参考资料，原则上不手工改写。
- `data/structured/`：最终结构化知识产物，是下游 graph、retrieval、memory、agent 的主要输入。
- `tmp/`：审计报告、修复补丁、GLMOCR/Paddle 输出、LLM 缓存和其他可复现数据统一放在这里，并随仓库上传给老师查看。
- `docs/release_audit.md`：上传 GitHub 前的路径、环境变量和体积检查记录。

## tmp 边界

新生成的中间和测试产物默认进入根目录 `tmp/`：

- `tmp/paddle_output/`：新运行的 paper2latex/Paddle 中间输出。
- `tmp/glmocr_output/`：新运行的 GLM OCR JSON/Markdown 输出。
- `tmp/structured_review/`：结构化质量审计结果。
- `tmp/structured_repair/`：GLM OCR 辅助修复候选、补丁和报告。
- `tmp/test_artifacts/`：测试和临时验证产物；`tmp/.pytest_cache`、`tmp/pytest_basetemp` 这类可再生缓存仍由 `.gitignore` 排除。

`data/structured/` 仍然是正式结构化结果；`data/背景资料/` 仍然是原始输入。`review_app/tmp/` 是历史审阅应用的局部产物，当前按原路径保留，其中旧 `source_file` 字符串不作为主流程路径来源。

## 常用命令

运行 GLM OCR，不触发时可先用 `--dry-run` 检查输入和输出路径：

```bash
python -m glmocr.run_glmocr --dry-run
python -m glmocr.run_glmocr
```

处理 paper2latex/Paddle 产出的 `main.tex`：

```bash
python -m knowledge_engineering.process ^
  -i tmp/paddle_output/chapter6_full/main.tex ^
  -o data/structured ^
  --chapter-name chapter6 ^
  --artifacts-dir tmp/knowledge_engineering
```

生成 GLM OCR 辅助修复候选：

```bash
python -m knowledge_engineering.structured_repair ^
  --structured-dir data/structured ^
  --glmocr-dir tmp/glmocr_output ^
  --audit-dir tmp/structured_review/current_2026_04_24 ^
  --out tmp/structured_repair/current ^
  --mode patch
```

## 环境变量

API 密钥和服务地址统一放在仓库根目录 `.env`，不要写进代码。可以从 `.env.example` 复制一份再填写真实值。常用变量包括：

- `ZHIPU_API_KEY`：GLM OCR 调用凭证。
- `GLMOCR_INPUT_DIR` / `GLMOCR_OUTPUT_DIR`：覆盖 GLM OCR 输入输出路径。
- `PAPER2LATEX_PADDLE_API_URL`、`PAPER2LATEX_PADDLE_API_TOKEN`、`PAPER2LATEX_PADDLE_PIPELINE`：paper2latex 的 Paddle 服务配置。
- `KE_LLM_*`：结构化修复里可选的 LLM 审核配置；未配置时走规则优先路径。

## 验证命令

```bash
python -B -c "import ast, pathlib; [ast.parse(p.read_text(encoding='utf-8')) for p in pathlib.Path('.').rglob('*.py') if 'tmp' not in p.parts and '__pycache__' not in p.parts]"
$env:PYTHONDONTWRITEBYTECODE="1"; python -m pytest paper2latex/tests -o cache_dir=tmp/.pytest_cache --basetemp=tmp/pytest_basetemp -q
$env:PYTHONDONTWRITEBYTECODE="1"; python -m knowledge_engineering.structured_repair --help *> tmp/test_artifacts/structured_repair_help.txt
$env:PYTHONDONTWRITEBYTECODE="1"; python -m glmocr.run_glmocr --help *> tmp/test_artifacts/glmocr_help.txt
```
