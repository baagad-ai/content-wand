# content-wand Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete content-wand agent skill that atomizes or repurposes any content into platform-native formats with optional brand voice matching.

**Architecture:** Main SKILL.md orchestrator (≤100 active lines, top-loaded) routes to 4 sub-skills: content-ingester (input handling), brand-voice-extractor (optional voice DNA), platform-writer (format generation with hard validation + quality heuristics), repurpose-transformer (type-to-type transformation). Two on-demand reference files: platform-specs.md and brandvoice-schema.md.

**Tech Stack:** SKILL.md (YAML frontmatter + Markdown instructions), structured handoff blocks (markdown delimiters), JSON schema for brand voice, WebFetch/WebSearch tools for URL ingestion and research.

**Critical Design Constraints (from 2-round audit, 17 findings, 65+ sources):**
- "Lost in the Middle" (MIT/TACL 2024): routing instructions MUST be in lines 1–50 of SKILL.md
- NOT contracts must preempt specific rationalizations, not just state prohibitions
- Structured handoff blocks (`---BLOCK-START---`) prevent inter-sub-skill ambiguity
- Brand voice: generate first, offer voice setup AFTER — never gate first output
- Brand voice interview: 5 questions max, samples-first (70% weight), no binary toggles
- `.brandvoice.json` is opt-in only; stored at `.content-wand/brand-voice.json`; schema-validated on read; never stores raw URL content
- Platform specs = hard constraints + quality heuristics (compliance ≠ quality)
- 7 edge cases explicitly handled (see Task 2)

---

## Task 1: Write `SKILL.md` — The Orchestrator

**Files:**
- Modify: `SKILL.md` (replace stub)

**Spec:** The main orchestrator. Maximum 100 active instruction lines. Routing logic on lines 1–50. Sub-skill invocation on lines 51–80. Fallback matrix on lines 81–100. Reference material only below line 100.

**Step 1: Replace SKILL.md stub with full orchestrator**

Write the following complete content to `SKILL.md`:

```markdown
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

All sub-skills communicate via structured blocks. Never interpret prose as handoff.

- **Input to content-ingester:** Raw user input (any format)
- **Output from content-ingester:** `---CONTENT-OBJECT-START---` ... `---CONTENT-OBJECT-END---`
- **Input to platform-writer:** `---CONTENT-OBJECT-START---` block + platform list + voice profile or `VOICE-PROFILE: none`
- **Output from platform-writer:** `---PLATFORM-OUTPUT-START---` ... `---PLATFORM-OUTPUT-END---` (one per platform)
- **Input to repurpose-transformer:** `---CONTENT-OBJECT-START---` block + `target_type:` + voice profile or `VOICE-PROFILE: none`
- **Output from repurpose-transformer:** `---TRANSFORMED-CONTENT-START---` ... `---TRANSFORMED-CONTENT-END---`
- **Input/output brand-voice-extractor:** `---VOICE-PROFILE-START---` ... `---VOICE-PROFILE-END---`
```

**Step 2: Verify structure**

Read the file and confirm:
- YAML frontmatter is valid (no unquoted colons in description)
- Routing table appears before line 50
- Sub-skill invocations appear before line 80
- Edge case table appears before line 100
- Total active instruction lines ≤ 100

**Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat: add content-wand orchestrator SKILL.md with top-loaded routing"
```

---

## Task 2: Write `content-ingester-SKILL.md`

**Files:**
- Modify: `content-ingester-SKILL.md` (replace stub)

**Spec:** Handles all input types. Fetches URLs. Runs WebSearch for topic-only inputs. Returns a structured ContentObject block. Strict NOT contract: never transforms, summarizes, or expands — only extracts.

**Step 1: Replace stub with full sub-skill**

```markdown
---
name: content-ingester
description: Use when content-wand needs to ingest raw input of any type (pasted text, URL, transcript, rough notes, or topic idea) and return a structured ContentObject for downstream processing.
---

