"""Session activation markers and the local audit log.

Plugin hooks fire for every tool call in every session. content-wand's guards
must only apply while the skill is actually in use, so the skill (or the
UserPromptExpansion / Skill hook) writes a small marker file keyed by session
id. Hooks check it and stay out of the way otherwise.

The audit log is local-only, append-only JSONL. It records decisions and
fingerprints, never page content, prompts or full URLs.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from . import paths

ACTIVE_TTL_SECONDS = 12 * 3600
AUDIT_MAX_BYTES = 1_000_000
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")


def _marker(session_id: str) -> Path:
    if not SESSION_ID_RE.match(session_id or ""):
        raise ValueError("invalid session id")
    return paths.sessions_dir() / f"{session_id}.json"


def activate(session_id: str, cwd: str = "", via: str = "hook") -> dict[str, Any]:
    try:
        marker = _marker(session_id)
    except ValueError:
        return {"ok": False, "error": "invalid session id"}
    paths.sessions_dir(create=True)
    data = {"session_id": session_id, "started_at": time.time(), "cwd": cwd, "via": via}
    already = False
    if marker.exists():
        try:
            prev = json.loads(marker.read_text(encoding="utf-8"))
            data["started_at"] = float(prev.get("started_at", data["started_at"]))
            data["via"] = prev.get("via", via) if prev.get("via") == "hook" else via
            already = True
        except (ValueError, OSError):
            pass
    data["refreshed_at"] = time.time()
    tmp = marker.with_suffix(".tmp")
    tmp.write_text(json.dumps(data), encoding="utf-8")
    os.replace(tmp, marker)
    _cleanup()
    return {"ok": True, "session_id": session_id, "already_active": already, "via": data["via"]}


def info(session_id: str) -> dict[str, Any] | None:
    try:
        marker = _marker(session_id)
    except ValueError:
        return None
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if time.time() - float(data.get("refreshed_at", 0)) > ACTIVE_TTL_SECONDS:
        return None
    return data


def is_active(session_id: str) -> bool:
    return info(session_id) is not None


def _cleanup(max_age_days: int = 7) -> None:
    d = paths.sessions_dir()
    if not d.is_dir():
        return
    cutoff = time.time() - max_age_days * 86400
    for f in d.glob("*.json"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except OSError:
            pass


def _redact_url(url: str) -> str:
    m = re.match(r"^(https?://[^/?#]+)(/[^?#]*)?", url or "")
    return (m.group(1) + (m.group(2) or "")) if m else "[unparsed]"


def audit(event: str, decision: str, session_id: str = "", tool: str = "", detail: str = "", extra: dict[str, Any] | None = None) -> None:
    try:
        log = paths.audit_log_path()
        paths.state_dir(create=True)
        if log.exists() and log.stat().st_size > AUDIT_MAX_BYTES:
            os.replace(log, log.with_suffix(".jsonl.1"))
        entry = {
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "session": hashlib.sha256(session_id.encode()).hexdigest()[:10] if session_id else "",
            "event": event,
            "decision": decision,
            "tool": tool,
            "detail": detail[:200],
        }
        if extra:
            entry["extra"] = extra
        fd = os.open(log, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def audit_tail(n: int = 20) -> list[dict[str, Any]]:
    log = paths.audit_log_path()
    if not log.exists():
        return []
    lines = log.read_text(encoding="utf-8").splitlines()[-n:]
    out = []
    for ln in lines:
        try:
            out.append(json.loads(ln))
        except ValueError:
            continue
    return out


redact_url = _redact_url
