项目名称：nju_coding_agent
Git 仓库：https://github.com/Konoha-Kai/nju_coding_agent

这是南京大学软件学院推免考核 Coding Agent Harness 项目，基于 DeepSeek API 和 tool_calls 协议实现，不使用 agent 框架或 SDK。项目按 Sprint 迭代，包含需求、Backlog、接口、架构、测试和实验报告。

主要功能：
1. 通过 CLI 接收编程任务。
2. 调用 DeepSeek 模型进行多轮推理。
3. 支持 list_files、read_file、write_file、run_command 工具。
4. 支持路径边界、危险命令拦截、超时、截断和实时输出。
5. 生成日志。
6. 使用公开 HumanEval 数据集进行轻量 coding benchmark。

环境：
C:\Users\23639\.conda\envs\nju\python.exe

安装依赖：
pip install -r requirements.txt

运行测试：
C:\Users\23639\.conda\envs\nju\python.exe -s -m pytest
当前结果：78 passed

运行 Agent：
C:\Users\23639\.conda\envs\nju\python.exe -s main.py "Read demo_workspace/calculator.py, run python -m pytest demo_workspace/tests -v, and summarize." --workspace . --max-steps 8 --verbose

HumanEval：
deepseek-chat 在公开 HumanEval 164 题中通过 159 题，pass@1 = 96.95%。报告位于 benchmarks/reports/humaneval_full_deepseek/。

SWE-bench 说明：
SWE-bench 更接近仓库级 bugfix，但官方复现依赖 Docker，当前机器难以稳定复现，因此仅记录复现较困难。

注意：.env 已加入 .gitignore，API key 不提交。
