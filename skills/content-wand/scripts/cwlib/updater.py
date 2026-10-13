"""Signed platform-spec feed: opt-in, verify-then-review, never auto-applied.

Platform rules change faster than skill releases. This module lets a
publisher ship corrected facts between releases without giving the feed any
authority over the agent.

Trust model
- Off by default. Network use needs the user's explicit opt-in
  (`pref set update_check on`) and is disabled outright by
  CONTENT_WAND_UPDATES=off. Nothing runs from a hook. Nothing is sent to the
  publisher: it is a plain HTTPS GET of two static files, with no identifiers.
- Only hosts in data/updater.json's allow-list are contacted; redirects to any
  other host are refused; size and time are capped.
- The feed must carry a valid Ed25519 signature from the publisher key shipped
  in data/updater-pubkey.b64. No key shipped means the updater is inert.
- The signed payload is DATA. It is parsed against a strict schema (typed,
  bounded, injection-scanned values; hard and policy facts must cite an
  official source), diffed against current facts, and stored as a pending
  proposal. The user reviews the diff; only then does `specs apply-remote`
  write a local override, with a rollback snapshot. A signature is re-checked
  at apply time, so a tampered pending file cannot be applied.
- Downgrades are refused: the feed's data_version must be newer than both the
  shipped data and the last applied feed.
"""

from __future__ import annotations

import base64
import datetime as dt
import hashlib
import json
import re
import urllib.error
import urllib.request
from typing import Any, Callable
from urllib.parse import urlsplit

from . import ed25519, paths, specs
from .jsonio import read_json, write_json_atomic
from .scan import scan_text
from .styles import load_config

Fetcher = Callable[[str], bytes]

VERSION_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}(\.\d+)?$")
SOURCE_TYPES = {"primary", "primary-code", "primary-mirror", "primary-quoted", "secondary", "none"}
FACT_KEYS = {"value", "kind", "verified_at", "source", "source_type", "note"}
MAX_FACTS = 400


def config() -> dict[str, Any]:
    return read_json(paths.DATA_DIR / "updater.json", default={}) or {}


def public_key() -> bytes | None:
    f = paths.DATA_DIR / "updater-pubkey.b64"
    try:
        raw = base64.b64decode(f.read_text(encoding="ascii").strip(), validate=True)
    except (OSError, ValueError):
        return None
    return raw if len(raw) == 32 else None


def user_opted_in() -> bool:
    import os

    if os.environ.get("CONTENT_WAND_UPDATES", "").lower() in ("off", "0", "false", "no"):
        return False
    return str(load_config().get("preferences", {}).get("update_check", "off")).lower() == "on"


def pending_path():
    return paths.cache_dir() / "pending-spec-update.json"


def _last_check_path():
    return paths.cache_dir() / "remote-check.json"


def verify_feed(payload: bytes, signature: bytes, key: bytes | None = None) -> bool:
    key = key or public_key()
    return bool(key) and ed25519.verify(key, payload, signature)


def _allowed(url: str, cfg: dict[str, Any]) -> bool:
    parts = urlsplit(url)
    return parts.scheme == "https" and bool(parts.hostname) and parts.hostname.lower() in [h.lower() for h in cfg.get("allowed_hosts", [])] and not parts.username


