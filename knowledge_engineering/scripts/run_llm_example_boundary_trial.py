"""Run the LLM example-boundary trial without touching data/structured."""

from __future__ import annotations

import argparse
from pathlib import Path

from knowledge_engineering.processors.llm_example_boundary import (
    DEFAULT_ARTIFACTS,
    DEFAULT_OUTPUT,
    parse_chapter_list,
    run_llm_example_boundary_trial,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run guarded LLM Example boundary trial.")
    parser.add_argument("--structured-dir", default=str(PROJECT_ROOT / "data" / "structured"))
    parser.add_argument("--project-root", default=str(PROJECT_ROOT))
    parser.add_argument("--chapters", "--llm-example-chapters", default="chapter6")
    parser.add_argument("--max-windows", "--llm-example-max-windows", type=int, default=20)
    parser.add_argument("--workers", "--llm-example-workers", type=int, default=1)
    parser.add_argument("--output-structured-dir", "--out", default=str(PROJECT_ROOT / DEFAULT_OUTPUT))
    parser.add_argument("--artifacts-dir", default=str(PROJECT_ROOT / DEFAULT_ARTIFACTS))
    parser.add_argument(
        "--include-all-example-headings",
        action="store_true",
        help="Review every raw Example heading instead of only suspicious/missing examples.",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Discard existing candidate/progress and start over.",
    )
    args = parser.parse_args()

    summary = run_llm_example_boundary_trial(
        structured_dir=Path(args.structured_dir),
        project_root=Path(args.project_root),
        output_structured_dir=Path(args.output_structured_dir),
        artifacts_dir=Path(args.artifacts_dir),
        chapters=parse_chapter_list(args.chapters),
        max_windows=args.max_windows,
        suspicious_only=not args.include_all_example_headings,
        resume=not args.no_resume,
        workers=max(1, args.workers),
    )
    print(
        "LLM example boundary trial: "
        f"windows={summary['windows']}, "
        f"auto_applied={summary['auto_applied']}, "
        f"review_queue={summary['review_queue']}, "
        f"output={summary['output_structured_dir']}, "
        f"artifacts={summary['artifacts_dir']}"
    )


if __name__ == "__main__":
    main()
