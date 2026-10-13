"""Deterministic UTM tagging so campaign links are consistent and never typed by the model."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from . import specs

_SAFE = re.compile(r"[^a-z0-9_.-]+")

MEDIUM_BY_PLATFORM = {
    "twitter": "social",
    "linkedin": "social",
    "instagram": "social",
    "youtube-shorts": "video",
    "tiktok": "video",
    "threads": "social",
    "bluesky": "social",
    "newsletter": "email",
    "podcast": "audio",
}
SOURCE_BY_PLATFORM = {"twitter": "x", "youtube-shorts": "youtube"}


def _clean(value: str) -> str:
    return _SAFE.sub("-", value.strip().lower()).strip("-")[:60]


def add_utm(url: str, platform: str, campaign: str, content: str = "") -> dict[str, Any]:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return {"ok": False, "error": "only http(s) URLs can be tagged"}
    pid = specs.canonical_platform(platform)
    camp = _clean(campaign)
    if not camp:
        return {"ok": False, "error": "campaign is required"}
    existing = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not k.lower().startswith("utm_")]
    tags = [
        ("utm_source", SOURCE_BY_PLATFORM.get(pid, pid)),
        ("utm_medium", MEDIUM_BY_PLATFORM.get(pid, "social")),
        ("utm_campaign", camp),
    ]
    if content:
        tags.append(("utm_content", _clean(content)))
    query = urlencode(existing + tags)
    return {"ok": True, "url": urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))}
