# Harness 架构图

## 1. 总体架构

```mermaid
flowchart TB
    User[User / CLI] --> Main[main.py]
    Main --> Agent[Agent Loop]
    Agent --> Context[Context Manager]
    Agent --> Actions[Lightweight Action Dispatcher]
    Agent --> ModelClient[Model Client]

    ModelClient --> DeepSeek[DeepSeek Chat Completions API]
    DeepSeek --> ModelClient

    Agent --> Parser[JSON Action Parser]
    Parser --> Actions

    Actions --> FS[list/read/write file]
    Actions --> Shell[run command]

    FS --> Workspace
    Shell --> Workspace

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
    participant T as Local Actions

    U->>CLI: 输入编程任务
    CLI->>A: run(task)
    A->>C: 写入 system + user messages
    A->>M: chat(messages, tools)
    M->>D: POST /chat/completions
    D-->>M: assistant message / tool_calls
    M-->>A: ModelReply

    alt 返回 action JSON
        A->>T: 执行本地动作
        T-->>A: ToolResult
        A->>C: 写入 Observation
        A->>M: 下一轮 chat(messages, tools)
    else 返回最终回复
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
    loop --> actions[agent.actions]
```

## 4. 设计说明

- Sprint 1 初版 Harness 负责把模型能力、轻量动作、本地执行和上下文组合成最小闭环。
- DeepSeek API 只负责模型推理，当前不使用正式 function tool calls。
- 文件读写、命令执行和循环控制都在本地项目中自行实现。
- 安全策略、正式工具注册和 session logs 将在 Sprint 2 加入。
