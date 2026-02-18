# content-wand Enterprise Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Push content-wand from 103/120 (Grade B) to 115+/120 (Grade A) by closing every remaining gap across all 8 skill-judge dimensions.

**Architecture:** 6-file targeted upgrade across the hub-spoke skill suite. No new files. No new sub-skills. Pure knowledge and coverage improvements — adding the expert knowledge, thinking frameworks, platform pipeline coverage, and description precision that separate good from state-of-the-art.

**Current Score:** 103/120 (85.8%) — Grade B
**Target Score:** 115+/120 (95.8%+) — Grade A

---

## Root Cause Analysis of Remaining Gaps

### D4: 11/15 — Description (highest leverage, +3 points available)
The description covers WHAT but not WHEN. No explicit trigger phrases. Brand voice capability is a major differentiator and it's not in the description. New platforms (TikTok, Threads, Bluesky) not mentioned.

### D8: 13/15 — Practical Usability (+2 points)
Critical gap: TikTok/Threads/Bluesky were added to platform-specs.md but the *content generation pipeline* was never extended. Users cannot select them in Step 2. platform-writer has no compliance checks or quality heuristics for them. The pipeline is broken for 3 of 10 supported platforms.

Secondary gap: No LOW confidence voice handling in platform-writer.

### D2: 13/15 — Mindset (+2 points)
Missing "Before X, ask yourself..." frameworks in platform-writer, brand-voice-extractor, and repurpose-transformer. Thinking patterns are implicit, not explicit.

### D1: 17/20 — Knowledge Delta (+2 points)
No hook selection methodology (HOW to choose which hook pattern for which content type). No "repurposable core" concept. No voice staleness awareness.

### D3: 14/15 — Anti-Patterns (+1 point)
brand-voice-extractor missing: NEVER list for what constitutes a bad writing sample.

### D5: 13/15 — Progressive Disclosure (+2 points)
Step 2.5 adds procedural weight to orchestrator. brand-voice-extractor platform_variants doesn't include new platforms.

### D6: 14/15 — Freedom Calibration (+1 point)
Minor: Hook selection table should use decision-tree style, not rigid prescription.

### D7: 8/10 — Pattern Recognition (+1 point)
Pattern deviates from official patterns. Needs cleaner hub-spoke routing with lighter orchestrator body.

---

## Implementation Tasks

---

### Task 1: Fix the Description (D4: 11→14, +3 pts)

**File:** `SKILL.md` — frontmatter only (lines 1-4)

**Change:** Rewrite `description` to answer WHAT/WHEN/KEYWORDS with explicit trigger phrases and brand voice capability.

**New description:**
```yaml
description: "Transforms content between formats and platforms. Use when user says 'turn this into', 'repurpose this as', 'make this a', 'atomize this', or 'reformat'. Creates Twitter/X threads, LinkedIn posts, email newsletters, Instagram carousels, YouTube Shorts scripts, TikTok scripts, Threads posts, Bluesky posts, podcast talking points from any source (pasted text, URL, transcript, rough notes, or topic idea). Also converts between content types: podcast→blog, thread→article, notes→newsletter, case study→template. Includes optional brand voice matching that learns writing style from samples and remembers it across sessions. Trigger keywords: repurpose, atomize, reformat, content repurposing, thread, carousel, newsletter, shorts script, brand voice, LinkedIn post, Twitter thread, TikTok script, content transformation."
```

---

### Task 2: Extend Platform Pipeline to Include TikTok/Threads/Bluesky (D8: 13→15, +2 pts)

This is the most critical missing piece. Three platforms are in platform-specs.md but NOT in the generation pipeline.

#### Task 2a: Add new platforms to SKILL.md Step 2 menu

**File:** `SKILL.md` — Step 2 platform list

**Change:** Replace the current platform list with:
```
→ Twitter/X thread
→ LinkedIn post
→ Email newsletter
→ Instagram carousel script
→ YouTube Shorts script
→ TikTok script
→ Threads post
→ Bluesky post
→ Podcast talking points
→ All of the above
```

Also update Step 1 Mode Detection Table trigger list:
```
Platform names = ATOMIZE trigger: Twitter, X, LinkedIn, newsletter, Instagram, carousel, YouTube Shorts, TikTok, Threads, Bluesky, podcast, talking points
```

#### Task 2b: Add new platforms to Content Strategy Check

**File:** `SKILL.md` — Content Strategy Check source-to-platform fit table

**Add rows:**
```markdown
| Short-form opinion / hot take | Twitter thread, TikTok, Threads | Podcast talking points |
| Community/conversation starter | Threads, Bluesky | YouTube Shorts |
| Visual/educational how-to | TikTok, Instagram carousel | Bluesky |
```

