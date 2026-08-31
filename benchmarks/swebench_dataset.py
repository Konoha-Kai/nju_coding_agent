from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from benchmarks.swebench_adapter import SwebenchInstance


def list_instance_ids(parquet_path: Path | str, limit: int | None = None) -> list[str]:
    table = pq.read_table(parquet_path, columns=["instance_id"])
    ids = [str(value.as_py()) for value in table["instance_id"]]
    return ids[:limit] if limit is not None else ids


def load_instance_from_parquet(parquet_path: Path | str, instance_id: str) -> SwebenchInstance:
    for row in _read_rows(parquet_path):
        if str(row["instance_id"]) == instance_id:
            return SwebenchInstance.from_mapping(row)
    raise ValueError(f"SWE-bench instance not found: {instance_id}")


def export_instance_json(
    parquet_path: Path | str,
    instance_id: str,
    output_path: Path | str,
) -> SwebenchInstance:
    instance = load_instance_from_parquet(parquet_path, instance_id)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(instance.__dict__, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return instance


def _read_rows(parquet_path: Path | str) -> list[dict[str, Any]]:
    table = pq.read_table(parquet_path)
    rows: list[dict[str, Any]] = []
    columns = table.column_names
    for values in zip(*[table[column].to_pylist() for column in columns]):
        rows.append(dict(zip(columns, values)))
    return rows
