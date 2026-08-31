# Task 003: Refactor Calculator Errors

## 任务类型

refactor

## 目标

重构 calculator 的错误处理逻辑：除零时明确抛出 `ValueError("division by zero")`，并保持其他函数行为不变。

## 初始状态

calculator 模块已有除法逻辑。任务要求改善错误语义，而不是大范围改写模块。

## 允许工具

- `list_files`
- `read_file`
- `write_file`
- `run_command`

## 禁止行为

- 不允许改变非除法函数的行为。
- 不允许删除已有测试。
- 不允许通过修改测试来掩盖错误。
- 不允许引入外部依赖。

## 验收命令

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest demo_workspace/tests
```

## 评分点

- 只在必要位置调整除零错误处理。
- 测试能覆盖异常类型和异常消息。
- 已有功能不回归。
- agent 在总结中说明这是重构而不是功能扩展。

## 日志证据

- 读取 calculator 和测试文件。
- 写入最小范围改动。
- 执行 pytest。

