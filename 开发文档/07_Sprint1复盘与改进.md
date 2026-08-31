# Sprint 1 复盘与改进

## 1. 本次检查结论

Sprint 1 的定位是“最小 Agent 闭环”，当前实现可以作为第一版通过：已经具备 DeepSeek 模型调用、上下文维护、轻量动作解析、本地文件动作、本地命令执行、CLI 入口和基础单元测试。

但从软件工程考核角度看，Sprint 1 仍有一些需要记录和改进的地方，尤其是提交粒度、验收证据和后续功能边界。

## 2. Sprint 1 已满足内容

- 有明确的 CLI 入口：`main.py`。
- 有模型客户端：`agent/model_client.py`。
- 有上下文管理：`agent/context.py`。
- 有主循环：`agent/loop.py`。
- 有本地动作执行：`agent/actions.py`。
- 有测试目录：`tests/`。
- 有基础测试覆盖：
  - JSON action 解析。
  - 上下文消息追加。
  - 文件写入、读取、列表。
  - 命令执行。
  - agent 多轮执行直到 final。
- 已用 `nju` 环境验证：

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest
```

验证结果：7 passed。

## 3. 当前缺少或较弱的内容

### 3.1 提交粒度不够细

Sprint 1 的工程代码和测试代码被放进同一次提交：

```text
5bc3ec2 implement sprint 1 minimal agent
```

这能证明功能完成，但从考核角度看，提交历史不够清晰。更好的做法是拆成两次：

```text
implement sprint 1 minimal agent
add sprint 1 tests
```

由于该提交已经推送到 GitHub，不建议为了拆分提交而改写公开历史。后续从 Sprint 2 开始按更细粒度提交。

### 3.2 验收证据需要更完整

当前文档记录了 `7 passed`，但还可以补充：

- 真实 DeepSeek 冒烟测试命令。
- agent 实际执行了哪些 action。
- 输出结果摘要。
- 是否产生文件修改。

后续每个 sprint 应增加“验收记录”小节。

### 3.3 轻量 action 协议只是过渡方案

Sprint 1 当前使用模型直接返回 JSON action，本地解析执行。这个方案简单、可运行，但还不是正式的 DeepSeek tool calls。

后续 Sprint 2 应升级为：

- `tools` schema。
- `tool_calls` 解析。
- tool message 回填。
- 多 tool calls 顺序执行。
- 工具注册表。

### 3.4 安全边界暂未实现

当前按用户要求没有加入安全边界，因此存在已知风险：

- 路径没有限制在 workspace 内。
- 写文件可能覆盖任意相对路径。
- shell 命令使用 `shell=True`。
- 没有危险命令审批。

这些问题不作为 Sprint 1 阻塞项，但必须在 Sprint 3 解决。

### 3.5 日志和可复盘能力不足

当前 `AgentResult` 保存 observations，但没有 JSONL session log。面试和视频复盘时，日志会是明显加分点。

Sprint 2 应加入：

- session id。
- 每轮模型请求摘要。
- 模型回复。
- 工具调用。
- 工具结果。
- 最终总结。

## 4. Sprint 1 是否需要立即修改代码

暂不建议为 Sprint 1 回头做大改，因为 Sprint 2 本来就要升级正式工具系统。当前更合理的处理方式：

- 保留 Sprint 1 作为最小闭环版本。
- 用本文档记录不足和改进计划。
- 从 Sprint 2 开始拆分提交粒度。
- Sprint 2 先提交工程代码，再提交测试代码，再提交文档更新。

## 5. 后续提交规范

从 Sprint 2 开始，即使是简单功能，也按最少两次提交组织：

1. 工程代码提交：

```text
implement ...
```

2. 测试代码提交：

```text
add tests for ...
```

必要时增加第三次文档提交：

```text
document ...
```

这样 Git 历史能体现：

- 先实现能力。
- 再补验证。
- 最后同步文档。

## 6. Sprint 2 开发前检查清单

- 明确本轮 backlog 项。
- 先写接口设计或更新接口文档。
- 工程代码和测试代码分开 commit。
- 每次 commit 前检查 `.env` 没有 staged。
- 每次 sprint 结束推送 GitHub。
- 文档更新单独 commit，方便评委看开发过程。

