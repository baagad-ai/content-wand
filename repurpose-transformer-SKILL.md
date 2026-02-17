---
name: repurpose-transformer
description: Use when content-wand needs to transform content between types (podcast→blog, thread→article, notes→newsletter). Classifies transformation distance and applies appropriate logic. Does not apply platform formatting — handoff to platform-writer for that.
---

# repurpose-transformer

## Overview

Transforms content from one type to another. The transformation class determines the logic applied.

**Core principle:** The further the transformation distance, the more you must anchor to the source's core ideas — not try to preserve everything.

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
- Add supporting context, examples, or explanation — but only what serves the stated angle
- Do not pad. Every added sentence must earn its place.

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
