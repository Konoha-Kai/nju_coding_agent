# Public Coding Agent Benchmarks

This project uses public benchmarks instead of self-authored benchmark tasks.

Current Sprint 3 benchmark:

1. HumanEval: lightweight public Python function-completion benchmark; runs without Docker.

SWE-bench was investigated because it better represents repository-level issue fixing, but it is not retained in the current project implementation. Its official evaluation is Docker-based and difficult to reproduce reliably on the current machine.

Local demo workspaces may still be used for smoke tests, but they are labeled as demos rather than benchmark datasets.
