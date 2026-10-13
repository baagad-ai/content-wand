"""Deterministic scanner for indirect prompt injection in untrusted text.

This is one layer of defence-in-depth. It is heuristic: it will not catch every
attack, which is why the skill also uses trust boundaries, tool restrictions,
human approval gates and output validators. What it does reliably is catch the
cheap, common attacks (instruction overrides, hidden Unicode, encoded payloads,
markdown-image exfiltration) in code instead of leaving them to an LLM's
judgement.
"""

from __future__ import annotations

import base64
import binascii
import re
import unicodedata
from typing import Any

ZERO_WIDTH = {
    0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x2060, 0x2061, 0x2062, 0x2063, 0x2064,
    0xFEFF, 0x00AD, 0x180E,
}
BIDI = {0x202A, 0x202B, 0x202C, 0x202D, 0x202E, 0x2066, 0x2067, 0x2068, 0x2069}


def _is_tag_char(cp: int) -> bool:
    return 0xE0000 <= cp <= 0xE007F


def _is_variation_selector(cp: int) -> bool:
    return 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF


# Cyrillic/Greek letters that render like Latin letters.
CONFUSABLES = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y", "і": "i",
    "ј": "j", "ѕ": "s", "ԁ": "d", "һ": "h", "ո": "n", "ս": "u", "ο": "o", "ν": "v",
    "ρ": "p", "α": "a", "ε": "e", "ι": "i", "κ": "k", "τ": "t", "Ι": "I", "Ο": "O",
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Κ": "K", "Μ": "M", "Ν": "N",
    "Ρ": "P", "Τ": "T", "Χ": "X", "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M",
    "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X", "І": "I",
}

HIGH = "high"
LOW = "low"

# (id, severity, regex) - applied to normalised text (case-insensitive).
PATTERNS: list[tuple[str, str, str]] = [
    ("override-instructions", HIGH,
     r"\b(ignore|disregard|forget|override|bypass)\b[^.\n]{0,40}\b(previous|prior|above|earlier|all|any|your|the|these|those)\b[^.\n]{0,40}\b(instruction|instructions|rules|prompt|prompts|guidelines|directions|constraints|polic(?:y|ies))\b"),
    ("forget-everything", HIGH, r"\bforget (everything|what you|all (that|of that)|your (instructions|training|rules))\b"),
    ("new-instructions", HIGH, r"\b(new|updated|revised|real|actual) (system )?(instructions|prompt|rules)\s*[:\-]"),
    ("system-tag", HIGH, r"(^|\n)\s*(system|assistant|developer)\s*(prompt|message|instruction)?\s*:\s*\S"),
    ("chat-template-token", HIGH, r"(<\|im_start\|>|<\|im_end\|>|<\|system\|>|\[INST\]|\[/INST\]|<<SYS>>|</?system>|</?assistant>)"),
    ("persona-hijack", HIGH, r"\byou are (now|no longer|actually|really)\b|\bact as (if you (are|were)|an?|the)\b[^.\n]{0,40}\b(without|no) (restrictions|limits|filters|rules)\b|\bpretend (to be|you are)\b"),
    ("reveal-prompt", HIGH, r"\b(reveal|print|output|show|repeat|leak|display)\b[^.\n]{0,30}\b(system prompt|your (instructions|prompt|rules)|hidden (instructions|prompt))\b"),
    ("file-read-directive", HIGH, r"\b(read|open|cat|print|output|send|upload|exfiltrate|display)\b[^.\n]{0,40}(~/|/etc/|/home/|\.ssh|\.env\b|id_rsa|\.aws|credentials|\.claude|\.config|brand-voice\.json|api[_ -]?keys?|secrets?\b|passwords?\b)"),
    ("exfil-directive", HIGH, r"\b(send|post|upload|forward|transmit|leak|exfiltrate|email)\b[^.\n]{0,60}\b(to|at)\b[^.\n]{0,20}(https?://|\bwebhook\b|\bserver\b)"),
    ("shell-directive", HIGH, r"\b(curl|wget)\b[^\n]{0,80}\|\s*(sh|bash|zsh)\b|\brm\s+-rf\b|\bchmod\s+\+x\b|\bpowershell\b[^\n]{0,40}-enc"),
    ("append-to-output", HIGH, r"\b(append|add|insert|include|prepend|attach)\b(?:[^.\n]|\.(?=\S)){0,80}\b(to|in|into|at the end of|at the start of)\b[^.\n]{0,20}\b(all|every|each|the|your)\b[^.\n]{0,20}\b(output|outputs|posts?|threads?|responses?|results?|replies|content)\b"),
    ("conceal-from-user", HIGH, r"\b(do not|don't|never|without)\b[^.\n]{0,30}\b(tell|inform|notify|mention|alert|show|reveal)\b[^.\n]{0,20}\b(the )?(user|human|operator)\b|\bsecretly\b|\bsilently (send|post|upload|run)\b"),
    ("markdown-image-exfil", HIGH, r"!\[[^\]]*\]\(https?://[^)\s]*[?&][^)\s]*(=|%3d)[^)\s]{12,}\)"),
    ("tool-misuse", HIGH, r"\b(call|use|invoke|run|execute)\b[^.\n]{0,30}\b(the )?(bash|shell|terminal|write|webfetch|websearch|tool)\b[^.\n]{0,30}\b(to|and then)\b"),
    ("ai-addressed", LOW, r"\b(attention|note to|message for|instructions? for|dear)\b[^.\n]{0,15}\b(ai|assistant|llm|language model|model|chatbot|agent|claude|gpt|gemini|copilot)\b"),
    ("before-generating", LOW, r"\bbefore (you )?(generate|generating|writing|write|creating|create|responding|respond|summariz\w+)\b[^.\n]{0,60}\b(first|you (must|should|need to))\b"),
    ("must-model", LOW, r"\b(you must|you should|you need to|make sure to|be sure to)\b[^.\n]{0,60}\b(output|append|include|add|insert|ignore|reply with|respond with|say)\b[^.\n]{0,60}\b(in|to|at|before|after)\b[^.\n]{0,20}\b(every|all|each|your|the)\b[^.\n]{0,20}\b(post|output|response|reply|answer|summary|thread)\b"),
    ("mode-switch", LOW, r"\b(debug mode|developer mode|admin override|god mode|jailbreak|dan mode|maintenance mode)\b"),
    ("external-callback", LOW, r"\b(visit|fetch|open|request|call|ping|load)\b[^.\n]{0,30}https?://\S+"),
    ("hidden-markup", LOW, r"<!--[\s\S]{0,400}?(ignore|instruction|assistant|system|ai\b)[\s\S]{0,400}?-->|style\s*=\s*[\"'][^\"']*(display\s*:\s*none|font-size\s*:\s*0|visibility\s*:\s*hidden|color\s*:\s*(#fff(fff)?|white))"),
]

