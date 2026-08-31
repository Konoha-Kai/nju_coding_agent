# Public Benchmark Selection

## Decision

Use public benchmark datasets and baseline protocols instead of self-authored benchmark tasks.

Primary target:

- SWE-bench Lite

Secondary targets:

- SWE-bench Verified
- Terminal-Bench
- LiveCodeBench
- HumanEval
- MBPP

## Public Sources

| Benchmark | Official Source | What It Measures |
| --- | --- | --- |
| SWE-bench | https://github.com/SWE-bench/SWE-bench | Real GitHub issue resolution with repository tests |
| SWE-bench datasets | https://huggingface.co/princeton-nlp | Public SWE-bench, Lite, and Verified datasets |
| Terminal-Bench | https://github.com/laude-institute/terminal-bench | End-to-end tasks in terminal environments |
| LiveCodeBench | https://github.com/LiveCodeBench/LiveCodeBench | Code generation, self-repair, code execution, test output prediction |
| HumanEval | https://github.com/openai/human-eval | Python function completion |
| MBPP | https://github.com/google-research/google-research/tree/master/mbpp | Basic Python programming problems with tests |

## Why SWE-bench Lite First

SWE-bench evaluates whether an agent can resolve real GitHub issues by producing patches against real repositories. It matches this project's goal better than single-function code generation benchmarks because the agent must inspect a repository, edit files, and rely on tests for verification.

SWE-bench Lite is smaller than the full set, so it is more practical for development and assessment demos. Once the adapter works, SWE-bench Verified can be used as a more credible benchmark subset.

## Benchmark Roles

| Benchmark | Role in This Project | Notes |
| --- | --- | --- |
| SWE-bench Lite | Main Sprint 3 benchmark | Real GitHub issue resolution; practical size for iteration |
| SWE-bench Verified | Stronger final benchmark | Human-verified solvable subset |
| Terminal-Bench | Optional agent benchmark | Tests terminal-based engineering tasks |
| LiveCodeBench | Optional coding baseline | Useful for code generation, self-repair, code execution, test output prediction |
| HumanEval | Optional simple baseline | Function completion only; not a full agent benchmark |
| MBPP | Optional simple baseline | Basic Python programming tasks; not repository-level |

## Sprint 3 Integration Plan

1. Install or document SWE-bench dependencies separately from the core agent environment.
2. Select a small public subset from SWE-bench Lite by public instance IDs.
3. Implement an adapter that converts each benchmark instance into a natural-language task for `main.py`.
4. Run the agent in the benchmark workspace.
5. Collect generated patches as JSONL predictions.
6. Evaluate patches with the official SWE-bench evaluator.
7. Store reports under `benchmarks/reports/`.

Official evaluator command shape:

```bash
swebench eval SWE-bench/SWE-bench_Lite -p <predictions.jsonl> --run-id <run_id>
```

The exact dataset argument should follow the installed SWE-bench version. The official README also documents aliases such as `verified` and supports HuggingFace dataset IDs.

## Minimal Evaluation Output

Each run should record:

- benchmark name
- dataset split
- public instance id
- model name
- run id
- final patch
- resolved status
- elapsed time
- executed commands
- changed files
- log path

## Baseline Strategy

For a software-school assessment, the baseline does not need to beat public leaderboards. It should show:

- the project uses a recognized public benchmark;
- the harness can run at least one public instance end to end;
- outputs are reproducible;
- failures are analyzed honestly.

Recommended first milestone:

```text
Run 1-3 SWE-bench Lite instances locally or document why local Docker evaluation is not available.
```

Recommended final milestone:

```text
Run a fixed 5-10 instance SWE-bench Lite subset and produce a small report.
```
