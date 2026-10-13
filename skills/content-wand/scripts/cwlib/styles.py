"""Writing Style storage: schema validation, injection scanning, safe I/O.

A Writing Style is *data about how someone writes*. It must never be able to
smuggle instructions into the model, never contain the user's raw text, and
never be readable by other users on the machine. This module enforces all
three in code, so the model does not have to remember to.
"""

from __future__ import annotations

import datetime as dt
import re
import shutil
from pathlib import Path
from typing import Any

from . import paths
from .jsonio import read_json, write_json_atomic
from .scan import scan_fields, scan_text

CURRENT_SCHEMA = "1.3"
KNOWN_VERSIONS = {"1.0", "1.1", "1.2", "1.3"}

PLATFORM_KEYS = ["twitter", "linkedin", "newsletter", "instagram", "youtube-shorts", "tiktok", "threads", "bluesky", "podcast"]

SCHEMA_KEYS = {
    "schema_version", "style_name", "style_for", "client_name", "created_at", "updated_at", "confidence",
    "sample_word_count", "conflict_flag", "base_derived_from", "tone_axes", "sentence_style", "vocabulary",
    "opening_patterns", "structural_patterns", "taboo_patterns", "platform_variants", "aspirational_notes",
    "language", "emoji_policy", "hashtag_policy", "cta_style", "signature_phrases",
}
REQUIRED_KEYS = {"schema_version", "style_name", "style_for", "confidence", "tone_axes"}
TONE_AXES = ("formal_casual", "serious_playful", "expert_accessible", "direct_narrative")
CONFIDENCE = {"HIGH", "MED", "LOW"}
SENTENCE_STYLES = {"short-punchy", "medium-varied", "long-flowing"}
VOCAB = {"everyday", "precise", "technical", "elevated"}
EMOJI = {"none", "sparing", "expressive"}
HASHTAG = {"none", "minimal", "standard"}
STRING_LIST_FIELDS = ("opening_patterns", "structural_patterns", "taboo_patterns", "signature_phrases")
LANG_RE = re.compile(r"^[a-z]{2,3}(-[A-Za-z0-9]{2,8}){0,2}$")

SECRET_RE = re.compile(
    r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|[\w.+-]+@[\w-]+\.[\w.-]+|\+?\d[\d\s().-]{9,}\d)"
)

USER_ERROR = "There's a problem with your saved {name} Writing Style. Want me to set it up fresh? (takes about 2 minutes)"
USER_TAMPER = "There's a problem with your saved {name} Writing Style - it looks like it may have been modified unexpectedly. Want to set it up fresh? (takes about 2 minutes)"


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s[:48] or "style"