**Add platform combination leverage rows:**
```markdown
| Twitter + TikTok | High leverage — same short-form muscle, different audiences (professional vs general) |
| LinkedIn + Threads | Redundancy risk — overlapping professional tone; lower value unless voice differs |
| Bluesky + newsletter | Complementary — link-positive platform drives newsletter signups naturally |
```

#### Task 2c: Add TikTok/Threads/Bluesky compliance checks to platform-writer Pass 1

**File:** `platform-writer-SKILL.md` — Pass 1: Compliance Checks section

**Add after Podcast section:**
```markdown
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
```

#### Task 2d: Add TikTok/Threads/Bluesky quality heuristics to platform-writer Pass 2

**File:** `platform-writer-SKILL.md` — Pass 2: Quality Heuristics section

**Add after Podcast section:**
```markdown
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
```

#### Task 2e: Update platform-writer output format enum

**File:** `platform-writer-SKILL.md` — Output Format section

**Change:**
```
platform: [twitter-x|linkedin|newsletter|instagram-carousel|youtube-shorts|tiktok|threads|bluesky|podcast]
```

#### Task 2f: Add LOW confidence voice handling to platform-writer

**File:** `platform-writer-SKILL.md` — after Voice Application section

**Add:**
```markdown
**LOW confidence voice profile handling:**
When `confidence: LOW` is present in the VOICE-PROFILE block:
- Apply the profile as specified, but weight `opening_patterns` and `structural_patterns` more heavily than tone axes (axes are less reliable with sparse samples)
- Add to `quality_flags`: "Voice profile is LOW confidence — output may not accurately reflect the user's voice. More writing samples would improve accuracy."
- Do NOT ask the user for more samples — flag it and proceed.
```

#### Task 2f: Update brand-voice-extractor platform_variants

**File:** `brand-voice-extractor-SKILL.md` — Output Format section

**Change platform_variants to include:**
```
platform_variants:
  twitter: [brief note if different from base voice]
  linkedin: [brief note if different from base voice]
  newsletter: [brief note if different from base voice]
  instagram: [brief note if different from base voice]
  youtube-shorts: [brief note if different from base voice]
  tiktok: [brief note if different from base voice]
  threads: [brief note if different from base voice]
  bluesky: [brief note if different from base voice]
  podcast: [brief note if different from base voice]
```

---

### Task 3: Add Hook Selection Framework (D1: 17→19, +2 pts)

This is the most valuable expert knowledge gap. platform-writer knows what makes hooks good/bad but has no methodology for SELECTING which hook type matches which content type. This is the non-obvious craft knowledge.

**File:** `platform-writer-SKILL.md` — add new section before Pass 1

```markdown
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

**Hook Failure Modes (by platform):**
- **Twitter:** Hook that requires context to understand. Every tweet must be self-contained.
- **LinkedIn:** Hook that's inside the first 210 characters but doesn't stop the scroll (uses the space without earning it).
- **TikTok:** Any hook that starts with "In this video..." or any greeting. Algorithm drops at second 2.
- **YouTube Shorts:** Hook that promises more than the payoff delivers — drives skip-to-end behavior which tanks retention.
- **Instagram carousel:** Slide 1 that's a title slide with no hook. The image is the headline.

**The Hook Test (run before committing to a hook):**
Remove the hook from the content. Can the reader instantly predict what value they'll get? If yes — the hook has done its job. If no — rewrite.
```

---

### Task 4: Add Thinking Frameworks (D2: 13→15, +2 pts)

#### Task 4a: Pre-Generation Quality Check in platform-writer

**File:** `platform-writer-SKILL.md` — add before Pass 1 (after Hook Selection Framework)

```markdown
## Pre-Generation Thinking Check

Before generating ANY platform output, run these three tests on the ContentObject:

**Test 1 — The Specificity Test:**
Can you name ONE specific detail, number, or perspective in this content that no one else could have written? If not — the output will be generic regardless of platform. Surface this: "This source lacks specific detail — generated content may feel generic. Want to add more before I generate?"

**Test 2 — The Intended Reader Test:**
Who is the ONE person who most needs this content? Write for that specific person, not for a demographic. Content written for "entrepreneurs" is unfocused. Content written for "a first-time founder who just hired their first employee" is specific enough to resonate broadly.

**Test 3 — The Hook Bet Test (for tweet 1, slide 1, email subject, TikTok/Shorts hook):**
Would this hook stop YOUR scroll — if you encountered it as a stranger, not knowing you wrote it? If you would scroll past it — rewrite it before proceeding to Pass 1. This test cannot be skipped.

These are silent checks. If all pass — proceed. If any fail — decide: fix silently, or surface to user (surface only if the gap is unfixable without more input from the user).
```

