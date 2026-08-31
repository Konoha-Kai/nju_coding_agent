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

## Sprint 3：安全与质量

目标：
- 增加软件工程质量保障。
- 让系统更适合面试解释和评分。
- 为本地文件和命令执行建立明确安全边界。

任务：
- 实现 workspace 路径边界检查。
- 阻止路径穿越和 workspace 外文件访问。
- 实现危险命令识别和确认机制。
- 完善命令超时、输出截断和失败处理。
- 增加错误阈值终止条件。
- 增加 safety、filesystem、shell、tool parser 单元测试。
- 增加代码风格检查或基础静态检查。
- 检查日志、README、视频脚本中不泄露 API key。

验收：
- 越界路径被拒绝。
- 高风险命令被拦截或要求确认。
- 超时命令被终止。
- 工具参数非法时返回清晰错误。
- `pytest` 覆盖核心安全与工具逻辑。
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
