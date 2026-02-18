---
name: platform-writer
description: Use when content-wand needs to generate platform-native content from a ContentObject. Applies hard platform constraints and quality heuristics per format. Handles Twitter/X, LinkedIn, newsletter, Instagram carousel, YouTube Shorts, TikTok scripts, Threads posts, Bluesky posts, podcast talking points.
---

# platform-writer

## Overview

Generates platform-native content from a structured ContentObject. Two validation passes: compliance (hard constraints) then quality (heuristics). Emits status at the start of each format.

**Core principle:** Technically compliant content is not enough. Each output must pass both a compliance check AND a quality check. Platform-native means a creator could publish it without editing.

---

## Input Requirements

Requires ALL of the following before starting:
1. `---CONTENT-OBJECT-START---` block (from content-ingester)
2. `selected_platforms: [list]` (from orchestrator)
3. Either a `---VOICE-PROFILE-START---` block OR the literal string `VOICE-PROFILE: none`

If any input is missing: STOP. Do not attempt generation. Return to orchestrator.

---

## Generation Process (per platform)

**Before starting any platform generation:**
MANDATORY — READ ENTIRE FILE: Read `references/platform-specs.md` completely from
start to finish. Do this ONCE before the per-platform loop. Do NOT re-read for each
platform. **Do NOT load** `references/brandvoice-schema.md` for this task.

If `references/platform-specs.md` is not found: proceed using built-in platform
knowledge. Emit once: "Platform specs file missing — using training data for platform
rules. Create references/platform-specs.md to enable spec freshness checks."

For each selected platform:

1. Emit: "Writing [platform name]..."
2. Generate content applying the ContentObject + voice profile (if provided)
3. If voice profile present: apply Voice Application rules (see section below) before Pass 1
4. Run compliance check (Pass 1)
5. Run quality check (Pass 2)
6. Output the `---PLATFORM-OUTPUT---` block

---

## Voice Application (when VOICE-PROFILE is not `VOICE-PROFILE: none`)

When a `---VOICE-PROFILE-START---` block is provided, apply it in this strict order:

**1. Read opening_patterns and structural_patterns first (ground truth):**
These override everything else. Read them before applying any other axis.

**2. Read tone_axes as calibration context:**
| Axis | Value | Apply as |
|------|-------|----------|
| `formal_casual > 0.6` | Casual | Use contractions, conversational asides, first-person informality |
| `formal_casual < 0.4` | Formal | No contractions, precise vocabulary, professional register |
| `direct_narrative > 0.6` | Narrative | Lead with story or anecdote before the takeaway; build to the point |
| `direct_narrative < 0.4` | Direct | State the point in sentence 1; structure as claim → evidence → action |
| `serious_playful > 0.6` | Playful | Dry humor, wit, unexpected comparisons are welcome |
| `expert_accessible < 0.4` | Expert | Assume deep domain knowledge; skip beginner context |

Axes are calibration signals, not rules. They set register; opening_patterns set form.
Where they conflict, opening_patterns win.

**3. Sentence style — enforce throughout:**
- `short-punchy`: Max 12 words per sentence. One idea per sentence. No compound clauses.
- `medium-varied`: Mix 10–20 word sentences. Vary rhythm. One short for every 2–3 longer.
- `long-flowing`: Sentences can reach 20–35 words. Subordinate clauses fine.

**4. Hook/opener — apply opening_patterns to the platform's hook:**
Use the listed opening_patterns for the hook. Do not default to generic hooks when
a pattern is specified.

**5. Taboo scan — run before emitting:**
Scan for any phrase or style listed in `taboo_patterns`. Rewrite any match. Mandatory.

**6. Platform variants override (if present):**
If `platform_variants.[this platform]` contains a note, it overrides the base tone
axes for that platform only.

**Conflict resolution:**
- Voice vs. compliance (Pass 1): **compliance wins**. Note the constraint in `quality_flags`.
- Voice vs. quality heuristics (Pass 2): apply voice; flag the trade-off if quality drops.
- NEVER sacrifice a hard constraint (character limit, link rule) to preserve voice.

