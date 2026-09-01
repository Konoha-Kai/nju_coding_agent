# Public Benchmark Selection

## Decision

Use public benchmark datasets instead of self-authored benchmark tasks.

Current retained benchmark:

- HumanEval

Benchmarks investigated but not retained in the current implementation:

- SWE-bench / SWE-bench Lite / SWE-bench Verified
- Terminal-Bench
- LiveCodeBench
- MBPP

## Current Benchmark Role

| Benchmark | Role in This Project | Notes |
| --- | --- | --- |
| HumanEval | Current lightweight evaluation set | Public function-level Python tasks, no Docker required |
| SWE-bench | Research note only | More realistic repository-level benchmark, but local reproduction is difficult |
| Terminal-Bench | Optional future research | Terminal task benchmark, not integrated |
| LiveCodeBench | Optional future research | Coding baseline, not integrated |
| MBPP | Optional future research | Basic Python programming tasks, not integrated |

## SWE-bench Reproduction Note

SWE-bench is a stronger benchmark for coding agents because it evaluates real repository issue fixing. However, the official evaluation path depends on Docker-compatible container execution, repository setup, dependency installation, and heavier machine/runtime requirements.

On this machine, Docker was not available, so official resolved scoring could not be reproduced reliably. To keep the project lightweight and reproducible for the current assessment, SWE-bench code, local data, adapter tests, and evaluator wrappers have been removed. The project keeps only this note to explain why SWE-bench was not used as the submitted benchmark.

## HumanEval Usage

HumanEval is lightweight and can run directly from the local public dataset:

```text
benchmarks/data/HumanEval/HumanEval.jsonl.gz
```

Full benchmark command:

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m benchmarks.humaneval_runner --limit 164 --output-dir benchmarks\reports\humaneval_full_deepseek --model deepseek-chat --resume
```

Current full result:

```text
passed = 159 / 164
pass@1 = 96.95%
```
