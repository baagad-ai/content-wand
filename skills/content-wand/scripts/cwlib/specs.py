"""Per-platform specification data with provenance, TTLs, safe updates.

Data model (see data/platform-specs.json):

    platforms.<id>.facts.<key> = {
        value, kind (hard|policy|algorithm), verified_at, source, source_type,
        note?
    }

`hard` facts are binary platform constraints (character limits). `policy`
facts are official rules that can change. `algorithm` facts are ranking
signals (official weights where a platform publishes them, otherwise
directional observations) and expire fastest. `heuristic` facts are craft
guidance with no official source (for example "keep subject lines short") and
are never presented as platform rules.

Local overrides live in the user's state directory and are only ever written
by `apply_proposal`, which validates every field and keeps rollback history.
Specification text is DATA: values are typed, bounded and scanned, and never
treated as instructions.
"""

from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from . import paths
from .jsonio import read_json, write_json_atomic
from .scan import scan_text

KINDS = ("hard", "policy", "algorithm", "heuristic")
KEY_RE = re.compile(r"^[a-z][a-z0-9_]{2,48}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALIASES = {
    "x": "twitter",
    "twitter-x": "twitter",
    "twitter/x": "twitter",
    "tweet": "twitter",
    "email": "newsletter",
    "email-newsletter": "newsletter",
    "ig": "instagram",
    "instagram-carousel": "instagram",
    "carousel": "instagram",
    "shorts": "youtube-shorts",
    "youtube": "youtube-shorts",
    "yt-shorts": "youtube-shorts",
    "tik-tok": "tiktok",
    "li": "linkedin",
    "bsky": "bluesky",
}


def canonical_platform(name: str) -> str:
    n = (name or "").strip().lower().replace("_", "-")
    return ALIASES.get(n, n)


def _today(today: dt.date | None) -> dt.date:
    return today or dt.date.today()


