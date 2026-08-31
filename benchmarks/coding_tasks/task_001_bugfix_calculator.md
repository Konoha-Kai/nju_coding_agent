# Task 001: Bugfix Calculator

## 任务类型

bugfix

## 目标

修复 `demo_workspace/calculator.py` 中的计算错误，并运行测试确认所有 calculator 测试通过。

## 初始状态

`demo_workspace/` 包含一个简单 calculator 模块和对应测试。后续 Sprint 3 可通过 fixture 复制一个带缺陷版本，让 agent 在隔离 workspace 中修复。

## 允许工具

- `list_files`
- `read_file`
- `write_file`
- `run_command`

## 禁止行为

- 不允许修改 `.env`。
- 不允许删除测试文件。
- 不允许跳过或弱化测试断言。
- 不允许修改项目根目录之外的文件。

## 验收命令

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest demo_workspace/tests
```

## 评分点

- 能读取 calculator 实现和测试。
- 能定位失败测试对应的函数。
- 修改范围只包含必要代码。
- 验收命令通过。
- 最终总结列出修改文件和测试结果。

## 日志证据

- 至少一次 `read_file`。
- 至少一次 `write_file`。
- 至少一次 `run_command`。
- `session_end` 中能看到任务最终状态。