# content-ingester

## Overview

Ingests any content signal and returns a structured ContentObject. That is the entire job.

**Core principle:** Extract, do not transform. Your output is raw material for other sub-skills. Never improve, summarize, or restructure the input.

---

## Input Classification

Classify the input before processing:

| Input Type | Signals | Action |
|-----------|---------|--------|
| `paste` | Plain text provided directly | Use as-is |
| `url` | Starts with http/https | Fetch via WebFetch tool |
| `transcript` | Contains timestamps, speaker labels, or "[inaudible]" | Use as-is; note it's a transcript |
| `notes` | Bullet points, fragments, incomplete sentences | Use as-is; note it's rough notes |
| `topic` | No content, just a subject/question | Run WebSearch (3–5 queries); assemble findings |

---

## Processing Rules

**For `url` input:**
1. Use WebFetch to retrieve the content
2. If 403/401/paywall response: STOP. Output `fetch_status: failed`. Do NOT proceed with HTML.
3. If redirect to login page: STOP. Output `fetch_status: login-required`.
4. If successful: extract the main body text only (strip nav, ads, footers)

**For `topic` input:**
1. Run 3–5 WebSearch queries to gather relevant information
2. Note all sources used
3. Assemble findings into raw text
4. Output `source_type: topic` with `sources_used: [list]`

**For all inputs:**
- Count words after extraction
- Identify 3 key themes (surface-level — do NOT editorialize)
- If word count < 100: include warning in output block
- If word count > 8,000: note this; do NOT truncate — pass full text

---

## Output Format

Output EXACTLY this block and nothing else after processing:

```
---CONTENT-OBJECT-START---
source_type: [paste|url|transcript|notes|topic]
word_count: [N]
fetch_status: [ok|failed|login-required]  (url only; omit for other types)
sources_used: [url1, url2, ...]  (topic only; omit for other types)
warnings: [list any: short-input, very-long-input, transcript-detected]
key_themes: [theme1, theme2, theme3]
raw_text:
[full extracted text — do not truncate, do not modify]
---CONTENT-OBJECT-END---
```

---

## NOT Contract

Do NOT transform, improve, clean up, summarize, or expand the input.
Even if the input is rough, incomplete, or unclear — do NOT restructure it.
Even if the content seems too short to be useful — do NOT add to it.
Even if you could write a better version — that is NOT your job.

Your job ends when the `---CONTENT-OBJECT-END---` delimiter is written.
The next sub-skill handles transformation.

---

## Fallback Behavior

