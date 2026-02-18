# Platform Writer — Generation Guide

> Loaded ONCE before the per-platform generation loop in platform-writer.
> Contains: hook framework, pre-generation checks, content quality anti-patterns.

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

## Content Quality Anti-Patterns

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
