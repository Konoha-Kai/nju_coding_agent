from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PathResolution:
    ok: bool
    requested_path: str
    resolved_path: Path | None = None
    error: str = ""


class WorkspacePathPolicy:
    def __init__(self, workspace: Path | str) -> None:
        self.workspace = Path(workspace).resolve()

    def resolve(self, requested_path: str) -> PathResolution:
        raw_path = Path(str(requested_path))
        candidate = raw_path if raw_path.is_absolute() else self.workspace / raw_path
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.workspace)
        except ValueError:
            return PathResolution(
                ok=False,
                requested_path=str(requested_path),
                error=f"Path is outside workspace: {requested_path}",
            )
        return PathResolution(
            ok=True,
            requested_path=str(requested_path),
            resolved_path=resolved,
        )
