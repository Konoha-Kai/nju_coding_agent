# nju_coding_agent

南京大学软件学院推免考核项目：基于 DeepSeek API 的最小可运行 Coding Agent Harness。

项目按软件工程流程开发，采用 Sprint 迭代、测试驱动开发和小步提交。当前重点是完成可运行、可测试、可复盘的 coding agent 基础系统，并用公开轻量 benchmark 验证代码生成能力。

## 当前功能

### DeepSeek 模型调用

- 通过项目自写 HTTP 客户端调用 DeepSeek OpenAI-compatible Chat Completions API。
- 从 `.env` 读取 API 配置。
- 默认模型为 `deepseek-chat`。
- 支持 DeepSeek/OpenAI 兼容的 `tools` 和 `tool_calls` 协议。

相关文件：

- `agent/model_client.py`
- `test_deepseek_api.py`

### Agent Harness 主循环

Agent 运行流程：

1. 接收用户任务。
2. 构造系统提示词和多轮上下文。
3. 调用 DeepSeek 模型。
4. 如果模型返回工具调用，则执行工具并把结果写回上下文。
5. 循环直到模型给出最终回答，或达到最大步数/错误阈值。

相关文件：

- `agent/loop.py`
- `agent/context.py`
- `main.py`

### 工具系统

项目实现了统一工具抽象：

- `ToolSpec`：描述工具名、说明、参数 schema 和处理函数。
- `ToolResult`：统一返回工具执行结果。
- `ToolRegistry`：负责注册、查找、运行工具，并导出 OpenAI-compatible tool schema。

内置工具：

| 工具名 | 功能 |
| --- | --- |
| `list_files` | 列出 workspace 下的文件或目录 |
| `read_file` | 读取 UTF-8 文本文件 |
| `write_file` | 写入 UTF-8 文本文件 |
| `run_command` | 在指定 workspace 中执行 shell 命令，返回 exit code、stdout、stderr |

### 安全与质量

- 文件工具限制在 workspace 内，阻止路径穿越和越界访问。
- shell 工具默认拦截删除、移动、安装依赖、网络下载等高风险命令。
- shell 工具支持超时和输出截断。
- Agent 支持连续工具错误阈值，避免无限循环。
- 每次运行可生成 JSONL 会话日志，便于复盘。
- CLI 支持 `--verbose`，运行时实时打印模型轮次、工具调用、工具结果和最终状态。
- CLI 支持 `--chat`，可以在终端里进行“用户一句、Agent 一句”的多轮交互。每轮都会保留前面的问答摘要，并继续使用同一套本地工具和安全策略。

### HumanEval 轻量 Benchmark

当前保留公开 OpenAI HumanEval 数据集作为轻量 coding benchmark：

```text
benchmarks/data/HumanEval/HumanEval.jsonl.gz
```

运行 1 题 smoke test：

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

完整实验结果：

```text
HumanEval, deepseek-chat
passed = 159 / 164
pass@1 = 96.95%
```

报告文件：

- `benchmarks/reports/humaneval_full_deepseek/README.md`
- `benchmarks/reports/humaneval_full_deepseek/report.json`
- `benchmarks/reports/humaneval_full_deepseek/samples.jsonl`
- `开发文档/10_HumanEval完整实验报告.md`

### SWE-bench 说明

SWE-bench 是更接近真实仓库修复任务的 coding agent benchmark，但官方复现依赖 Docker/容器环境、仓库依赖安装和较重的评测流程。本机当前不具备稳定 Docker 评测条件，因此项目不再保留 SWE-bench adapter、数据文件、测试脚本和官方评测封装，只在开发文档中记录“复现较困难，暂不作为当前版本交付内容”。

## 项目结构

```text
nju_ai_coding_agent/
├── agent/                  # Agent 主循环、上下文、模型客户端、日志、工具注册
├── tools/                  # 文件系统工具和 shell 工具
├── tests/                  # 单元测试
├── benchmarks/             # HumanEval 数据、runner 和实验报告
├── demo_workspace/         # 演示 workspace
├── 开发文档/               # 软件工程过程文档
├── main.py                 # CLI 入口
├── requirements.txt
├── pytest.ini
└── test_deepseek_api.py
```

## 环境准备

项目使用 `nju` conda 虚拟环境：

```bash
conda create -n nju python=3.12 pip -y
conda activate nju
pip install -r requirements.txt
```

不激活环境时可以直接使用：

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

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s test_deepseek_api.py
```

## 运行 Agent

基本运行：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "List the workspace files, then give a final summary."
```

指定 workspace：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "Read calculator.py and run its tests." --workspace demo_workspace --max-steps 6
```

指定日志目录和 session id：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "List files and summarize the project." --workspace demo_workspace --log-dir logs --session-id demo
```

实时查看执行过程：

```powershell
$env:PYTHONIOENCODING='utf-8'
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "Read demo_workspace/calculator.py, run python -m pytest demo_workspace/tests -v, and summarize the result." --workspace . --max-steps 8 --verbose
```

交互式对话：

```powershell
$env:PYTHONIOENCODING='utf-8'
C:\Users\23639\.conda\envs\nju\python.exe -s main.py --chat --workspace . --max-steps 8 --verbose
```

进入后可以这样输入：

```text
You: 先看一下 demo_workspace/calculator.py 做了什么
You: 再帮我运行 demo_workspace/tests，并总结测试结果
You: exit
```

## 运行测试

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest
```

当前验证结果：

```text
73 passed
```

## 开发文档

软件工程过程文档位于：

```text
开发文档/
```

主要内容包括需求分析、Backlog、Sprint 计划、后端接口文档、Harness 架构图、DeepSeek 参考记录、Sprint 复盘和 HumanEval 完整实验报告。
