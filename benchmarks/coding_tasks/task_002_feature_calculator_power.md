# Task 002: Feature Calculator Power

## 任务类型

feature

## 目标

为 `demo_workspace/calculator.py` 增加 `power(base, exponent)` 函数，并补充测试覆盖正指数、零指数和负指数。

## 初始状态

calculator 模块当前只包含基础运算函数。任务要求 agent 扩展功能并同步维护测试。

## 允许工具

- `list_files`
- `read_file`
- `write_file`
- `run_command`

## 禁止行为

- 不允许删除已有函数。
- 不允许删除已有测试。
- 不允许引入非标准库依赖。
- 不允许修改 workspace 外文件。

## 验收命令

```powershell
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest demo_workspace/tests
```

## 评分点

- 新增函数命名和行为符合任务目标。
- 正指数、零指数、负指数均有测试。
- 已有测试继续通过。
- 修改集中在 calculator 和对应测试文件。
- 最终总结说明新增功能和测试结果。

## 日志证据

- 读取实现文件和测试文件。
- 写入实现文件和测试文件。
- 执行 pytest 并记录结果。

