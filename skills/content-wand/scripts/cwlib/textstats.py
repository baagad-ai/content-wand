"""Character, grapheme and word counting that matches how platforms count."""

from __future__ import annotations

import re
import unicodedata

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)
BARE_DOMAIN_RE = re.compile(r"\b(?:[a-z0-9-]+\.)+(?:com|org|net|io|co|dev|ai|app|me|ly|gg|tv|xyz|news|blog)\b(?:/[^\s]*)?", re.IGNORECASE)
HASHTAG_RE = re.compile(r"(?<![\w&])#[^\W\d_][\w]*", re.UNICODE)
MENTION_RE = re.compile(r"(?<![\w@])@\w{1,30}")
WORD_RE = re.compile(r"[\w'\u2019-]+", re.UNICODE)

_ZWJ = 0x200D
_VS16 = 0xFE0F
_KEYCAP = 0x20E3


def _is_regional(cp: int) -> bool:
    return 0x1F1E6 <= cp <= 0x1F1FF


def _is_skin_tone(cp: int) -> bool:
    return 0x1F3FB <= cp <= 0x1F3FF


def _is_extender(ch: str) -> bool:
    cp = ord(ch)
    if cp in (_ZWJ, _VS16, _KEYCAP) or _is_skin_tone(cp) or 0xE0020 <= cp <= 0xE007F:
        return True
    return unicodedata.category(ch) in ("Mn", "Me", "Mc")


def graphemes(text: str) -> list[str]:
    """Approximate extended grapheme clusters using only the stdlib.

    Handles combining marks, ZWJ emoji sequences, variation selectors, skin
    tones, keycaps and regional-indicator flag pairs. Good enough for limit
    checks with a small safety margin (Bluesky counts graphemes).
    """
    clusters: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        cluster = ch
        i += 1
        if _is_regional(ord(ch)) and i < n and _is_regional(ord(text[i])):
            cluster += text[i]
            i += 1
        while i < n:
            nxt = text[i]
            if _is_extender(nxt):
                cluster += nxt
                i += 1
                if ord(nxt) == _ZWJ and i < n:
                    cluster += text[i]
                    i += 1
                continue
            break
        clusters.append(cluster)
    return clusters


def grapheme_len(text: str) -> int:
    return len(graphemes(text))


def codepoint_len(text: str) -> int:
    return len(text)


def _x_char_weight(ch: str) -> int:
    cp = ord(ch)
    if cp <= 4351 or 8192 <= cp <= 8205 or 8208 <= cp <= 8223 or 8242 <= cp <= 8247:
        return 1
    return 2


def _x_segment_weight(segment: str) -> int:
    """Weight of non-URL text. X counts every emoji sequence as 2, however complex."""
    total = 0
    for cluster in graphemes(unicodedata.normalize("NFC", segment)):
        cps = [ord(c) for c in cluster]
        if any(cp >= 0x1F000 or cp in (_VS16, _KEYCAP) for cp in cps):
            total += 2
        else:
            total += sum(_x_char_weight(c) for c in cluster)
    return total


def x_weighted_len(text: str, link_weight: int = 23) -> int:
    """Length as X counts it: URLs are a fixed weight, CJK and emoji count double."""
    total = 0
    pos = 0
    for m in URL_RE.finditer(text):
        total += _x_segment_weight(text[pos:m.start()])
        total += link_weight
        pos = m.end()
    total += _x_segment_weight(text[pos:])
    return total


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def word_count(text: str) -> int:
    return len(words(text))


def urls(text: str) -> list[str]:
    return URL_RE.findall(text)


def hashtags(text: str) -> list[str]:
    return HASHTAG_RE.findall(text)


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def strip_directions(text: str) -> str:
    """Remove stage/visual directions: [bracketed], (parenthetical) lines, VISUAL:/CUT: labels."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^\[.*\]$", s) or re.match(r"^\(.*\)$", s):
            continue
        if re.match(r"^(visual|cut to|show|text overlay|b-roll|on[- ]screen|sfx|music|note|camera)\s*:", s, re.IGNORECASE):
            continue
        s = re.sub(r"\[[^\]]*\]", "", s)
        out.append(s)
    return "\n".join(out)


def count_emoji(text: str) -> int:
    n = 0
    for ch in text:
        cp = ord(ch)
        if 0x1F300 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF or 0x1F000 <= cp <= 0x1F2FF:
            n += 1
    return n
