# Public Coding Agent Benchmarks

This project should use public benchmarks instead of self-authored benchmark tasks.

Sprint 3 uses this directory only for benchmark integration notes, selected public instance IDs, generated reports, and adapter scripts. It must not define private benchmark tasks as the primary scoring set.

Recommended benchmark order:

1. SWE-bench Lite: primary evaluation target for early iterations.
2. SWE-bench Verified: stronger evaluation target after the harness is stable.
3. Terminal-Bench: optional terminal-oriented agent evaluation.
4. LiveCodeBench: optional code generation, self-repair, code execution, and test output prediction baseline.
5. HumanEval / MBPP: optional small-function generation baselines, not enough to prove full coding-agent ability.

Local demo workspaces may still be used for smoke tests, but they should be clearly labeled as demos rather than benchmark datasets.