**LOW confidence voice profile handling:**
When `confidence: LOW` is present in the VOICE-PROFILE block:
- Apply the profile as specified, but weight `opening_patterns` and `structural_patterns`
  more heavily than tone axes (axes are less reliable with sparse samples)
- Add to `quality_flags`: "VOICE_CONFIDENCE_LOW — output may not accurately reflect
  the user's voice. The orchestrator will offer sample expansion."
- Do NOT ask the user for samples yourself — the orchestrator handles recovery.

If the CONTENT-OBJECT block contains a `condensed_summary:` field: use
condensed_summary as the primary generation input. Reference raw_text only
when generating direct quotes or the user specifically asks to include a
verbatim passage. This preserves context budget for long-source sessions.

---

## Hook Selection Framework

Hook type selection is not creative choice — it's matching content shape to hook pattern. Wrong hook type + good content = low engagement. Right hook type + average content = solid performance.

**Content-to-Hook Mapping:**

| Content Shape | Best Hook Type | Why | Example |
|---------------|----------------|-----|---------|
| Data / research | Outcome-first or Contrarian claim | Data without context is ignored; lead with the surprising conclusion | "Companies that do X earn 3x more. Most do the opposite." |
| Personal story | Tension-first | Must establish stakes before the story | "I lost everything I built in 18 months. Here's the one decision that caused it." |
| Tactical how-to | Specificity shock | Specific beats generic every time | "I write 5 tweets in 12 minutes. Not by writing faster." |
| Opinion / hot take | Direct assertion | Don't soften a hot take with qualifiers | "Productivity systems don't fail. Owners do." NOT "I think productivity systems might be overrated." |
| Curated list / frameworks | Curiosity gap | Imply the list solves a felt problem | "7 frameworks top founders use that business schools never teach" |
| Interview / conversation | Quote extraction | Pull the single most surprising statement | Start with the quote, attribute second |
| Myth-busting / contrarian reversal | Contrarian claim | Name the common belief before destroying it | "Everyone says you need 10K followers to monetize. You don't." |
| Retrospective / lessons learned | Tension-first with time anchor | Establish what was at stake before the lesson lands | "3 years ago I made the single most expensive mistake of my career." |
| Trend / prediction | Stakes-first | What happens if they miss this? | "Something is about to change in [domain] that most people aren't watching." |
| Case study walk-through | Outcome-first | Lead with the result; make them want the story | "We grew from 0 to $1M in 11 months. Here's the one decision that made it possible." |
| Commentary / reactive content | Quote extraction or Direct assertion | Ground in the triggering event before your take | Start with the quote/claim you're reacting to; your response follows |

> This table is a starting point, not a rule. When in doubt: choose the hook type that surfaces the content's most surprising or specific element. Surprise and specificity beat correct category selection every time.

**Hook Failure Modes (by platform):**
- **Twitter:** Hook that requires context to understand. Every tweet must be self-contained.
- **LinkedIn:** Hook that's inside the first 210 characters but doesn't stop the scroll (uses the space without earning it).
- **TikTok:** Any hook that starts with "In this video..." or any greeting. Algorithm drops at second 2.
- **YouTube Shorts:** Hook that promises more than the payoff delivers — drives skip-to-end behavior which tanks retention.
- **Instagram carousel:** Slide 1 that's a title slide with no hook. The image is the headline.

**The Hook Test (run before committing to a hook):**
Remove the hook from the content. Can the reader instantly predict what value they'll get? If yes — the hook has done its job. If no — rewrite.

---

## Pre-Generation Thinking Check

Before generating ANY platform output, run these three tests on the ContentObject:

**Test 1 — The Specificity Test:**
Can you name ONE specific detail, number, or perspective in this content that no one else could have written? If not — the output will be generic regardless of platform. Surface this: "This source lacks specific detail — generated content may feel generic. Want to add more before I generate?"

**Test 2 — The Intended Reader Test:**
Who is the ONE person who most needs this content? Write for that specific person, not for a demographic. Content written for "entrepreneurs" is unfocused. Content written for "a first-time founder who just hired their first employee" is specific enough to resonate broadly.

