"""Deterministic compliance and quality checks for generated platform outputs.

Language models are unreliable at counting characters. Every hard constraint
the skill promises (character limits, slide counts, markdown bans, link
rules) is therefore enforced here in code, using limits read from
data/platform-specs.json (plus approved local overrides).

Output file conventions (see references/output-formats.md):
- Units of a multi-part output (thread tweets, carousel slides, reply-chain
  posts) are separated by a line containing only `---`.
- Newsletter files start with `Subject:` and optional `Preheader:` lines.
- Instagram/TikTok/Shorts files may include a `Caption:` unit.
- `[square-bracket]` lines are visual/stage directions and do not count as
  spoken words.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import paths, specs, textstats
from .jsonio import read_json
from .scan import normalise

# Contract between code and data/platform-specs.json. Any fact present in the
# data file (base or approved override) wins over these defaults.
DEFAULTS: dict[str, dict[str, Any]] = {
    "twitter": {
        "post_char_limit": 280,
        "thread_units_min": 3,
        "thread_units_max": 10,
        "link_weight": 23,
        "links_in_body_severity": "ignore",
    },
    "linkedin": {"post_char_limit": 3000, "hook_visible_chars": 210, "hashtags_max": 5, "links_in_body_severity": "ignore"},
    "newsletter": {"subject_min_chars": 30, "subject_max_chars": 50, "subject_hard_max_chars": 78, "subject_max_words": 7, "cta_max": 2},
    "instagram": {"slides_min": 2, "slides_max": 20, "caption_char_limit": 2200, "hashtags_max": 5, "slide_body_lines_max": 3},
    "youtube-shorts": {"max_seconds": 180, "target_seconds": 60, "words_per_second": 2.4, "title_char_limit": 100, "hashtags_max": 3},
    "tiktok": {"caption_char_limit": 2200, "hashtags_max": 5, "hook_words_max": 10},
    "threads": {"post_char_limit": 500, "links_per_post_max": 5, "topic_tags_max": 1},
    "bluesky": {"post_grapheme_limit": 300},
    "podcast": {"bullet_words_max": 12},
}

PLACEHOLDER_RE = re.compile(r"(\[(insert|your|link|name|todo|tbd|add)[^\]]*\]|\bTODO\b|\bTBD\b|lorem ipsum|\{\{[^}]*\}\}|<insert[^>]*>)", re.IGNORECASE)
MD_BOLD = re.compile(r"(\*\*[^*\n]+\*\*|__[^_\n]+__)")
MD_HEADER = re.compile(r"(?m)^\s{0,3}#{1,6}\s+\S")
MD_BACKTICK = re.compile(r"`[^`\n]+`")
MD_LINK = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")
MD_BULLET = re.compile(r"(?m)^\s*[-*]\s+\S")
MD_ORDERED = re.compile(r"(?m)^\s*\d+\.\s+\S")
EM_DASH = "\u2014"
SPLIT_RE = re.compile(r"(?m)^\s*---\s*$")

_AI_PATTERNS_CACHE: dict[str, Any] | None = None


def ai_patterns() -> dict[str, Any]:
    global _AI_PATTERNS_CACHE
    if _AI_PATTERNS_CACHE is None:
        data = read_json(paths.DATA_DIR / "ai-patterns.json", default={})
        compiled: dict[str, Any] = {}
        for tier in ("tier1", "tier2"):
            compiled[tier] = [(e["term"], re.compile(e["pattern"], re.IGNORECASE)) for e in data.get(tier, [])]
        for group in ("filler", "opening_cliches", "closing_cliches", "false_intimacy", "corporate_inspirational"):
            compiled[group] = [(e["phrase"], re.compile(e["pattern"], re.IGNORECASE)) for e in data.get(group, [])]
        _AI_PATTERNS_CACHE = compiled
    return _AI_PATTERNS_CACHE


def lint_ai_patterns(text: str) -> dict[str, Any]:
    """Count AI-writing tells in text. Deterministic; used for honest before/after numbers."""
    pats = ai_patterns()
    t = text.replace("\u2019", "'").replace("\u2018", "'")
    found: dict[str, list[str]] = {}
    total = 0
    for group, entries in pats.items():
        hits: list[str] = []
        for label, rx in entries:
            n = len(rx.findall(t))
            if n:
                hits.extend([label] * n)
        if hits:
            found[group] = hits
            total += len(hits)
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    em_overuse = sum(1 for p in paragraphs if p.count(EM_DASH) >= 2)
    if em_overuse:
        found["em_dash_overuse_paragraphs"] = [str(em_overuse)]
        total += em_overuse
    return {"total": total, "by_group": {k: len(v) for k, v in found.items()}, "hits": found}


def _spec(platform: str) -> dict[str, Any]:
    cfg = dict(DEFAULTS.get(platform, {}))
    data = specs.merged()
    plat = data["platforms"].get(platform, {})
    for key, f in plat.get("facts", {}).items():
        cfg[key] = f.get("value")
    return cfg


def _check(findings: list[dict[str, Any]], level: str, check_id: str, message: str, unit: int | None = None) -> None:
    item = {"level": level, "id": check_id, "message": message}
    if unit is not None:
        item["unit"] = unit
    findings.append(item)


def split_units(text: str) -> list[str]:
    parts = [p.strip("\n") for p in SPLIT_RE.split(text)]
    return [p.strip() for p in parts if p.strip()]


def _markdown_hits(text: str) -> list[str]:
    hits = []
    if MD_BOLD.search(text):
        hits.append("**bold** / __bold__")
    if MD_HEADER.search(text):
        hits.append("# header")
    if MD_BACKTICK.search(text):
        hits.append("`backticks`")
    if MD_LINK.search(text):
        hits.append("[text](url) link")
    if MD_BULLET.search(text):
        hits.append("'- ' / '* ' bullet")
    if MD_ORDERED.search(text):
        hits.append("'1.' ordered list")
    return hits


def _generic(text: str, findings: list[dict[str, Any]], platform: str) -> None:
    if PLACEHOLDER_RE.search(text):
        _check(findings, "fail", "placeholder", "contains a placeholder (e.g. [insert ...], TODO, {{...}}) that must be resolved before publishing")
    if "[CW-ESCAPED]" in text:
        _check(findings, "fail", "escaped-fence", "contains an escaped structural token from untrusted source text; remove it")
    if re.search(r"(ignore (all |your )?(previous|prior) instructions|as an ai language model|i cannot assist|as a large language model)", normalise(text), re.IGNORECASE):
        _check(findings, "fail", "assistant-artifact", "contains assistant boilerplate or instruction-like text")
    letters = [c for c in text if c.isalpha()]
    if len(letters) > 40 and sum(1 for c in letters if c.isupper()) / len(letters) > 0.5:
        _check(findings, "warn", "all-caps", "more than half of the letters are uppercase")
    lint = lint_ai_patterns(text)
    tier1 = lint["by_group"].get("tier1", 0)
    if tier1:
        _check(findings, "warn", "ai-vocabulary", f"{tier1} Tier-1 AI-vocabulary hit(s): {', '.join(sorted(set(lint['hits']['tier1']))[:6])}")
    if lint["by_group"].get("opening_cliches"):
        _check(findings, "warn", "cliche-opener", "starts with a stock AI opener")
    if platform in ("twitter", "threads", "bluesky") and EM_DASH in text:
        _check(findings, "warn", "em-dash", "em dash found (reads as AI-written on short-form platforms)")


def validate_text(platform: str, text: str, spec_overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    pid = specs.canonical_platform(platform)
    findings: list[dict[str, Any]] = []
    metrics: dict[str, Any] = {}
    if pid not in DEFAULTS:
        return {"platform": pid, "compliance": "fail", "findings": [{"level": "fail", "id": "unknown-platform", "message": f"unknown platform '{platform}'"}], "metrics": {}}
    cfg = _spec(pid)
    if spec_overrides:
        cfg.update(spec_overrides)

    text = text.replace("\r\n", "\n").strip()
    if not text:
        _check(findings, "fail", "empty", "output is empty")
        return {"platform": pid, "compliance": "fail", "findings": findings, "metrics": metrics}

    _generic(text, findings, pid)
    fn = {
        "twitter": _twitter, "linkedin": _linkedin, "newsletter": _newsletter, "instagram": _instagram,
        "youtube-shorts": _shorts, "tiktok": _tiktok, "threads": _threads, "bluesky": _bluesky, "podcast": _podcast,
    }[pid]
    fn(text, cfg, findings, metrics)
    failed = [f for f in findings if f["level"] == "fail"]
    return {
        "platform": pid,
        "compliance": "fail" if failed else "pass",
        "fail_count": len(failed),
        "warn_count": sum(1 for f in findings if f["level"] == "warn"),
        "findings": findings,
        "metrics": metrics,
    }


def _twitter(text: str, cfg: dict[str, Any], f: list[dict[str, Any]], m: dict[str, Any]) -> None:
    units = split_units(text)
    limit = int(cfg["post_char_limit"])
    weights = [textstats.x_weighted_len(u, int(cfg.get("link_weight", 23))) for u in units]
    m.update({"units": len(units), "weighted_chars": weights, "limit": limit})
    for i, w in enumerate(weights, 1):
        if w > limit:
            _check(f, "fail", "char-limit", f"tweet {i} is {w} weighted characters (limit {limit})", i)
    if len(units) > 1:
        lo, hi = int(cfg["thread_units_min"]), int(cfg["thread_units_max"])
        if len(units) < lo or len(units) > hi:
            _check(f, "warn", "thread-length", f"thread has {len(units)} tweets (recommended {lo}-{hi})")
    sev = cfg.get("links_in_body_severity", "warn")
    for i, u in enumerate(units, 1):
        if textstats.urls(u) and i != len(units) and sev != "ignore":
            _check(f, "fail" if sev == "fail" else "warn", "link-in-body", f"tweet {i} contains a link (style preference only: X's published ranking code has no link penalty)", i)
    if units and len(units[0]) > 140:
        _check(f, "warn", "hook-length", "tweet 1 is long; a short opener is easier to read in the feed (craft advice, not a platform rule)")
    if units and units[0].lstrip().startswith(("\U0001F9F5", "Thread:", "A thread")):
        _check(f, "warn", "weak-opener", "avoid '🧵 Thread:' style openers; lead with the hook")
    for i, u in enumerate(units, 1):
        if len(textstats.hashtags(u)) > 2:
            _check(f, "warn", "hashtags", f"tweet {i} has more than 2 hashtags", i)


def _linkedin(text: str, cfg: dict[str, Any], f: list[dict[str, Any]], m: dict[str, Any]) -> None:
    limit = int(cfg["post_char_limit"])
    n = len(text)
    m.update({"chars": n, "limit": limit})
    if n > limit:
        _check(f, "fail", "char-limit", f"post is {n} characters (limit {limit})")
    md = _markdown_hits(text)
    if md:
        _check(f, "fail", "markdown", f"markdown does not render on LinkedIn: {', '.join(md)}")
    hook_zone = int(cfg["hook_visible_chars"])
    first_break = text.find("\n")
    first_line = text if first_break == -1 else text[:first_break]
    m["first_line_chars"] = len(first_line)
    if len(first_line) > hook_zone:
        _check(f, "warn", "hook-zone", f"first line is {len(first_line)} chars; the hook should land inside ~{hook_zone} chars before 'see more'")
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    long_paras = [i for i, p in enumerate(paragraphs, 1) if len(textstats.sentences(p)) > 3]
    if long_paras:
        _check(f, "warn", "paragraph-length", f"paragraph(s) {long_paras} have more than 3 sentences")
    tags = textstats.hashtags(text)
    if len(tags) > int(cfg["hashtags_max"]):
        _check(f, "warn", "hashtags", f"{len(tags)} hashtags (recommended max {cfg['hashtags_max']})")
    if textstats.urls(text) and cfg.get("links_in_body_severity") != "ignore":
        _check(f, "warn", "link-in-body", "link in post body (style preference only: LinkedIn says it does not intentionally limit link posts)")
    if re.search(r"(?i)(i'?m (so )?(excited|thrilled|humbled) to (share|announce)|just wanted to share|honou?red and humbled)", text):
        _check(f, "warn", "hollow-opener", "hollow LinkedIn opener")


def _newsletter(text: str, cfg: dict[str, Any], f: list[dict[str, Any]], m: dict[str, Any]) -> None:
    sm = re.search(r"(?im)^\s*subject\s*:\s*(.+)$", text)
    if not sm:
        _check(f, "fail", "subject-missing", "newsletter needs a 'Subject:' line")
        subject = ""
    else:
        subject = sm.group(1).strip()
    lo, hi, wmax = int(cfg["subject_min_chars"]), int(cfg["subject_max_chars"]), int(cfg["subject_max_words"])
    m.update({"subject_chars": len(subject), "subject_words": textstats.word_count(subject)})
    if subject:
        hard = int(cfg.get("subject_hard_max_chars", 78))
        if len(subject) > hard:
            _check(f, "fail", "subject-too-long", f"subject is {len(subject)} chars (RFC 5322 recommends at most {hard})")
        elif len(subject) > hi:
            _check(f, "warn", "subject-long", f"subject is {len(subject)} chars (target {lo}-{hi}; longer subjects are clipped on mobile)")
        if len(subject) < lo:
            _check(f, "warn", "subject-too-short", f"subject is {len(subject)} chars (target {lo}-{hi})")
        if textstats.word_count(subject) > wmax:
            _check(f, "warn", "subject-words", f"subject has {textstats.word_count(subject)} words (target <= {wmax})")
    pm = re.search(r"(?im)^\s*preheader\s*:\s*(.+)$", text)
    if pm and subject and pm.group(1).strip().lower() == subject.lower():
        _check(f, "warn", "preheader-repeat", "preheader repeats the subject line")
    ctas = re.findall(r"(?im)^\s*(?:cta|button)\s*:\s*(.+)$", text)
    m["ctas"] = len(ctas)
    if len(ctas) > int(cfg["cta_max"]):
        _check(f, "fail", "cta-count", f"{len(ctas)} CTAs (max {cfg['cta_max']})")
    if not ctas:
        _check(f, "warn", "cta-missing", "no 'CTA:' line found; newsletters need one primary call to action")
    body = re.sub(r"(?im)^\s*(subject|preheader|cta|button)\s*:.*$", "", text)
    m["body_words"] = textstats.word_count(body)


def _instagram(text: str, cfg: dict[str, Any], f: list[dict[str, Any]], m: dict[str, Any]) -> None:
    units = split_units(text)
    caption = ""
    slides: list[str] = []
    for u in units:
        if re.match(r"(?i)^\s*caption\s*:", u):
            caption = re.sub(r"(?i)^\s*caption\s*:\s*", "", u)
        elif re.match(r"(?i)^\s*(aspect ratio|format|alt text)\s*:", u) and "\n" not in u:
            continue
        else:
            slides.append(u)
    m.update({"slides": len(slides), "caption_chars": len(caption)})
    lo, hi = int(cfg["slides_min"]), int(cfg["slides_max"])
    if len(slides) < lo or len(slides) > hi:
        _check(f, "fail", "slide-count", f"{len(slides)} slides (allowed {lo}-{hi})")
    if len(caption) > int(cfg["caption_char_limit"]):
        _check(f, "fail", "caption-limit", f"caption is {len(caption)} chars (limit {cfg['caption_char_limit']})")
    tags = textstats.hashtags(caption or text)
    if len(tags) > int(cfg["hashtags_max"]):
        _check(f, "warn", "hashtags", f"{len(tags)} hashtags (recommended max {cfg['hashtags_max']})")
    if not caption:
        _check(f, "warn", "caption-missing", "no 'Caption:' unit found")
    max_lines = int(cfg["slide_body_lines_max"])
    for i, s in enumerate(slides, 1):
        lines = [ln for ln in s.splitlines() if ln.strip()]
        body = [ln for ln in lines if not re.match(r"(?i)^\s*(slide\s*\d+|visual|alt text|image)\s*[:\-]", ln)]
        if len(body) > max_lines + 1:
            _check(f, "warn", "slide-density", f"slide {i} has {len(body)} lines (headline + max {max_lines})", i)
    if slides and not re.search(r"(?i)alt\s*text", text):
        _check(f, "warn", "alt-text-missing", "no alt text provided for slides (accessibility)")


def _spoken_words(text: str) -> int:
    body = re.sub(r"(?im)^\s*(caption|title|description|hashtags?)\s*:.*$", "", text)
    return textstats.word_count(textstats.strip_directions(body))


def _shorts(text: str, cfg: dict[str, Any], f: list[dict[str, Any]], m: dict[str, Any]) -> None:
    words = _spoken_words(text)
    wps = float(cfg["words_per_second"])
    seconds = words / wps if wps else 0
    max_s = int(cfg["max_seconds"])
    m.update({"spoken_words": words, "est_seconds": round(seconds, 1), "max_seconds": max_s})
    target_s = int(cfg.get("target_seconds", max_s))
    m["target_seconds"] = target_s
    if seconds > max_s:
        _check(f, "fail", "duration", f"~{seconds:.0f}s spoken at {wps} words/sec (platform max {max_s}s)")
    elif seconds > target_s:
        _check(f, "warn", "duration-target", f"~{seconds:.0f}s spoken; above the {target_s}s target (platform max {max_s}s). Tighten unless the extra length earns its place")
    if textstats.urls(text):
        _check(f, "warn", "link-in-script", "links in a Shorts script are not clickable; use the pinned comment/description")
    first = textstats.words(textstats.strip_directions(text))[:5]
    if first and re.match(r"(?i)^(hey|hi|hello|welcome|so|today)$", first[0]):
        _check(f, "warn", "weak-hook", "script opens with a greeting instead of the hook")
    tags = textstats.hashtags(text)
    if len(tags) > int(cfg["hashtags_max"]):
        _check(f, "warn", "hashtags", f"{len(tags)} hashtags (recommended max {cfg['hashtags_max']})")
    if not re.search(r"(?m)^\s*\[", text):
        _check(f, "warn", "directions-missing", "no [visual direction] lines found")


def _tiktok(text: str, cfg: dict[str, Any], f: list[dict[str, Any]], m: dict[str, Any]) -> None:
    cap = ""
    cm = re.search(r"(?is)^\s*caption\s*:\s*(.+?)(?:\n\s*\n|\Z)", text, re.MULTILINE)
    if cm:
        cap = cm.group(1)
    m.update({"caption_chars": len(cap), "spoken_words": _spoken_words(text)})
    if len(cap) > int(cfg["caption_char_limit"]):
        _check(f, "fail", "caption-limit", f"caption is {len(cap)} chars (limit {cfg['caption_char_limit']})")
    tags = textstats.hashtags(cap or text)
    if len(tags) > int(cfg["hashtags_max"]):
        _check(f, "warn", "hashtags", f"{len(tags)} hashtags (recommended max {cfg['hashtags_max']})")
    spoken = textstats.words(textstats.strip_directions(re.sub(r"(?im)^\s*caption\s*:.*$", "", text)))
    if spoken and re.match(r"(?i)^(hey|hi|hello|welcome|what's up|whats up)$", spoken[0]):
        _check(f, "fail", "intro", "TikTok scripts must not open with a greeting or intro")
    first_sentence = " ".join(spoken[: int(cfg["hook_words_max"]) + 1])
    m["hook_preview"] = first_sentence
    if len(spoken) > 0 and not re.search(r"[.?!:,]", " ".join(spoken[: int(cfg["hook_words_max"])])) and len(spoken) > int(cfg["hook_words_max"]) + 8:
        _check(f, "warn", "hook-length", f"no sentence break in the first {cfg['hook_words_max']} words; hook may land too late")


def _threads(text: str, cfg: dict[str, Any], f: list[dict[str, Any]], m: dict[str, Any]) -> None:
    units = split_units(text)
    limit = int(cfg["post_char_limit"])
    m.update({"units": len(units), "chars": [len(u) for u in units], "limit": limit})
    for i, u in enumerate(units, 1):
        if len(u) > limit:
            _check(f, "fail", "char-limit", f"post {i} is {len(u)} chars (limit {limit})", i)
        if len(textstats.urls(u)) > int(cfg["links_per_post_max"]):
            _check(f, "warn", "links", f"post {i} has more than {cfg['links_per_post_max']} links (Threads allows {cfg['links_per_post_max']} unique links per post; the preview card shows on text-only posts)", i)
        if len(textstats.hashtags(u)) > int(cfg["topic_tags_max"]):
            _check(f, "warn", "topic-tags", f"post {i} has more than {cfg['topic_tags_max']} topic tag", i)
    if re.search(r"(?i)(comment below|like and share|drop a [\U0001F300-\U0001FAFF]|smash that)", text):
        _check(f, "warn", "engagement-bait", "engagement-bait phrasing is penalised; ask a real question instead")


def _bluesky(text: str, cfg: dict[str, Any], f: list[dict[str, Any]], m: dict[str, Any]) -> None:
    units = split_units(text)
    limit = int(cfg["post_grapheme_limit"])
    lens = [textstats.grapheme_len(u) for u in units]
    m.update({"units": len(units), "graphemes": lens, "limit": limit})
    for i, n in enumerate(lens, 1):
        if n > limit:
            _check(f, "fail", "grapheme-limit", f"post {i} is {n} graphemes (limit {limit})", i)
    if len(units) == 1 and not textstats.urls(text):
        _check(f, "warn", "no-link", "no link in this post; add the source link if one exists and it helps the reader")
    if re.search(r"(?i)(comment below|like and share|smash that)", text):
        _check(f, "warn", "engagement-bait", "engagement-bait phrasing is poorly received on Bluesky")


def _podcast(text: str, cfg: dict[str, Any], f: list[dict[str, Any]], m: dict[str, Any]) -> None:
    bullets = [ln.strip().lstrip("-*• ").strip() for ln in text.splitlines() if re.match(r"^\s*[-*•]\s+", ln)]
    maxw = int(cfg["bullet_words_max"])
    long_b = [b for b in bullets if textstats.word_count(b) > maxw]
    m.update({"bullets": len(bullets), "long_bullets": len(long_b)})
    if bullets and len(long_b) > max(2, len(bullets) // 4):
        _check(f, "fail", "full-sentences", f"{len(long_b)} bullets exceed {maxw} words; talking points must be keywords, not scripted sentences")
    if not re.search(r"(?im)^\s*(\#+\s*)?(cta|call to action)\b", text):
        _check(f, "warn", "cta-missing", "no CTA section; the CTA is the one verbatim-scripted part")
    if not re.search(r"(?i)transition", text):
        _check(f, "warn", "transitions", "no explicit TRANSITION cues between segments")


def validate_file(platform: str, file: Path, **kw: Any) -> dict[str, Any]:
    text = file.read_text(encoding="utf-8")
    text = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    res = validate_text(platform, text, **kw)
    res["file"] = str(file)
    return res


def platform_from_filename(name: str) -> str | None:
    stem = Path(name).stem.lower()
    pid = specs.canonical_platform(stem)
    return pid if pid in DEFAULTS else None


def validate_dir(directory: Path) -> dict[str, Any]:
    results = []
    for p in sorted(directory.glob("*.md")):
        pid = platform_from_filename(p.name)
        if pid is None:
            continue
        results.append(validate_file(pid, p))
    return {
        "directory": str(directory),
        "files": results,
        "compliance": "fail" if any(r["compliance"] == "fail" for r in results) else "pass",
        "checked": len(results),
    }
