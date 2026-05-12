# Data

`data/` stores the project’s formal data assets, not source code.

This is the boundary that downstream systems should read from.

## Top-Level Directories

- `背景资料/`
  Original PDF教材、参考资料、人工收集素材
- `structured/`
  Structured knowledge outputs, including chapter JSON files, formula library, table library, and optionally `example_library.json`
- `textbook/`
  Readable Markdown exported from `structured/`, saved as `chapterX_textbook.md`
- `knowledge_graph/`
  Future graph or entity-relation outputs; not the main processing entry yet

## Recommended Reading Order

1. `背景资料/` to understand the raw input
2. `tmp/paddle_output/` to inspect the LaTeX-stage intermediate result
3. `structured/` as the direct input for graph / retrieval / memory / agent layers
4. `textbook/` as the readable rendered form for review and downstream display

## Current Data Boundary

`data/structured/` is the knowledge base. `data/textbook/` is the readable derivative.

Current baseline counts:

- structured unit JSON files: 987
- formula library entries: 2248
- table library entries: 164
- example library entries: 322
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
