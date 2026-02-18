# content-wand

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> A Claude skill that turns any content into platform-ready posts — or transforms it between formats — with optional brand voice matching.

You paste a blog post, drop a URL, or say "write about X." content-wand outputs platform-native content for up to 9 platforms. Each output passes a two-pass check: hard constraints first (character limits, link rules, format requirements), quality heuristics second (hook strength, CTA clarity, engagement design). It never guesses at your platform specs — they're kept current and loaded fresh each run.

---

## Two modes

**ATOMIZE** — One input, multiple platform outputs.

```
blog post → Twitter/X thread + LinkedIn post + Email newsletter
           + Instagram carousel + YouTube Shorts script + Podcast talking points
           + TikTok script + Threads post + Bluesky post
```

**REPURPOSE** — Transform between content types.

```
Podcast transcript   → Blog post
Twitter thread       → LinkedIn article
Rough notes          → Newsletter issue
Blog post            → Email course
Case study           → Template
Interview transcript → Twitter thread
```

REPURPOSE classifies transformation distance before writing: same-length restructure (DIRECT), long-to-short with idea selection (COMPRESS), short-to-long with structured expansion (EXPAND), or full type change (STRUCTURAL). Each gets different logic.

---

## 9 platforms

| Platform | What you get | Key constraint |
|----------|-------------|----------------|
| Twitter/X | Full thread — hook tweet + 4–8 body tweets | 280 chars/tweet; external links go in reply, not body |
| LinkedIn | Long-form post with structured line breaks | 3,000 chars; no Markdown rendering; hook in first 210 chars |
| Email newsletter | Subject line + full issue body | Subject ≤50 chars; single goal per email; max 2 CTAs |
| Instagram | Carousel script — slide-by-slide text + CTA | 3–20 slides; slide 1 = scroll-stopping hook |
| YouTube Shorts | Timed script with visual direction notes | ≤45s spoken; hook in first 3 seconds |
| Podcast | Talking point bullets (not a script) | Keyword cues only; CTA section scripted verbatim |
| TikTok | Script starting mid-action, no intro | Hook in first 2 seconds; searchable language throughout |
| Threads | Standalone post or reply-chain thread | ≤500 chars/post; written for conversation |
| Bluesky | Post or reply-chain thread | ≤300 chars; direct links encouraged; intellectual tone |

Platform specs include current algorithm signals (engagement weighting, reach penalties, format preferences) updated February 2026. The skill flags when specs may be stale and prompts a refresh.

---

## Works with any input

| Input | Example | What happens |
|-------|---------|-------------|
| Pasted text | Blog post, essay, rough draft | Classified and processed directly |
| URL | Article, tweet, landing page | Fetched, extracted, classified |
| Transcript | Podcast, video, interview recording | Re-ordered from non-linear structure; key themes extracted |
| Notes | Bullet points, fragments, braindump | Core concept identified; gaps surfaced if too sparse |
| Topic | "why cold email open rates are falling" | 3–5 WebSearch queries run; content synthesized |

---

## Brand voice (optional)

First run always generates in a clean, neutral voice. After output, content-wand offers to learn yours.

A 5-question interview takes about 2 minutes. Question 1 — writing samples — carries 70% of the profile weight. Confidence scores as HIGH (≥3,000 sample words across ≥2 content types), MED, or LOW (<1,500 words). Low-confidence profiles are flagged and applied conservatively.

The profile saves to `.content-wand/brand-voice.json` in your project. It stores extracted style patterns only — tone axes on a 0.0–1.0 scale, sentence style, vocabulary level, opening patterns, structural patterns, and platform-specific notes. It never stores your raw writing, fetched URLs, or any personal data.

To reset: delete `.content-wand/brand-voice.json`.

Add to your project's `.gitignore`:
```
.content-wand/
```

---

## Installation

```bash
# Claude Code
git clone https://github.com/baagad-ai/content-wand ~/.claude/skills/content-wand

# Codex CLI
git clone https://github.com/baagad-ai/content-wand ~/.codex/skills/content-wand
```

No dependencies. No build step. Clone and use.

---

## Usage

```
/content-wand [content, URL, or description]
```

Works with natural language — describe what you want:

```
/content-wand atomize this article for Twitter and LinkedIn: [paste]

/content-wand https://example.com/article → newsletter and podcast notes

/content-wand repurpose this transcript into a blog post: [paste]

/content-wand write about "why most productivity systems fail" → TikTok script

/content-wand turn my rough notes into a LinkedIn post: [paste]
```

You can also just describe intent directly to Claude:

> "Turn this podcast transcript into a Twitter thread and email newsletter"
> "Take my rough notes and make a LinkedIn post"
> "Repurpose this YouTube transcript into a blog post and TikTok script"

---

## How it works

content-wand is an orchestrated Claude skill — one entry point, four specialized sub-skills, two reference files:

```
content-wand (SKILL.md)
│
├── content-ingester          Classifies input, fetches URLs, runs WebSearch for topics
├── brand-voice-extractor     Reads or builds voice profile; flags low-confidence
├── repurpose-transformer     Classifies transformation distance; applies DIRECT/COMPRESS/EXPAND/STRUCTURAL logic
├── platform-writer           Generates output; 2-pass validation per platform
│
└── references/
    ├── platform-specs.md     Hard constraints + algorithm signals, 9 platforms, Feb 2026
    ├── brandvoice-schema.md  Brand voice JSON schema + validation rules + migration rules
    └── platform-writer-guide.md  Hook framework + quality anti-patterns
```

**Design decisions worth knowing:**

- Routing instructions load in the first 50 lines of SKILL.md to counter attention degradation in long contexts ("Lost in the Middle" — MIT/TACL 2024)
- Platform specs load once before generation, not per-platform — prevents redundant token use in multi-platform runs
- Brand voice is never a gate — first output always runs without it; setup is offered after
- All sub-skills communicate via structured delimiter blocks (`---BLOCK-NAME-START---`) to prevent cross-skill ambiguity
- Every NOT contract names specific rationalizations Claude might use, not just states prohibitions

---

## Files in this repo

| File | Purpose |
|------|---------|
| `SKILL.md` | Orchestrator — entry point, mode detection, routing |
| `content-ingester-SKILL.md` | Input classification + URL fetch + topic research |
| `brand-voice-extractor-SKILL.md` | Voice profile read/write/interview |
| `platform-writer-SKILL.md` | Platform-native generation with 2-pass validation |
| `repurpose-transformer-SKILL.md` | Type-to-type transformation with distance classification |
| `references/platform-specs.md` | Platform constraints + algorithm signals (Feb 2026) |
| `references/brandvoice-schema.md` | Brand voice JSON schema + validation rules |
| `references/platform-writer-guide.md` | Hook framework + pre-generation checks |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — platform spec updates, new platform support, edge case handling, and NOT contract improvements are all welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the skill file conventions before opening a PR.

---

## Author

Prajwal Mishra — [@baagad_ai](https://x.com/baagad_ai)

---

## License

MIT — see [LICENSE](LICENSE).