def _parse_date(s: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def base_path() -> Path:
    return paths.DATA_DIR / "platform-specs.json"


def load_base() -> dict[str, Any]:
    data = read_json(base_path())
    if not isinstance(data, dict) or "platforms" not in data:
        raise RuntimeError("platform-specs.json missing or malformed")
    return data


def load_overrides() -> dict[str, Any]:
    try:
        data = read_json(paths.overrides_path(), default={})
    except (ValueError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def merged() -> dict[str, Any]:
    """Base data with approved local overrides applied (newest verification wins)."""
    data = copy.deepcopy(load_base())
    overrides = load_overrides().get("platforms", {})
    for pid, pdata in overrides.items():
        target = data["platforms"].get(pid)
        if target is None:
            continue
        for key, fact in pdata.get("facts", {}).items():
            existing = target["facts"].get(key)
            if existing is None or (fact.get("verified_at", "") >= existing.get("verified_at", "")):
                fact = dict(fact)
                fact["origin"] = "local-override"
                target["facts"][key] = fact
    return data


def platform_ids(data: dict[str, Any] | None = None) -> list[str]:
    return list((data or merged())["platforms"].keys())


def fact(platform: str, key: str, default: Any = None, data: dict[str, Any] | None = None) -> Any:
    d = data or merged()
    p = d["platforms"].get(canonical_platform(platform), {})
    f = p.get("facts", {}).get(key)
    return default if f is None else f.get("value", default)


def ttl_days(data: dict[str, Any], kind: str) -> int:
    return int(data.get("ttl_days", {}).get(kind, {"hard": 90, "policy": 60, "algorithm": 30, "heuristic": 180}[kind]))


def status(platforms: list[str] | None = None, today: dt.date | None = None) -> dict[str, Any]:
    data = merged()
    now = _today(today)
    wanted = [canonical_platform(p) for p in platforms] if platforms else platform_ids(data)
    report: dict[str, Any] = {
        "data_version": data.get("data_version"),
        "today": now.isoformat(),
        "platforms": {},
        "stale_platforms": [],
        "unknown_platforms": [],
    }
    for pid in wanted:
        p = data["platforms"].get(pid)
        if p is None:
            report["unknown_platforms"].append(pid)
            continue
        stale: list[dict[str, Any]] = []
        oldest: dt.date | None = None
        for key, f in p.get("facts", {}).items():
            verified = _parse_date(f.get("verified_at", ""))
            kind = f.get("kind", "hard")
            limit = ttl_days(data, kind)
            age = (now - verified).days if verified else None
            if verified and (oldest is None or verified < oldest):
                oldest = verified
            if verified is None or (age is not None and age > limit):
                stale.append({"key": key, "kind": kind, "age_days": age, "ttl_days": limit})
        entry = {
            "label": p.get("label", pid),
            "oldest_verified_at": oldest.isoformat() if oldest else None,
            "stale_fact_count": len(stale),
            "stale_facts": stale,
            "stale": bool(stale),
        }
        report["platforms"][pid] = entry
        if stale:
            report["stale_platforms"].append(pid)
    return report


def primary_domains(platform: str, data: dict[str, Any] | None = None) -> list[str]:
    d = data or merged()
    return list(d["platforms"].get(canonical_platform(platform), {}).get("primary_domains", []))


def _host_matches(host: str, domains: list[str]) -> bool:
    host = host.lower().rstrip(".")
    return any(host == dom or host.endswith("." + dom) for dom in domains)


def is_primary_url(url: str, platform: str, data: dict[str, Any] | None = None) -> bool:
    """True if the URL is an official source for the platform.

    Official sources are whole domains the platform controls (help.example.com)
    or URL prefixes inside shared hosts (github.com/<org>/<repo>,
    support.google.com/youtube/). Bare user-content hosts such as x.com are
    deliberately not listed, because anyone can publish there.
    """
    d = data or merged()
    p = d["platforms"].get(canonical_platform(platform), {})
    parts = urlsplit(url) if isinstance(url, str) else None
    if not parts or parts.scheme != "https" or not parts.hostname:
        return False
    if _host_matches(parts.hostname, list(p.get("primary_domains", []))):
        return True
    lowered = url.lower()
    return any(lowered.startswith(pref.lower()) for pref in p.get("primary_url_prefixes", []))


def check_value(value: Any, existing: Any = None) -> str | None:
    """Return a reason the value is unacceptable as a spec fact, or None if it is fine."""
    if isinstance(value, bool):
        pass
    elif isinstance(value, (int, float)):
        if not (-1_000_000 <= value <= 1_000_000):
            return "numeric value out of sane range"
    elif isinstance(value, str):
        if len(value) > 240:
            return "string value too long"
        if scan_text(value)["severity"] != "none":
            return "value rejected by safety scan"
    elif isinstance(value, list):
        if len(value) > 20 or not all(isinstance(v, (str, int, float)) and not isinstance(v, bool) for v in value):
            return "list values must be at most 20 simple items"
        if any(isinstance(v, str) and (len(v) > 120 or scan_text(v)["severity"] != "none") for v in value):
            return "list item rejected"
    else:
        return "unsupported value type"
    if existing is not None:
        numeric = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)  # noqa: E731
        if type(existing) is not type(value) and not (numeric(existing) and numeric(value)):
            return f"value type changed from {type(existing).__name__} to {type(value).__name__}"
    return None


def validate_proposal(proposal: Any, today: dt.date | None = None) -> dict[str, Any]:
    """Validate an agent-authored spec update. Never trusts free text."""
    now = _today(today)
    errors: list[str] = []
    warnings: list[str] = []
    accepted: list[dict[str, Any]] = []
    data = merged()

    if not isinstance(proposal, dict):
        return {"ok": False, "errors": ["proposal must be a JSON object"], "warnings": [], "changes": []}
    allowed_top = {"proposal_version", "created_at", "platform", "changes", "summary"}
    extra = set(proposal) - allowed_top
    if extra:
        errors.append(f"unknown top-level keys: {sorted(extra)}")
    pid = canonical_platform(str(proposal.get("platform", "")))
    platform = data["platforms"].get(pid)
    if platform is None:
        errors.append(f"unknown platform '{proposal.get('platform')}'")
        return {"ok": False, "errors": errors, "warnings": warnings, "changes": []}
    changes = proposal.get("changes")
    if not isinstance(changes, list) or not changes:
        errors.append("changes must be a non-empty list")
        return {"ok": False, "errors": errors, "warnings": warnings, "changes": []}
    if len(changes) > 40:
        errors.append("too many changes in one proposal (max 40)")
        return {"ok": False, "errors": errors, "warnings": warnings, "changes": []}

    domains = primary_domains(pid, data)
    allowed_change_keys = {"key", "value", "kind", "source_url", "source_quote", "retrieved_at", "note"}
    for i, ch in enumerate(changes):
        tag = f"change[{i}]"
        if not isinstance(ch, dict):
            errors.append(f"{tag}: must be an object")
            continue
        extra_keys = set(ch) - allowed_change_keys
        if extra_keys:
            errors.append(f"{tag}: unknown keys {sorted(extra_keys)}")
            continue
        key = ch.get("key")
        if not isinstance(key, str) or not KEY_RE.match(key):
            errors.append(f"{tag}: invalid key")
            continue
        existing = platform["facts"].get(key)
        kind = ch.get("kind", existing.get("kind") if existing else None)
        if kind not in KINDS:
            errors.append(f"{tag}: kind must be one of {KINDS}")
            continue
        if existing and existing.get("kind") != kind:
            errors.append(f"{tag}: kind cannot change for existing fact '{key}'")
            continue

        value = ch.get("value")
        problem = check_value(value, existing.get("value") if existing else None)
        if problem:
            errors.append(f"{tag}: {problem}")
            continue

        url = ch.get("source_url", "")
        parts = urlsplit(url) if isinstance(url, str) else None
        if not parts or parts.scheme != "https" or not parts.hostname:
            errors.append(f"{tag}: source_url must be an https URL")
            continue
        primary = is_primary_url(url, pid, data)
        if kind in ("hard", "policy") and not primary:
            errors.append(f"{tag}: '{kind}' facts require an official source for {pid} ({', '.join(domains + list(platform.get('primary_url_prefixes', []))) or 'none configured'}); got {parts.hostname}")
            continue
        if not primary:
            warnings.append(f"{tag}: secondary source ({parts.hostname}) - will be marked secondary")

        quote = ch.get("source_quote")
        if not isinstance(quote, str) or not (8 <= len(quote) <= 400):
            errors.append(f"{tag}: source_quote (8-400 chars) is required")
            continue
        if scan_text(quote)["severity"] != "none":
            errors.append(f"{tag}: source_quote rejected by safety scan")
            continue
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            numerals = {n.replace(",", "").rstrip(".") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", quote)}
            magnitude = abs(float(value))
            shown = str(int(magnitude)) if magnitude.is_integer() else repr(magnitude)
            if shown not in numerals and f"{magnitude:g}" not in numerals:
                errors.append(f"{tag}: numeric value {value} does not appear in the supplied source_quote")
                continue

        retrieved = _parse_date(ch.get("retrieved_at", ""))
        if retrieved is None or retrieved > now or (now - retrieved).days > 3:
            errors.append(f"{tag}: retrieved_at must be a date within the last 3 days")
            continue

        note = ch.get("note", "")
        if note and (not isinstance(note, str) or len(note) > 300 or scan_text(note)["severity"] != "none"):
            errors.append(f"{tag}: note rejected")
            continue

        if existing is not None and isinstance(existing.get("value"), (int, float)) and not isinstance(existing.get("value"), bool):
            old = float(existing["value"])
            new = float(value)
            if old > 0 and (new / old >= 10 or new / old <= 0.1):
                warnings.append(f"{tag}: '{key}' changes by more than 10x ({old:g} -> {new:g}); double-check the source")

        accepted.append({
            "key": key,
            "kind": kind,
            "old": None if existing is None else existing.get("value"),
            "new": value,
            "is_new_fact": existing is None,
            "source_url": url,
            "source_quote": quote,
            "source_type": "primary" if primary else "secondary",
            "retrieved_at": retrieved.isoformat(),
            "note": note or "",
        })

    diff_fp = hashlib.sha256(json.dumps(accepted, sort_keys=True).encode()).hexdigest()[:12]
    return {
        "ok": not errors,
        "platform": pid,
        "errors": errors,
        "warnings": warnings,
        "changes": accepted,
        "unchanged_count": sum(1 for c in accepted if c["old"] == c["new"]),
        "fingerprint": diff_fp,
    }


def snapshot_overrides(overrides: dict[str, Any]) -> str:
    history_dir = paths.state_dir(create=True) / "specs-history"
    history_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    write_json_atomic(history_dir / f"{stamp}.json", overrides if overrides else {"platforms": {}})
    return stamp


def apply_facts(facts_by_platform: dict[str, dict[str, dict[str, Any]]], origin: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge already-validated facts into the local override file, with rollback history."""
    overrides = load_overrides()
    stamp = snapshot_overrides(overrides)
    overrides.setdefault("schema_version", 1)
    for pid, facts in facts_by_platform.items():
        plat = overrides.setdefault("platforms", {}).setdefault(pid, {"facts": {}})
        for key, entry in facts.items():
            plat["facts"][key] = {**entry, "applied_via": origin}
    if meta:
        overrides.setdefault("meta", {}).update(meta)
    write_json_atomic(paths.overrides_path(), overrides)
    return {"ok": True, "history_snapshot": stamp, "platforms": sorted(facts_by_platform)}


def apply_proposal(proposal: dict[str, Any], today: dt.date | None = None) -> dict[str, Any]:
    """Apply a validated proposal to the local override file (with history)."""
    result = validate_proposal(proposal, today=today)
    if not result["ok"]:
        return result
    now = _today(today)
    overrides = load_overrides()
    stamp = snapshot_overrides(overrides)

    overrides.setdefault("schema_version", 1)
    plat = overrides.setdefault("platforms", {}).setdefault(result["platform"], {"facts": {}})
    for ch in result["changes"]:
        entry = {
            "value": ch["new"],
            "kind": ch["kind"],
            "verified_at": now.isoformat(),
            "source": ch["source_url"],
            "source_type": ch["source_type"],
            "source_quote": ch["source_quote"],
        }
        if ch["note"]:
            entry["note"] = ch["note"]
        plat["facts"][ch["key"]] = entry
    write_json_atomic(paths.overrides_path(), overrides)
    result["applied"] = True
    result["history_snapshot"] = f"{stamp}.json"
    return result


def rollback() -> dict[str, Any]:
    history_dir = paths.state_dir() / "specs-history"
    snaps = sorted(history_dir.glob("*.json")) if history_dir.exists() else []
    if not snaps:
        return {"ok": False, "error": "no history to roll back to"}
    last = snaps[-1]
    snapshot = read_json(last, default={"platforms": {}})
    if snapshot.get("platforms"):
        write_json_atomic(paths.overrides_path(), snapshot)
    else:
        try:
            paths.overrides_path().unlink()
        except FileNotFoundError:
            pass
    last.unlink()
    return {"ok": True, "restored": last.name}


def show(platform: str) -> dict[str, Any]:
    data = merged()
    pid = canonical_platform(platform)
    p = data["platforms"].get(pid)
    if p is None:
        return {"ok": False, "error": f"unknown platform '{platform}'", "known": platform_ids(data)}
    return {"ok": True, "platform": pid, **p}
