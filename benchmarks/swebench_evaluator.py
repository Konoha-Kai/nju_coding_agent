from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def build_eval_command(
    dataset: str,
    predictions_path: Path | str,
    run_id: str,
    instance_ids: list[str] | None = None,
    max_workers: int = 1,
) -> list[str]:
    if not str(predictions_path).strip():
        raise ValueError("predictions_path must not be empty")
    if not run_id.strip():
        raise ValueError("run_id must not be empty")
    predictions = (
        predictions_path.as_posix()
        if isinstance(predictions_path, Path)
        else str(predictions_path)
    )
    command = [
        "swebench",
        "eval",
        dataset,
        "-p",
        predictions,
        "--run-id",
        run_id,
        "-j",
        str(max_workers),
    ]
    if instance_ids:
        command.extend(["-i", *instance_ids])
    return command


def build_gold_validation_command(run_id: str = "validate-gold") -> list[str]:
    if not run_id.strip():
        raise ValueError("run_id must not be empty")
    return [
        "swebench",
        "eval",
        "verified",
        "--gold",
        "-i",
        "sympy__sympy-20590",
        "--run-id",
        run_id,
    ]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or run official SWE-bench evaluation commands")
    parser.add_argument("--dataset", default="lite", help="SWE-bench dataset alias or HuggingFace id")
    parser.add_argument("--predictions-path", help="Path to predictions JSONL")
    parser.add_argument("--run-id", required=True, help="Stable SWE-bench run id")
    parser.add_argument("--instance-id", action="append", default=[], help="Specific instance id to evaluate")
    parser.add_argument("--max-workers", type=int, default=1, help="Number of evaluator workers")
    parser.add_argument("--gold-validation", action="store_true", help="Use official gold validation instance")
    parser.add_argument("--dry-run", action="store_true", help="Print command without running it")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.gold_validation:
        command = build_gold_validation_command(run_id=args.run_id)
    else:
        if not args.predictions_path:
            raise SystemExit("--predictions-path is required unless --gold-validation is used")
        command = build_eval_command(
            dataset=args.dataset,
            predictions_path=args.predictions_path,
            run_id=args.run_id,
            instance_ids=args.instance_id,
            max_workers=args.max_workers,
        )

    print(" ".join(command))
    if args.dry_run:
        return 0
    completed = subprocess.run(command)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