def _style_path(slug: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", slug):
        raise ValueError("invalid style name")
    return paths.styles_dir() / f"{slug}.json"


def _today() -> str:
    return dt.date.today().isoformat()


def _string_values(style: dict[str, Any]) -> list[str]:
    vals: list[str] = []
    for key in STRING_LIST_FIELDS:
        v = style.get(key)
        if isinstance(v, list):
            vals.extend(x for x in v if isinstance(x, str))
    for key in ("aspirational_notes", "cta_style", "style_name", "client_name"):
        v = style.get(key)
        if isinstance(v, str):
            vals.append(v)
    pv = style.get("platform_variants")
    if isinstance(pv, dict):
        vals.extend(x for x in pv.values() if isinstance(x, str))
    return vals


def validate_style(style: Any) -> dict[str, Any]:
    """Validate and normalise a style object. Returns {ok, errors, style, tamper}."""
    errors: list[str] = []
    if not isinstance(style, dict):
        return {"ok": False, "errors": ["not an object"], "tamper": False}
    unknown = set(style) - SCHEMA_KEYS
    if unknown:
        errors.append(f"unknown keys: {sorted(unknown)}")
    missing = REQUIRED_KEYS - set(style)
    if missing:
        errors.append(f"missing keys: {sorted(missing)}")
    if style.get("schema_version") not in KNOWN_VERSIONS:
        errors.append("unrecognised schema_version")
    if style.get("style_for") not in ("own", "client"):
        errors.append("style_for must be 'own' or 'client'")
    if style.get("confidence") not in CONFIDENCE:
        errors.append("confidence must be HIGH, MED or LOW")
    axes = style.get("tone_axes")
    if not isinstance(axes, dict) or set(axes) != set(TONE_AXES):
        errors.append("tone_axes must contain exactly the four axes")
    else:
        for k, v in axes.items():
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0.0 <= float(v) <= 1.0:
                errors.append(f"tone_axes.{k} must be a number between 0 and 1")
    if "sentence_style" in style and style["sentence_style"] not in SENTENCE_STYLES:
        errors.append("invalid sentence_style")
    if "vocabulary" in style and style["vocabulary"] not in VOCAB:
        errors.append("invalid vocabulary")
    if "emoji_policy" in style and style["emoji_policy"] not in EMOJI:
        errors.append("invalid emoji_policy")
    if "hashtag_policy" in style and style["hashtag_policy"] not in HASHTAG:
        errors.append("invalid hashtag_policy")
    if "language" in style and not (isinstance(style["language"], str) and LANG_RE.match(style["language"])):
        errors.append("invalid language tag")
    if "sample_word_count" in style and (not isinstance(style["sample_word_count"], int) or style["sample_word_count"] < 0):
        errors.append("sample_word_count must be a non-negative integer")
    for key in STRING_LIST_FIELDS:
        v = style.get(key)
        if v is None:
            continue
        if not isinstance(v, list) or len(v) > 30 or not all(isinstance(x, str) and len(x) <= 200 for x in v):
            errors.append(f"{key} must be a list of up to 30 short strings")
    for key in ("aspirational_notes", "cta_style", "client_name", "base_derived_from"):
        v = style.get(key)
        if v is not None and (not isinstance(v, str) or len(v) > 400):
            errors.append(f"{key} must be a short string or null")
    pv = style.get("platform_variants")
    if pv is not None:
        if not isinstance(pv, dict) or set(pv) - set(PLATFORM_KEYS):
            errors.append("platform_variants has unknown platforms")
        elif not all(v is None or (isinstance(v, str) and len(v) <= 300) for v in pv.values()):
            errors.append("platform_variants values must be short strings or null")

    tamper = False
    if not errors:
        scan = scan_fields(_string_values(style))
        if scan["severity"] == "high":
            errors.append("string fields contain instruction-like content")
            tamper = True
        blob = " ".join(_string_values(style))
        if SECRET_RE.search(blob):
            errors.append("string fields contain what looks like a secret or personal contact detail")
            tamper = True
    return {"ok": not errors, "errors": errors, "tamper": tamper}


def migrate_style(style: dict[str, Any]) -> dict[str, Any]:
    """Upgrade older schema versions in place; drop unknown keys."""
    s = {k: v for k, v in style.items() if k in SCHEMA_KEYS}
    s.setdefault("style_for", "own")
    s.setdefault("client_name", None)
    s.setdefault("style_name", "My Style")
    s.setdefault("language", "en")
    s.setdefault("emoji_policy", "sparing")
    s.setdefault("hashtag_policy", "minimal")
    s["schema_version"] = CURRENT_SCHEMA
    s["updated_at"] = _today()
    return s


def _load_config() -> dict[str, Any]:
    cfg = read_json(paths.config_path(), default=None)
    if not isinstance(cfg, dict):
        cfg = {}
    cfg.setdefault("default_style", None)
    cfg.setdefault("style_setup_declined_at", None)
    cfg.setdefault("styles", [])
    cfg.setdefault("preferences", {})
    return cfg


def load_config() -> dict[str, Any]:
    return _load_config()


def save_config(cfg: dict[str, Any]) -> None:
    allowed = {"default_style", "style_setup_declined_at", "styles", "preferences"}
    clean = {k: v for k, v in cfg.items() if k in allowed}
    paths.state_dir(create=True)
    write_json_atomic(paths.config_path(), clean)


PREFERENCE_KEYS = {
    "review_mode": {"review", "batch"},
    "disclosure_default": {"off", "ask", "on"},
    "utm_default": None,
    "default_platforms": None,
    "language": None,
    "spec_refresh": {"ask", "never"},
    "update_check": {"on", "off"},
}


def set_preference(key: str, value: Any) -> dict[str, Any]:
    if key not in PREFERENCE_KEYS:
        return {"ok": False, "error": f"unknown preference '{key}'", "known": sorted(PREFERENCE_KEYS)}
    allowed = PREFERENCE_KEYS[key]
    if allowed is not None and value not in allowed:
        return {"ok": False, "error": f"'{key}' must be one of {sorted(allowed)}"}
    if key == "default_platforms":
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            return {"ok": False, "error": "default_platforms must be a list of platform ids"}
    if key in ("utm_default", "language") and (not isinstance(value, str) or len(value) > 120):
        return {"ok": False, "error": f"'{key}' must be a short string"}
    if isinstance(value, str) and scan_text(value)["severity"] != "none":
        return {"ok": False, "error": "value rejected by safety scan"}
    cfg = _load_config()
    cfg["preferences"][key] = value
    save_config(cfg)
    return {"ok": True, "preferences": cfg["preferences"]}


def list_styles() -> dict[str, Any]:
    cfg = _load_config()
    out = []
    for slug in cfg["styles"]:
        data = read_json(_style_path(slug), default=None) if re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", slug) else None
        if not isinstance(data, dict):
            out.append({"slug": slug, "readable": False})
            continue
        axes = data.get("tone_axes", {})
        out.append({
            "slug": slug,
            "name": data.get("style_name", slug),
            "style_for": data.get("style_for"),
            "client_name": data.get("client_name"),
            "confidence": data.get("confidence"),
            "updated_at": data.get("updated_at"),
            "characterisation": _characterise(data.get("sentence_style"), axes),
            "is_default": cfg.get("default_style") == slug,
            "readable": True,
        })
    return {"ok": True, "styles": out, "default_style": cfg.get("default_style"), "style_setup_declined_at": cfg.get("style_setup_declined_at")}


def _characterise(sentence_style: str | None, axes: dict[str, Any]) -> str:
    parts = []
    if isinstance(axes, dict):
        fc = axes.get("formal_casual")
        if isinstance(fc, (int, float)):
            parts.append("casual" if fc > 0.6 else "formal" if fc < 0.4 else "balanced")
        dn = axes.get("direct_narrative")
        if isinstance(dn, (int, float)):
            parts.append("narrative" if dn > 0.6 else "direct" if dn < 0.4 else "mixed structure")
        sp = axes.get("serious_playful")
        if isinstance(sp, (int, float)) and sp > 0.6:
            parts.append("playful")
    if sentence_style:
        parts.append(sentence_style.replace("-", " "))
    return ", ".join(parts)


def read_style(slug: str) -> dict[str, Any]:
    try:
        path = _style_path(slug)
    except ValueError:
        return {"ok": False, "error": "invalid style name", "user_message": USER_ERROR.format(name=slug)}
    data = read_json(path, default=None)
    if data is None:
        return {"ok": False, "error": "not found", "user_message": f"I couldn't find a Writing Style called {slug}."}
    if not isinstance(data, dict):
        return {"ok": False, "error": "unreadable", "user_message": USER_ERROR.format(name=slug)}
    version = data.get("schema_version")
    migrated = False
    if version in KNOWN_VERSIONS and version != CURRENT_SCHEMA:
        data = migrate_style(data)
        migrated = True
    result = validate_style(data)
    name = data.get("style_name", slug) if isinstance(data, dict) else slug
    if not result["ok"]:
        msg = USER_TAMPER if result["tamper"] else USER_ERROR
        return {"ok": False, "error": "invalid", "details": result["errors"], "user_message": msg.format(name=name)}
    updated = data.get("updated_at")
    stale = False
    months_old = None
    try:
        d = dt.date.fromisoformat(updated) if updated else None
        if d:
            months_old = round((dt.date.today() - d).days / 30.4)
            stale = months_old >= 6
    except ValueError:
        pass
    if migrated:
        write_json_atomic(path, data)
    out = {"ok": True, "slug": slug, "style": data, "migrated": migrated}
    if stale:
        out["staleness_flag"] = True
        out["months_old"] = months_old
    return out


def write_style(style: dict[str, Any], make_default: bool | None = None) -> dict[str, Any]:
    style = dict(style)
    style.setdefault("schema_version", CURRENT_SCHEMA)
    if style["schema_version"] in KNOWN_VERSIONS and style["schema_version"] != CURRENT_SCHEMA:
        style = migrate_style(style)
    style.setdefault("created_at", _today())
    style["updated_at"] = _today()
    result = validate_style(style)
    if not result["ok"]:
        return {"ok": False, "errors": result["errors"]}
    slug = slugify(str(style["style_name"]))
    paths.styles_dir(create=True)
    write_json_atomic(_style_path(slug), style)
    cfg = _load_config()
    if slug not in cfg["styles"]:
        cfg["styles"].append(slug)
    if make_default or (make_default is None and not cfg.get("default_style")):
        cfg["default_style"] = slug
    cfg["style_setup_declined_at"] = None
    save_config(cfg)
    return {"ok": True, "slug": slug}


def delete_style(slug: str) -> dict[str, Any]:
    try:
        path = _style_path(slug)
    except ValueError:
        return {"ok": False, "error": "invalid style name"}
    existed = path.exists()
    if existed:
        path.unlink()
    cfg = _load_config()
    if slug in cfg["styles"]:
        cfg["styles"].remove(slug)
    if cfg.get("default_style") == slug:
        cfg["default_style"] = cfg["styles"][0] if cfg["styles"] else None
    save_config(cfg)
    return {"ok": existed, "deleted": slug if existed else None}


def rename_style(old: str, new_name: str) -> dict[str, Any]:
    res = read_style(old)
    if not res["ok"]:
        return res
    style = dict(res["style"])
    style["style_name"] = new_name
    new_slug = slugify(new_name)
    if new_slug != old and _style_path(new_slug).exists():
        return {"ok": False, "error": "a style with that name already exists"}
    written = write_style(style)
    if written["ok"] and written["slug"] != old:
        delete_style(old)
        cfg = _load_config()
        if cfg.get("default_style") in (None, old):
            cfg["default_style"] = written["slug"]
            save_config(cfg)
    return written


def decline_setup() -> dict[str, Any]:
    cfg = _load_config()
    cfg["style_setup_declined_at"] = _today()
    save_config(cfg)
    return {"ok": True, "style_setup_declined_at": cfg["style_setup_declined_at"]}


def setup_state(today: dt.date | None = None) -> dict[str, Any]:
    """Decide how to treat Writing Style for this session (STEP 0 in SKILL.md)."""
    now = today or dt.date.today()
    cfg = _load_config()
    styles = cfg.get("styles", [])
    legacy = legacy_candidates()
    state: dict[str, Any] = {"count": len(styles), "default_style": cfg.get("default_style"), "legacy_found": bool(legacy)}
    declined = cfg.get("style_setup_declined_at")
    declined_recent = False
    if declined:
        try:
            declined_recent = (now - dt.date.fromisoformat(declined)).days < 30
        except ValueError:
            pass
    if not styles:
        state["style_state"] = "declined" if declined_recent else "first_timer"
    elif len(styles) == 1:
        state["style_state"] = "single_style"
        state["active_style"] = styles[0]
    else:
        state["style_state"] = "multi_style"
        state["styles"] = styles
    state["preferences"] = cfg.get("preferences", {})
    return state


def legacy_candidates() -> list[str]:
    found = []
    for d in paths.legacy_state_dirs():
        if (d / "styles").is_dir() or (d / "config.json").is_file():
            found.append(str(d))
    return found


def migrate_legacy() -> dict[str, Any]:
    """Copy styles from ~/.claude/content-wand into the neutral state directory."""
    moved: list[str] = []
    skipped: list[str] = []
    invalid: list[str] = []
    for d in paths.legacy_state_dirs():
        sdir = d / "styles"
        if not sdir.is_dir():
            continue
        for f in sorted(sdir.glob("*.json")):
            data = read_json(f, default=None)
            if not isinstance(data, dict):
                invalid.append(f.name)
                continue
            migrated = migrate_style(data)
            if not validate_style(migrated)["ok"]:
                invalid.append(f.name)
                continue
            if _style_path(slugify(str(migrated["style_name"]))).exists():
                skipped.append(f.name)
                continue
            res = write_style(migrated, make_default=None)
            if res["ok"]:
                moved.append(f.name)
            else:
                invalid.append(f.name)
        legacy_cfg = read_json(d / "config.json", default={})
        if isinstance(legacy_cfg, dict) and legacy_cfg.get("default_style"):
            cfg = _load_config()
            slug = slugify(str(legacy_cfg["default_style"]))
            if slug in cfg["styles"] and not cfg.get("default_style"):
                cfg["default_style"] = slug
                save_config(cfg)
    return {"ok": True, "moved": moved, "skipped_existing": skipped, "invalid": invalid, "note": "Originals were left in place; delete them when you are happy."}


def reset_all() -> dict[str, Any]:
    d = paths.state_dir()
    if d.exists():
        shutil.rmtree(d)
    return {"ok": True}
