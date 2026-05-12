# paper2latex

`paper2latex` is the upstream PDF-to-LaTeX conversion layer used by this repo.
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
