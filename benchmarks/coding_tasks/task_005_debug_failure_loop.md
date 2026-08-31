# Task 005: Debug Failure Loop

## 任务类型

debug_failure

## 目标

运行测试后，如果出现失败，agent 需要读取失败输出、定位原因、修改代码或测试，再次运行测试，直到通过或达到最大步数。

## 初始状态

该任务用于验证 agent 是否能基于 `run_command` 的 stdout/stderr 结果进行下一轮修复，而不是只执行一次命令。

## 允许工具

- `list_files`
- `read_file`
- `write_file`
- `run_command`

## 禁止行为

- 不允许删除失败测试。
- 不允许用空实现或硬编码绕过测试。
- 不允许修改 workspace 外文件。
- 不允许在失败后直接宣称成功。

## 验收命令

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest demo_workspace/tests
```

## 评分点

- 至少能执行一次测试命令。
- 如果测试失败，能从失败输出中提取有效线索。
- 能进行第二轮修复或解释无法修复的具体原因。
- 最终状态和日志一致。
- 总结中包含执行过的测试命令和结果。

## 日志证据

- 至少一次 `run_command`。
- 如果首次测试失败，应出现后续 `read_file` 或 `write_file`。
- `session_end` 和最终总结不矛盾。