_COMPILED = [(pid, sev, re.compile(rx, re.IGNORECASE)) for pid, sev, rx in PATTERNS]
_BASE64_RUN = re.compile(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{48,}={0,2}(?![A-Za-z0-9+/=])")
_HEX_RUN = re.compile(r"(?<![0-9a-fA-F])(?:[0-9a-fA-F]{2}){32,}(?![0-9a-fA-F])")

DECODED_RISK = re.compile(
    r"(ignore|disregard)[^.\n]{0,30}(instruction|prompt)|system prompt|you are now|curl |wget |~/\.ssh|\.env|api[_ ]?key|exfiltrate",
    re.IGNORECASE,
)


def invisible_report(text: str) -> dict[str, Any]:
    counts = {"zero_width": 0, "bidi": 0, "tag": 0, "variation_selector": 0}
    for ch in text:
        cp = ord(ch)
        if cp in ZERO_WIDTH:
            counts["zero_width"] += 1
        elif cp in BIDI:
            counts["bidi"] += 1
        elif _is_tag_char(cp):
            counts["tag"] += 1
        elif _is_variation_selector(cp) and cp > 0xFE0F:
            counts["variation_selector"] += 1
    counts["total"] = sum(counts.values())
    return counts


def strip_invisible(text: str) -> str:
    out = []
    for ch in text:
        cp = ord(ch)
        if cp in ZERO_WIDTH or cp in BIDI or _is_tag_char(cp):
            continue
        if cp > 0xFE0F and _is_variation_selector(cp):
            continue
        out.append(ch)
    return "".join(out)


def decode_tag_chars(text: str) -> str:
    """Reveal ASCII smuggled via Unicode tag characters (U+E0000 block)."""
    decoded = []
    for ch in text:
        cp = ord(ch)
        if 0xE0020 <= cp <= 0xE007E:
            decoded.append(chr(cp - 0xE0000))
    return "".join(decoded)


def normalise(text: str) -> str:
    """Normalise text for matching: strip invisibles, fold confusables, NFKC."""
    tagged = decode_tag_chars(text)
    cleaned = strip_invisible(text)
    folded = "".join(CONFUSABLES.get(ch, ch) for ch in cleaned)
    folded = unicodedata.normalize("NFKC", folded)
    if tagged:
        folded += "\n" + tagged
    return folded


def mixed_script_words(text: str, limit: int = 5) -> list[str]:
    hits: list[str] = []
    for word in re.findall(r"\w{4,}", text):
        scripts = set()
        for ch in word:
            if ch.isalpha():
                try:
                    name = unicodedata.name(ch)
                except ValueError:
                    continue
                if name.startswith("LATIN"):
                    scripts.add("latin")
                elif name.startswith("CYRILLIC"):
                    scripts.add("cyrillic")
                elif name.startswith("GREEK"):
                    scripts.add("greek")
        if len(scripts) > 1:
            hits.append(word)
            if len(hits) >= limit:
                break
    return hits


def _snippet(text: str, start: int, end: int, width: int = 100) -> str:
    s = max(0, start - 10)
    e = min(len(text), max(end, start + 1) + 10)
    snippet = text[s:e].replace("\n", " ")
    return snippet[:width]


def _decoded_payloads(text: str) -> list[str]:
    found: list[str] = []
    for m in _BASE64_RUN.finditer(text):
        blob = m.group(0)
        pad = "=" * (-len(blob) % 4)
        try:
            raw = base64.b64decode(blob + pad, validate=False)
        except (binascii.Error, ValueError):
            continue
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        printable = sum(1 for c in decoded if c.isprintable() or c in "\n\t")
        if decoded and printable / len(decoded) > 0.9:
            found.append(decoded)
    for m in _HEX_RUN.finditer(text):
        try:
            decoded = bytes.fromhex(m.group(0)).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            continue
        if decoded and sum(1 for c in decoded if c.isprintable()) / len(decoded) > 0.9:
            found.append(decoded)
    return found


def scan_text(text: str) -> dict[str, Any]:
    """Scan untrusted text. Returns severity none|low|high plus findings."""
    findings: list[dict[str, Any]] = []
    if not text:
        return {"severity": "none", "findings": [], "invisible": invisible_report("")}

    inv = invisible_report(text)
    if inv["tag"] >= 1:
        revealed = decode_tag_chars(text)
        findings.append({
            "id": "unicode-tag-smuggling", "severity": HIGH,
            "snippet": (revealed or "hidden tag characters")[:100],
        })
    if inv["bidi"] >= 1:
        findings.append({"id": "bidi-control-chars", "severity": LOW, "snippet": f"{inv['bidi']} bidi control characters"})
    if inv["zero_width"] >= 8:
        findings.append({"id": "heavy-zero-width", "severity": LOW, "snippet": f"{inv['zero_width']} zero-width characters"})
    if inv["variation_selector"] >= 8:
        findings.append({"id": "variation-selector-payload", "severity": HIGH, "snippet": f"{inv['variation_selector']} variation selectors"})

    mixed = mixed_script_words(text)
    if mixed:
        findings.append({"id": "mixed-script-words", "severity": LOW, "snippet": ", ".join(mixed)[:100]})

    norm = normalise(text)
    for pid, sev, rx in _COMPILED:
        m = rx.search(norm)
        if m:
            findings.append({"id": pid, "severity": sev, "snippet": _snippet(norm, m.start(), m.end())})

    for decoded in _decoded_payloads(norm):
        if DECODED_RISK.search(decoded):
            findings.append({"id": "encoded-instructions", "severity": HIGH, "snippet": decoded[:100].replace("\n", " ")})
            break

    severity = "none"
    if any(f["severity"] == HIGH for f in findings):
        severity = HIGH
    elif findings:
        severity = LOW
    return {"severity": severity, "findings": findings, "invisible": inv}


def scan_fields(values: list[str]) -> dict[str, Any]:
    """Scan a list of short strings (e.g. stored style fields)."""
    merged: list[dict[str, Any]] = []
    for v in values:
        if isinstance(v, str):
            res = scan_text(v)
            merged.extend(res["findings"])
    severity = "none"
    if any(f["severity"] == HIGH for f in merged):
        severity = HIGH
    elif merged:
        severity = LOW
    return {"severity": severity, "findings": merged}


FENCE_TOKENS = re.compile(r"---\s*(CONTENT|PLATFORM|TRANSFORMED|VOICE|CW)[A-Z_-]*(START|END)?\s*---|<\/?untrusted_source[^>]*>|<\|[a-z_]{2,24}\|>|\[\/?INST\]|<<\/?SYS>>", re.IGNORECASE)


def sanitise_source(text: str) -> tuple[str, dict[str, Any]]:
    """Return text safe to embed in a structured block, plus a change report."""
    report = {"invisible_removed": invisible_report(text)["total"], "fences_escaped": 0}
    cleaned = strip_invisible(text)

    def _esc(m: re.Match[str]) -> str:
        report["fences_escaped"] += 1
        return "[CW-ESCAPED]"

    cleaned = FENCE_TOKENS.sub(_esc, cleaned)
    return cleaned, report


SECRET_TOKEN_RE = re.compile(
    r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)
