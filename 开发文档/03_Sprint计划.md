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
- 使用公开、轻量、可直接复现的 HumanEval 数据集验证代码生成和执行评测能力。
- 在 coding 场景下补齐必要的安全边界和质量保障，避免 agent 在执行本地代码任务时越界访问、误执行高风险命令或生成不可复盘结果。
- 调研 SWE-bench，但不把它作为当前版本交付内容；仅记录其官方复现依赖 Docker/容器环境，复现成本较高。

任务：
- 接入 OpenAI HumanEval 公开数据集，不自建 benchmark 数据集。
- 实现 HumanEval runner：加载公开数据、构造 agent 任务、收集 completion、执行测试、生成 `samples.jsonl` 和 `report.json`。
- 支持 HumanEval 断点续跑，长实验中断后可复用已有样本继续执行。
- 增加 coding 场景执行摘要：列出修改文件、执行命令、测试结果、失败重试次数和最终状态。
- 实现 workspace 路径边界检查，阻止路径穿越和 workspace 外文件访问。
- 实现危险命令识别和确认机制，删除、移动、安装依赖、网络下载等高风险命令需要用户确认后才执行。
- 完善命令超时、输出截断和失败处理，让测试失败信息能稳定回填给模型。
- 增加错误阈值终止条件，避免 coding 任务无限循环。
- 增加 HumanEval、safety、filesystem、shell、tool parser 单元测试。
- 检查日志、README、视频脚本中不泄露 API key。

验收：
- HumanEval 公开数据集可直接从本地运行。
- 完成 HumanEval 164 题完整实验，并产出可复盘报告。
- benchmark 结果可以从 `samples.jsonl`、`report.json` 和 JSONL session log 中复盘。
- agent 能在公开 benchmark 派生的 workspace 中完成“理解题目 -> 写入代码 -> 运行测试 -> 记录结果”的闭环。
- 越界路径被拒绝。
- 高风险命令被拦截或要求确认。
- 超时命令被终止，失败信息清晰返回。
- 工具参数非法时返回清晰错误。
- `pytest` 覆盖核心 coding 工作流、安全与工具逻辑。
- `.env` 和敏感日志不会进入 Git。

已完成：
- 下载 OpenAI HumanEval 公开数据到 `benchmarks/data/HumanEval/HumanEval.jsonl.gz`。
- 实现 `benchmarks/humaneval_runner.py`，支持 HumanEval 加载、agent 运行、样本输出和报告生成。
- 实现 HumanEval 断点续跑和单题异常兜底。
- 完成 HumanEval 164 题完整实验：159/164 通过，pass@1 = 96.95%。
- 实现 workspace 路径边界检查。
- 实现危险 shell 命令默认拦截。
- 实现 shell 输出截断。
- 实现 agent 连续工具错误阈值。
- 调研 SWE-bench，确认官方复现依赖 Docker/容器环境和较重工程环境；当前版本已删除 SWE-bench adapter、数据文件、测试脚本和 evaluator 封装，仅保留复现困难记录。

验证：
- `C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest` 通过，84 passed。
- HumanEval 完整实验报告位于 `开发文档/10_HumanEval完整实验报告.md`。

状态：Done。

## Sprint 4：演示与交付

目标：
- 准备稳定可复现的最终演示流程和提交材料。
- 确保交付内容能说明项目目标、运行方式、测试结果、benchmark 结果和工程过程。
- 进行敏感信息检查，避免 API key、`.env`、缓存日志等进入提交材料。

任务：
- 整理最终 `README.txt`，控制在 1000 汉字以内，说明项目简介、环境、运行命令、测试命令和 HumanEval 结果。
- 编写 `开发文档/11_演示脚本.md`，用于 2 分钟以内视频录制。
- 编写 `开发文档/12_交付检查清单.md`，记录提交前检查项和结果。
- 确认 `README.md` 与开发文档中的 Sprint 状态一致。
- 运行全量 pytest。
- 扫描仓库文档和 benchmark 产物，确认不泄露 API key。
- 检查 Git 状态并推送最终提交到 GitHub。

验收：
- demo 能稳定复现。
- README.txt 不超过 1000 汉字。
- README.txt、演示脚本、交付检查清单均已提交。
- `pytest` 全量通过。
- API key 扫描无命中。
- GitHub `main` 分支已包含 Sprint4 交付材料。

已完成：
- 已编写最终 `README.txt`。
- 已编写 `开发文档/11_演示脚本.md`。
- 已编写 `开发文档/12_交付检查清单.md`。
- 已补充 `--verbose` 实时事件输出，运行时展示模型轮次、工具调用、工具结果和最终状态。
- 已验证全量测试：84 passed。
- 已验证 Sprint4 Agent demo：`--verbose` 运行成功，demo tests 2 passed。
- 已完成 API key 文档扫描：无命中。

状态：Done

## Sprint 5：特色功能 - 结构化上下文压缩

目标：
- 在长对话和多轮工具调用场景下控制上下文长度。
- 不依赖额外 agent 框架或 SDK，不额外调用模型做摘要。
- 用规则方式生成结构化 summary，保留 coding agent 最重要的工程状态。

任务：
- 新增 `agent/context_compressor.py`。
- 支持配置 `max_messages`、`keep_recent_messages`、`max_summary_chars`。
- 压缩时保留原始 system prompt 和最近若干条原始消息。
- 将旧消息摘要为结构化状态，包括原始任务、工具调用、修改文件、执行命令、错误和最近工具结果。
- 在 Agent 主循环中每轮模型调用前执行可选压缩。
- CLI 增加 `--compress-context`、`--context-max-messages`、`--context-keep-recent`。
- `--verbose` 增加 `context_compressed` 事件。
- 按 TDD 增加压缩器、主循环和 CLI 测试。

验收：
- 短上下文不压缩。
- 长上下文压缩后仍保留 system prompt、summary 和最近消息。
- summary 能提取 changed files、commands、errors。
- 压缩事件写入日志并能通过 verbose 展示。
- 全量测试通过。

验证：
- `C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest` 通过，84 passed。

状态：Done
