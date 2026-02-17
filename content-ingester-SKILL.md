---
name: content-ingester
description: Use when content-wand needs to ingest raw input of any type (pasted text, URL, transcript, rough notes, or topic idea) and return a structured ContentObject for downstream processing.
---

# content-ingester

## Overview

Ingests any content signal and returns a structured ContentObject. That is the entire job.

**Core principle:** Extract, do not transform. Your output is raw material for other sub-skills. Never improve, summarize, or restructure the input.

---

## Input Classification

Classify the input before processing:

| Input Type | Signals | Action |
|-----------|---------|--------|
| `paste` | Plain text provided directly | Use as-is |
| `url` | Starts with http/https | Fetch via WebFetch tool |
| `transcript` | Contains timestamps, speaker labels, or "[inaudible]" | Use as-is; note it's a transcript |
| `notes` | Bullet points, fragments, incomplete sentences | Use as-is; note it's rough notes |
| `topic` | No content, just a subject/question | Run WebSearch (3–5 queries); assemble findings |

---

## Processing Rules

**For `url` input:**
1. Use WebFetch to retrieve the content
2. If 403/401/paywall response: STOP. Output `fetch_status: failed`. Do NOT proceed with HTML.
3. If redirect to login page: STOP. Output `fetch_status: login-required`.
4. If successful: extract the main body text only (strip nav, ads, footers)

**For `topic` input:**
1. Run 3–5 WebSearch queries to gather relevant information
2. Note all sources used
3. Assemble findings into raw text
4. Output `source_type: topic` with `sources_used: [list]`

**For all inputs:**
- Count words after extraction
- Identify 3 key themes (surface-level — do NOT editorialize)
- If word count < 100: include warning in output block
- If word count > 8,000: note this; do NOT truncate — pass full text

---

## Output Format

Output EXACTLY this block and nothing else after processing:

```
---CONTENT-OBJECT-START---
source_type: [paste|url|transcript|notes|topic]
word_count: [N]
fetch_status: [ok|failed|login-required]  (url only; omit for other types)
sources_used: [url1, url2, ...]  (topic only; omit for other types)
warnings: [list any: short-input, very-long-input, transcript-detected]
key_themes: [theme1, theme2, theme3]
raw_text:
[full extracted text — do not truncate, do not modify]
---CONTENT-OBJECT-END---
```

---

## NOT Contract

Do NOT transform, improve, clean up, summarize, or expand the input.
Even if the input is rough, incomplete, or unclear — do NOT restructure it.
Even if the content seems too short to be useful — do NOT add to it.
Even if you could write a better version — that is NOT your job.

Your job ends when the `---CONTENT-OBJECT-END---` delimiter is written.
The next sub-skill handles transformation.

---

## Fallback Behavior

| Failure | Response |
|---------|---------|
| URL fetch fails (403) | Output block with `fetch_status: failed`; add to warnings |
| URL is behind login | Output block with `fetch_status: login-required`; add to warnings |
| Topic search returns irrelevant results | Proceed with what was found; add `low-confidence-research` to warnings |
| Input is empty | Do NOT proceed. Ask user: "What content should I work with?" |
