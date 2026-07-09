# Data

`data/` stores the project’s formal data assets. Source code should read from this boundary instead of from temporary OCR or experiment directories.

## Top-Level Directories

- `背景资料/`: original PDFs and reference material. Local only, ignored by Git.
- `paddle_output/`: Paddle / paper2latex raw outputs. Local only, ignored by Git.
- `structured/`: structured knowledge outputs, including chapter JSON files and formula/table/example libraries.
- `textbook/`: readable Markdown exported from `structured/`; figures referenced by Markdown live in `textbook/figures/`.
- `figures/`: canonical cropped figure assets used by the exporter and figure library.
- `figure_library.json`: figure metadata, captions, source pages, bbox provenance, and asset mapping.
- `knowledge_graph/`: future graph/entity-relation exports; large exports remain local-only.

## Current Reading Boundary

The Study Reader currently uses:

- `data/textbook/Evolution_chapter*_textbook.md`
- `data/textbook/Evolution_appendix*_textbook.md`
- `data/textbook/Genetics_chapter*_textbook.md`
- `data/textbook/figures/*.png`
- `study_reader/data/generated/study_dataset.json`

Current local counts:

- Evolution textbook files: 36
- Genetics textbook files: 27
- textbook figure files: 381

## Rebuild Markdown

```powershell
python -m textbook_exporter --structured-dir data/structured --out-dir data/textbook
```

Chapter-scoped export:

```powershell
python -m textbook_exporter --structured-dir data/structured --out-dir data/textbook --chapters Evolution_chapter25
```

## Maintenance Rules

1. Do not hand-edit raw source material unless absolutely necessary.
2. Temporary or experimental outputs belong in `tmp/`.
3. Structured outputs must keep stable fields and traceable provenance.
4. `textbook/` should be regenerated from `structured/`.
5. Inline LaTeX repairs should only touch formula spans, not whole paragraphs or table structure.
6. Figure filenames should stay aligned with textbook figure ids, e.g. `figures/Evolution_5.1.png` and `figures/Genetics_5.1.png`.
7. `背景资料/`, `paddle_output/`, and `knowledge_graph/knowledge_graph_export.json` are local-only assets and should remain ignored by Git.
