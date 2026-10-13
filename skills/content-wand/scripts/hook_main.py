#!/usr/bin/env python3
"""Lightweight entry point for Claude Code hooks.

Plugin hooks fire on every tool call in every session, so the common case, a
session that is not using content-wand, must cost almost nothing. This file
loads only the session marker module and exits immediately unless content-wand
is active (or the event is one that can activate it). The full guard logic in
cwlib.hooks is imported only when needed. Any internal error exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    event = sys.argv[1]
    raw = sys.stdin.read(4_000_000)
    try:
        data = json.loads(raw) if raw.strip() else {}
        sid = str(data.get("session_id", ""))
        if event in ("pre_tool_use", "post_tool_use") and data.get("tool_name") != "Skill":
            from cwlib import session

            if not session.is_active(sid):
                return 0
        elif event == "stop":
            from cwlib import session

            if not session.info(sid):
                return 0
        from cwlib import hooks

        code, out = hooks.run(event, raw)
    except Exception:  # noqa: BLE001 - a guard must never break the user's session
        return 0
    if out:
        sys.stdout.write(out + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
