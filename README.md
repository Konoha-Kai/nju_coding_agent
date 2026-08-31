# nju_coding_agent

Minimal coding agent harness for the NJU software engineering assessment.

## Current Scope

Sprint 1 implements a first runnable version:

- DeepSeek API client.
- Conversation context.
- Minimal agent loop.
- Lightweight JSON action protocol.
- Local file actions: list, read, write.
- Local command action: run command with timeout.
- CLI entrypoint.
- Unit tests.

Formal tool registry, workspace safety boundary, dangerous command approval, and JSONL session logs are planned for later sprints.

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

## Run Tests

```bash
python -m pytest
```

Without activating the shell:

```bash
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest
```
