# Harness 架构图

## 1. 总体架构

```mermaid
flowchart TB
    User[User / CLI] --> Main[main.py]
    Main --> Agent[Agent Loop]
    Agent --> Context[Context Manager]
    Agent --> Compressor[Structured Context Compressor]
    Agent --> Registry[Tool Registry]
    Agent --> ModelClient[Model Client]
    Agent --> Logger[JSONL Logger]

    ModelClient --> DeepSeek[DeepSeek Chat Completions API]
    DeepSeek --> ModelClient

    ModelClient --> Parser[Tool Calls Parser]
    Parser --> Agent

    Registry --> FS[Filesystem Tools]
    Registry --> Shell[Shell Tool]

    FS --> Workspace
    Shell --> Workspace
    Logger --> Logs[(Session Logs)]

    Agent --> Result[Final Response]
    Result --> User
```

## 2. Agent 执行时序

```mermaid
sequenceDiagram
    participant U as User
    participant CLI as CLI
    participant A as Agent Loop
    participant C as Context
    participant X as Context Compressor
    participant M as Model Client
    participant D as DeepSeek API
    participant R as Tool Registry
    participant T as Local Tools
    participant L as JSONL Logger

    U->>CLI: 输入编程任务
    CLI->>A: run(task)
    A->>C: 写入 system + user messages
    opt 上下文超过阈值
        A->>X: compress(messages)
        X-->>A: system prompt + structured summary + recent messages
        A->>L: 记录 context_compressed
    end
    A->>M: chat(messages, tools)
    M->>D: POST /chat/completions
    D-->>M: assistant message / tool_calls
    M-->>A: ModelReply
    A->>L: 记录 model_reply

    alt 返回 tool_calls
        A->>R: 按 function name 查找工具
        R->>T: 执行本地工具
        T-->>A: ToolResult
        A->>C: 写入 role=tool 消息
        A->>L: 记录 tool_call / tool_result
        A->>M: 下一轮 chat(messages, tools)
    else 返回最终回复
        A->>L: 记录 agent_finish
        A-->>CLI: AgentResult
        CLI-->>U: 输出最终结果
    end
```

## 3. 模块依赖图

```mermaid
graph LR
    main[main.py] --> loop[agent.loop]
    main --> bootstrap[agent.bootstrap]
    bootstrap --> filesystem[tools.filesystem]
    bootstrap --> shell[tools.shell]
    loop --> context[agent.context]
    loop --> compressor[agent.context_compressor]
    loop --> model[agent.model_client]
    loop --> tooling[agent.tooling]
    loop --> logger[agent.logger]
    filesystem --> tooling
    shell --> tooling
```

## 4. 设计说明

- Harness 负责把模型能力、正式工具系统、本地执行、上下文压缩和 JSONL 日志组合成可复盘闭环。
- DeepSeek API 负责模型推理和 function tool call 决策。
- 文件读写、命令执行、工具分发、日志和循环控制都在本地项目中自行实现。
- 结构化上下文压缩不额外调用模型，而是用规则提取任务、工具调用、修改文件、命令、错误和最近工具结果。
