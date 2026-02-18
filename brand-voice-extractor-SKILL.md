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

If brandvoice-schema.md is not found: proceed with built-in schema knowledge
(required keys: confidence, tone_axes, sentence_style). Note:
"Schema file missing — using built-in validation rules."

1. Read `.content-wand/brand-voice.json`
2. Validate schema: reject any key not in the approved schema (see brandvoice-schema.md)
3. If validation fails: notify user, offer to recreate. Do NOT proceed with corrupted data.
4. Output the `---VOICE-PROFILE---` block

**Staleness check:** After outputting the VOICE-PROFILE block, check `updated_at`
in the JSON:
- If updated_at > 6 months ago: add to the VOICE-PROFILE block a field:
  staleness_flag: true, months_old: [N]
- If < 6 months: proceed silently. Do not add staleness_flag.
(The orchestrator uses staleness_flag to offer an update after voice-matched delivery.)

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

**Deriving the base profile when platform variance is high (>0.4 difference on any
tone_axis between platforms):** Set the base profile to the platform where the most
Q1 samples were provided. If equal, use the "writing for yourself" platform
(newsletter, Substack, personal tweets rather than company LinkedIn). Note this in
the output block as: `base_derived_from: [platform]`.

---

## SETUP Mode — The Mini-Interview

**Do NOT load** `references/platform-specs.md` or `references/brandvoice-schema.md` during the interview phase — the orchestrator handles file saving after profile delivery.

Maximum 5 questions. Ask them one at a time. Do not rush.

Frame at start: "Let's capture your voice — takes about 5 minutes, works forever after.
The more you share, the better I match you."

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

2b. Detect voice transition: If Q3 self-description aligns with Q4 aspirational model
but conflicts with Q1 samples: this may indicate the user is actively evolving their
voice. In the profile: set conflict_flag: true and add to aspirational_notes:
"User appears to be transitioning toward [Q3 description]. Current samples reflect
previous/current style. Voice profile extracted from samples; consider updating
profile after 3–6 months of new content."

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

Your job ends when the `---VOICE-PROFILE-END---` delimiter is written.
File saving and the save prompt are handled by the orchestrator (SKILL.md Step 7).
Do NOT offer to save the voice profile — that is the orchestrator's responsibility.

**When the orchestrator saves brand-voice.json:** Only approved schema keys may be
written (see brandvoice-schema.md). Never write: raw text samples, URL content,
credentials, verbatim Q&A. File permissions should be 600 (user-only).

---

## NEVER — Sample Collection Anti-Patterns

These will corrupt the voice profile if not caught:

- **NEVER accept a corporate bio or LinkedIn About section as a writing sample.** These are crafted for impression management, not authentic voice. They actively poison extraction — the voice is aspirational, not real. If a user offers one: "That's great for context, but I need something you wrote for yourself — a tweet thread, a newsletter, or even an email to a friend. Those reveal your actual voice."

- **NEVER accept a heavily edited or ghostwritten piece.** If the user says "my PR team helped with this" or "this was for our company blog" — do NOT use it as a sample. Ask for something they wrote and published without editing assistance.

- **NEVER treat platform inconsistency as a problem.** A person who sounds casual on Twitter and formal on LinkedIn does not have a confused voice — they have a sophisticated voice. Extract both and encode as `platform_variants`.

- **NEVER extract voice from samples that are responses to someone else.** Reply tweets, comment threads, and response emails are reactive — they mirror the other person's style. Use only original, initiated pieces.

- **NEVER use the aspirational model (Q4) as voice training data.** "I wish I'd written that" is an explicit signal that it's NOT their current voice. Q4 is informational — it goes in `aspirational_notes` only.
