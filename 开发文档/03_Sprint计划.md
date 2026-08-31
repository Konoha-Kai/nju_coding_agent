# Sprint 计划

## Sprint 0：项目初始化

时间：2026-08-31

目标：
- 建立 Git 仓库。
- 配置 `nju` 虚拟环境。
- 验证 DeepSeek API key。
- 建立开发文档目录。

任务：
- 创建项目骨架。
- 创建 `.env`、`.env.example`、`.gitignore`。
- 编写 `test_deepseek_api.py`。
- 推送初始提交到 GitHub。

验收：
- `conda run -n nju python -s test_deepseek_api.py` 返回 `deepseek api ok`。
- `.env` 未进入 Git。

状态：Done

## Sprint 1：最小 Agent 闭环

目标：
- 实现可运行的 coding agent 主循环。
- 支持模型请求、轻量动作解析、本地动作执行和结果回填。
- 本 sprint 暂不实现正式工具系统和安全边界，先保证基础功能闭环。

任务：
- 实现 `agent/model_client.py`。
- 实现 `agent/loop.py`。
- 实现 `agent/context.py`。
- 实现 `agent/actions.py`，提供初版 list/read/write/run_command 动作。
- 实现 `main.py`。
- 建立 `tests/` 测试目录。
- 为上下文、动作解析、本地动作和主循环编写初版测试。

验收：
- agent 能读取一个 demo 项目文件。
- agent 能修改文件。
- agent 能执行一条测试命令。
- agent 能基于工具结果继续下一轮。
- `conda run -n nju python -s -m pytest` 通过。

已完成：
- `agent/context.py`：维护 system、user、assistant 和 observation 消息。
- `agent/model_client.py`：封装 DeepSeek API 调用。
- `agent/actions.py`：实现轻量 JSON action 解析和本地动作执行。
- `agent/loop.py`：实现最小 agent 循环。
- `main.py`：提供 CLI 入口。
- `tests/`：建立测试目录并覆盖上下文、动作和主循环。

暂缓：
- 正式工具系统。
- workspace 安全边界。
- 危险命令审批。
- JSONL session logs。

验证：
- `C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest` 通过，7 passed。

状态：Done

## Sprint 2：完整功能补齐

目标：
- 在 Sprint 1 最小闭环基础上补齐 agent 的主要功能。
- 将轻量 JSON action 协议升级为正式工具系统。
- 先完成可用性和功能完整度，安全强化放到 Sprint 3。

提交策略：
- 每完成一个工具就本地 commit 一次。
- 工程实现和测试代码分开 commit。
- 坚持测试驱动开发：先写测试，再实现功能。
- 每个小工具或小功能完成后立即运行相关测试和全量测试。
- 测试内容尽可能丰富，覆盖正常路径、异常路径、边界输入和返回格式。
- 每个小功能测试成功后立即 commit 到 `main`。
- Sprint 2 全部完成并通过验证后，再统一 push 到 GitHub；开发过程中不要 push 半成品。

任务：
- 实现 `ToolSpec` / `ToolResult` 工具抽象。
- 实现工具注册表 `ToolRegistry`。
- 接入 DeepSeek Chat Completions 的 `tools` / `tool_calls`。
- 将 `list_files`、`read_file`、`write_file`、`run_command` 从轻量 action 迁移为正式 function tools。
- 支持模型返回多个 tool calls 时顺序执行。
- 支持清晰的最终任务总结，列出修改文件、执行命令和验证结果。
- 实现 JSONL 执行日志。
- 增加一个可复现 demo workspace，用于端到端演示。

验收：
- 日志可复盘完整 agent 执行过程。
- agent 使用 DeepSeek 原生 tool calls 完成一次真实编程任务。
- agent 能读取文件、修改文件、运行测试，并根据测试结果继续下一轮。
- README 能说明正式工具系统和主循环流程。

