项目名称：nju_coding_agent

这是一个面向南京大学软件学院推免考核的 Coding Agent Harness 项目，基于 DeepSeek API 和 OpenAI-compatible tool_calls 协议实现。项目按 Sprint 迭代开发，包含需求、Backlog、接口、架构、测试流程和实验报告。

主要功能：
1. 通过 CLI 接收编程任务。
2. 调用 DeepSeek 模型进行多轮推理。
3. 支持 list_files、read_file、write_file、run_command 四类工具。
4. 支持路径边界检查、危险命令拦截、超时、输出截断和错误阈值终止。
5. 生成 JSONL 会话日志，便于复盘。
6. 使用公开 HumanEval 数据集进行轻量 coding benchmark。

环境：
C:\Users\23639\.conda\envs\nju\python.exe

安装依赖：
pip install -r requirements.txt

运行测试：
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest

运行 Agent：
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "Read demo_workspace/calculator.py, run python -m pytest demo_workspace/tests -v, and summarize the result." --workspace . --max-steps 8

HumanEval 完整实验：
模型 deepseek-chat，公开 HumanEval 164 题，通过 159 题，pass@1 = 96.95%。报告位于 benchmarks/reports/humaneval_full_deepseek/。

SWE-bench 说明：
SWE-bench 更接近真实仓库级 bugfix，但官方复现依赖 Docker/容器环境，当前机器难以稳定复现，因此本版本仅记录复现较困难。

注意：
.env 已加入 .gitignore，API key 不提交到 GitHub。
