# nju_coding_agent

Minimal project scaffold for the NJU software engineering coding agent assessment.

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
