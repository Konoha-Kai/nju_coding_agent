# HumanEval Local Data

This directory stores a local copy of the public OpenAI HumanEval dataset.

Source:

```text
https://github.com/openai/human-eval
https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz
```

File:

| File | Size | SHA256 |
| --- | ---: | --- |
| `HumanEval.jsonl.gz` | 44877 bytes | `B796127E635A67F93FB35C04F4CB03CF06F38C8072EE7CEE8833D7BEE06979EF` |

HumanEval is lightweight and does not require Docker. It is useful for quick code-generation and self-test smoke evaluation. SWE-bench was investigated as a repository-level benchmark, but it is not retained in the current implementation because official reproduction is Docker-based and comparatively heavy.