| Failure | Response |
|---------|---------|
| URL fetch fails (403) | Output block with `fetch_status: failed`; add to warnings |
| URL is behind login | Output block with `fetch_status: login-required`; add to warnings |
| Topic search returns irrelevant results | Proceed with what was found; add `low-confidence-research` to warnings |
| Input is empty | Do NOT proceed. Ask user: "What content should I work with?" |
```

**Step 2: Verify the NOT contract is specific**

Read the file. Confirm the NOT contract section names at least 4 specific rationalizations Claude might use to justify transforming content.

**Step 3: Commit**

```bash
git add content-ingester-SKILL.md
git commit -m "feat: add content-ingester sub-skill with strict NOT contract"
```

---

## Task 3: Write `brand-voice-extractor-SKILL.md`

**Files:**
- Modify: `brand-voice-extractor-SKILL.md` (replace stub)

**Spec:** Two paths — READ existing profile, or SETUP via 5-question samples-first interview. Samples weighted 70% over self-report (30%). Max 5 questions (research-confirmed ceiling before abandonment spikes). Opt-in file save. Security: never store raw URL content, validate schema on read.

**Step 1: Replace stub with full sub-skill**

```markdown
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
```

**Step 2: Verify security constraints**

Read the file and confirm:
- "Never write raw URL content" appears explicitly
- Schema validation rejects unknown keys
- Save is explicitly opt-in (user must say Yes)
- File is written to `.content-wand/brand-voice.json` (not project root)

**Step 3: Commit**

```bash
git add brand-voice-extractor-SKILL.md
git commit -m "feat: add brand-voice-extractor with samples-first interview and opt-in save"
```

---

## Task 4: Write `platform-writer-SKILL.md`

**Files:**
- Modify: `platform-writer-SKILL.md` (replace stub)

**Spec:** Generates platform-native content. Two-pass validation: (1) hard constraint compliance, (2) quality heuristics. References `references/platform-specs.md` for specs. Emits status at start of each format. Strict NOT contract: never ingests or fetches content.

**Step 1: Replace stub with full sub-skill**

```markdown
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
2. Load the platform's hard constraints from `references/platform-specs.md`
3. Generate content applying the ContentObject + voice profile (if provided)
4. Run compliance check (Pass 1)
5. Run quality check (Pass 2)
6. Output the `---PLATFORM-OUTPUT---` block

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
```

**Step 2: Verify quality heuristics are present for all 6 platforms**

Read the file. Confirm each platform (Twitter, LinkedIn, newsletter, Instagram, YouTube Shorts, podcast) has both a compliance section AND a quality heuristics section.

**Step 3: Commit**

```bash
git add platform-writer-SKILL.md
git commit -m "feat: add platform-writer with 2-pass validation (compliance + quality heuristics)"
```

---

## Task 5: Write `repurpose-transformer-SKILL.md`

**Files:**
- Modify: `repurpose-transformer-SKILL.md` (replace stub)

**Spec:** Handles type-to-type content transformation. Classifies transformation distance (direct/compress/expand/structural). Applies different logic per class. Strict NOT contract: never applies platform formatting.

**Step 1: Replace stub with full sub-skill**

```markdown
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
```

**Step 2: Verify all 4 distance classes have explicit logic**

Read the file. Confirm DIRECT, COMPRESS, EXPAND, and STRUCTURAL each have specific handling instructions. Confirm the NOT contract names platform formatting as the specific prohibited action.

**Step 3: Commit**

```bash
git add repurpose-transformer-SKILL.md
git commit -m "feat: add repurpose-transformer with 4-class distance logic"
```

---

## Task 6: Write `references/platform-specs.md`

**Files:**
- Modify: `references/platform-specs.md` (replace stub)

**Spec:** Comprehensive hard constraints for all 6 platforms. Loaded on-demand by platform-writer. Must include: character limits, formatting rules, algorithm signals, link rules, quality heuristics, and 2026-current data.

**Step 1: Replace stub with full reference file**

Write the following complete content:

```markdown
# Platform Specifications — 2026 Current

> Loaded on-demand by platform-writer. All specs verified as of February 2026.
> Hard constraints = FAIL if violated. Quality signals = WARN if failing.

---

## Twitter / X

### Hard Constraints
- **Character limit:** 280 per tweet (standard); 25,000 (X Premium long-form post)
- **Thread length:** 3–10 tweets for most content (threads 3x engagement vs. single tweets)
- **External links:** NON-PREMIUM ACCOUNTS: posting external links = near-zero median engagement since March 2026. Links suppressed 50–90% by algorithm. Link placement rule: put URL in a REPLY to tweet 1, NOT in the thread body.
- **Images/media:** Include when possible — media tweets outperform text-only

### Algorithm Signals (2026)
- Replies: 13.5x weight
- Retweets: 20x weight
- Bookmarks: 10x weight
- Likes: 1x weight
- Premium accounts: 2x–4x reach boost
- Recency: top-tier ranking signal — engagement window is hours, not days
- Positive/constructive tone: boosted
- Combative/negative tone: suppressed even with high engagement

