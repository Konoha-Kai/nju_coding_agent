# Product Backlog

## P0：必须完成

| ID | 用户故事 | 验收标准 | 状态 |
| --- | --- | --- | --- |
| BL-001 | 作为用户，我可以通过 CLI 输入一个编程任务 | `main.py` 支持命令行任务参数 | Todo |
| BL-002 | 作为系统，我可以调用 DeepSeek API | `test_deepseek_api.py` 在 `nju` 环境下通过 | Done |
| BL-003 | 作为 agent，我可以维护多轮消息上下文 | 工具结果能进入下一轮模型请求 | Todo |
| BL-004 | 作为 agent，我可以读取 workspace 文件 | 支持 list/read 工具，限制路径 | Todo |
| BL-005 | 作为 agent，我可以写入 workspace 文件 | 支持 write/replace 工具，限制路径 | Todo |
| BL-006 | 作为 agent，我可以执行本地命令 | 返回 stdout、stderr、exit code、timeout | Todo |
| BL-007 | 作为 agent，我可以解析模型 tool_calls | 支持 function name 和 JSON arguments | Todo |
| BL-008 | 作为系统，我可以判断循环终止 | 支持 done、max steps、error threshold | Todo |

## P1：建议完成

| ID | 用户故事 | 验收标准 | 状态 |
| --- | --- | --- | --- |
| BL-101 | 作为开发者，我可以查看执行日志 | 每轮请求、响应、工具结果写入 JSONL | Todo |
| BL-102 | 作为用户，我可以确认危险命令 | 删除、移动、安装依赖等命令前拦截 | Todo |
| BL-103 | 作为开发者，我可以运行单元测试 | 覆盖 safety、filesystem、shell、parser | Todo |
| BL-104 | 作为用户，我能看到清晰最终总结 | 总结修改文件、执行命令、测试结果 | Todo |
| BL-105 | 作为评委，我能看到设计文档 | 开发文档持续更新 | In Progress |

## P2：可选增强

| ID | 用户故事 | 验收标准 | 状态 |
| --- | --- | --- | --- |
| BL-201 | 支持流式输出 | 用户能实时看到模型输出 | Todo |
| BL-202 | 支持上下文压缩 | 超长历史可摘要保留关键信息 | Todo |
| BL-203 | 支持计划面板 | agent 每轮更新任务计划 | Todo |
| BL-204 | 支持更细粒度文件补丁 | 用 patch 而不是整文件覆盖 | Todo |

