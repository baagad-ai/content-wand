#!/usr/bin/env python3
"""Release gate: tests, evals, packaging and archive content checks.

    python3 scripts/check_release.py

Exits non-zero on any failure, so CI and the publish workflow can rely on it.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import package  # noqa: E402

failures: list[str] = []


def step(name: str, ok: bool, detail: str = "") -> None:
    print(("PASS  " if ok else "FAIL  ") + name + (f"  {detail}" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def run(*cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)


def main() -> int:
    tests = run(sys.executable, "-m", "unittest", "discover", "-s", "tests")
    step("unit and integration tests", tests.returncode == 0, tests.stderr[-800:])
    evals = run(sys.executable, "evals/run_evals.py")
    step("evals", evals.returncode == 0, evals.stdout[-800:])

    with tempfile.TemporaryDirectory() as tmp:
        first, second = Path(tmp) / "a", Path(tmp) / "b"
        built = package.build(first)
        package.build(second)
        skill_zip, plugin_zip = built[0], built[1]
        same = all(
            hashlib.sha256((first / n).read_bytes()).digest() == hashlib.sha256((second / n).read_bytes()).digest()
            for n in (skill_zip.name, plugin_zip.name)
        )
        step("archives are reproducible", same)

        with zipfile.ZipFile(skill_zip) as zf:
            names = zf.namelist()
        step("skill zip has a single top-level folder", {n.split("/")[0] for n in names} == {"content-wand"})
        step("skill zip contains SKILL.md at the folder root", "content-wand/SKILL.md" in names)
        step("skill zip has no caches or secrets", not any(("__pycache__" in n or n.endswith((".pyc", ".secret"))) for n in names))
        with zipfile.ZipFile(plugin_zip) as zf:
            pnames = set(zf.namelist())
        step("plugin zip has manifests and hooks", {".claude-plugin/plugin.json", "hooks/hooks.json", "skills/content-wand/SKILL.md"} <= pnames)

    print()
    print("release gate FAILED" if failures else "release gate passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
