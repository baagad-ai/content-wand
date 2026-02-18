---
name: repurpose-transformer
description: Use when content-wand needs to transform content between types (podcast→blog, thread→article, notes→newsletter). Classifies transformation distance and applies appropriate logic. Does not apply platform formatting — handoff to platform-writer for that.
---

# repurpose-transformer

## Overview

Transforms content from one type to another. The transformation class determines the logic applied.

**Core principle:** The further the transformation distance, the more you must anchor to the source's core ideas — not try to preserve everything.

---

## Pre-Transformation Check

Before classifying transformation distance, identify the "repurposable core":

**The Repurposable Core** = the single insight, claim, or story that would survive any format change. Everything else in the source is supporting material.

**How to find it:** Ask: "If I could only take ONE thing from this source into the new format, what would make the output still worth reading?" That is the repurposable core.

**Why this matters:** Most repurposing fails because it tries to preserve EVERYTHING — the structure, the examples, the qualifications. A podcast repurposed as a Twitter thread that covers all 8 segments produces an incoherent thread. A podcast repurposed as a Twitter thread that drives ONE of the 8 segments to maximum depth produces a great thread.

**Core Claim Test:** State the repurposable core in 12 words or fewer. If you can't — the source lacks a clear core and you must notify the user before proceeding: "This source covers several disconnected ideas — which one should I build the [target format] around?"

---

## Transformation Distance Classification

Classify the transformation before starting:

| Class | Definition | Examples |
|-------|-----------|---------|
| `DIRECT` | Same approximate length, similar structure | blog → newsletter, thread → LinkedIn post |
| `COMPRESS` | Long source → shorter output | podcast → tweet thread, video → Instagram carousel |
| `EXPAND` | Short source → longer output | notes → blog post, tweet → newsletter |
| `STRUCTURAL` | Different content type entirely | podcast → ebook outline, case study → template |

---

## Logic Per Class

### DIRECT transformation
- Preserve the original's structure as much as possible
- Adapt only what the target format requires (tone, formality, length adjustments)
- Do not add new ideas not present in the source

### COMPRESS transformation
- Identify the 3 strongest ideas in the source (not the first 3 — the strongest 3)
- Build the output around these 3 ideas only
- Do not try to preserve everything — compression means selection
- Note what was omitted: `omitted_themes: [...]` in output block

### EXPAND transformation
- Ask ONE clarifying question if the angle is ambiguous: "What aspect should I develop most?"
- If the user has already specified the angle, proceed directly
- **Target length:** Aim for 3–5× the source word count. If source is 100 words, target 300–500 words. If source is a single tweet (20–30 words), do not stop until the output has genuine depth.
- **Expansion structure:**
  1. State the core claim from the source — make it sharper, not softer
  2. Add 2–3 concrete examples, analogies, or supporting evidence that serve the stated angle
  3. Anticipate and address the most obvious objection or misunderstanding
  4. Close with a takeaway that goes one step beyond restating the opening

**NEVER when expanding:**
- NEVER pad with transitions that add no information ("As I mentioned above...", "In conclusion, as we can see...")
- NEVER add ideas not present or clearly implied in the source material
- NEVER expand symmetrically — pick the 1–2 ideas worth developing and go deep; cut the rest
- NEVER treat "more words" as success — every sentence must add meaning, not length
- NEVER lose the source's distinctive angle in an attempt to be comprehensive

### STRUCTURAL transformation
- This is the highest-effort class
- The output type has its own structural requirements — apply them explicitly
- Example: podcast → ebook outline requires: title, chapter structure, chapter summaries, CTA
- Example: case study → template requires: [Problem] [Approach] [Result] [Lesson] structure

---

## Input Requirements

Requires:
1. `---CONTENT-OBJECT-START---` block
2. `target_type:` specified (e.g., "blog post", "email newsletter", "ebook outline")
3. Either a `---VOICE-PROFILE-START---` block OR `VOICE-PROFILE: none`

If target type is ambiguous: ask ONE clarifying question before proceeding.

---

## Fallback Behavior

| Situation | Response |
|-----------|---------|
| `---CONTENT-OBJECT-START---` block missing | STOP. Return to orchestrator — do not attempt transformation without structured input. |
| Target type not specified and cannot be inferred | Ask ONE clarifying question: "What should this be converted to?" |
| Transformation class cannot be determined | Default to DIRECT; note the assumption in the output block |
| Source content < 50 words (COMPRESS class) | STOP. Notify: "Source is too short to compress meaningfully — consider EXPAND or DIRECT instead." |

---

## Output Format

```
---TRANSFORMED-CONTENT-START---
source_type: [original content type]
target_type: [target content type]
distance_class: [DIRECT|COMPRESS|EXPAND|STRUCTURAL]
word_count: [N]
omitted_themes: [themes not included — COMPRESS class only; empty for others]
content:
[Full transformed content]
---TRANSFORMED-CONTENT-END---
```

---

## NOT Contract

Do NOT apply platform-specific formatting.
Even if the target type is obviously "a LinkedIn post" — do NOT format it for LinkedIn.
Even if you know the Twitter character limit — do NOT split into tweets.
Platform formatting is platform-writer's job. Hand off the `---TRANSFORMED-CONTENT---` block to the orchestrator, which routes to platform-writer.

Your job ends when the `---TRANSFORMED-CONTENT-END---` delimiter is written.
