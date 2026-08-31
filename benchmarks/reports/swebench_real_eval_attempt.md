# SWE-bench Real Evaluation Attempt

Date: 2026-08-31

## Goal

Run an official SWE-bench evaluation command to validate that the coding agent benchmark path can reach the real Docker-based evaluator.

## Environment

- Python environment: `nju`
- Official SWE-bench CLI: installed and callable from `C:\Users\23639\.conda\envs\nju\Scripts\swebench.exe`
- Local SWE-bench Lite data: `benchmarks/data/SWE-bench_Lite/`
- Local Hugging Face cache: `.tmp/hf`
- Docker: not installed or not running

## Commands Tried

Official verified gold validation:

```powershell
$env:PYTHONNOUSERSITE='1'
C:\Users\23639\.conda\envs\nju\Scripts\swebench.exe eval verified --gold -i sympy__sympy-20590 --run-id validate-gold-nju-real
```

Result:

- Failed before Docker because the command tried to fetch `SWE-bench/SWE-bench_Verified` from Hugging Face and the network connection was refused.

Local SWE-bench Lite data with project-local Hugging Face cache:

```powershell
$env:PYTHONNOUSERSITE='1'
$env:HF_HOME=(Resolve-Path '.tmp').Path + '\hf'
C:\Users\23639\.conda\envs\nju\Scripts\swebench.exe eval benchmarks/data/SWE-bench_Lite --gold -i marshmallow-code__marshmallow-1343 --split validation --run-id validate-lite-local-gold-4 --workers 1
```

Result:

- Local parquet dataset loaded successfully.
- Official evaluator reached Docker initialization.
- Evaluation failed because Docker is unavailable.

Key failure:

```text
docker.errors.DockerException: Error while fetching server API version
```

Docker probes:

```powershell
docker --version
podman --version
wsl --status
```

Result:

- `docker` was not found.
- `podman` was not found.
- WSL is not installed/configured.

## Conclusion

The project-side Sprint 3 integration is ready up to the official evaluator boundary:

- public SWE-bench Lite data is downloaded;
- official SWE-bench CLI is installed;
- local dataset path can be loaded;
- evaluator command reaches Docker initialization.

True SWE-bench resolved scoring cannot run on this machine until a Docker-compatible runtime is installed and running.

## Recommended Runtime

For SWE-bench on Windows, use Docker Desktop with WSL2 because this is the most compatible path with the official Docker-based evaluator.

Podman Desktop and Rancher Desktop can be lighter alternatives, but they require Docker API compatibility to work with the Python Docker SDK used by SWE-bench. They are therefore less predictable for this benchmark than Docker Desktop.
