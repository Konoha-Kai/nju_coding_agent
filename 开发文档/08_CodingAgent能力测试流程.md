# Coding Agent 能力测试流程

## 目标

本流程用于验证项目是否真正具备 coding agent 能力，而不只是能调用大模型或执行单个工具。评估数据应优先来自公开 benchmark，不自建 benchmark 数据集。

核心验证闭环：

```text
理解任务 -> 读取代码 -> 定位修改点 -> 修改代码 -> 运行测试 -> 根据失败结果继续修复 -> 输出最终总结 -> 日志可复盘
```

## 公开 Benchmark 选择

主 benchmark：

- SWE-bench Lite

增强 benchmark：

- SWE-bench Verified
- Terminal-Bench
- LiveCodeBench
- HumanEval
- MBPP

轻量直接运行 benchmark：

- HumanEval：不需要 Docker，适合快速验证 agent 的代码生成、写文件和本地测试能力。

`benchmarks/` 目录只保存接入说明、公开 instance id、运行结果和报告，不保存自建 benchmark 题目作为主评分依据。

## 能力维度

| 维度 | 验证内容 | 证据 |
| --- | --- | --- |
| 代码理解 | 是否能读取相关文件并说明当前逻辑 | `read_file` 调用和最终总结 |
| 修改能力 | 是否能写入正确文件并保持局部修改 | Git diff 和 `write_file` 日志 |
| 测试意识 | 是否会运行指定测试或主动运行相关测试 | `run_command` 日志 |
| 失败迭代 | 测试失败后是否能读取失败信息并继续修复 | 多轮 tool call 日志 |
| 工程约束 | 是否遵守 workspace、禁止行为和任务边界 | 安全工具结果和 diff |
| 结果复盘 | 是否能从日志复现执行过程 | JSONL session log |

## 完整工作测试流程

### 1. 准备环境

在项目根目录执行：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest
```

预期：

```text
44 passed
```

### 2. 选择 benchmark 任务

从公开 benchmark 中选择一个实例。Sprint 3 优先选择 SWE-bench Lite。官方 SWE-bench README 中的安装验证示例使用过如下公开 instance id：

```text
sympy__sympy-20590
```

该 id 可用于验证 SWE-bench 环境，不直接代表最终 Lite 子集。实际评估 instance id 以 SWE-bench Lite 数据集为准。不要手写私有 benchmark 题目代替公开数据集。

### 3. 准备 isolated workspace

每次 benchmark 应使用官方 evaluator 或干净 workspace，避免前一次任务的修改影响本次评分。

推荐做法：

```powershell
git status --short --branch
```

确认没有未提交的代码改动后再运行 benchmark。后续 Sprint 3 应接入 SWE-bench 的官方 Docker evaluator 或生成官方 predictions JSONL。

### 4. 运行 agent

本项目 adapter 的目标命令形态：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "<SWE-bench issue text>" --workspace <prepared_repo_workspace> --max-steps 20 --session-id swebench-<instance-id>
```

### 5. 导出 Patch

```powershell
git diff
```

检查内容：

- 是否只修改任务需要的文件。
- 是否没有改动 `.env`、日志、缓存等无关文件。
- 是否没有大范围重写无关代码。

同时将 diff 转换为 SWE-bench 官方 predictions JSONL。

### 6. 运行官方验收

SWE-bench 官方流程使用 Docker 进行可复现评测。目标命令形态：

```bash
swebench eval SWE-bench/SWE-bench_Lite -p <predictions.jsonl> --run-id <run_id>
```

具体 dataset 参数应以当前安装的 SWE-bench 版本为准。

本机当前已安装 `swebench` CLI，但未检测到 Docker，因此可以先运行 dry-run 和 predictions JSONL 生成流程；真实 resolved 评分需要 Docker 可用。

### 9. HumanEval 轻量替代流程

当本机没有 Docker 时，使用 HumanEval 做轻量性能 smoke test：

```powershell
$env:HTTP_PROXY=''
$env:HTTPS_PROXY=''
$env:ALL_PROXY=''
C:\Users\23639\.conda\envs\nju\python.exe -s -m benchmarks.humaneval_runner --limit 1 --output-dir benchmarks\reports\humaneval_real_1 --model deepseek-chat
```

当前真实运行结果：

```text
HumanEval/0
pass@1 = 1.0
passed = 1 / 1
agent steps = 4
```

输出文件：

```text
benchmarks/reports/humaneval_real_1/report.json
benchmarks/reports/humaneval_real_1/samples.jsonl
```

### 7. 检查日志

日志路径示例：

```text
<prepared_repo_workspace>/logs/swebench-<instance-id>.jsonl
```

检查日志是否包含：

- `session_start`
- `model_reply`
- `tool_call`
- `tool_result`
- `session_end`

同时确认日志中没有 API key。

### 8. 记录评分

建议每个任务满分 10 分：

| 项目 | 分值 |
| --- | --- |
| 正确理解任务 | 2 |
| 修改范围合理 | 2 |
| 功能实现正确 | 2 |
| 测试通过 | 2 |
| 日志和总结可复盘 | 1 |
| 遵守安全和禁止行为 | 1 |

## Sprint 3 需要补齐的自动化能力

- SWE-bench Lite instance 下载和 workspace 准备。
- benchmark runner 自动执行 agent。
- 自动收集 Git diff、pytest 或官方 evaluator 结果和 JSONL 日志。
- 自动生成 SWE-bench predictions JSONL。
- 自动生成 benchmark report。
- coding 场景安全策略：限制越界路径、危险命令、依赖安装和网络下载。

## 当前结论

Sprint 2 已证明 agent 具备工具调用和基础 demo 能力，但还没有接入公开 coding benchmark。Sprint 3 的重点应调整为 coding 场景专项适配，优先接入 SWE-bench Lite，用公开基准证明 agent 的真实编码闭环能力。
