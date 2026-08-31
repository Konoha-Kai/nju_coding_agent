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


@dataclass(frozen=True)
class CommandSafetyDecision:
    allowed: bool
    reason: str = ""
    message: str = ""


class CommandSafetyPolicy:
    def evaluate(self, command: str, allow_dangerous: bool = False) -> CommandSafetyDecision:
        if allow_dangerous:
            return CommandSafetyDecision(True)

        normalized = command.strip().lower()
        tokens = normalized.replace(";", " ").replace("&&", " ").replace("||", " ").split()
        if not tokens:
            return CommandSafetyDecision(False, "empty_command", "Refusing to run empty command.")

        if self._contains_any(tokens, {"rm", "del", "erase", "rmdir", "rd", "remove-item"}):
            return self._blocked("delete_or_remove")
        if self._contains_any(tokens, {"mv", "move", "move-item"}):
            return self._blocked("move_or_rename")
        if self._is_dependency_install(tokens):
            return self._blocked("dependency_install")
        if self._contains_any(tokens, {"curl", "wget", "iwr", "invoke-webrequest"}):
            return self._blocked("network_download")

        return CommandSafetyDecision(True)

    def _blocked(self, reason: str) -> CommandSafetyDecision:
        return CommandSafetyDecision(
            allowed=False,
            reason=reason,
            message=f"Blocked dangerous command: {reason}",
        )

    def _contains_any(self, tokens: list[str], dangerous: set[str]) -> bool:
        return any(token.strip("\"'") in dangerous for token in tokens)

    def _is_dependency_install(self, tokens: list[str]) -> bool:
        cleaned = [token.strip("\"'") for token in tokens]
        command_pairs = {
            ("pip", "install"),
            ("python", "-m", "pip", "install"),
            ("python3", "-m", "pip", "install"),
            ("conda", "install"),
            ("npm", "install"),
            ("yarn", "add"),
            ("pnpm", "add"),
        }
        for pattern in command_pairs:
            size = len(pattern)
            for index in range(0, len(cleaned) - size + 1):
                if tuple(cleaned[index : index + size]) == pattern:
                    return True
        return False