### Quality Heuristics
- Tweet 1 must contain: curiosity gap, bold claim, or outcome-first hook
- Test: would tweet 1 get engagement as a standalone post?
- Final tweet: must close the loop / deliver the payoff
- Optimal tweet 1 length: 70–100 characters for maximum interaction rate
- Avoid: "🧵 Thread:" as the opener (overused, no hook value)

---

## LinkedIn

### Hard Constraints
- **Post character limit:** 3,000 characters
- **Visible before "see more":** ~210–220 characters — THIS IS YOUR HOOK ZONE
- **NO native markdown:** `**bold**` renders as literal asterisks. Use Unicode bold if emphasis needed.
- **No headers** with `#` syntax — renders as plain text with the `#` symbol
- **Hashtags:** Count toward character limit (including `#` symbol)
- **Maximum CTAs:** 1 primary
- **Carousel format:** PDF upload only; technical max 300 slides; practical sweet spot: 8–15 slides
- **Carousel dimensions:** 1080×1080px (1:1) or 1080×1350px (4:5)
- **Carousel aspect ratio:** Must be consistent across all slides

### Algorithm Signals (2026)
- Dwell time and saves are high-weight signals
- Native content outperforms external link posts
- First-hour engagement gates wider distribution
- Carousels drive 3× more reach than standard text posts for educational content
- Polls and "ask a question" posts get high early engagement

### Quality Heuristics
- Hook must be in first 210 characters (before "see more" truncation)
- Single-sentence paragraphs dominate high-performing LinkedIn posts
- Short paragraphs (1–3 sentences) with line breaks between each
- One primary CTA — placed at the end of the post
- Avoid: corporate speak, passive voice, hollow openers ("I'm excited to share...")
- High-performing openers: bold statement, contrarian claim, specific data point, personal story

---

## Email Newsletter

### Hard Constraints
- **Subject line:** 30–50 characters; max 7 words
- **Preheader text:** Should complement subject line, not repeat it; can contain secondary CTA
- **Maximum CTAs:** 2 (1 primary above fold + 1 repeat at end) — never more
- **Single goal:** One primary CTA per email
- **Mobile-first:** Single-column layout; minimum 44px touch targets

### Structure (Standard)
1. Header/branding
2. Hook/opener (3–5 sentences — get to the point)
3. Main content block
4. Supporting section (optional)
5. Primary CTA (button format: 45% higher CTR than text links)
6. Footer with unsubscribe

### Quality Heuristics
- Subject line must contain an action verb
- CTA above fold for low-commitment actions; below fold after narrative build for complex offers
- High-converting subject line patterns: number + outcome ("3 ways to..."), curiosity gap, urgency (genuine only)
- Avoid: "checking in", "following up", spam trigger phrases (free, guaranteed, act now)
- Pre-flight check: does reading the first 2 sentences tell you exactly what this email is about?

---

## Instagram Carousel

### Hard Constraints
- **Maximum slides:** 20 (expanded from previous 10-slide limit)
- **Optimal slide count:** 8–10 slides (2.07% engagement rate at 10 slides)
- **Average carousel engagement:** 1.92% (vs. 0.50% Reels, 0.45% single images)
- **Caption limit:** 2,200 characters technical; ~125 characters visible before truncation
- **Square format:** 1080×1080px (1:1)
- **Portrait format:** 1080×1350px (4:5)
- **Aspect ratio lock:** First slide's ratio applies to ALL slides — cannot mix
- **Text overlay limit:** Max 20% of any slide should be text
- **Video slide limit:** 60 seconds; 4GB max

### Structure
- **Slide 1:** Hook — must stop the scroll. Bold claim, striking visual direction, or strong question.
- **Slides 2–N-1:** Body — each slide earns the next swipe. Cliffhanger or incomplete thought at the end of each slide.
- **Final slide:** CTA — clear and specific. For 10-slide carousels: CTA at end only. For 20-slide: CTA mid-carousel AND at end.

