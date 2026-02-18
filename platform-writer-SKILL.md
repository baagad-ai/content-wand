---
name: platform-writer
description: Use when content-wand needs to generate platform-native content from a ContentObject. Applies hard platform constraints and quality heuristics per format. Handles Twitter/X, LinkedIn, newsletter, Instagram carousel, YouTube Shorts, podcast talking points.
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

For each selected platform:

1. Emit: "Writing [platform name]..."
2. **MANDATORY — READ ENTIRE FILE**: Before generating any platform output, read
   `references/platform-specs.md` completely from start to finish. This file contains
   2026-current algorithm weights and character limits not in training data.
   **Do NOT load** `references/brandvoice-schema.md` for this task.
3. Generate content applying the ContentObject + voice profile (if provided)
4. If voice profile present: apply Voice Application rules (see section below) before Pass 1
5. Run compliance check (Pass 1)
6. Run quality check (Pass 2)
7. Output the `---PLATFORM-OUTPUT---` block

---

## Voice Application (when VOICE-PROFILE is not `VOICE-PROFILE: none`)

When a `---VOICE-PROFILE-START---` block is provided, apply it in this strict order:

**1. Tone axes — map values to register choices:**
| Axis | Value | Apply as |
|------|-------|----------|
| `formal_casual > 0.6` | Casual | Use contractions, conversational asides, first-person informality |
| `formal_casual < 0.4` | Formal | No contractions, precise vocabulary, professional register |
| `direct_narrative > 0.6` | Narrative | Lead with story or anecdote before the takeaway; build to the point |
| `direct_narrative < 0.4` | Direct | State the point in sentence 1; structure as claim → evidence → action |
| `serious_playful > 0.6` | Playful | Dry humor, wit, unexpected comparisons are welcome |
| `expert_accessible < 0.4` | Expert | Assume deep domain knowledge; skip beginner context |

Do not apply axes mechanically. Read `opening_patterns` and `structural_patterns` first — they are the ground truth. Axes are calibration signals, not absolute rules.

**2. Sentence style — enforce throughout:**
- `short-punchy`: Max 12 words per sentence. One idea per sentence. No compound clauses.
- `medium-varied`: Mix 10–20 word sentences. Vary rhythm. One short for every 2–3 longer.
- `long-flowing`: Sentences can reach 20–35 words. Subordinate clauses are fine. Build to a conclusion.

**3. Opening patterns — apply to the platform's hook/opener:**
Use the listed `opening_patterns` for the hook. Do not default to generic hooks when a pattern is specified.

**4. Taboo patterns — scan before emitting:**
After drafting, scan for any phrase or style listed in `taboo_patterns`. Rewrite any match. This is mandatory — do not emit taboo content.

**5. Platform variants — override base profile if present:**
If `platform_variants.[this platform]` contains a note, it overrides the base tone axes for that platform only.

**Conflict resolution:**
- Voice vs. compliance (Pass 1): **compliance wins**. Note the constraint in `quality_flags`.
- Voice vs. quality heuristics (Pass 2): apply voice; flag the trade-off if quality drops.
- NEVER sacrifice a hard constraint (character limit, link rule) to preserve voice.

---

## Pass 1: Compliance Checks (Hard Constraints)

These are FAIL conditions — fix before outputting:

**Twitter/X:**
- Each tweet ≤ 280 characters (standard account)
- No external links in thread body (non-Premium: 50–90% reach suppression since March 2026)
- Links go in a reply to tweet 1, or as "link in bio" reference only
- Thread between 3–10 tweets for most topics

**LinkedIn:**
- Total post ≤ 3,000 characters
- NO markdown (no `**bold**`, no `_italic_`, no headers with `#`)
- Bold/italic must use Unicode characters if emphasis needed
- Maximum 1 primary CTA

**Email newsletter:**
- Subject line ≤ 50 characters
- Maximum 2 CTAs total (1 primary above fold, 1 repeat at end)
- Single goal per email

**Instagram carousel:**
- Between 3 and 20 slides
- Caption ≤ 2,200 characters
- Slide 1 aspect ratio applies to ALL slides — do not mix
- Text direction: each slide gets headline + max 3 lines of body

**YouTube Shorts script:**
- Script reads in ≤ 45 seconds at natural pace (≈ 110–120 words)
- Hook stated in first 5 words of script
- No external links in script

**Podcast talking points:**
- Bullet KEYWORDS only — not full sentences
- CTA section is the only verbatim scripted section
- Total outline readable in target episode length

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
platform: [twitter-x|linkedin|newsletter|instagram-carousel|youtube-shorts|podcast]
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

These are the most common failure modes for AI-generated content. All are `compliance: fail` for content quality:

- **NEVER open with hollow filler:** "In today's fast-paced world...", "As we navigate the digital landscape...", "It's no secret that..."
- **NEVER use vague superlatives without evidence:** "groundbreaking", "revolutionary", "game-changing" — ground every strong claim in a specific number, name, or outcome
- **NEVER default to bullet lists:** AI defaults to bullets because they're safe. Use bullets only when the content is genuinely list-shaped. Prose is harder to write and more engaging to read.
- **NEVER write a generic CTA:** "Check out the link below", "Don't miss out", "Click here to learn more" — every CTA must name what the reader gets, not just that they should click
- **NEVER summarize when you should select:** A thread or carousel that covers 6 mediocre points loses to one that drives 2 great ones deep
- **NEVER use passive voice in hooks:** "It has been found that..." kills momentum. Active, direct voice for all openings.
- **NEVER produce content that could have been written by anyone about anything:** Every output must contain at least one specific detail, number, or perspective that makes it un-swappable with generic content on the same topic