#### Task 4b: Pre-Interview thinking framework in brand-voice-extractor

**File:** `brand-voice-extractor-SKILL.md` — add before SETUP Mode section

```markdown
## Voice Authenticity Framework

Before running the mini-interview, understand what you're trying to capture:

**Authentic voice** = the patterns that appear consistently when the writer is writing for THEMSELVES — not for a job application, not for a press release, not to impress anyone.

**Aspirational voice** = the patterns the writer WISHES they had — often more formal, more polished, more "professional" than their natural writing.

The interview is designed to surface authentic voice. But users will often offer aspirational artifacts:
- LinkedIn About sections → aspirational (crafted for impression)
- Corporate bios → aspirational (written for credibility)
- Published articles with heavy editing → may be authentic if self-published; not if professionally edited
- Personal tweets, newsletters, Substack posts, unedited emails → most authentic

Your job is to extract what they actually sound like, not what they wish they sound like. When in conflict, authentic wins.

**Cross-platform variance is signal, not noise:**
A person who writes casually on Twitter and formally on LinkedIn doesn't have an inconsistent voice — they have a sophisticated voice that adapts. Capture the variance in `platform_variants`, not the average.
```

#### Task 4c: Pre-Transformation thinking check in repurpose-transformer

**File:** `repurpose-transformer-SKILL.md` — add before Transformation Distance Classification

```markdown
## Pre-Transformation Check

Before classifying transformation distance, identify the "repurposable core":

**The Repurposable Core** = the single insight, claim, or story that would survive any format change. Everything else in the source is supporting material.

**How to find it:** Ask: "If I could only take ONE thing from this source into the new format, what would make the output still worth reading?" That is the repurposable core.

**Why this matters:** Most repurposing fails because it tries to preserve EVERYTHING — the structure, the examples, the qualifications. A podcast repurposed as a Twitter thread that covers all 8 segments produces an incoherent thread. A podcast repurposed as a Twitter thread that drives ONE of the 8 segments to maximum depth produces a great thread.

**Core Claim Test:** State the repurposable core in 12 words or fewer. If you can't — the source lacks a clear core and you must notify the user before proceeding: "This source covers several disconnected ideas — which one should I build the [target format] around?"
```

---

### Task 5: Add Brand Voice Sample Anti-Patterns (D3: 14→15, +1 pt)

**File:** `brand-voice-extractor-SKILL.md` — add after NOT Contract

```markdown
## NEVER — Sample Collection Anti-Patterns

These will corrupt the voice profile if not caught:

- **NEVER accept a corporate bio or LinkedIn About section as a writing sample.** These are crafted for impression management, not authentic voice. They actively poison extraction — the voice is aspirational, not real. If a user offers one: "That's great for context, but I need something you wrote for yourself — a tweet thread, a newsletter, or even an email to a friend. Those reveal your actual voice."

- **NEVER accept a heavily edited/ghostwritten piece.** If the user says "my PR team helped with this" or "this was for our company blog" — do NOT use it as a sample. Ask for something they wrote and published without editing assistance.

- **NEVER treat platform consistency as a problem.** A person who sounds casual on Twitter and formal on LinkedIn does not have a confused voice — they have a sophisticated voice. Extract both and encode as `platform_variants`. The problem is only when the user says they're "casual" but ALL samples are formal.

- **NEVER extract voice from samples that are responses to someone else.** Reply tweets, comment threads, and response emails are reactive — they mirror the other person's style. Use only original, initiated pieces.

- **NEVER use the aspirational model (Q4) as voice training data.** "I wish I'd written that" is an explicit signal that it's NOT their current voice. Q4 is informational — it goes in `aspirational_notes` only.
```

---

### Task 6: Add Voice Staleness Awareness (D1 +content, D8 +usability)

**File:** `brand-voice-extractor-SKILL.md` — add to Save Prompt section

```markdown
**Voice profile staleness:**
Voice evolves. A profile captured 6+ months ago may no longer match the user's current writing style, especially after:
- A significant platform shift (started writing on a new platform)
- An audience change (new niche, new role)
- A deliberate style evolution (decided to write more casually, more technically, etc.)

When loading a saved profile (READ mode), check `updated_at` in the JSON:
- If `updated_at` > 6 months ago: after applying voice, offer: "Your voice profile is [N] months old. Want to update it? (takes 2 min)"
- If < 6 months: proceed silently.

This offer is ALWAYS post-generation — never a gate before generating.
```

---

### Task 7: Add Repurposable Core Expert Knowledge to Content Strategy (D1 +content)

**File:** `SKILL.md` — Content Strategy Check section

