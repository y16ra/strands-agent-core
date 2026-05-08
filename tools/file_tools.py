from __future__ import annotations

import os
from pathlib import Path
import subprocess

from strands.tools import tool


WORKING_DIR_ENV_VAR = "STRANDS_WORKING_DIR"


def _get_working_dir() -> Path:
    configured_dir = os.getenv(WORKING_DIR_ENV_VAR, "").strip()
    if configured_dir:
        target = Path(configured_dir).expanduser()
        if target.is_dir():
            return target.resolve()
    return Path.cwd()


def get_working_dir() -> Path:
    """Get current working directory for app and tools."""
    return _get_working_dir()


def is_git_repository() -> bool:
    """Return true when working directory is inside git work tree."""
    completed = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=_get_working_dir(),
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0 and completed.stdout.strip() == "true"


def get_current_branch_name() -> str | None:
    """Return current branch name, detached HEAD marker, or None."""
    if not is_git_repository():
        return None

    completed = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
        cwd=_get_working_dir(),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        return completed.stdout.strip()

    detached = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=_get_working_dir(),
        capture_output=True,
        text=True,
        check=False,
    )
    if detached.returncode == 0:
        return f"(detached at {detached.stdout.strip()})"
    return None


def _resolve_workspace_path(path: str) -> Path:
    target = Path(path)
    if target.is_absolute():
        raise ValueError("絶対パスは指定できません。")
    return _get_working_dir() / target


@tool
def read_file(path: str) -> str:
    """Read a file from local workspace."""
    target = _resolve_workspace_path(path)
    return target.read_text(encoding="utf-8")


def _run_git_command(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=_get_working_dir(),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "git command failed."
        raise ValueError(stderr)
    return completed.stdout


def _default_base_branch() -> str:
    for candidate in ("main", "master"):
        try:
            _run_git_command(["rev-parse", "--verify", candidate])
            return candidate
        except ValueError:
            continue
    return "HEAD"


@tool
def list_changed_files(scope: str = "working_tree") -> str:
    """List changed files from git.

    scope: working_tree | staged | branch
    """
    if scope == "working_tree":
        output = _run_git_command(["diff", "--name-only"])
    elif scope == "staged":
        output = _run_git_command(["diff", "--cached", "--name-only"])
    elif scope == "branch":
        base = _default_base_branch()
        output = _run_git_command(["diff", "--name-only", f"{base}...HEAD"])
    else:
        raise ValueError("scope must be one of: working_tree, staged, branch")
    return output.strip()


@tool
def get_git_diff(scope: str = "working_tree") -> str:
    """Get git diff text.

    scope: working_tree | staged | branch
    """
    if scope == "working_tree":
        output = _run_git_command(["diff"])
    elif scope == "staged":
        output = _run_git_command(["diff", "--cached"])
    elif scope == "branch":
        base = _default_base_branch()
        output = _run_git_command(["diff", f"{base}...HEAD"])
    else:
        raise ValueError("scope must be one of: working_tree, staged, branch")
    return output.strip()


@tool
def write_markdown(path: str, content: str) -> str:
    """Write markdown content to local workspace."""
    target = _resolve_workspace_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"saved: {target}"
