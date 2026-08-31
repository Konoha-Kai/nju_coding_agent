from __future__ import annotations

from pathlib import Path

from benchmarks.swebench_dataset import list_instance_ids


def test_selected_swebench_lite_dev_ids_exist_in_downloaded_public_data() -> None:
    selected_ids = [
        line.strip()
        for line in Path("benchmarks/selected_swebench_lite_dev_ids.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip() and not line.startswith("#")
    ]
    public_ids = set(
        list_instance_ids(Path("benchmarks/data/SWE-bench_Lite/dev-00000-of-00001.parquet"))
    )

    assert len(selected_ids) == 10
    assert set(selected_ids).issubset(public_ids)
