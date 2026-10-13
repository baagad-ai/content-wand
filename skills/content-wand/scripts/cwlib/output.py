"""Safe creation of versioned output folders with a review manifest.

Every run writes to content-output/YYYY-MM-DD-<slug>[-vN]/ and never
overwrites earlier runs. A manifest.json records the source fingerprint,
validation results and the human review status of each file, which is what the
publish guard and the Stop hook rely on.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import unicodedata
from pathlib import Path
from typing import Any

from . import specs
from .jsonio import read_json, write_json_atomic, write_text_atomic

MAX_VERSION = 9
STOPWORDS = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are", "was", "were", "this", "that", "it", "my", "your", "how", "why", "what"}
MANIFEST = "manifest.json"
OUTPUT_ROOT_NAME = "content-output"
PLATFORM_IDS = {"twitter", "linkedin", "newsletter", "instagram", "youtube-shorts", "tiktok", "threads", "bluesky", "podcast"}
EXTRA_FILENAMES = {"transformed", "source-brief", "calendar", "hook-variants", "article", "show-notes", "pull-quotes", "faq", "announcement", "email-sequence"}


def make_slug(text: str, max_words: int = 5) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii").lower()
    words = [w for w in re.findall(r"[a-z0-9]+", text) if w not in STOPWORDS]
    slug = "-".join(words[:max_words])
    if not slug or slug in {".", ".."} or "/" in slug or "\\" in slug:
        return "untitled"
    return slug[:48]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def output_root(cwd: Path) -> Path:
    return Path(cwd).resolve() / OUTPUT_ROOT_NAME


def create_run_dir(cwd: Path, title: str, today: dt.date | None = None) -> dict[str, Any]:
    root = output_root(cwd)
    if root.is_symlink():
        return {"ok": False, "error": "content-output is a symlink; refusing to write through it"}
    root.mkdir(parents=True, exist_ok=True)
    day = (today or dt.date.today()).isoformat()
    slug = make_slug(title)
    base = f"{day}-{slug}"
    for n in range(1, MAX_VERSION + 1):
        name = base if n == 1 else f"{base}-v{n}"
        target = root / name
        try:
            target.mkdir()
        except FileExistsError:
            continue
        return {"ok": True, "dir": str(target), "name": name, "version": n, "previous_preserved": n > 1}
    return {"ok": False, "error": f"Maximum output versions reached for '{slug}'. Clear old outputs or change the title."}


def _inside_root(path: Path, cwd: Path) -> bool:
    try:
        path.resolve().relative_to(output_root(cwd).resolve())
        return True
    except ValueError:
        return False


def save_file(cwd: Path, run_dir: Path, name: str, text: str, validation: dict[str, Any] | None = None, claims: dict[str, Any] | None = None) -> dict[str, Any]:
    run_dir = Path(run_dir)
    if not _inside_root(run_dir, cwd):
        return {"ok": False, "error": "run directory is outside content-output"}
    stem = specs.canonical_platform(name)
    if stem not in PLATFORM_IDS and stem not in EXTRA_FILENAMES:
        return {"ok": False, "error": f"unsupported output name '{name}'"}
    target = run_dir / f"{stem}.md"
    if target.exists():
        return {"ok": False, "error": f"{target.name} already exists in this run; create a new version instead"}
    if validation and validation.get("compliance") == "fail":
        return {"ok": False, "error": "refusing to save an output that failed compliance", "failures": [f for f in validation.get("findings", []) if f.get("level") == "fail"]}
    write_text_atomic(target, text.rstrip("\n") + "\n")
    manifest = read_json(run_dir / MANIFEST, default=None) or {"manifest_version": 1, "created_at": dt.datetime.now(dt.timezone.utc).isoformat(), "files": {}}
    manifest["files"][target.name] = {
        "platform": stem,
        "sha256": sha256_text(text.strip()),
        "validation": None if not validation else {"compliance": validation.get("compliance"), "warn_count": validation.get("warn_count", 0)},
        "claims": None if not claims else {"ok": claims.get("ok"), "unsupported_count": claims.get("unsupported_count", 0), "unsupported": [{"type": u.get("type"), "text": u.get("text")} for u in claims.get("unsupported", [])[:10]]},
        "status": "draft",
    }
    write_json_atomic(run_dir / MANIFEST, manifest, private=False)
    return {"ok": True, "file": str(target)}


def update_manifest(run_dir: Path, patch: dict[str, Any]) -> dict[str, Any]:
    manifest = read_json(Path(run_dir) / MANIFEST, default=None)
    if manifest is None:
        return {"ok": False, "error": "no manifest in this directory"}
    for key, value in patch.items():
        if key in ("source", "style", "specs_data_version", "mode", "title", "disclosure", "notes"):
            manifest[key] = value
    write_json_atomic(Path(run_dir) / MANIFEST, manifest, private=False)
    return {"ok": True}


def update_manifest_create(run_dir: Path, patch: dict[str, Any]) -> dict[str, Any]:
    run_dir = Path(run_dir)
    manifest = read_json(run_dir / MANIFEST, default=None) or {"manifest_version": 1, "created_at": dt.datetime.now(dt.timezone.utc).isoformat(), "files": {}}
    for key, value in patch.items():
        if key in ("source", "style", "specs_data_version", "mode", "title", "disclosure", "notes"):
            manifest[key] = value
    write_json_atomic(run_dir / MANIFEST, manifest, private=False)
    return {"ok": True}


def review(run_dir: Path, names: list[str], status: str, note: str = "", accept_unsupported_claims: bool = False) -> dict[str, Any]:
    if status not in ("approved", "rejected", "draft"):
        return {"ok": False, "error": "status must be approved, rejected or draft"}
    run_dir = Path(run_dir)
    manifest = read_json(run_dir / MANIFEST, default=None)
    if manifest is None:
        return {"ok": False, "error": "no manifest in this directory"}
    files = manifest.get("files", {})
    targets = list(files) if names == ["all"] else [f"{specs.canonical_platform(n)}.md" for n in names]
    changed = []
    problems = []
    for t in targets:
        entry = files.get(t)
        if entry is None:
            problems.append(f"{t}: not in manifest")
            continue
        path = run_dir / t
        current = path.read_text(encoding="utf-8").strip() if path.exists() else ""
        if status == "approved":
            if sha256_text(current) != entry["sha256"]:
                problems.append(f"{t}: file changed since it was validated; re-run validation before approving")
                continue
            if entry.get("validation") is None or entry["validation"].get("compliance") != "pass":
                problems.append(f"{t}: has not passed validation")
                continue
            claims_entry = entry.get("claims")
            if claims_entry and not claims_entry.get("ok") and not accept_unsupported_claims:
                problems.append(f"{t}: {claims_entry.get('unsupported_count', 0)} claim(s) are not supported by the source; fix them or confirm with --accept-unsupported-claims")
                continue
            if claims_entry and not claims_entry.get("ok"):
                entry["claims_accepted_by_reviewer"] = True
        entry["status"] = status
        entry["reviewed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        if note:
            entry["review_note"] = note[:300]
        changed.append(t)
    write_json_atomic(run_dir / MANIFEST, manifest, private=False)
    return {"ok": not problems, "changed": changed, "problems": problems}


def run_status(run_dir: Path) -> dict[str, Any]:
    manifest = read_json(Path(run_dir) / MANIFEST, default=None)
    if manifest is None:
        return {"ok": False, "error": "no manifest"}
    files = manifest.get("files", {})
    return {
        "ok": True,
        "files": {k: {"status": v.get("status"), "validation": (v.get("validation") or {}).get("compliance"), "claims_ok": (v.get("claims") or {}).get("ok")} for k, v in files.items()},
        "all_validated": all(v.get("validation") for v in files.values()) if files else False,
        "all_approved": all(v.get("status") == "approved" for v in files.values()) if files else False,
    }


def _normalise_for_match(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip().casefold()


def approved_texts(cwd: Path) -> list[str]:
    """Texts of every approved output under content-output/, for the publish guard."""
    root = output_root(cwd)
    texts: list[str] = []
    if not root.is_dir():
        return texts
    for manifest_path in root.glob(f"*/{MANIFEST}"):
        manifest = read_json(manifest_path, default={})
        for name, entry in manifest.get("files", {}).items():
            if entry.get("status") != "approved":
                continue
            p = manifest_path.parent / name
            if p.is_file():
                body = p.read_text(encoding="utf-8")
                texts.append(_normalise_for_match(body))
                for unit in re.split(r"(?m)^\s*---\s*$", body):
                    if unit.strip():
                        texts.append(_normalise_for_match(unit))
    return texts


def match_approved(candidate: str, approved: list[str]) -> str | None:
    """Return the approved text that `candidate` is, contains, or is contained in."""
    c = _normalise_for_match(candidate)
    if not c:
        return None
    for a in approved:
        if c in a or (len(a) > 20 and a in c):
            return a
    return None


def text_matches_approved(candidate: str, approved: list[str]) -> bool:
    return match_approved(candidate, approved) is not None


def unvalidated_runs(cwd: Path, since_epoch: float) -> list[str]:
    root = output_root(cwd)
    problems: list[str] = []
    if not root.is_dir():
        return problems
    for manifest_path in root.glob(f"*/{MANIFEST}"):
        try:
            if os.path.getmtime(manifest_path) < since_epoch:
                continue
        except OSError:
            continue
        manifest = read_json(manifest_path, default={})
        for name, entry in manifest.get("files", {}).items():
            if not entry.get("validation"):
                problems.append(f"{manifest_path.parent.name}/{name}")
    return problems


def packet(run_dir: Path) -> dict[str, Any]:
    """Build the human review card for a run: one section per output with its
    validation findings and unsupported claims, so a reviewer can approve or
    reject from a single page. Findings are recomputed from the files on disk."""
    from . import validate

    run_dir = Path(run_dir)
    manifest = read_json(run_dir / MANIFEST, default=None)
    if manifest is None:
        return {"ok": False, "error": "no manifest in this directory"}
    lines = [f"# Review packet: {manifest.get('title') or run_dir.name}", ""]
    if manifest.get("source"):
        lines.append(f"Source: {manifest['source']}")
    if manifest.get("style"):
        lines.append(f"Writing Style: {manifest['style']} (voice match is advisory; you are the judge)")
    if manifest.get("specs_data_version"):
        lines.append(f"Platform rules version: {manifest['specs_data_version']}")
    lines.append("")
    summary: dict[str, Any] = {}
    for name, entry in sorted(manifest.get("files", {}).items()):
        path = run_dir / name
        pid = entry.get("platform", Path(name).stem)
        status = entry.get("status", "draft")
        lines.append(f"## {name} ({status})")
        if not path.is_file():
            lines += ["File is missing.", ""]
            continue
        body = path.read_text(encoding="utf-8")
        edited = sha256_text(body.strip()) != entry.get("sha256")
        if edited:
            lines.append("Edited since it was validated. Re-validate before approving.")
        if pid in validate.DEFAULTS:
            res = validate.validate_text(pid, body)
            lines.append(f"Compliance: {res['compliance']} ({res.get('fail_count', 0)} fail, {res.get('warn_count', 0)} warn)")
            for f in res["findings"][:8]:
                lines.append(f"- [{f['level']}] {f['message']}")
            summary[name] = res["compliance"]
        claims = entry.get("claims")
        if claims is None:
            lines.append("Claims check: not run (no source file supplied).")
        elif claims.get("ok"):
            lines.append("Claims check: every quote, number and link traces to the source.")
        else:
            lines.append(f"Claims check: {claims.get('unsupported_count', 0)} unsupported item(s):")
            for u in claims.get("unsupported", []):
                lines.append(f"- {u.get('type')}: {u.get('text')}")
        lines.append("")
    text = "\n".join(lines).rstrip() + "\n"
    write_text_atomic(run_dir / "review-packet.md", text)
    return {"ok": True, "file": str(run_dir / "review-packet.md"), "packet": text, "compliance": summary}
