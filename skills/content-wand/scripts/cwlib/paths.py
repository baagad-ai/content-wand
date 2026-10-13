"""Filesystem locations used by content-wand.

State is stored outside any project, in a platform-neutral location, so the
same Writing Styles work in Claude Code, Codex, Gemini CLI, Cursor, Copilot and
every other agent that runs this skill.
"""

from __future__ import annotations

import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = SKILL_ROOT / "data"
REFERENCES_DIR = SKILL_ROOT / "references"

APP_NAME = "content-wand"


def legacy_state_dirs() -> list[Path]:
    home = Path.home()
    return [home / ".claude" / APP_NAME]


def state_dir(create: bool = False) -> Path:
    """Resolve the per-user state directory.

    Order: $CONTENT_WAND_HOME, then $XDG_CONFIG_HOME/content-wand, then
    ~/.config/content-wand.
    """
    override = os.environ.get("CONTENT_WAND_HOME")
    if override:
        base = Path(override).expanduser()
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        root = Path(xdg).expanduser() if xdg else Path.home() / ".config"
        base = root / APP_NAME
    if create:
        base.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            os.chmod(base, 0o700)
        except OSError:
            pass
    return base


def styles_dir(create: bool = False) -> Path:
    d = state_dir(create) / "styles"
    if create:
        d.mkdir(parents=True, exist_ok=True, mode=0o700)
    return d


def config_path() -> Path:
    return state_dir() / "config.json"


def overrides_path() -> Path:
    return state_dir() / "specs-overrides.json"


def proposals_dir(create: bool = False) -> Path:
    d = state_dir(create) / "proposals"
    if create:
        d.mkdir(parents=True, exist_ok=True, mode=0o700)
    return d


def cache_dir(create: bool = False) -> Path:
    d = state_dir(create) / "cache"
    if create:
        d.mkdir(parents=True, exist_ok=True, mode=0o700)
    return d


def audit_log_path() -> Path:
    return state_dir() / "audit.jsonl"


def sessions_dir(create: bool = False) -> Path:
    d = state_dir(create) / "sessions"
    if create:
        d.mkdir(parents=True, exist_ok=True, mode=0o700)
    return d


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False
