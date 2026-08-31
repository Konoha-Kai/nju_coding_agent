# nju_coding_agent

Minimal coding agent harness for the NJU software engineering assessment.

## Current Scope

Sprint 2 implements the current runnable version:

- DeepSeek API client.
- Conversation context.
- Agent loop with DeepSeek/OpenAI-compatible `tools` and `tool_calls`.
- Tool registry and OpenAI-compatible tool schema export.
- Filesystem tools: list, read, write.
- Shell tool: run command with timeout.
- JSONL session logs.
- Execution summary tracking for changed files and commands.
- CLI entrypoint.
- Unit tests.

Workspace safety boundary, dangerous command approval, richer output truncation, and quality hardening are planned for Sprint 3.

## API Key Test

1. Create and activate the conda environment:

```bash
conda create -n nju python=3.12 pip -y
conda activate nju
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure `.env`:

```bash
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

4. Run the API test:

```bash
python test_deepseek_api.py
```

You can also run it without activating the shell:

```bash
conda run -n nju python -s test_deepseek_api.py
```

## Run the Agent

```bash
python main.py "List the workspace files, then give a final summary."
```

Without activating the shell:

```bash
conda run -n nju python -s main.py "List the workspace files, then give a final summary."
```

Run against the demo workspace:

```bash
conda run -n nju python -s main.py "Use tools to inspect the project, then summarize it." --workspace demo_workspace --session-id demo
```

Session logs are written to `logs/<session-id>.jsonl` under the selected workspace.

## Run Tests

```bash
python -m pytest
```

Without activating the shell:

```bash
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest
```

Current validation:

```text
44 passed
```
