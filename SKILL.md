---
name: content-wand
description: "Use when transforming content between formats or platforms. Handles: atomizing long-form content into Twitter/X threads, LinkedIn posts, newsletters, Instagram carousel scripts, YouTube Shorts scripts, podcast talking points; repurposing content between types (podcast→blog, thread→article, notes→newsletter). Works from text, URLs, transcripts, rough notes, or a topic idea."
---

# content-wand

## Overview

content-wand transforms any content into platform-native formats or converts between content types. It has two modes and optional brand voice matching.

**Architecture (hub-spoke orchestrator):** This file routes only — it contains strategy and sequencing. All execution lives in named sub-skills. Read this file completely before loading any sub-skill. Sub-skills are loaded one at a time, at their invocation point, and never communicate directly with each other.

**Core principle:** Generate immediately. Never gate output behind setup. Brand voice is an optional enhancement offered after the first output.

---

## STEP 1 — Classify the Request (Lines 1–50: Read this first)

Before anything else, identify the mode:

### Mode Detection Table

| Signal | Mode | Action |
|--------|------|--------|
| "turn this into..." + platform names (Twitter, LinkedIn, etc.) | **ATOMIZE** | One piece → multiple platform formats |
| "repurpose this as..." / "convert to..." / "make this a [type]" | **REPURPOSE** | Type A → Type B |
| Input is already a tweet thread + user wants other platforms | **ATOMIZE** | Expand to other platforms |
| Input is already a tweet thread + user wants "a blog post" | **REPURPOSE** | Thread → long-form |
| Ambiguous: could be either | Ask ONE question: "Transform to multiple platforms, or convert to a different content type?" |

**Platform names = ATOMIZE trigger:** Twitter, X, LinkedIn, newsletter, Instagram, carousel, YouTube Shorts, podcast, talking points

---

## STEP 2 — Ask Platform Selection (max 2 questions total)

**If ATOMIZE:** Ask which platforms (show the list, let them pick):
```
Which formats do you want?
→ Twitter/X thread
→ LinkedIn post
→ Email newsletter
→ Instagram carousel script
→ YouTube Shorts script
→ Podcast talking points
→ All of the above
```

**If REPURPOSE:** If target type is not clear from the request, ask what they want it converted to. Otherwise, proceed directly.

---

## Content Strategy Check

Before ingesting, assess platform-content fit. These are non-obvious strategy calls:

**Platform combination leverage** (matters when user picks multiple):
| Combination | Assessment |
|-------------|-----------|
| Twitter + newsletter | High leverage — different consumption contexts (snackable vs. deep) |
| Twitter + LinkedIn | High redundancy — same professional audience, similar tone; lower value |
| LinkedIn + Instagram carousel | Complementary — same idea, different format depth |
| All 6 platforms | Quality risk — warn user: "Generating all 6 at once dilutes quality. Recommend 2–3. Want to narrow it down?" |

**Source-to-platform fit:**
| Source type | Strong fit | Poor fit |
|-------------|-----------|----------|
| Tactical how-to / framework | Twitter thread, Instagram carousel | Podcast talking points |
| Personal story / experience | LinkedIn, newsletter | Instagram carousel |
| Data, research, findings | Twitter thread, newsletter | YouTube Shorts |
| Conversational, interview | Podcast talking points, YouTube Shorts | LinkedIn |
| Opinion / hot take | Twitter thread, LinkedIn | Email newsletter |

If there's a mismatch between source type and selected platforms, note it — don't silently produce weak output.

**Content viability:** If the source has no clear point of view, no concrete takeaway, and no memorable insight, the output will reflect that regardless of platform. Say so before generating: "This source is light on original ideas — the output will reflect that. Want to add more substance first?"

---

## STEP 2.5 — Reference Freshness Check

Before ingesting content, verify platform specs are current:

1. Read `references/platform-specs.md` — check the `last_verified:` date in the file header
2. Calculate days elapsed since `last_verified`
3. **If `last_verified` is missing OR age > `refresh_after_days` (30 days):**
   - Emit: "Platform specs are outdated — refreshing before we start..."
   - Run WebSearch for each major platform being used (or all if "all platforms" selected):
     - `"[platform] algorithm update [current year]"`
     - `"[platform] character limit changes [current year]"`
   - Compare findings against current sections in `platform-specs.md`
   - Update ONLY the sections where changes are confirmed. Do not guess.
   - Update `last_verified:` to today's date in the file header
   - Emit: "Specs updated. Generating now."
4. **If `last_verified` < 30 days old:** Proceed without refresh.

---

## STEP 3 — Ingest Content

Invoke `content-ingester` sub-skill.

Pass: user's raw input (text, URL, transcript, notes, or topic).

Receive: `---CONTENT-OBJECT---` block.

Emit status: "Got your content. Analyzing..."

---

## STEP 4 — Generate Content (no voice matching yet)

**ATOMIZE path:** Invoke `platform-writer` sub-skill.
Pass: `---CONTENT-OBJECT---` block + selected platforms + `VOICE-PROFILE: none`.

**REPURPOSE path:** Invoke `repurpose-transformer` sub-skill.
Pass: `---CONTENT-OBJECT---` block + target type + `VOICE-PROFILE: none`.
Then invoke `platform-writer` IF user also wants specific platform formats.

---

