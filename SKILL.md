---
name: content-wand
description: "Use when transforming content between formats or platforms. Handles: atomizing long-form content into Twitter/X threads, LinkedIn posts, newsletters, Instagram carousel scripts, YouTube Shorts scripts, podcast talking points; repurposing content between types (podcast→blog, thread→article, notes→newsletter). Works from text, URLs, transcripts, rough notes, or a topic idea."
---

# content-wand

## Overview

content-wand transforms any content into platform-native formats or converts between content types. It has two modes and optional brand voice matching.

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
Save each format to `content-output/YYYY-MM-DD-[slug]/[platform].md`.
Emit: "Files saved to content-output/[date]-[slug]/"

**If platform-writer returns `compliance: fail` for any platform:**
Surface the failure immediately — do NOT save that output:
```
[Platform] output failed compliance — [list failures].
Want me to fix and regenerate? → Yes / Skip this platform
```

---

## STEP 6 — Offer Brand Voice (AFTER output, never before)

After delivery, ask:
```
Want these to sound more like you?
I can learn your voice in 2 minutes — and remember it for every future use.

→ Yes, set up my voice
→ No thanks, this is fine
```

If YES: Invoke `brand-voice-extractor` sub-skill in SETUP mode.
If NO: Done.

---

## STEP 7 — Regenerate with Voice (if brand voice was set up)

After brand voice extraction:
- Invoke `brand-voice-extractor` in APPLY mode (reads the extracted profile)
- Invoke `platform-writer` again with the `---VOICE-PROFILE---` block
- Deliver voice-matched versions
- Offer to save: "Save this voice profile so I remember it next time? → Yes / No"

---

## NEVER

- NEVER ask for brand voice before delivering the first output — voice is always step 6, never step 1
- NEVER ask more than 2 questions to clarify the request — disambiguate mode, pick platforms, then generate
- NEVER invoke platform-writer with a missing CONTENT-OBJECT — return to Step 3
- NEVER invoke repurpose-transformer and platform-writer in parallel — transformer output feeds writer input
- NEVER save files to content-output/ if compliance: fail — surface the failure to the user first

---

## Edge Case Handling

| Input | Handling |
|-------|---------|
| <50 words | Proceed; warn: "Short input — outputs will be concise" |
| >8,000 words | Summarize to top 3 themes; note this in output |
| URL → 403/paywall | Notify; ask for paste; do NOT proceed on raw HTML |
| Non-English input | Proceed in input language; note platform specs may vary for non-Latin scripts |
| Already a tweet thread | Trigger mode-detection question (Step 1) |
| Corrupted `.content-wand/brand-voice.json` | Reject; offer to recreate; never proceed on corrupt data |
| Topic-only input (no content) | content-ingester runs WebSearch; note sources used |

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
