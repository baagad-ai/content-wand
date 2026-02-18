# content-wand

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](CHANGELOG.md)
[![Claude Compatible](https://img.shields.io/badge/Claude-Code%20%7C%20Claude.ai-orange.svg)](https://claude.ai)
[![Last commit](https://img.shields.io/github/last-commit/baagad-ai/content-wand)](https://github.com/baagad-ai/content-wand/commits/main)

> Turn any content into platform-native formats — or transform between content types — with optional brand voice matching.

You have one piece of content. You need it on six platforms, each with its own character limits, algorithm signals, and hook patterns. Or you have a podcast transcript and need a newsletter. content-wand handles the transformation logic so you don't have to.

---

## Two modes

**ATOMIZE** — Take one piece of content and distribute it across platforms.

```text
One blog post → Twitter thread + LinkedIn post + Email newsletter + Instagram carousel + YouTube Shorts script + Podcast talking points
```

**REPURPOSE** — Transform between content types.

```text
Podcast transcript → Blog post
Twitter thread → LinkedIn article
Rough notes → Newsletter issue
Blog post → Email course
Case study → Template
```

---

## Platforms supported

| Platform | What you get | Character / format constraint |
|----------|-------------|-------------------------------|
| Twitter/X | Full thread (hook + 4–8 tweets) | 280 chars/tweet |
| LinkedIn | Long-form post | 3,000 char soft ceiling |
| Email newsletter | Full issue (subject + body) | Optimized for deliverability |
| Instagram | Carousel script (10 slides max) | Hook on slide 1 |
| YouTube Shorts | Script + hook | Under 60 sec spoken |
| Podcast | Talking points (not a script) | 5–7 key beats |
| TikTok | Script with SEO language | 150-char caption |
| Threads | Standalone post or thread | 500 chars/post |
| Bluesky | Post or thread | 300 chars/post |

---

## Works with any input

| Input | Example | What content-wand does |
|-------|---------|----------------------|
| Pasted text | Blog post, essay, article | Reads and classifies directly |
| URL | Article, tweet, page | Fetches and extracts key content |
| Transcript | Podcast, video, interview | Reorders non-linearly, extracts themes |
| Rough notes | Bullet points, fragments | Identifies the repurposable core |
| Topic idea | "best practices for cold email" | Researches with WebSearch, then writes |

---

## Optional: Brand Voice

On first use, content-wand generates content in a clean, generic voice.

After your first output, it offers a 5-question voice interview (~2 minutes). Answers are saved to `.content-wand/brand-voice.json` in your project — an opt-in, schema-validated file that stores only extracted style patterns, never raw content. All future runs in that project use your voice automatically.

To reset: delete `.content-wand/brand-voice.json`. That is it.

---

## Installation

```bash
# Claude Code (recommended)
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

**Examples:**

```
/content-wand atomize this article for Twitter and LinkedIn: [paste]

/content-wand repurpose my podcast transcript into a newsletter: [paste]

/content-wand https://example.com/article → all platforms

/content-wand write content about "why most productivity systems fail" → newsletter
```

Or describe naturally — Claude understands intent:

> "Turn this into a Twitter thread and email newsletter"
> "Take my rough notes and make a LinkedIn post"
> "Repurpose this YouTube transcript into a blog post"

---

## How it works

content-wand is an orchestrated Claude skill — one entry point, five specialized sub-skills:

```
content-wand (SKILL.md)
├── content-ingester       — classifies input, handles URLs and research
├── brand-voice-extractor  — reads or builds your voice profile
├── repurpose-transformer  — transforms content type-to-type (REPURPOSE mode)
├── platform-writer        — generates platform-native output with 2-pass validation
└── references/
    ├── platform-specs.md  — 2026 algorithm constraints for all 9 platforms
    └── brandvoice-schema.md — brand voice JSON schema and validation rules
```

Each sub-skill has a strict NOT contract — explicit prohibitions with named rationalizations that prevents Claude from taking well-meaning but wrong shortcuts.

Platform specs are loaded once before generation begins, not per-platform, to avoid redundant token use across multi-platform runs.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add platforms, update algorithm specs, or improve edge case handling. Read [docs/plans/](docs/plans/) for the architecture decisions behind the current design.

---

## License

MIT — see [LICENSE](LICENSE).

---

Made by [Prajwal Mishra](https://x.com/baagad_ai)
