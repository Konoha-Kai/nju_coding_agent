# nju_coding_agent

南京大学软件学院推免考核项目：一个基于 DeepSeek API 的最小可运行 Coding Agent Harness。

项目按软件工程流程开发，当前处于 Sprint 2 版本。核心目标是先完成可运行、可测试、可追踪的 Agent 主流程，后续 Sprint 3 将围绕 coding agent 场景做专项适配，优先接入 SWE-bench Lite 等公开 benchmark，并补齐安全边界、危险命令审批和质量加固。

## 当前功能

### 1. DeepSeek 模型调用

- 通过 OpenAI-compatible SDK 调用 DeepSeek。
- 支持从 `.env` 读取配置。
- 默认模型为 `deepseek-chat`。
- 支持 DeepSeek/OpenAI 兼容的 `tools` 和 `tool_calls` 协议。

相关文件：

- `agent/model_client.py`
- `test_deepseek_api.py`

### 2. Agent Harness 主循环

Agent 会按以下流程运行：

1. 接收用户任务。
2. 构造系统提示词和对话上下文。
3. 调用 DeepSeek 模型。
4. 如果模型返回工具调用，则执行工具并把结果写回上下文。
5. 循环直到模型给出最终回答，或达到最大步数。

相关文件：

- `agent/loop.py`
- `agent/context.py`
- `main.py`

### 3. 工具注册系统

项目实现了统一的工具抽象：

- `ToolSpec`：描述工具名称、说明、参数 schema 和处理函数。
- `ToolResult`：统一返回工具执行结果。
- `ToolRegistry`：负责注册、查找、运行工具，并导出 OpenAI-compatible tool schema。

相关文件：

- `agent/tooling.py`
- `agent/bootstrap.py`

### 4. 文件系统工具

当前内置 3 个文件工具：

| 工具名 | 功能 |
| --- | --- |
| `list_files` | 列出 workspace 下的文件或目录 |
| `read_file` | 读取 UTF-8 文本文件 |
| `write_file` | 写入 UTF-8 文本文件 |

相关文件：

- `tools/filesystem.py`
- `tests/test_filesystem_tools.py`

### 5. Shell 命令工具

当前内置 1 个命令工具：

| 工具名 | 功能 |
| --- | --- |
| `run_command` | 在指定 workspace 中执行 shell 命令，返回退出码、标准输出和标准错误 |

支持参数：

- `command`：要执行的命令。
- `timeout_seconds`：超时时间，默认 30 秒。

相关文件：

- `tools/shell.py`
- `tests/test_shell_tool.py`

### 6. JSONL 会话日志

每次 Agent 运行都会记录结构化日志，便于复盘和考核展示。

默认日志路径：

```text
<workspace>/logs/<session-id>.jsonl
```

日志包含：

- 会话开始和结束。
- 模型回复。
- 工具调用。
- 工具执行结果。
- 修改过的文件。
- 执行过的命令。

相关文件：

- `agent/logger.py`
- `tests/test_logger.py`

### 7. 执行摘要

Agent 运行结果会追踪：

- 是否成功。
- 最终回复。
- 执行步数。
- 工具观察结果。
- 修改过的文件。
- 执行过的命令。

相关文件：

- `agent/loop.py`
- `tests/test_loop.py`

### 8. Demo Workspace

项目包含一个简单的 demo workspace，用于展示 Agent 可以检查项目、运行测试并总结结果。

路径：

```text
demo_workspace/
```

内容包括：

- `calculator.py`
- `tests/test_calculator.py`

### 9. 公开 Coding Benchmark 接入

项目不自建 benchmark 数据集，后续 Sprint 3 优先接入公开 benchmark：

```text
benchmarks/
```

推荐顺序：

- SWE-bench Lite：主评估目标，验证真实 GitHub issue 修复能力。
- SWE-bench Verified：增强评估目标，使用人工确认可解的问题子集。
- Terminal-Bench：可选，验证终端环境下的工程任务执行能力。
- LiveCodeBench：可选，验证代码生成、自修复、代码执行和测试输出预测。
- HumanEval / MBPP：可选，只作为函数级代码生成 baseline。
- HumanEval：已接入轻量本地 runner，可不依赖 Docker 直接跑小规模 pass/fail。

## 当前限制

以下内容计划在 Sprint 3 完成：

- SWE-bench Lite adapter 和 benchmark runner。
- 自动收集 Git diff、pytest 结果和 JSONL 日志。
- workspace 路径安全边界。
- 防止 `..`、绝对路径等越界访问。
- 危险 shell 命令拦截。
- 命令审批机制。
- 更严格的输出截断。
- 更完整的异常分类。
- 质量门禁和集成测试增强。

因此当前版本适合在受控目录内做功能演示和测试，不适合作为无监督生产 Agent 使用。

Sprint 3 当前已接入 SWE-bench Lite 公共数据和官方 CLI，但真实官方评测依赖 Docker。本机当前未检测到 `docker` 命令，因此可以完成 instance 读取、任务构造、agent 运行、patch 导出和 evaluator dry-run；完整容器评测需要安装并启动 Docker 后执行。

## 项目结构

