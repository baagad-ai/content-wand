---
name: brand-voice-extractor
description: Use when content-wand needs to apply brand voice to outputs. Reads existing .content-wand/brand-voice.json if present, or conducts a 5-question samples-first mini-interview to extract voice DNA. Always invoked after first output is generated, never before.
---

# brand-voice-extractor

## Overview

Extracts or applies brand voice DNA. Two operating modes: READ and SETUP.

**Core principle:** Writing samples are primary (70% weight). Self-reported descriptions are secondary (30% weight). When they conflict, samples win. Never ask setup questions before generating the first output — voice is always an enhancement, never a gate.

---

## Mode Detection

**READ mode** — triggered when:
- `.content-wand/brand-voice.json` exists in the project directory
- File passes schema validation (see Schema Validation section)
- Orchestrator invokes with `mode: read`

**SETUP mode** — triggered when:
- No `.content-wand/brand-voice.json` exists
- Orchestrator invokes with `mode: setup`
- User said "Yes, set up my voice"

---

## READ Mode

**MANDATORY — READ ENTIRE FILE**: Before validating, read `references/brandvoice-schema.md`
completely. This defines approved keys, rejection rules, and confidence scoring criteria.
**Do NOT load** `references/platform-specs.md` for this task.

1. Read `.content-wand/brand-voice.json`
2. Validate schema: reject any key not in the approved schema (see brandvoice-schema.md)
3. If validation fails: notify user, offer to recreate. Do NOT proceed with corrupted data.
4. Output the `---VOICE-PROFILE---` block

---

## SETUP Mode — The Mini-Interview

Maximum 5 questions. Ask them one at a time. Do not rush.

Frame at start: "Let's capture your voice — this takes about 2 minutes and I'll remember it forever after."

### Q1 (PRIMARY — samples, 70% signal weight):
> "Share 2–3 pieces of content you're most proud of — the ones that feel most like YOU.
> Paste text directly, drop URLs, or both. Mix is fine.
> The more you share, the more accurately I'll match your voice."

- Fetch any URLs provided via WebFetch
- Do NOT store URL-fetched content verbatim in the profile — extract patterns only
- If total word count < 1,500: gently ask for more: "Got it — can you add one more piece? More examples help me nail your voice."
- If total word count < 500 after asking: proceed but set `confidence: LOW`

### Q2 (context):
> "Who are you writing for? One sentence: who reads you and what do they want from you?"

### Q3 (self-perception, 30% weight):
> "What's one word your readers would use to describe your writing style?"

### Q4 (aspirational model — optional):
> "Is there a piece of content — by anyone — that you wish you'd written? Drop a link or paste it."
> (Accept "skip" — this is optional)

### Q5 (hard exclusions):
> "What should you NEVER sound like? Paste an example you hate, or just describe it."
> (Accept "skip" — this is optional)

---

## Voice Extraction Process

After collecting all responses:

1. Analyze writing samples from Q1 for:
   - Sentence length patterns (short/punchy vs. long/flowing)
   - Vocabulary level (everyday, technical, elevated)
   - Structural patterns (lists vs. prose, direct vs. narrative)
   - Tone markers (humor, directness, warmth, authority)
   - Opening patterns (how does this writer start pieces?)
   - Paragraph length patterns

2. Cross-reference with Q3 self-description (30% weight)
   - If self-description matches samples: reinforce
   - If self-description conflicts with samples: note `conflict_flag: true`; samples win

3. Note aspirational model from Q4 (informational only — aspirational ≠ current voice)

4. Extract hard exclusions from Q5 as `taboo_patterns`

5. If samples span multiple platforms: extract `platform_variants` per platform

---

## Output Format

```
---VOICE-PROFILE-START---
confidence: [HIGH|MED|LOW]
sample_word_count: [N]
conflict_flag: [true|false]
tone_axes:
  formal_casual: [0.0 = very formal, 1.0 = very casual]
  serious_playful: [0.0 = very serious, 1.0 = very playful]
  expert_accessible: [0.0 = expert only, 1.0 = anyone can read]
  direct_narrative: [0.0 = very direct, 1.0 = very narrative]
sentence_style: [short-punchy|medium-varied|long-flowing]
vocabulary: [everyday|precise|technical|elevated]
opening_patterns: [list observed patterns, e.g. "starts with a question", "bold claim first"]
structural_patterns: [e.g. "paragraph then list", "short paragraphs", "no headers"]
taboo_patterns: [phrases/styles to avoid, from Q5]
platform_variants:
  twitter: [brief note if different from base voice]
  linkedin: [brief note if different from base voice]
  newsletter: [brief note if different from base voice]
aspirational_notes: [brief note from Q4, marked as aspirational not current]
---VOICE-PROFILE-END---
```

Confidence thresholds:
- HIGH: 3,000+ words, 2+ content types, no conflict flag
- MED: 1,500–3,000 words OR only 1 content type
- LOW: <1,500 words — warn user that voice matching may be approximate

---

## Save Prompt (after generation with voice applied)

After voice-matched content is delivered, ask:

```
Save this voice profile so I remember it next time?
I'll write it to .content-wand/brand-voice.json in this project.

→ Yes, save it
→ No, just use it this session
```

**If YES:**
- Create `.content-wand/` directory if it doesn't exist
- Write only approved schema keys (see brandvoice-schema.md)
- Never write: raw text samples, URL content, credentials, verbatim Q&A
- Notify: "Saved to .content-wand/brand-voice.json — you can delete this file anytime."

**If NO:** Use the profile this session only. Do not write any file.

---

## Fallback Behavior

| Situation | Response |
|-----------|---------|
| User skips Q1 entirely (no writing samples) | STOP. Ask once more: "I need at least one writing sample to accurately match your voice. Can you paste something you've written?" If still skipped: proceed with Q2–Q5 only; set `confidence: LOW`; note `no_samples: true` in profile |
| User provides < 500 words total from Q1 | Proceed after one gentle ask for more; set `confidence: LOW` |
| User abandons interview after Q1 only | Proceed with samples alone; set `confidence: LOW`; skip remaining questions |
| User abandons before Q1 | Do NOT generate a profile. Offer to restart or skip voice matching entirely |
| Q4 or Q5 skipped | Accept skip — these are explicitly optional |

---

## Schema Validation (READ mode)

On read, reject the file if:
- Any key is present that is not in the approved schema (see brandvoice-schema.md)
- `confidence` is missing
- `tone_axes` is missing or malformed
- File is empty or not valid JSON

On rejection: "Brand voice file appears corrupted. Want me to recreate it? (takes 2 min)"

---

## NOT Contract

Do NOT generate any content in this sub-skill.
Even if you have everything you need to write a LinkedIn post — do NOT write it.
Even if the voice profile suggests obvious content — do NOT generate content.
Do NOT store raw writing samples or URL-fetched text in the JSON file.
Do NOT ask brand voice questions before the first output is delivered.

Your job ends when the `---VOICE-PROFILE-END---` delimiter is written, or the JSON file is saved.