### Quality Heuristics
- First slide determines ~80% of carousel performance
- Each slide: 1 headline + max 3 lines of body
- Swipe-cliffhanger pattern: "But there's one more thing..." / "Until slide 5 changed everything..."
- Algorithm rewards swipe completions heavily — engineer for completion, not just slide 1
- Consistent visual style (same fonts, colors, layout) across all slides

---

## YouTube Shorts

### Hard Constraints
- **Maximum length:** 60 seconds
- **Optimal retention length:** 20–45 seconds (entertainment: 15–30s; educational: 35–45s)
- **Aspect ratio:** 9:16 (vertical only)
- **Hook window:** First 3 seconds critical — 50–60% of drop-off happens here
- **Target retention past 3 seconds:** >70%
- **Captions:** Burned-in captions increase retention 15–25% — note this in script

### Script Structure
```
HOOK (0–5 seconds): [Bold claim, curiosity gap, or outcome-first in ≤ 10 words]
BODY (5 sec to near-end): [Build — deliver on the hook's promise]
PAYOFF (final seconds): [Resolution that makes watching worth it]
```

### Quality Heuristics
- Hook must be stated in the first 5 words of the script
- Visual direction note: every 2–4 seconds ("cut to:", "show:", "text overlay:")
- End with a payoff — not a "like and subscribe" — that serves the viewer
- High-performing hook categories:
  - Curiosity gap: "Most people don't know this about [X]"
  - Bold claim: "This changed everything about how I [do X]"
  - Outcome-first: Show result in frame 1, explain how
  - Pattern interrupt: Unexpected visual or statement

---

## Podcast Talking Points

### Hard Constraints
- **Format:** Bullet KEYWORDS only — NOT full sentences. Full sentences cause scripted delivery; keywords allow natural speech.
- **CTA section:** The ONLY verbatim scripted section. Write CTA word-for-word.
- **Hook discipline:** Episode point must be stated within 60 seconds of the outline. Test by reading aloud.
- **Segment timing:** Write target time for each segment. Read aloud with a timer to verify.

### Structure by Episode Length
| Length | Talking Points | Segment Structure |
|--------|---------------|-------------------|
| 10–15 min | 2–3 strong points | Intro (30s) + 2–3 segments (3–5 min each) + Outro (1 min) |
| 20–40 min | 4–6 points | Intro (30s) + segments (5–8 min each) + Recap + Outro |
| 60+ min | 6–8 points | Must include explicit chapter/segment breaks + pacing variation |

### Quality Heuristics
- Transitions between segments must be explicitly noted ("TRANSITION: bridge line")
- Interview question structure: 4–6 questions; first 2 must be open-ended; rest cued from answers
- Segment boundaries: each should have a clear entry and exit point noted
- CTA timing: place at natural pause point — after a segment, before the next, never mid-thought
```

**Step 2: Verify all 6 platforms are present with both hard constraints AND quality heuristics**

**Step 3: Commit**

```bash
git add references/platform-specs.md
git commit -m "feat: add platform-specs reference with 2026-current constraints and quality heuristics"
```

---

## Task 7: Write `references/brandvoice-schema.md`

**Files:**
- Modify: `references/brandvoice-schema.md` (replace stub)

**Spec:** Defines the `.content-wand/brand-voice.json` schema. Security constraints. Confidence scoring rubric. Update cadence guide. What is NEVER stored.

**Step 1: Replace stub with full reference file**

```markdown
# Brand Voice Schema Reference

> Defines the exact structure of `.content-wand/brand-voice.json`.
> Read by brand-voice-extractor on every load. Reject any file with unknown keys.

---

## Approved JSON Schema

