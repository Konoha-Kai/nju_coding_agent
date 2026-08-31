# DeepSeek 开发文档参考记录

## 1. API 接入

参考 DeepSeek API Quick Start：

- OpenAI 兼容 base URL：`https://api.deepseek.com`。
- API key 通过环境变量提供。
- 可使用 OpenAI SDK 调用 DeepSeek。
- Chat API 路径为 `/chat/completions`。

项目采用：

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)
```

## 2. Chat Completions

参考 DeepSeek Chat Completions API：

- 请求核心字段：`model`、`messages`。
- 支持 `stream`、`temperature`、`max_tokens` 等参数。
- 支持 `response_format={"type": "json_object"}`。
- 支持 `tools` 和 `tool_choice`。
- assistant 可能返回 `tool_calls`。
- tool message 需要携带 `tool_call_id`。

本项目计划使用 Chat Completions 作为模型决策接口。

## 3. Tool Calls

参考 DeepSeek Tool Calls：

- 工具类型为 `function`。
- 工具参数使用 JSON Schema 描述。
- 模型返回的 function arguments 是 JSON 字符串。
- 文档提醒模型生成的参数不一定总是合法，调用前必须由业务代码校验。

本项目对应设计：

- `ToolSpec` 管理工具名称、描述和参数 schema。
- `ToolCallParser` 解析工具调用。
- `SafetyGuard` 在执行前校验路径和命令。
- `ToolResult` 统一返回工具执行结果。

## 4. Harness 思路

参考 DeepSeek Harness 文档：

- 需要选择 workspace。
- agent 可以读写 workspace 文件、运行命令、维护计划。
- 操作可能受权限策略约束。
- session 目录可以保存 JSONL 日志。
- Python SDK 示例强调 workspace、session root、session id。

本项目不直接使用 DeepSeek Harness SDK，因为题目禁止使用 agent 框架 / SDK。这里只参考它的工程思想：

- workspace 隔离。
- session 日志。
- 持久上下文。
- 工具分层。
- 权限审批。

## 5. 参考链接

- DeepSeek API Quick Start: https://api-docs.deepseek.com/
- DeepSeek Chat Completions API: https://api-docs.deepseek.com/api/create-chat-completion/
- DeepSeek Tool Calls: https://api-docs.deepseek.com/guides/tool_calls/
- DeepSeek Harness Guide: https://deepseek-harness.github.io/deepseek-harness/en/guide/quickstart
- DeepSeek Harness Python SDK: https://deepseek-harness.github.io/deepseek-harness/en/guide/python-sdk