**Test 3 — The Hook Bet Test (for tweet 1, slide 1, email subject, TikTok/Shorts hook):**
Would this hook stop YOUR scroll — if you encountered it as a stranger, not knowing you wrote it? If you would scroll past it — rewrite it before proceeding to Pass 1. This test cannot be skipped.

These are silent checks. If all pass — proceed. If any fail — decide: fix silently, or surface to user (surface only if the gap is unfixable without more input from the user).

---

## Pass 1: Compliance Checks (Hard Constraints)

These are FAIL conditions — fix before outputting:

**Twitter/X:**
- Each tweet ≤ 280 characters (standard account)
- No external links in thread body (non-Premium: significant organic reach suppression
  confirmed — links in body reduce thread reach 50–90% vs. links-in-reply)
- Links go in a reply to tweet 1, or as "link in bio" reference only
- Thread between 3–10 tweets for most topics

**LinkedIn:**
- Total post ≤ 3,000 characters
- NO markdown (no `**bold**`, no `_italic_`, no headers with `#`)
- Bold/italic must use Unicode characters if emphasis needed
- Maximum 1 primary CTA
- ALSO BANNED (renders as literal text): `- ` bullets (use "→" "✦" "•"), `` `backticks` ``, `[text](url)` links (use plain URLs), `1.` ordered lists (use prose)

**Email newsletter:**
- Subject line ≤ 50 characters
- Maximum 2 CTAs total (1 primary above fold, 1 repeat at end)
- Single goal per email

**Instagram carousel:**
- Between 3 and 20 slides
- Caption ≤ 2,200 characters
- Slide 1 aspect ratio applies to ALL slides — do not mix
- Text direction: each slide gets headline + max 3 lines of body
- Recommended aspect ratio: 4:5 (1080×1350px) or 1:1 square. Avoid 16:9 — loses 40% of feed space. Declare aspect ratio at top of script so copy density can be calibrated.

**YouTube Shorts script:**
- Script reads in ≤ 45 seconds (80–130 words by pace; target 95–110 for measured delivery, up to 130 for fast talking-head). When in doubt write 100 words — add note: [adjust to speaker pace].
- Hook stated in first 5 words of script
- No external links in script

**Podcast talking points:**
- Bullet KEYWORDS only — not full sentences
- CTA section is the only verbatim scripted section
- Total outline readable in target episode length

**TikTok script:**
- Hook stated in first 2 seconds of script (≤ 10 words before first cut)
- No traditional intro ("Hey everyone, welcome back...")
- No competitor platform watermarks referenced in script
- Caption ≤ 2,200 characters including hashtags
- 3–5 hashtags maximum (more reduces reach)
- Script format: keyword talking points or full sentences for on-screen text

**Threads post:**
- Post ≤ 500 characters
- Maximum 1 link (only first link generates a preview card)
- Images: up to 10 per post; video up to 5 minutes

**Bluesky post:**
- Post ≤ 300 characters
- No character count wasted on URL shorteners (full URLs fine)
- Single-post format (thread via reply chain — note this if content requires thread)

---

## Pass 2: Quality Heuristics (per platform)

These are WARN conditions — flag in output if failing:

**Twitter/X thread:**
- Does tweet 1 contain a curiosity gap, bold claim, or outcome-first hook?
- Does the thread have a narrative payoff in the final tweet?
- Is tweet 1 strong enough to stand alone if the thread isn't read?

**LinkedIn post:**
- Does the hook appear in the first 210 characters (visible before "see more")?
- Is there exactly 1 clear CTA?
- Does each paragraph contain ≤ 3 sentences?

**Email newsletter:**
- Does the subject line contain an action verb?
- Is there a hook in the first 3–5 sentences?
- Is the primary CTA a button-style element (not just a text link)?

**Instagram carousel:**
- Does slide 1 stop the scroll? (Bold claim, striking visual direction, or strong question)
- Does each slide earn the next swipe? (Cliffhanger or incomplete thought)
- Is the CTA on the final slide clear and specific?