```json
{
  "schema_version": "1.0",
  "created_at": "ISO-8601 date",
  "updated_at": "ISO-8601 date",
  "confidence": "HIGH | MED | LOW",
  "sample_word_count": 0,
  "conflict_flag": false,
  "tone_axes": {
    "formal_casual": 0.5,
    "serious_playful": 0.5,
    "expert_accessible": 0.5,
    "direct_narrative": 0.5
  },
  "sentence_style": "short-punchy | medium-varied | long-flowing",
  "vocabulary": "everyday | precise | technical | elevated",
  "opening_patterns": ["string", "string"],
  "structural_patterns": ["string", "string"],
  "taboo_patterns": ["string", "string"],
  "platform_variants": {
    "twitter": "brief note or null",
    "linkedin": "brief note or null",
    "newsletter": "brief note or null",
    "instagram": "brief note or null",
    "youtube-shorts": "brief note or null",
    "podcast": "brief note or null"
  },
  "aspirational_notes": "string or null"
}
```

---

## Confidence Scoring Rubric

| Level | Criteria |
|-------|---------|
| HIGH | ≥3,000 words of samples; ≥2 content types represented; no conflict flag |
| MED | 1,500–3,000 words OR only 1 content type; OR conflict flag is true |
| LOW | <1,500 words — outputs will be approximate; recommend adding more samples |

---

## Security Constraints — NEVER Store

The following must NEVER appear in `brand-voice.json`:
- Raw text of writing samples provided by the user
- Content fetched from URLs (only extracted patterns)
- API keys, passwords, or credentials of any kind
- Personal contact information (email, phone, address)
- Full sentences that could reconstruct the user's original content

If any of these are detected during schema validation: reject the file entirely and offer to recreate.

---

## File Location

Always: `.content-wand/brand-voice.json` relative to the current project directory.

NEVER:
- Home directory (`~/.brandvoice.json`)
- System directories
- Alongside API key files or `.env` files

The `.content-wand/` directory should be added to `.gitignore` by the user if they work in a version-controlled project.

---

## Update Cadence

The brand voice profile should be refreshed:
- After a significant shift in writing style (new audience, new platform, rebranding)
- If outputs consistently don't feel "right" despite having a profile
- At minimum: review every 6 months

To update: delete `.content-wand/brand-voice.json` and run content-wand — it will offer to recreate the profile automatically.

---

## Schema Validation Rules

On load, reject the file if ANY of:
- Missing required keys: `schema_version`, `confidence`, `tone_axes`
- Unknown keys present (not in the approved schema above)
- `tone_axes` values outside 0.0–1.0 range
- File is empty, not valid JSON, or binary
- `schema_version` is not "1.0"

On rejection: notify user and offer to recreate. Do not attempt to repair the file automatically.
```

**Step 2: Verify security constraints section explicitly lists all prohibited content types**

**Step 3: Commit**

```bash
git add references/brandvoice-schema.md
git commit -m "feat: add brandvoice-schema reference with security constraints and validation rules"
```

---

## Task 8: Final Commit — README and Scaffold

**Files:**
- All remaining scaffold files already created

**Step 1: Stage and commit all scaffold files**

```bash
git add README.md CHANGELOG.md LICENSE .gitignore package.json docs/
git commit -m "chore: add repo scaffold (README, package.json, LICENSE, CHANGELOG)"
```

**Step 2: Verify repo structure**

```bash
ls -la /Users/prajwalmishra/Desktop/Experiments/skills/content-wand-github/
```

Expected structure:
```
.git/
.github/
.gitignore
CHANGELOG.md
LICENSE
README.md
SKILL.md
brand-voice-extractor-SKILL.md
content-ingester-SKILL.md
docs/
  plans/
    2026-02-18-content-wand.md
package.json
platform-writer-SKILL.md
references/
  brandvoice-schema.md
  platform-specs.md
