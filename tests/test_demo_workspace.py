import os
import subprocess
import sys
from pathlib import Path


def test_demo_workspace_contains_runnable_python_project() -> None:
    demo = Path("demo_workspace")

    assert (demo / "calculator.py").is_file()
    assert (demo / "tests" / "test_calculator.py").is_file()


def test_demo_workspace_tests_pass_before_agent_changes() -> None:
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    completed = subprocess.run(
        [
            sys.executable,
            "-s",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "demo_workspace/tests",
        ],
        text=True,
        capture_output=True,
        timeout=20,
        env=env,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
