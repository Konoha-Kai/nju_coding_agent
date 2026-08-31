from __future__ import annotations

import json
from pathlib import Path

from benchmarks.swebench_dataset import (
    export_instance_json,
    list_instance_ids,
    load_instance_from_parquet,
)


DATASET_PATH = Path("benchmarks/data/SWE-bench_Lite/dev-00000-of-00001.parquet")


def test_list_instance_ids_reads_downloaded_public_lite_data() -> None:
    ids = list_instance_ids(DATASET_PATH, limit=3)

    assert len(ids) == 3
    assert all("__" in instance_id for instance_id in ids)


def test_load_instance_from_parquet_returns_swebench_instance() -> None:
    instance_id = list_instance_ids(DATASET_PATH, limit=1)[0]

    instance = load_instance_from_parquet(DATASET_PATH, instance_id)

    assert instance.instance_id == instance_id
    assert "/" in instance.repo
    assert instance.base_commit
    assert instance.problem_statement


def test_export_instance_json_writes_runner_input_shape() -> None:
    instance_id = list_instance_ids(DATASET_PATH, limit=1)[0]
    output_path = Path("test_workspace") / "swebench_exported_instance.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    instance = export_instance_json(DATASET_PATH, instance_id, output_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["instance_id"] == instance.instance_id
    assert payload["repo"] == instance.repo
    assert payload["base_commit"] == instance.base_commit
    assert payload["problem_statement"] == instance.problem_statement