repurpose-transformer-SKILL.md
```

**Step 3: Verify git log**

```bash
git log --oneline
```

Expected: 6 commits (scaffold + 5 skill files).

---

## Task 9: Test the Skill — Baseline Scenarios

Per the writing-skills skill TDD methodology: run test scenarios to verify the skill files are complete and internally consistent. These are documentation tests, not code tests.

**Test Scenario 1 — ATOMIZE, no brand voice:**
> User: "Turn this blog post intro into a Twitter thread and LinkedIn post: [paste 300 words]"

Expected orchestrator behavior:
1. Detects ATOMIZE mode (platform names present)
2. Confirms platforms: Twitter/X + LinkedIn
3. Invokes content-ingester → gets ContentObject
4. Invokes platform-writer with `VOICE-PROFILE: none`
5. Outputs both formats with compliance + quality checks
6. Saves files to `content-output/`
7. Offers brand voice setup AFTER output

Verify: platform-writer output includes `compliance: pass` and `quality_flags:` section for both platforms.

**Test Scenario 2 — REPURPOSE:**
> User: "Repurpose this podcast transcript as a blog post" [paste 2,000-word transcript]

Expected:
1. Detects REPURPOSE mode
2. Invokes content-ingester → ContentObject with `source_type: transcript`
3. Invokes repurpose-transformer with `target_type: blog post`
4. Classifies distance: COMPRESS (long → structured)
5. Anchors to 3 strongest ideas
6. Outputs `---TRANSFORMED-CONTENT---` block
7. Offers brand voice after delivery

**Test Scenario 3 — URL input, brand voice setup:**
> User: "Turn this article into a LinkedIn post" + URL

Expected:
1. content-ingester fetches URL via WebFetch
2. Generates LinkedIn post
3. Offers brand voice setup
4. If user accepts: Q1 asks for samples (not vibe toggles)
5. After extraction: asks to save (opt-in)
6. Regenerates LinkedIn post with voice applied

**Test Scenario 4 — Edge case: corrupted brand voice file**
> User invokes with existing `.content-wand/brand-voice.json` that has unknown keys

Expected:
1. brand-voice-extractor reads file
2. Schema validation detects unknown keys
3. Rejects file with notification
4. Offers to recreate
5. Does NOT attempt to use corrupted data

**Step 1: Read through each SKILL.md file**

Verify each file:
- Has valid YAML frontmatter
- Has clear NOT contract
- Has explicit fallback behavior
- Uses structured handoff blocks correctly
- Has no markdown that would cause YAML parsing errors (quoted colons, etc.)

**Step 2: Verify handoff blocks are consistent across files**

The block delimiters must be identical across all files:
- `---CONTENT-OBJECT-START---` / `---CONTENT-OBJECT-END---`
- `---VOICE-PROFILE-START---` / `---VOICE-PROFILE-END---`
- `---PLATFORM-OUTPUT-START---` / `---PLATFORM-OUTPUT-END---`
- `---TRANSFORMED-CONTENT-START---` / `---TRANSFORMED-CONTENT-END---`

Check: search each SKILL.md file for these delimiters and verify spelling is consistent.

**Step 3: Final commit**

```bash
git add docs/plans/2026-02-18-content-wand.md
git commit -m "docs: add full implementation plan"
git log --oneline
```

---

## Execution Notes

**Token budget per task:**
- Task 1 (SKILL.md): ~1,500 tokens to write
- Task 2 (content-ingester): ~800 tokens
- Task 3 (brand-voice-extractor): ~1,500 tokens
- Task 4 (platform-writer): ~1,200 tokens
- Task 5 (repurpose-transformer): ~800 tokens
- Task 6 (platform-specs): ~2,000 tokens
- Task 7 (brandvoice-schema): ~600 tokens
- Task 8 (scaffold + verification): ~200 tokens
- Task 9 (testing): ~500 tokens

**Total estimated:** ~9,100 tokens across 9 tasks.

**Commit frequently.** Each task ends with a commit. This makes it easy to roll back if a sub-skill needs revision.

**Test in Claude Code after Task 9** by invoking `/content-wand [some content]` and observing whether Claude follows the routing logic correctly.
