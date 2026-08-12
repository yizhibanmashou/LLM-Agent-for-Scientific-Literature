# paper2latex

> **Unsupported legacy service.** The former MCP/Web entry points and automatic
> GROBID startup are not part of the supported build, CI, or release surface.
> The package is retained only because maintained batch scripts still import
> its Paddle conversion, structure parsing, and LaTeX generation modules.

`paper2latex` is the historical upstream PDF-to-LaTeX conversion layer used by this repo.
In this workspace it is treated as the source stage that feeds `tmp/paddle_output/`.

## Role in the Pipeline

```text
PDF -> paper2latex / Paddle -> tmp/paddle_output/*_full/main.tex -> knowledge_engineering -> data/structured -> textbook_exporter -> data/textbook
```

`paper2latex` itself is not the final knowledge-base layer. The production data
boundary is now `data/structured` and `data/textbook`.

## What This Code Covers

- PDF to LaTeX conversion orchestration
- citation / bibliography handling
- structure parsing
- formula and figure extraction helpers

## Notes

- This repository no longer treats legacy GROBID wording as the primary workflow.
- The downstream structured/textbook pipeline lives in `knowledge_engineering/` and `textbook_exporter/`.
- Test and scratch outputs should stay under `tmp/`.
