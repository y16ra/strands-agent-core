from __future__ import annotations

from pathlib import Path
import subprocess

from strands.tools import tool


def _resolve_workspace_path(path: str) -> Path:
    target = Path(path)
    if target.is_absolute():
        raise ValueError("絶対パスは指定できません。")
    return Path.cwd() / target


@tool
def read_file(path: str) -> str:
    """Read a file from local workspace."""
    target = _resolve_workspace_path(path)
    return target.read_text(encoding="utf-8")


def _run_git_command(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=Path.cwd(),
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
