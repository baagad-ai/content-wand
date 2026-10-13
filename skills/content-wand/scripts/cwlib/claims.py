"""Source-fidelity check: every quote, statistic and link in an output must be
traceable to the source material.

The most damaging failure of AI repurposing is a confident fabricated number
or quote attributed to a real person. This module extracts the verifiable
claims from generated text and checks each against the source, so the agent
(and the human reviewer) get a concrete list of unsupported claims instead of
a vague 'please double-check'.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

QUOTE_RE = re.compile(r"[\u201c\"]([^\u201c\u201d\"\n]{20,300})[\u201d\"]")
PERCENT_RE = re.compile(r"(?<![\w.])(\d{1,3}(?:[.,]\d+)?)\s?(?:%|(?:percent|per cent|pct)\b)", re.IGNORECASE)
MONEY_RE = re.compile(r"(?<!\w)([$€£¥₹])\s?(\d[\d,]*(?:\.\d+)?)\s?([kKmMbB]|million|billion|thousand|bn|mm)?\b")
MULTIPLE_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s?[x×]\b")
BIG_NUMBER_RE = re.compile(r"(?<![\w.$€£])(\d{1,3}(?:,\d{3})+|\d{4,})(?![\w%])")
DECIMAL_RE = re.compile(r"(?<![\w.])(\d+\.\d+)(?![\w.%])")
URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

_SCALE = {"k": 1e3, "thousand": 1e3, "m": 1e6, "mm": 1e6, "million": 1e6, "b": 1e9, "bn": 1e9, "billion": 1e9}


def _norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2013", "-").replace("\u2014", "-").replace("\u2026", "...")
    s = re.sub(r"\s+", " ", s)
    return s.casefold().strip()


def _num(s: str) -> float | None:
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def _source_numbers(source: str) -> set[float]:
    nums: set[float] = set()
    src = unicodedata.normalize("NFKC", source)
    for m in re.finditer(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(?:\s?([kKmMbB]|million|billion|thousand|bn|mm)\b)?", src):
        v = _num(m.group(1))
        if v is None:
            continue
        nums.add(v)
        scale = m.group(2)
        if scale and scale.lower() in _SCALE:
            nums.add(v * _SCALE[scale.lower()])
    for m in re.finditer(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty|hundred)\b", src, re.IGNORECASE):
        word = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100}[m.group(1).lower()]
        nums.add(float(word))
    return nums


def _quote_supported(quote: str, source_norm: str) -> bool:
    q = _norm_text(quote).strip(" .,;:!?\"'")
    if q in source_norm:
        return True
    # tolerate ellipsis-joined quotes: every fragment must appear
    frags = [x.strip(" .,;:!?\"'") for x in re.split(r"\.\.\.|\u2026|\[\.\.\.\]", q) if len(x.strip()) >= 12]
    return bool(frags) and all(fr in source_norm for fr in frags)


def extract_claims(output: str) -> dict[str, list[Any]]:
    return {
        "quotes": [m.group(1) for m in QUOTE_RE.finditer(output)],
        "percentages": [m.group(0).strip() for m in PERCENT_RE.finditer(output)],
        "money": [m.group(0).strip() for m in MONEY_RE.finditer(output)],
        "multiples": [m.group(0).strip() for m in MULTIPLE_RE.finditer(output)],
        "big_numbers": [m.group(1) for m in BIG_NUMBER_RE.finditer(output) if not YEAR_RE.fullmatch(m.group(1))],
        "decimals": [m.group(1) for m in DECIMAL_RE.finditer(output)],
        "urls": URL_RE.findall(output),
    }


def check_claims(source: str, output: str, extra_allowed_urls: list[str] | None = None) -> dict[str, Any]:
    """Check that quotes, statistics and URLs in `output` come from `source`."""
    source_norm = _norm_text(source)
    src_nums = _source_numbers(source)
    claims = extract_claims(output)
    unsupported: list[dict[str, Any]] = []
    supported = 0

    for q in claims["quotes"]:
        if _quote_supported(q, source_norm):
            supported += 1
        else:
            unsupported.append({"type": "quote", "text": q[:160], "why": "quoted text not found in the source"})

    def check_numeric(kind: str, raw: str, value: float | None) -> None:
        nonlocal supported
        if value is not None and any(abs(value - n) <= max(1e-9, abs(n) * 0.005) for n in src_nums):
            supported += 1
        else:
            unsupported.append({"type": kind, "text": raw, "why": "number not found in the source"})

    for raw in claims["percentages"]:
        m = PERCENT_RE.search(raw)
        check_numeric("percentage", raw, _num(m.group(1)) if m else None)
    for raw in claims["money"]:
        m = MONEY_RE.search(raw)
        if m:
            v = _num(m.group(2))
            scale = (m.group(3) or "").lower()
            amounts = {v} if v is not None else set()
            if v is not None and scale in _SCALE:
                amounts.add(v * _SCALE[scale])
            ok = any(any(abs(a - n) <= max(1e-9, abs(n) * 0.005) for n in src_nums) for a in amounts)
            if ok:
                supported += 1
            else:
                unsupported.append({"type": "money", "text": raw, "why": "amount not found in the source"})
    for raw in claims["multiples"]:
        m = MULTIPLE_RE.search(raw)
        check_numeric("multiple", raw, _num(m.group(1)) if m else None)
    seen_big = set()
    for raw in claims["big_numbers"]:
        if raw in seen_big:
            continue
        seen_big.add(raw)
        check_numeric("number", raw, _num(raw))
    for raw in claims["decimals"]:
        check_numeric("decimal", raw, _num(raw))

    allowed = {u.rstrip("/.,;") for u in (extra_allowed_urls or [])}
    src_urls = {u.rstrip("/.,;") for u in URL_RE.findall(source)}
    for u in claims["urls"]:
        key = u.rstrip("/.,;")
        if key in src_urls or key in allowed:
            supported += 1
        else:
            unsupported.append({"type": "url", "text": u[:160], "why": "URL not present in the source or provided by the user"})

    return {
        "ok": not unsupported,
        "supported_count": supported,
        "unsupported_count": len(unsupported),
        "unsupported": unsupported,
        "extracted": {k: len(v) for k, v in claims.items()},
        "guidance": "Remove each unsupported claim or ask the user to confirm it. Never invent statistics, quotes or links.",
    }
