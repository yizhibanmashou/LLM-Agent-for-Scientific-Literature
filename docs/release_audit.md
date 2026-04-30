# Release Audit

This note records the upload-preparation checks for `yizhibanmashou/LLM-Agent-for-Scientific-Literature`.

## Current Status

- The working tree is prepared as a single repository rooted at this folder.
- Root `.env` is the only intended local secret file. Real `.env` files are ignored; `.env.example` is safe to commit.
- Temporary and generated run artifacts are kept under root `tmp/`; root `tmp/` is included in Git because the reviewer may need the reproduced data. Disposable pytest/bytecode caches are still ignored.
- `review_app/tmp/` is retained in place as an explicit legacy review-app exception.
- The extra upstream/backup copies of `paper2latex` were deleted. The retained `paper2latex/` directory is the production module.
- Generated source paths in active code and main generated data now use `tmp/paddle_output` and `tmp/glmocr_output` instead of stale `data/paddle_output` or `data/glmocr_output` references.
- Some `source_file` strings inside `review_app/tmp/` still preserve their historical `data/paddle_output` values; this directory is intentionally left untouched as requested.

## Upload Notes

- No single non-ignored file is currently over GitHub's 100 MB hard limit.
- The non-ignored working tree is about 599 MiB, mostly because raw PDFs, root `tmp/`, and generated JSON assets are included.
- The remote repository currently has `main` at `6967eb96bffc3ac0fd60fca67451725f4d0f5396`; overwriting it should be done with a deliberate force push only after a final local review.

## Verification Commands

```powershell
python -B -c "import ast, pathlib; [ast.parse(p.read_text(encoding='utf-8-sig')) for p in pathlib.Path('.').rglob('*.py') if 'tmp' not in p.parts and '__pycache__' not in p.parts]"
$env:PYTHONDONTWRITEBYTECODE="1"; python -m pytest paper2latex/tests -o cache_dir=tmp/.pytest_cache --basetemp=tmp/pytest_basetemp -q
$env:PYTHONDONTWRITEBYTECODE="1"; python -m knowledge_engineering.structured_repair --help *> tmp/test_artifacts/structured_repair_help.txt
$env:PYTHONDONTWRITEBYTECODE="1"; python -m glmocr.run_glmocr --help *> tmp/test_artifacts/glmocr_help.txt
```
