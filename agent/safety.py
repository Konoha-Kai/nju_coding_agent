from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shlex


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
    def evaluate(
        self,
        command: str,
        allow_dangerous: bool = False,
        workspace: Path | str | None = None,
    ) -> CommandSafetyDecision:
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
        if workspace is not None:
            path_decision = self._evaluate_workspace_paths(command, Path(workspace).resolve())
            if not path_decision.allowed:
                return path_decision

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

    def _evaluate_workspace_paths(self, command: str, workspace: Path) -> CommandSafetyDecision:
        for index, token in enumerate(_split_command_tokens(command)):
            cleaned = token.strip().strip("\"'")
            if not cleaned or cleaned.startswith("-"):
                continue
            if index == 0 and _looks_like_executable_path(cleaned):
                continue
            if _looks_like_path_argument(cleaned) and not _is_path_inside_workspace(cleaned, workspace):
                return CommandSafetyDecision(
                    allowed=False,
                    reason="outside_workspace_path",
                    message=f"Blocked command path outside workspace: {cleaned}",
                )
        return CommandSafetyDecision(True)


def _split_command_tokens(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=False)
    except ValueError:
        return command.split()


def _looks_like_path_argument(token: str) -> bool:
    if ".." in Path(token).parts:
        return True
    if re.match(r"^[A-Za-z]:[\\/]", token):
        return True
    if token.startswith(("/", "\\")):
        return True
    return "\\" in token or "/" in token


def _looks_like_executable_path(token: str) -> bool:
    lowered = token.lower()
    return _looks_like_path_argument(token) and lowered.endswith((".exe", ".bat", ".cmd", ".ps1"))


def _is_path_inside_workspace(token: str, workspace: Path) -> bool:
    path = Path(token)
    candidate = path if path.is_absolute() else workspace / path
    try:
        candidate.resolve().relative_to(workspace)
    except (OSError, ValueError):
        return False
    return True