```text
nju_ai_coding_agent/
├── agent/
│   ├── bootstrap.py        # 默认工具注册
│   ├── context.py          # 对话上下文和系统提示词
│   ├── logger.py           # JSONL 会话日志
│   ├── loop.py             # Agent 主循环
│   ├── model_client.py     # DeepSeek/OpenAI-compatible 客户端
│   └── tooling.py          # ToolSpec / ToolResult / ToolRegistry
├── tools/
│   ├── filesystem.py       # 文件系统工具
│   └── shell.py            # Shell 命令工具
├── tests/                  # 单元测试
├── benchmarks/             # Coding agent 能力测试任务集
├── demo_workspace/         # 演示 workspace
├── 开发文档/               # 软件工程过程文档
├── main.py                 # CLI 入口
├── requirements.txt
├── pytest.ini
└── test_deepseek_api.py    # DeepSeek API key 连通性测试
```

## 环境准备

项目使用 `nju` conda 虚拟环境。

```bash
conda create -n nju python=3.12 pip -y
conda activate nju
pip install -r requirements.txt
```

如果不想激活环境，也可以直接使用：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest
```

## 配置 API Key

在项目根目录创建 `.env`：

```text
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

`.env` 已加入 `.gitignore`，不会提交到 GitHub。

## 测试 DeepSeek API Key

```bash
python test_deepseek_api.py
```

不激活环境时：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s test_deepseek_api.py
```

如果配置正确，程序会向 DeepSeek 发送一次简单请求并输出模型返回内容。

## 运行 Agent

### 基本运行

```bash
python main.py "List the workspace files, then give a final summary."
```

不激活环境时：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "List the workspace files, then give a final summary."
```

### 指定 workspace

```bash
python main.py "Use tools to inspect the project, then summarize it." --workspace demo_workspace
```

### 指定最大循环步数

```bash
python main.py "Read calculator.py and run its tests." --workspace demo_workspace --max-steps 6
```

### 指定日志目录和 session id

```bash
python main.py "List files and summarize the project." --workspace demo_workspace --log-dir logs --session-id demo
```

运行后会生成：

```text
demo_workspace/logs/demo.jsonl
```

## 推荐演示命令

### 1. 只列出 demo workspace

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "Use the available tools to list the workspace files once, then give a final summary. Do not write files and do not run commands." --workspace demo_workspace --max-steps 4 --session-id demo-list
```

### 2. 读取代码并总结

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "Read calculator.py and summarize what functions it provides. Do not modify files." --workspace demo_workspace --max-steps 6 --session-id demo-read
```

### 3. 运行 demo 测试

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "Run the demo workspace tests and summarize the result. Do not modify files." --workspace demo_workspace --max-steps 6 --session-id demo-test
```

## SWE-bench 使用

本项目已下载 SWE-bench Lite 公共数据：

```text
benchmarks/data/SWE-bench_Lite/
```

固定小规模公开 dev 子集：

```text
benchmarks/selected_swebench_lite_dev_ids.txt
```

官方 SWE-bench 参考仓库下载在本地：

```text
benchmarks/vendor/SWE-bench
```

该目录已加入 `.gitignore`，不会提交第三方源码。

生成官方 gold validation 命令：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s benchmarks\swebench_evaluator.py --gold-validation --run-id validate-gold --dry-run
```

输出：

```text
swebench eval verified --gold -i sympy__sympy-20590 --run-id validate-gold
```

真实官方评测需要 Docker：

```powershell
C:\Users\23639\.conda\envs\nju\Scripts\swebench.exe eval lite -p benchmarks/reports/<run>.predictions.jsonl --run-id <run_id> -j 1
```

## HumanEval 轻量测试

HumanEval 是 OpenAI 官方公开数据集，当前项目已下载到：

```text
benchmarks/data/HumanEval/HumanEval.jsonl.gz
```

运行 1 道题的轻量 benchmark：

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

结果文件：

```text
benchmarks/reports/humaneval_real_1/report.json
benchmarks/reports/humaneval_real_1/samples.jsonl
```

注意：HumanEval 很轻量，适合快速看 agent 的代码生成和执行测试能力；它不是仓库级 bugfix benchmark，最终仍应以 SWE-bench Lite/Verified 作为更强证明。

## 运行测试

```bash
python -m pytest
```

不激活环境时：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest
```

当前验证结果：

```text
79 passed
```

## 开发文档

软件工程过程文档位于：

```text
开发文档/
```

主要文档：

- `00_项目开发规划.md`
- `01_需求分析.md`
- `02_Backlog.md`
- `03_Sprint计划.md`
- `04_后端接口文档.md`
- `05_Harness架构图.md`
- `06_DeepSeek参考记录.md`
- `07_Sprint1复盘与改进.md`
- `08_CodingAgent能力测试流程.md`

这些文档用于展示需求分析、Backlog、Sprint 拆分、接口设计、架构设计和开发复盘。

## Git 说明

当前 Sprint 2 按用户要求采用小步提交：

- 每完成一个小功能先补测试。
- 测试通过后立即 commit。
- Sprint 2 完成前不 push。
- `.env`、日志、缓存文件不进入版本库。

常用检查命令：

```bash
git status --short --branch --ignored
git log --oneline --decorate -8
```