**Add new subsection:**
```markdown
**Content viability depth — the repurposable core test:**
Before routing to sub-skills, identify whether the source has a repurposable core: a single insight, claim, or story that would survive any format change.

Ask: "If I could take only ONE thing from this source — what would make the output still worth reading?"

| Core present? | Confidence level | Action |
|---------------|-----------------|--------|
| Clear, specific core | HIGH | Proceed to ingestion |
| Implied but not stated | MED | Proceed; note to platform-writer: "extract and foreground the core claim in every hook" |
| No clear core — multiple disconnected ideas | LOW | Surface before generating: "This content covers [X, Y, Z] without a central claim — which one should I build around?" |
| No core at all — purely informational with no POV | CRITICAL | "This source has no point of view or distinctive insight. I can technically generate content from it, but every output will be generic. Want to add an angle before I proceed?" |
```

---

### Task 8: Improve Progressive Disclosure — brand-voice-extractor schema reference loading (D5)

**File:** `brand-voice-extractor-SKILL.md` — Schema Validation section

Currently references brandvoice-schema.md at the top of READ mode. The loading instruction should be more specific about what it needs from that file:

**Change READ Mode to:**
```markdown
## READ Mode

**MANDATORY — READ ENTIRE FILE**: Before validating, read `references/brandvoice-schema.md`
completely. This defines: (1) approved keys for validation, (2) rejection rules,
(3) confidence scoring criteria, and (4) schema migration rules for older versions.
**Do NOT load** `references/platform-specs.md` for this task.
```

Also add to SETUP Mode — to make loading conditional on what's needed:
```markdown
**Do NOT load** `references/platform-specs.md` or `references/brandvoice-schema.md` during the interview phase — only load brandvoice-schema.md when writing the final JSON file (at Save Prompt).
```

---

### Task 9: Tighten Orchestrator for D7 Pattern Clarity

The orchestrator SKILL.md follows a compound Navigation + Process pattern. To score 9/10 on D7, the orchestrator should read more like a routing document (Navigation) with embedded decision tables (Process), and less like a procedural script. The main change is framing.

**File:** `SKILL.md` — Overview section

**Change to:**
```markdown
**Architecture (hub-spoke orchestrator):** This file is a routing document. It classifies the request, makes strategy decisions, and sequences sub-skill invocations. It does NOT generate content directly. Every content decision lives in a named sub-skill. Read this file completely before loading any sub-skill.

**Decision sequence:** Classify request → Select platforms → Verify strategy fit → Check reference freshness → Ingest content → Generate → Deliver → Offer voice enhancement

**Sub-skills are stateless.** Each sub-skill receives its full input in the handoff block and returns its full output in a structured block. They do not share state. They do not communicate with each other. All state lives in this orchestrator.
```

---

### Task 10: Minor precision for D6 Freedom Calibration

**File:** `platform-writer-SKILL.md` — Hook Selection Framework

The Hook-Content mapping table should explicitly mark it as a starting point for judgment, not a rigid lookup:

Add footnote to the table:
```markdown
> This table is a starting point, not a rule. When in doubt: choose the hook type that surfaces the content's most surprising or specific element. Surprise and specificity beat correct category selection every time.
```

---

## Execution Order

Tasks must be executed in this order due to dependencies:

1. **Task 1** — Description fix (independent, highest impact)
2. **Task 2a, 2b** — SKILL.md platform pipeline additions
3. **Task 3, 4a** — platform-writer expert additions (Hook Selection + Pre-Generation Check)
4. **Task 2c, 2d, 2e, 2f (platform-writer)** — platform-writer compliance + quality heuristics
5. **Task 4b, 5, 6, 8** — brand-voice-extractor additions
6. **Task 4c, 7** — repurpose-transformer and SKILL.md content strategy
7. **Task 9, 10** — Framing and polish

**Commit after all changes:** Single atomic commit with full summary.

---

## Expected Score After Implementation

| Dimension | Current | Target | Key Change |
|-----------|---------|--------|------------|
| D1: Knowledge Delta | 17 | 19 | Hook selection framework, repurposable core |
| D2: Mindset | 13 | 15 | 3 thinking frameworks added |
| D3: Anti-Patterns | 14 | 15 | Brand voice sample NEVER list |
| D4: Specification | 11 | 14 | Description rewrite |
| D5: Progressive Disclosure | 13 | 14 | Schema loading precision |
| D6: Freedom Calibration | 14 | 15 | Hook table framing |
| D7: Pattern Recognition | 8 | 9 | Orchestrator framing |
| D8: Practical Usability | 13 | 15 | Platform pipeline + LOW voice |
| **TOTAL** | **103** | **116** | **+13 points** |

**Projected grade: A (96.7%)**
