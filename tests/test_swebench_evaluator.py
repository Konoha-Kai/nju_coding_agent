from __future__ import annotations

from pathlib import Path

from benchmarks.swebench_evaluator import build_eval_command, build_gold_validation_command


def test_build_eval_command_for_lite_predictions() -> None:
    command = build_eval_command(
        dataset="lite",
        predictions_path=Path("benchmarks/reports/run.predictions.jsonl"),
        run_id="nju-run",
        instance_ids=["sympy__sympy-20590", "django__django-12497"],
        max_workers=2,
    )

    assert command == [
        "swebench",
        "eval",
        "lite",
        "-p",
        "benchmarks/reports/run.predictions.jsonl",
        "--run-id",
        "nju-run",
        "-j",
        "2",
        "-i",
        "sympy__sympy-20590",
        "django__django-12497",
    ]


def test_build_eval_command_rejects_empty_predictions_path() -> None:
    try:
        build_eval_command(dataset="lite", predictions_path="", run_id="nju-run")
    except ValueError as exc:
        assert "predictions_path" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_build_gold_validation_command_uses_official_example_instance() -> None:
    command = build_gold_validation_command(run_id="validate-gold")

    assert command == [
        "swebench",
        "eval",
        "verified",
        "--gold",
        "-i",
        "sympy__sympy-20590",
        "--run-id",
        "validate-gold",
    ]
