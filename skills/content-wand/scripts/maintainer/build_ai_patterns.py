#!/usr/bin/env python3
"""Derive data/ai-patterns.json from references/ai-patterns.md.

The markdown file is the human-edited source of truth (the humanizer reads it).
The JSON file is what scripts/cw.py uses for deterministic linting. CI runs
this script with --check to make sure the two never drift apart.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD = ROOT / "references" / "ai-patterns.md"
OUT = ROOT / "data" / "ai-patterns.json"


def _section(txt: str, start: str, end: str) -> str:
    s = txt.index(start)
    e = txt.index(end, s) if end else len(txt)
    return txt[s:e]


def _rows(block: str) -> list[list[str]]:
    rows = []
    for line in block.splitlines():
        if line.startswith("|") and not line.startswith("|---") and "AI Word/Phrase" not in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3:
                rows.append(cells[:3])
    return rows


def _terms(cell: str) -> list[str]:
    cell = re.sub(r"\([^)]*\)", "", cell)
    out = []
    for part in cell.split("/"):
        t = part.strip().lower()
        if t:
            out.append(t)
    return out


def _stem_regex(term: str) -> str:
    words = term.split()
    if len(words) > 1:
        return r"\b" + r"\s+".join(re.escape(w) for w in words) + r"\b"
    w = words[0]
    if len(w) > 5 and w.endswith("e"):
        stem = w[:-1]
    elif len(w) > 5 and w.endswith("y"):
        stem = w[:-1]
    else:
        stem = w
    return r"\b" + re.escape(stem) + r"\w{0,4}\b" if len(w) > 5 else r"\b" + re.escape(w) + r"s?\b"


def _bullets(block: str) -> list[str]:
    items = []
    for line in block.splitlines():
        m = re.match(r'^- "(.+?)"', line)
        if m:
            items.append(re.sub(r"\.\.\.$|\u2026$", "", m.group(1)).strip())
    return items


def _phrase_regex(p: str) -> str:
    p = re.sub(r"\[[^\]]*\]", "", p).strip(" ,.")
    p = re.sub(r"\s+", " ", p)
    return r"\b" + r"\s+".join(re.escape(w) for w in p.split(" ")) + r"\b"


def build() -> dict:
    txt = MD.read_text(encoding="utf-8")
    tier1, tier2 = [], []
    for cells in _rows(_section(txt, "## Tier 1", "## Tier 2")):
        for t in _terms(cells[0]):
            tier1.append({"term": t, "pattern": _stem_regex(t), "replace": cells[1], "exception": cells[2]})
    for cells in _rows(_section(txt, "## Tier 2", "## Filler Phrases")):
        for t in _terms(cells[0]):
            tier2.append({"term": t, "pattern": _stem_regex(t), "replace": cells[1], "keep_when": cells[2]})
    filler = _bullets(_section(txt, "## Filler Phrases", "## Opening"))
    opening = _bullets(_section(txt, "## Opening", "## Closing"))
    closing = _bullets(_section(txt, "## Closing", "## Structural"))
    intimacy = _bullets(_section(txt, "### False Intimacy", "### Excessive"))
    inspirational = _bullets(_section(txt, "### Corporate Inspirational", "---"))

    def _p(items):
        return [{"phrase": i, "pattern": _phrase_regex(i)} for i in items if len(i) > 4]

    return {
        "schema_version": 1,
        "source": "references/ai-patterns.md",
        "tier1": tier1,
        "tier2": tier2,
        "filler": _p(filler),
        "opening_cliches": _p(opening),
        "closing_cliches": _p(closing),
        "false_intimacy": _p(intimacy),
        "corporate_inspirational": _p(inspirational),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if data/ai-patterns.json is out of date")
    args = ap.parse_args()
    data = build()
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("data/ai-patterns.json is out of date; run scripts/maintainer/build_ai_patterns.py", file=sys.stderr)
            return 1
        print("ai-patterns.json is in sync")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT} ({len(data['tier1'])} tier1, {len(data['tier2'])} tier2)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
