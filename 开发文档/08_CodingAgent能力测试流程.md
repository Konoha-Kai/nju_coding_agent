# Coding Agent 能力测试流程

## 目标

本流程用于验证项目是否真正具备 coding agent 能力，而不只是能调用大模型或执行单个工具。

核心验证闭环：

```text
理解任务 -> 读取代码 -> 定位修改点 -> 修改代码 -> 运行测试 -> 根据失败结果继续修复 -> 输出最终总结 -> 日志可复盘
```

## 测试数据集位置

```text
benchmarks/coding_tasks/
```

每个 benchmark 任务使用 Markdown 描述，包含以下字段：

- `任务类型`：bugfix、feature、refactor、test_generation、debug_failure。
- `目标`：用户交给 agent 的自然语言任务。
- `初始状态`：任务开始前项目的关键状态。
- `允许工具`：允许 agent 使用的工具。
- `禁止行为`：不能执行的操作。
- `验收命令`：完成后必须运行的命令。
- `评分点`：用于人工或脚本化评分的标准。
- `日志证据`：JSONL 日志中应能看到的关键事件。

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

从 `benchmarks/coding_tasks/` 中选择一个任务，例如：

```text
task_001_bugfix_calculator.md
```

读取任务中的 `目标` 和 `验收命令`。

### 3. 准备 isolated workspace

每次 benchmark 应使用干净 workspace，避免前一次任务的修改影响本次评分。

推荐做法：

```powershell
git status --short --branch
```

确认没有未提交的代码改动后再运行 benchmark。后续 Sprint 3 可以实现自动复制 benchmark fixture 的脚本。

### 4. 运行 agent

示例命令：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "Read calculator.py, fix the described bug, run the tests, and summarize changed files and test result." --workspace demo_workspace --max-steps 8 --session-id benchmark-task-001
```

### 5. 检查 Git diff

```powershell
git diff -- demo_workspace
```

检查内容：

- 是否只修改任务需要的文件。
- 是否没有改动 `.env`、日志、缓存等无关文件。
- 是否没有大范围重写无关代码。

### 6. 运行验收命令

按任务文件中的 `验收命令` 执行，例如：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest demo_workspace/tests
```

### 7. 检查日志

日志路径示例：

```text
demo_workspace/logs/benchmark-task-001.jsonl
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

- benchmark fixture 自动复制。
- benchmark runner 自动执行 agent。
- 自动收集 Git diff、pytest 结果和 JSONL 日志。
- 自动生成 benchmark report。
- coding 场景安全策略：限制越界路径、危险命令、依赖安装和网络下载。

## 当前结论

Sprint 2 已证明 agent 具备工具调用和基础 demo 能力，但还没有完整 coding benchmark 数据集。Sprint 3 的重点应调整为 coding 场景专项适配，用可复现任务集证明 agent 的真实编码闭环能力。
