# Task 004: Test Generation Calculator

## 任务类型

test_generation

## 目标

在不修改生产代码的前提下，为 calculator 增加边界测试，覆盖负数、零、浮点数和异常输入。

## 初始状态

calculator 已有基础测试，但边界覆盖不足。任务要求体现 agent 的测试补全能力。

## 允许工具

- `list_files`
- `read_file`
- `write_file`
- `run_command`

## 禁止行为

- 不允许修改 `demo_workspace/calculator.py`。
- 不允许删除已有测试。
- 不允许写无断言测试。
- 不允许跳过测试。

## 验收命令

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest demo_workspace/tests
```

## 评分点

- 新测试覆盖有实际边界价值。
- 不修改生产代码。
- 测试命名清晰。
- 所有测试通过。
- 最终总结说明新增测试覆盖范围。

## 日志证据

- 读取生产代码理解函数行为。
- 写入测试文件。
- 执行 pytest。