## STEP 5 — Deliver First Output

Show all generated content inline (preview).

**Save path:** `content-output/YYYY-MM-DD-[slug]/[platform].md`
- If `content-output/YYYY-MM-DD-[slug]/` already exists: use `content-output/YYYY-MM-DD-[slug]-v2/` (increment until unique — never overwrite existing outputs)

Emit: "Files saved to content-output/[date]-[slug]/"

**If platform-writer returns `compliance: fail` for any platform:**
Surface the failure immediately — do NOT save that output:
```
[Platform] output failed compliance — [list failures].
Want me to fix and regenerate? → Yes / Skip this platform
```

**If ALL platforms fail compliance:**
```
All outputs failed compliance checks. This usually means the source content
is incompatible with the selected platforms. Want to:
→ Fix and retry all platforms
→ Choose different platforms
→ Review the source content first
```

---

## STEP 6 — Offer Brand Voice (AFTER output, never before)

After delivery, check whether `.content-wand/brand-voice.json` exists in the project directory.

**If saved voice profile exists:**
```
I found your saved voice profile.
Want me to regenerate these in your voice?

→ Yes, apply my voice
→ No thanks, this is fine
```
If YES: Invoke `brand-voice-extractor` in READ mode → proceed to Step 7.

**If no saved profile:**
```
Want these to sound more like you?
I can learn your voice in 2 minutes — and remember it for every future use.

→ Yes, set up my voice
→ No thanks, this is fine
```
If YES: Invoke `brand-voice-extractor` in SETUP mode → proceed to Step 7.

If NO (either path): Done.

---

## STEP 7 — Regenerate with Voice (if brand voice was set up)

After brand voice extraction:

- **If SETUP mode just ran this session:** The `---VOICE-PROFILE-END---` block is already in memory. Do NOT re-invoke `brand-voice-extractor` — pass the in-memory block directly to `platform-writer`.
- **If READ mode ran (loading from saved file):** The `---VOICE-PROFILE-END---` block was returned by `brand-voice-extractor`. Pass it directly to `platform-writer`.

Then:
- Invoke `platform-writer` with: original `---CONTENT-OBJECT---` block + same platform list + `---VOICE-PROFILE---` block
- Deliver voice-matched versions inline
- Offer to save (only if SETUP mode ran — READ mode already has a saved file):
  "Save this voice profile so I remember it next time? → Yes / No"

---

## NEVER

- NEVER ask for brand voice before delivering the first output — voice is always step 6, never step 1
- NEVER ask more than 2 questions to clarify the request — disambiguate mode, pick platforms, then generate
- NEVER invoke platform-writer with a missing CONTENT-OBJECT — return to Step 3
- NEVER invoke repurpose-transformer and platform-writer in parallel — transformer output feeds writer input
- NEVER save files to content-output/ if compliance: fail — surface the failure to the user first
- NEVER use platform-specs.md without running the Step 2.5 freshness check — stale specs silently produce non-compliant content
- NEVER overwrite an existing content-output/ directory — use versioned directory names (-v2, -v3, etc.)

---

## Edge Case Handling

| Input | Handling |
|-------|---------|
| <50 words | Proceed; warn: "Short input — outputs will be concise" |
| >8,000 words | content-ingester passes full text; emit warning to platform-writer: "Source is long — prioritize depth on 2–3 themes over covering everything" |
| URL → 403/paywall | Notify; ask for paste; do NOT proceed on raw HTML |
| Non-English input | Proceed in input language; note platform specs may vary for non-Latin scripts |
| Already a tweet thread | Trigger mode-detection question (Step 1) |
| Corrupted `.content-wand/brand-voice.json` | Reject; offer to recreate; never proceed on corrupt data |
| Topic-only input (no content) | content-ingester runs WebSearch; note sources used |
| User changes mode mid-flow | Stop current generation; re-run mode detection from Step 1; re-use same CONTENT-OBJECT (skip Step 3) |
| Same content processed twice same day | Detect existing output directory; use -v2 suffix; notify: "Previous output preserved at [dir], new output at [dir-v2]" |

---

## Sub-Skill Handoff Reference

**How to invoke a sub-skill**: Load the named sub-skill's SKILL.md and follow its instructions exactly. When it completes, its output block is returned to the orchestrator — not to other sub-skills. Sub-skills never communicate directly with each other; all routing goes through this orchestrator.

All sub-skills communicate via structured blocks. Never interpret prose as handoff.

- **Input to content-ingester:** Raw user input (any format)
- **Output from content-ingester:** `---CONTENT-OBJECT-START---` ... `---CONTENT-OBJECT-END---`
- **Input to platform-writer:** `---CONTENT-OBJECT-START---` block + platform list + voice profile or `VOICE-PROFILE: none`
- **Output from platform-writer:** `---PLATFORM-OUTPUT-START---` ... `---PLATFORM-OUTPUT-END---` (one per platform)
- **Input to repurpose-transformer:** `---CONTENT-OBJECT-START---` block + `target_type:` + voice profile or `VOICE-PROFILE: none`
- **Output from repurpose-transformer:** `---TRANSFORMED-CONTENT-START---` ... `---TRANSFORMED-CONTENT-END---`
- **Input/output brand-voice-extractor:** `---VOICE-PROFILE-START---` ... `---VOICE-PROFILE-END---`