已完成：
- `agent/tooling.py`：实现 `ToolSpec`、`ToolResult`、`ToolRegistry`。
- `tools/filesystem.py`：实现 `list_files`、`read_file`、`write_file` 正式工具。
- `tools/shell.py`：实现 `run_command` 正式工具。
- `agent/model_client.py`：支持传入 `tools` 并解析 `tool_calls`。
- `agent/context.py`：支持 assistant tool calls 和 tool role 结果回填。
- `agent/loop.py`：支持正式 tool_calls 执行循环、执行摘要和日志事件。
- `agent/logger.py`：实现 JSONL session logs。
- `agent/bootstrap.py`：装配默认工具注册表。
- `demo_workspace/`：提供可复现 demo 项目。

验证：
- `C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest` 通过，44 passed。
- DeepSeek 真实冒烟测试通过：使用正式 tools 列出 `demo_workspace` 文件并返回最终总结。

状态：Done

## Sprint 3：Coding 场景专项适配

目标：
- 将当前通用 harness 适配成更像真实 coding agent 的系统。
- 接入公开 coding agent benchmark，优先使用 SWE-bench Lite，验证读代码、定位问题、修改代码、运行测试和基于失败结果迭代修复的闭环能力。
- 在 coding 场景下补齐必要的安全边界和质量保障，避免 agent 在执行本地代码任务时越界访问、误执行高风险命令或生成不可复盘结果。

任务：
- 选定公开 benchmark：SWE-bench Lite 作为主目标，SWE-bench Verified 作为增强目标。
- 调研并记录 SWE-bench、Terminal-Bench、LiveCodeBench、HumanEval、MBPP 的适用范围和本项目取舍。
- 基于公开 SWE-bench Lite instance id 选择一个小规模固定子集，不自建 benchmark 数据集。
- 实现或整理一套完整工作测试流程：准备公开 benchmark workspace、运行 agent、检查 patch、运行官方 evaluator、检查日志、记录评分。
- 实现 SWE-bench 输入适配：将公开 issue、repo、base commit 转换为 agent 可执行任务。
- 实现 SWE-bench 输出适配：将 agent 产生的 diff 转换为官方 predictions JSONL。
- 增加 coding 场景执行摘要：列出修改文件、执行命令、测试结果、失败重试次数和最终状态。
- 实现 workspace 路径边界检查，阻止路径穿越和 workspace 外文件访问。
- 实现危险命令识别和确认机制，拦截删除、移动、安装依赖、网络下载等高风险命令。
- 完善命令超时、输出截断和失败处理，让测试失败信息能稳定回填给模型。
- 增加错误阈值终止条件，避免 coding 任务无限循环。
- 增加 benchmark、safety、filesystem、shell、tool parser 单元测试。
- 检查日志、README、视频脚本中不泄露 API key。

验收：
- 至少 1 个 SWE-bench Lite 公开 instance 能完成从任务读取到 patch 输出的端到端流程。
- 固定 5-10 个 SWE-bench Lite 公开 instance id 作为小规模评估子集。
- benchmark 结果可以从 predictions JSONL、JSONL session log 和 Git diff 中复盘。
- agent 能在公开 benchmark 或公开 instance 派生的 workspace 中完成“读代码 -> 修改代码 -> 运行测试 -> 根据失败继续修复 -> 最终总结”的闭环。
- 越界路径被拒绝。
- 高风险命令被拦截或要求确认。
- 超时命令被终止，失败信息清晰返回。
- 工具参数非法时返回清晰错误。
- `pytest` 覆盖核心 coding 工作流、安全与工具逻辑。
- `.env` 和敏感日志不会进入 Git。

## Sprint 4：演示与交付

目标：
- 准备稳定视频 demo 和最终提交材料。

任务：
- 准备 demo 项目。
- 准备演示任务脚本。
- 编写最终 `README.txt`。
- 录制 2 分钟以内视频。
- 检查仓库、视频、README 是否泄露凭据。

验收：
- demo 能稳定复现。
- README.txt 不超过 1000 汉字。
- zip 只包含 README.txt 和 mp4。
