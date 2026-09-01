# Coding Agent 能力测试流程

## 目标

使用公开 benchmark 验证当前 coding agent 的基础能力，不使用自建题目作为主要评分集。

当前版本采用 OpenAI HumanEval 作为轻量 benchmark。HumanEval 可以直接在本地运行，不依赖 Docker，适合作为考核项目中的可复现实验。

## 数据集

公开数据集路径：

```text
benchmarks/data/HumanEval/HumanEval.jsonl.gz
```

来源：

```text
https://github.com/openai/human-eval
```

## 测试流程

1. 读取 HumanEval 公开题目。
2. 将每道题转换成 agent 可执行任务。
3. Agent 在独立 workspace 中生成 `solution.py` 或最终 completion。
4. runner 收集 completion，写入 `samples.jsonl`。
5. runner 将 prompt、completion 和官方 test 拼接后本地执行。
6. 每题记录 pass/fail、stdout、stderr、agent 步数和样本来源。
7. 汇总生成 `report.json`。
8. 将实验结论写入 markdown 报告。

## 运行命令

运行 1 道题 smoke test：

```powershell
$env:HTTP_PROXY=''
$env:HTTPS_PROXY=''
$env:ALL_PROXY=''
C:\Users\23639\.conda\envs\nju\python.exe -s -m benchmarks.humaneval_runner --limit 1 --output-dir benchmarks\reports\humaneval_real_1 --model deepseek-chat
```

运行完整 164 题：

```powershell
$env:HTTP_PROXY=''
$env:HTTPS_PROXY=''
$env:ALL_PROXY=''
C:\Users\23639\.conda\envs\nju\python.exe -s -m benchmarks.humaneval_runner --limit 164 --output-dir benchmarks\reports\humaneval_full_deepseek --model deepseek-chat --resume
```

## 输出文件

```text
benchmarks/reports/humaneval_full_deepseek/report.json
benchmarks/reports/humaneval_full_deepseek/samples.jsonl
benchmarks/reports/humaneval_full_deepseek/README.md
```

## 当前结果

```text
Benchmark: HumanEval
Model: deepseek-chat
Total: 164
Passed: 159
Failed: 5
pass@1: 96.95%
```

失败题目：

```text
HumanEval/47
HumanEval/101
HumanEval/145
HumanEval/160
HumanEval/163
```

## SWE-bench 复现记录

SWE-bench 更接近真实 coding agent 的仓库级 bugfix 场景，但官方评测依赖 Docker/容器运行、仓库环境准备和较重的依赖安装流程。本机没有稳定可用的 Docker 环境，官方 resolved 评分无法可靠复现。

因此当前版本删除 SWE-bench adapter、数据文件、测试脚本和 evaluator 封装，不将其作为交付代码。这里只保留结论：SWE-bench 适合作为后续更强评估方向，但当前考核项目中复现较困难，优先使用 HumanEval 保证实验可运行、可复盘。

## 后续改进方向

- 针对失败的 5 道 HumanEval 题分析错误模式。
- 增强 agent 的自测循环，让模型在提交前主动构造边界样例。
- 增加代码审查提示，要求模型检查排序、边界、空输入和异常输入。
- 在具备 Docker 环境后，再重新评估是否恢复 SWE-bench。
