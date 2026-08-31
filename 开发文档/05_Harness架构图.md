# Harness 架构图

## 1. 总体架构

```mermaid
flowchart TB
    User[User / CLI] --> Main[main.py]
    Main --> Agent[Agent Loop]
    Agent --> Context[Context Manager]
    Agent --> Registry[Tool Registry]
    Agent --> ModelClient[Model Client]

    ModelClient --> DeepSeek[DeepSeek Chat Completions API]
    DeepSeek --> ModelClient

    Agent --> Parser[Tool Call Parser]
    Parser --> Registry

    Registry --> FS[Filesystem Tools]
    Registry --> Shell[Shell Tool]
    Registry --> Safety[Safety Guard]

    Safety --> Workspace[(Workspace)]
    FS --> Workspace
    Shell --> Workspace

    Agent --> Logger[JSONL Logger]
    Logger --> SessionLog[(Session Logs)]

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
    participant M as Model Client
    participant D as DeepSeek API
    participant T as Local Tools
    participant L as Logger

    U->>CLI: 输入编程任务
    CLI->>A: run(task)
    A->>C: 写入 system + user messages
    A->>M: chat(messages, tools)
    M->>D: POST /chat/completions
    D-->>M: assistant message / tool_calls
    M-->>A: ModelReply
    A->>L: 记录模型回复

    alt 返回 tool_calls
        A->>T: 校验并执行本地工具
        T-->>A: ToolResult
        A->>C: 写入 tool message
        A->>L: 记录工具结果
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
    loop --> context[agent.context]
    loop --> model[agent.model_client]
    loop --> schema[agent.tool_schema]
    loop --> logger[agent.logger]
    schema --> filesystem[tools.filesystem]
    schema --> shell[tools.shell]
    filesystem --> safety[tools.safety]
    shell --> safety
```

## 4. 设计说明

- Harness 负责把模型能力、本地工具、上下文和执行日志组合成一个可控运行环境。
- DeepSeek API 只负责模型推理和 function tool call 决策。
- 文件读写、命令执行、安全策略、日志和循环控制都在本地项目中自行实现。
- workspace 是所有文件和命令操作的边界。
- session logs 用于复盘每一次任务执行过程，也便于录制视频和面试说明。

