#!/usr/bin/env python3
"""Deterministic evals for content-wand.

    python3 evals/run_evals.py [--verbose]

Runs without a model. Covers the properties the skill promises in code:
platform compliance, claims fidelity, injection detection (with benign
negatives), humanizer fidelity, and structural checks on the trigger set.
Model-in-the-loop trigger and behaviour evals are described in evals/README.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent / "skills" / "content-wand"
sys.path.insert(0, str(SKILL / "scripts"))

os.environ["CONTENT_WAND_HOME"] = tempfile.mkdtemp(prefix="cw-evals-")

from cwlib import claims, scan, validate  # noqa: E402


def load(name: str):
    return json.loads((HERE / "data" / name).read_text(encoding="utf-8"))


def run_compliance() -> list[str]:
    errors = []
    for case in load("compliance.json"):
        text = case["text"]
        if "text_repeat" in case:
            rep = case["text_repeat"]
            text = rep.get("prefix", "") + rep["unit"] * rep["times"]
        res = validate.validate_text(case["platform"], text)
        if res["compliance"] != case["expect"]:
            errors.append(f"compliance/{case['name']}: expected {case['expect']}, got {res['compliance']} {[f['id'] for f in res['findings']]}")
            continue
        for want in case.get("ids", []):
            if not any(f["id"] == want for f in res["findings"]):
                errors.append(f"compliance/{case['name']}: expected finding '{want}', got {[f['id'] for f in res['findings']]}")
    return errors


def run_claims() -> list[str]:
    errors = []
    for case in load("claims.json"):
        res = claims.check_claims(case["source"], case["output"], case.get("allow_url", []))
        if res["ok"] != case["expect_ok"]:
            errors.append(f"claims/{case['name']}: expected ok={case['expect_ok']}, got {res['ok']} {res['unsupported']}")
            continue
        kinds = {u["type"] for u in res["unsupported"]}
        for want in case.get("types", []):
            if want not in kinds:
                errors.append(f"claims/{case['name']}: expected unsupported type '{want}', got {sorted(kinds)}")
    return errors


def run_injection() -> list[str]:
    errors = []
    data = load("injection.json")
    caught = 0
    for text in data["malicious"]:
        if scan.scan_text(text)["severity"] == "high":
            caught += 1
        else:
            errors.append(f"injection/missed: {text[:70]!r}")
    for text in data["benign"]:
        if scan.scan_text(text)["severity"] == "high":
            errors.append(f"injection/false-positive: {text[:70]!r}")
    return errors


def run_humanizer() -> list[str]:
    errors = []
    for case in load("humanizer.json"):
        before = validate.lint_ai_patterns(case["before"])["total"]
        after = validate.lint_ai_patterns(case["after"])["total"]
        if not before > after:
            errors.append(f"humanizer/{case['name']}: pattern hits did not drop ({before} -> {after})")
        if after > case["max_after_hits"]:
            errors.append(f"humanizer/{case['name']}: {after} pattern hits remain")
        for fact in case["must_keep"]:
            if fact not in case["after"]:
                errors.append(f"humanizer/{case['name']}: fact '{fact}' was lost")
        grew = len(case["after"].split()) > len(case["before"].split())
        if grew:
            errors.append(f"humanizer/{case['name']}: the edit made the text longer")
    return errors


def run_triggers() -> list[str]:
    errors = []
    data = load("triggers.json")
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    description = re.search(r"^description: (.*)$", text, re.M).group(1).lower()
    for phrase in ("turn this into", "repurpose", "atomize", "reformat for", "hook variants", "content calendar", "thread", "newsletter", "carousel"):
        if phrase not in description:
            errors.append(f"triggers: description does not mention '{phrase}'")
    if len(data["should_trigger"]) < 8 or len(data["should_not_trigger"]) < 8:
        errors.append("triggers: keep at least 8 positive and 8 near-miss negative prompts")
    if set(data["should_trigger"]) & set(data["should_not_trigger"]):
        errors.append("triggers: a prompt appears in both lists")
    for neg in ("not for original", "posting to social accounts without review"):
        if neg not in description:
            errors.append(f"triggers: description is missing the boundary text '{neg}'")
    return errors


SUITES = {
    "compliance": run_compliance,
    "claims": run_claims,
    "injection": run_injection,
    "humanizer": run_humanizer,
    "triggers": run_triggers,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    total_errors = 0
    for name, fn in SUITES.items():
        errors = fn()
        total_errors += len(errors)
        print(f"{'PASS' if not errors else 'FAIL'}  {name}")
        for e in errors:
            print("   -", e)
    print()
    print("evals passed" if not total_errors else f"{total_errors} eval failure(s)")
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main())
