# Data

`data/` stores the project’s formal data assets, not source code.

This is the boundary that downstream systems should read from.

## Top-Level Directories

- `背景资料/`
  Original PDF教材、参考资料、人工收集素材。本地保留并被 Git 忽略，不上传。
- `paddle_output/`
  Paddle / paper2latex 原始输出。本地保留并被 Git 忽略，是 structured 生成和 figure relink 的主要布局证据。
- `glmocr_output/`
  GLM OCR 辅助输出。本地保留并被 Git 忽略，只作为修复和核查参考。
- `structured/`
  Structured knowledge outputs, including chapter JSON files, formula library, table library, example library, and figure placeholders
- `textbook/`
  Readable Markdown exported from `structured/`, saved as `chapterX_textbook.md`
- `figures/`
  Cropped figure assets referenced by `textbook/`
- `figure_library.json`
  Figure metadata, captions, source pages, bbox provenance, and asset mapping
- `knowledge_graph/`
  Future graph or entity-relation outputs; large exports are local-only and ignored

## Recommended Reading Order

1. `背景资料/` to understand the raw input
2. `data/paddle_output/` to inspect the LaTeX-stage intermediate result
3. `structured/` as the direct input for graph / retrieval / memory / agent layers
4. `textbook/` as the readable rendered form for review and downstream display
5. `figure_library.json` and `figures/` when auditing image placement

## Current Data Boundary

`data/structured/` is the knowledge base. `data/textbook/` is the readable derivative. `data/figures/` and `data/figure_library.json` are the formal figure assets used by textbook Markdown.

Current baseline counts:

- structured unit JSON files: 988
- formula library entries: 2248
- table library entries: 164
- example library entries: 323
- figure image files: 228
- textbook Markdown files: 36

All downstream systems should treat these as the canonical inputs:

- knowledge graph
- retrieval
- memory
- agent
- teaching system

`data/textbook/` is rebuilt from the repo-root exporter:

```powershell
python -m textbook_exporter --structured-dir data/structured --out-dir data/textbook
```

Chapter-scoped export:

```powershell
python -m textbook_exporter --structured-dir data/structured --out-dir data/textbook --chapters chapter25
```

The maintenance goal for `data/structured/` is structural stability, not prose polish:
chunk order, block order, formula references, table references, and source metadata must stay traceable.

## Maintenance Rules

1. Do not hand-edit raw source material unless absolutely necessary.
2. Temporary or experimental outputs belong in `tmp/`.
3. Structured outputs must keep stable fields and traceable provenance.
4. `textbook/` should always be regenerated from `structured/`.
5. Debug caches, trial outputs, and run junk do not belong in `data/`.
6. Inline LaTeX repairs should only touch formula spans, not whole paragraphs or table structure.
7. High-confidence repairs backed by PDF rendering, Paddle raw layout, or direct source evidence may be applied to `structured/`; exploratory candidates should stay in `tmp/`.
8. Figure image files should contain only the figure body; captions live in `figure_library.json` and are expanded by the textbook exporter.
9. `背景资料/`, `paddle_output/`, `glmocr_output/`, and `knowledge_graph/knowledge_graph_export.json` are local-only assets and should remain ignored by Git.
