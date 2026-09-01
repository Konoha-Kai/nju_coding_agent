# HumanEval Full Benchmark Report

Date: 2026-09-01

## Objective

Use the public OpenAI HumanEval dataset as a lightweight coding-agent benchmark to evaluate the current `nju_ai_coding_agent` implementation without Docker.

This benchmark is function-level code generation and can run directly from the local dataset without Docker. It does not measure repository-level issue fixing, dependency handling, or multi-file patch quality.

## Environment

- Project: `nju_ai_coding_agent`
- Python environment: `C:\Users\23639\.conda\envs\nju\python.exe`
- Model: `deepseek-chat`
- Dataset: `benchmarks/data/HumanEval/HumanEval.jsonl.gz`
- Dataset source: OpenAI HumanEval public dataset
- Output directory: `benchmarks/reports/humaneval_full_deepseek`

## Command

```powershell
$env:HTTP_PROXY='';
$env:HTTPS_PROXY='';
$env:ALL_PROXY='';
$env:GIT_HTTP_PROXY='';
$env:GIT_HTTPS_PROXY='';
C:\Users\23639\.conda\envs\nju\python.exe -s -m benchmarks.humaneval_runner --limit 164 --output-dir benchmarks\reports\humaneval_full_deepseek --model deepseek-chat --resume
```

## Result

- Total tasks: 164
- Passed tasks: 159
- Failed tasks: 5
- pass@1: 0.9695121951219512
- pass@1 percentage: 96.95%

## Failed Tasks

| Task ID | Source | Result |
| --- | --- | --- |
| HumanEval/47 | resumed_sample | AssertionError |
| HumanEval/101 | resumed_sample | AssertionError |
| HumanEval/145 | agent | AssertionError |
| HumanEval/160 | agent | AssertionError |
| HumanEval/163 | agent | AssertionError: Test 1 |

`resumed_sample` means the completion was generated in the earlier interrupted run and reused by `--resume`. `agent` means the completion was generated during the resumed run.

## Artifacts

- `report.json`: structured benchmark summary and per-task evaluation results.
- `samples.jsonl`: one model completion per HumanEval task.
- `workspaces/`: ignored by git; contains per-task temporary agent workspaces and logs.

## Interpretation

The current coding agent can complete most standalone Python function tasks under HumanEval. The 96.95% pass@1 result shows the basic prompt, file-writing workflow, and execution-based validation are usable for lightweight coding evaluation.

The remaining gap is mostly in coding-task adaptation quality rather than infrastructure failure: all failed tasks produced executable candidates but failed hidden assertions. Sprint3 should focus on coding-specific review loops, stronger self-testing, edge-case extraction from prompts, and better use of local execution feedback before finalizing solutions.

SWE-bench was considered for repository-level evaluation, but its official reproduction path is Docker-based and comparatively heavy. It is recorded as difficult to reproduce on the current machine and is not retained as submitted project code.