**YouTube Shorts script:**
- Is the hook in the first 3 seconds of the script?
- Is there a clear visual direction note every 2–4 seconds?
- Does the script end with a payoff that justifies watching to the end?

**Podcast talking points:**
- Is the episode's main point stated within the first 60 seconds of the outline?
- Are transitions between segments explicitly noted?
- Is the CTA section written verbatim?

**TikTok script:**
- Does the script start mid-thought or mid-action (no intro)?
- Is the hook in the first 2 seconds (first ≤ 10 words)?
- Is the content specific enough to rank in TikTok search for its topic?
- Does the script have a visual direction note every 3–5 seconds?

**Threads post:**
- Does the post invite a substantive reply (5+ words), not just emoji reactions?
- Is it written for conversation, not broadcast? (Threads penalizes low-effort engagement)
- Does it avoid engagement-bait ("comment below!")? Use genuine conversation starters instead.

**Bluesky post:**
- Does it contain a direct link to the source article or resource? (Bluesky rewards link posts)
- Is the tone intellectually engaged, not promotional? (Community is sensitive to marketing-speak)
- At 300 chars, is every word earning its place?
- If content is sensitive to reply context (controversial take, community discussion):
  note that Bluesky threadgate allows controlling who can reply — mention this option
  to the user as a publishing consideration.

---

## Handling Quality Warnings

When a quality check fails (WARN):

1. List the failure in `quality_flags` in the output block
2. Attempt to self-correct: revise the content to address the warning
3. If self-correction resolves it: remove it from `quality_flags`
4. If self-correction cannot resolve it without distorting the source content: keep in `quality_flags` and note why

**NEVER suppress a warning without attempting to fix it first.**
**NEVER sacrifice compliance (Pass 1) to resolve a quality warning (Pass 2).**
**NEVER ask the user about a quality warning — fix it silently or flag it.**

---

## Output Format (per platform)

```
---PLATFORM-OUTPUT-START---
platform: [twitter-x|linkedin|newsletter|instagram-carousel|youtube-shorts|tiktok|threads|bluesky|podcast]
compliance: [pass|fail]
compliance_failures: [list — empty if pass]
quality_flags: [list of quality warnings — empty if all pass]
char_count: [N]  (where applicable)
content:
[Full generated content for this platform]
---PLATFORM-OUTPUT-END---
```

After all platforms: save each to `content-output/YYYY-MM-DD-[content-slug]/[platform].md`

---

## NOT Contract

Do NOT fetch content from URLs.
Even if the ContentObject seems incomplete — do NOT go back to the source.
Even if you could improve the ContentObject — do NOT modify it.
Do NOT re-run content-ingester. If the ContentObject is missing, return to the orchestrator.

Your job starts at the `---CONTENT-OBJECT-END---` delimiter.
Everything before that delimiter is not your input.

---

## NEVER — Content Quality Anti-Patterns

These are the most common failure modes for AI-generated content. All belong in
`quality_flags` (Pass 2 warnings), NOT in `compliance: fail` (Pass 1). If any
of these appear in a draft: self-correct silently per Pass 2 handling rules.
Only surface in quality_flags if self-correction fails.

- **NEVER open with hollow filler:** "In today's fast-paced world...", "As we navigate the digital landscape...", "It's no secret that..."
- **NEVER use vague superlatives without evidence:** "groundbreaking", "revolutionary", "game-changing" — ground every strong claim in a specific number, name, or outcome
- **NEVER default to bullet lists:** AI defaults to bullets because they're safe. Use bullets only when the content is genuinely list-shaped. Prose is harder to write and more engaging to read.
- **NEVER write a generic CTA:** "Check out the link below", "Don't miss out", "Click here to learn more" — every CTA must name what the reader gets, not just that they should click
- **NEVER summarize when you should select:** A thread or carousel that covers 6 mediocre points loses to one that drives 2 great ones deep
- **NEVER use passive voice in hooks:** "It has been found that..." kills momentum. Active, direct voice for all openings.
- **NEVER produce content that could have been written by anyone about anything:** Every output must contain at least one specific detail, number, or perspective that makes it un-swappable with generic content on the same topic