class _SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, cfg: dict[str, Any]):
        self.cfg = cfg

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        if not _allowed(newurl, self.cfg):
            raise urllib.error.URLError(f"redirect to non-allowed host refused: {urlsplit(newurl).hostname}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def http_fetch(url: str, cfg: dict[str, Any] | None = None) -> bytes:
    cfg = cfg or config()
    if not _allowed(url, cfg):
        raise urllib.error.URLError("host is not in the updater allow-list")
    opener = urllib.request.build_opener(_SameHostRedirect(cfg))
    req = urllib.request.Request(url, headers={"User-Agent": "content-wand-spec-check", "Accept": "application/json"})
    limit = int(cfg.get("max_bytes", 262144))
    with opener.open(req, timeout=float(cfg.get("timeout_seconds", 8))) as resp:
        body = resp.read(limit + 1)
    if len(body) > limit:
        raise urllib.error.URLError("feed exceeds the size limit")
    return body


def _date_ok(value: Any, today: dt.date) -> bool:
    try:
        d = dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return d <= today


def validate_bundle(bundle: Any, today: dt.date | None = None) -> dict[str, Any]:
    """Strictly validate a decoded feed. Returns accepted facts and any errors."""
    now = today or dt.date.today()
    errors: list[str] = []
    accepted: dict[str, dict[str, dict[str, Any]]] = {}
    if not isinstance(bundle, dict):
        return {"ok": False, "errors": ["feed must be a JSON object"], "facts": {}}
    extra = set(bundle) - {"feed_version", "data_version", "published_at", "platforms", "summary"}
    if extra:
        errors.append(f"unknown top-level keys: {sorted(extra)}")
    if bundle.get("feed_version") != 1:
        errors.append("unsupported feed_version")
    if not isinstance(bundle.get("data_version"), str) or not VERSION_RE.match(bundle["data_version"]):
        errors.append("data_version must look like YYYY.MM.DD")
    if not _date_ok(bundle.get("published_at"), now):
        errors.append("published_at must be a past or current date")
    summary = bundle.get("summary", "")
    if summary and (not isinstance(summary, str) or len(summary) > 400 or scan_text(summary)["severity"] != "none"):
        errors.append("summary rejected")
    platforms = bundle.get("platforms")
    if not isinstance(platforms, dict) or not platforms:
        errors.append("platforms must be a non-empty object")
        return {"ok": False, "errors": errors, "facts": {}}

    data = specs.merged()
    total = 0
    for pid, pdata in platforms.items():
        base = data["platforms"].get(pid)
        if base is None:
            errors.append(f"unknown platform '{pid}'")
            continue
        facts = pdata.get("facts") if isinstance(pdata, dict) else None
        if not isinstance(facts, dict) or set(pdata) - {"facts"}:
            errors.append(f"{pid}: malformed platform entry")
            continue
        for key, fact in facts.items():
            total += 1
            tag = f"{pid}.{key}"
            if total > MAX_FACTS:
                errors.append("too many facts in feed")
                break
            if not specs.KEY_RE.match(key) or not isinstance(fact, dict) or set(fact) - FACT_KEYS or not {"value", "kind", "verified_at", "source_type"} <= set(fact):
                errors.append(f"{tag}: malformed fact")
                continue
            kind = fact["kind"]
            existing = base["facts"].get(key)
            if kind not in specs.KINDS or (existing and existing.get("kind") != kind):
                errors.append(f"{tag}: invalid or changed kind")
                continue
            problem = specs.check_value(fact["value"], existing.get("value") if existing else None)
            if problem:
                errors.append(f"{tag}: {problem}")
                continue
            if fact["source_type"] not in SOURCE_TYPES:
                errors.append(f"{tag}: unknown source_type")
                continue
            source = fact.get("source", "")
            if kind in ("hard", "policy") and fact["source_type"].startswith("primary") and not specs.is_primary_url(source, pid, data):
                errors.append(f"{tag}: primary source claimed but URL is not an official source for {pid}")
                continue
            if source and not str(source).startswith("https://"):
                errors.append(f"{tag}: source must be https")
                continue
            note = fact.get("note", "")
            if note and (not isinstance(note, str) or len(note) > 400 or scan_text(note)["severity"] != "none"):
                errors.append(f"{tag}: note rejected")
                continue
            if not _date_ok(fact["verified_at"], now):
                errors.append(f"{tag}: verified_at must be a past or current date")
                continue
            accepted.setdefault(pid, {})[key] = {k: fact[k] for k in FACT_KEYS if k in fact}
    return {"ok": not errors, "errors": errors, "facts": accepted}


def diff_facts(accepted: dict[str, dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    data = specs.merged()
    changes: list[dict[str, Any]] = []
    for pid, facts in accepted.items():
        for key, fact in facts.items():
            existing = data["platforms"][pid]["facts"].get(key)
            if existing is not None and existing.get("value") == fact["value"] and existing.get("verified_at", "") >= fact["verified_at"]:
                continue
            if existing is not None and existing.get("verified_at", "") > fact["verified_at"]:
                continue
            changes.append({
                "platform": pid,
                "key": key,
                "kind": fact["kind"],
                "old": None if existing is None else existing.get("value"),
                "new": fact["value"],
                "is_new_fact": existing is None,
                "value_changed": existing is None or existing.get("value") != fact["value"],
                "source": fact.get("source", ""),
                "source_type": fact["source_type"],
                "verified_at": fact["verified_at"],
                "note": fact.get("note", ""),
            })
    return changes


def _current_floor() -> str:
    base = str(specs.load_base().get("data_version", ""))
    applied = str(specs.load_overrides().get("meta", {}).get("feed_data_version", ""))
    return max(base, applied)


def _write_last_check(result: dict[str, Any]) -> None:
    paths.cache_dir(create=True)
    write_json_atomic(_last_check_path(), {"checked_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "status": result.get("status")})


def _recently_checked(hours: float, now: dt.datetime | None = None) -> bool:
    last = read_json(_last_check_path(), default=None)
    if not last:
        return False
    try:
        then = dt.datetime.fromisoformat(last["checked_at"])
    except (KeyError, ValueError):
        return False
    return ((now or dt.datetime.now(dt.timezone.utc)) - then).total_seconds() < hours * 3600


def check_remote(force: bool = False, fetcher: Fetcher | None = None, today: dt.date | None = None) -> dict[str, Any]:
    cfg = config()
    key = public_key()
    if key is None or not cfg.get("feed_url"):
        return {"ok": True, "status": "unavailable", "reason": "This build ships without a publisher key, so the signed feed is inert. Use the web-research refresh instead."}
    if not user_opted_in():
        return {"ok": True, "status": "disabled", "reason": "Remote spec checks are off. Enable with: cw.py pref set update_check on"}
    if not force and _recently_checked(float(cfg.get("min_interval_hours", 24))):
        pending = pending_path().exists()
        return {"ok": True, "status": "skipped-recent", "pending_update": pending}
    get = fetcher or (lambda url: http_fetch(url, cfg))
    try:
        payload = get(cfg["feed_url"])
        sig_raw = get(cfg["signature_url"])
    except (urllib.error.URLError, OSError, ValueError) as exc:
        result = {"ok": False, "status": "error", "reason": f"could not fetch the feed ({type(exc).__name__}); specs left unchanged"}
        _write_last_check(result)
        return result
    try:
        signature = base64.b64decode(sig_raw.strip(), validate=True)
    except ValueError:
        signature = sig_raw
    if not verify_feed(payload, signature, key):
        result = {"ok": False, "status": "bad-signature", "reason": "feed signature did not verify; ignored"}
        _write_last_check(result)
        return result
    try:
        bundle = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return {"ok": False, "status": "error", "reason": "feed is not valid JSON"}
    checked = validate_bundle(bundle, today)
    if not checked["ok"]:
        result = {"ok": False, "status": "invalid-feed", "errors": checked["errors"][:10]}
        _write_last_check(result)
        return result
    if bundle["data_version"] <= _current_floor():
        result = {"ok": True, "status": "up-to-date", "data_version": _current_floor()}
        _write_last_check(result)
        try:
            pending_path().unlink()
        except FileNotFoundError:
            pass
        return result
    changes = diff_facts(checked["facts"])
    result = {"ok": True, "status": "update-available" if changes else "up-to-date", "data_version": bundle["data_version"], "change_count": len(changes), "changes": changes[:60]}
    if changes:
        paths.cache_dir(create=True)
        write_json_atomic(pending_path(), {
            "data_version": bundle["data_version"],
            "platforms": {pid: sorted(f) for pid, f in checked["facts"].items()},
            "payload_b64": base64.b64encode(payload).decode("ascii"),
            "signature_b64": base64.b64encode(signature).decode("ascii"),
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
        })
    _write_last_check(result)
    return result


def pending_summary() -> dict[str, Any]:
    """Re-verify and describe the pending update for the review step."""
    raw = read_json(pending_path(), default=None)
    if not raw:
        return {"ok": False, "error": "no pending update"}
    try:
        payload = base64.b64decode(raw["payload_b64"])
        signature = base64.b64decode(raw["signature_b64"])
    except (KeyError, ValueError):
        return {"ok": False, "error": "pending update is malformed; discard it"}
    if not verify_feed(payload, signature):
        return {"ok": False, "error": "pending update failed signature re-check; discarded"}
    bundle = json.loads(payload.decode("utf-8"))
    checked = validate_bundle(bundle)
    if not checked["ok"]:
        return {"ok": False, "error": "pending update no longer validates", "errors": checked["errors"][:10]}
    if bundle["data_version"] <= _current_floor():
        return {"ok": False, "error": "pending update is not newer than the installed data"}
    return {"ok": True, "data_version": bundle["data_version"], "facts": checked["facts"], "changes": diff_facts(checked["facts"]), "summary": bundle.get("summary", "")}


def apply_pending() -> dict[str, Any]:
    info = pending_summary()
    if not info["ok"]:
        return info
    result = specs.apply_facts(info["facts"], origin="signed-feed", meta={"feed_data_version": info["data_version"]})
    try:
        pending_path().unlink()
    except FileNotFoundError:
        pass
    result.update({"applied": True, "data_version": info["data_version"], "change_count": len(info["changes"])})
    return result


def discard_pending() -> dict[str, Any]:
    try:
        pending_path().unlink()
        return {"ok": True, "discarded": True}
    except FileNotFoundError:
        return {"ok": True, "discarded": False}
