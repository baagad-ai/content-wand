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
completely. This defines: (1) approved keys for validation, (2) rejection rules,
(3) confidence scoring criteria, and (4) schema migration rules for older versions.
**Do NOT load** `references/platform-specs.md` for this task.

1. Read `.content-wand/brand-voice.json`
2. Validate schema: reject any key not in the approved schema (see brandvoice-schema.md)
3. If validation fails: notify user, offer to recreate. Do NOT proceed with corrupted data.
4. Output the `---VOICE-PROFILE---` block

---

## Voice Authenticity Framework

Before running the mini-interview, understand what you're trying to capture:

**Authentic voice** = the patterns that appear consistently when the writer is writing for THEMSELVES — not for a job application, not for a press release, not to impress anyone.

**Aspirational voice** = the patterns the writer WISHES they had — often more formal, more polished, more "professional" than their natural writing.

The interview is designed to surface authentic voice. But users will often offer aspirational artifacts:
- LinkedIn About sections → aspirational (crafted for impression management)
- Corporate bios → aspirational (written for credibility)
- Published articles with heavy editing → may be authentic if self-published; not if professionally edited
- Personal tweets, newsletters, Substack posts, unedited emails → most authentic

Your job is to extract what they actually sound like, not what they wish they sound like. When in conflict, authentic wins.

**Cross-platform variance is signal, not noise:**
A person who writes casually on Twitter and formally on LinkedIn doesn't have an inconsistent voice — they have a sophisticated voice that adapts. Capture the variance in `platform_variants`, not the average. The problem is only when the user says they're "casual" but ALL samples are formal.

---

## SETUP Mode — The Mini-Interview

**Do NOT load** `references/platform-specs.md` or `references/brandvoice-schema.md` during the interview phase — only load `references/brandvoice-schema.md` when writing the final JSON file (at Save Prompt).

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
  instagram: [brief note if different from base voice]
  youtube-shorts: [brief note if different from base voice]
  tiktok: [brief note if different from base voice]
  threads: [brief note if different from base voice]
  bluesky: [brief note if different from base voice]
  podcast: [brief note if different from base voice]
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

**Voice profile staleness:**
Voice evolves. A profile captured 6+ months ago may no longer match the user's current writing style, especially after a platform shift, audience change, or deliberate style evolution.

When loading a saved profile (READ mode), check `updated_at` in the JSON:
- If `updated_at` > 6 months ago: after applying voice, offer: "Your voice profile is [N] months old. Want to update it? (takes 2 min)"
- If < 6 months: proceed silently.

This offer is ALWAYS post-generation — never a gate before generating.

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

---

## NEVER — Sample Collection Anti-Patterns

These will corrupt the voice profile if not caught:

- **NEVER accept a corporate bio or LinkedIn About section as a writing sample.** These are crafted for impression management, not authentic voice. They actively poison extraction — the voice is aspirational, not real. If a user offers one: "That's great for context, but I need something you wrote for yourself — a tweet thread, a newsletter, or even an email to a friend. Those reveal your actual voice."

- **NEVER accept a heavily edited or ghostwritten piece.** If the user says "my PR team helped with this" or "this was for our company blog" — do NOT use it as a sample. Ask for something they wrote and published without editing assistance.

- **NEVER treat platform inconsistency as a problem.** A person who sounds casual on Twitter and formal on LinkedIn does not have a confused voice — they have a sophisticated voice. Extract both and encode as `platform_variants`.

- **NEVER extract voice from samples that are responses to someone else.** Reply tweets, comment threads, and response emails are reactive — they mirror the other person's style. Use only original, initiated pieces.

- **NEVER use the aspirational model (Q4) as voice training data.** "I wish I'd written that" is an explicit signal that it's NOT their current voice. Q4 is informational — it goes in `aspirational_notes` only.
