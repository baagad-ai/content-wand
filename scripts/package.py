#!/usr/bin/env python3
"""Build release archives.

    python3 scripts/package.py [--out dist]

Produces, reproducibly (sorted entries, fixed timestamps):

  content-wand-skill-<version>.zip    top-level folder content-wand/ (upload to claude.ai,
                                      marketplaces, or unzip into any skills directory)
  content-wand-plugin-<version>.zip   Claude Code / Cursor plugin layout
  SHA256SUMS                          checksums for both archives
  manifest.json                       every file with size and SHA-256

Only files needed at run time are shipped. Tests, evals, docs and dev tooling stay in the repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "content-wand"
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", "node_modules", "content-output"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".log", ".secret"}
EXCLUDE_NAMES = {".DS_Store"}
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
EXECUTABLE = {"cw.py", "hook_main.py", "run-hook.sh"}


def version() -> str:
    text = (SKILL / "scripts" / "cwlib" / "__init__.py").read_text(encoding="utf-8")
    return re.search(r'__version__\s*=\s*"([^"]+)"', text).group(1)


def files_under(root: Path) -> list[Path]:
    out = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if set(rel.parts) & EXCLUDE_DIRS or p.suffix in EXCLUDE_SUFFIX or p.name in EXCLUDE_NAMES:
            continue
        out.append(p)
    return out


def add(zf: zipfile.ZipFile, src: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    mode = 0o755 if src.name in EXECUTABLE else 0o644
    info.external_attr = (mode | 0o100000) << 16
    zf.writestr(info, src.read_bytes())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(out: Path) -> list[Path]:
    v = version()
    out.mkdir(parents=True, exist_ok=True)
    skill_zip = out / f"content-wand-skill-{v}.zip"
    plugin_zip = out / f"content-wand-plugin-{v}.zip"
    manifest: dict[str, dict[str, object]] = {}

    with zipfile.ZipFile(skill_zip, "w") as zf:
        for p in files_under(SKILL):
            arc = f"content-wand/{p.relative_to(SKILL).as_posix()}"
            add(zf, p, arc)
            manifest[arc] = {"bytes": p.stat().st_size, "sha256": sha256(p)}

    plugin_extra = [
        (REPO / ".claude-plugin" / "plugin.json", ".claude-plugin/plugin.json"),
        (REPO / ".claude-plugin" / "marketplace.json", ".claude-plugin/marketplace.json"),
        (REPO / ".cursor-plugin" / "plugin.json", ".cursor-plugin/plugin.json"),
        (REPO / "hooks" / "hooks.json", "hooks/hooks.json"),
        (REPO / "LICENSE", "LICENSE"),
        (REPO / "README.md", "README.md"),
    ]
    with zipfile.ZipFile(plugin_zip, "w") as zf:
        for src, arc in plugin_extra:
            add(zf, src, arc)
        for p in files_under(SKILL):
            add(zf, p, f"skills/content-wand/{p.relative_to(SKILL).as_posix()}")

    (out / "manifest.json").write_text(json.dumps({"version": v, "files": manifest}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    sums = "".join(f"{sha256(p)}  {p.name}\n" for p in (skill_zip, plugin_zip))
    (out / "SHA256SUMS").write_text(sums, encoding="utf-8")
    return [skill_zip, plugin_zip, out / "SHA256SUMS", out / "manifest.json"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(REPO / "dist"))
    args = ap.parse_args()
    for p in build(Path(args.out)):
        print(f"{p}  ({p.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
