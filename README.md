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

## In practice

Input — a rough note, pasted directly:

> Most productivity advice is wrong. Not because the tactics are bad — they're fine. But they optimize for the wrong constraint. You don't lack systems. You lack clarity on what actually matters. I spent 3 years optimizing my task manager before I realized I was organizing noise.

`/content-wand atomize for Twitter and LinkedIn`

---

**Twitter/X thread** — 6 tweets, all under 280 characters, no links in body

```
Most productivity advice optimizes for the wrong constraint.
You don't lack systems. You lack clarity on what actually matters.

---

I spent 3 years perfecting my task manager. Color-coded priorities.
Nested projects. Weekly reviews. The whole thing.

I was just organizing noise more efficiently.

---

The productivity industry sells systems because systems are sellable.
Clarity isn't. You can't charge $49/month for
"figure out what you actually want."

---

Here's the tell: if your task list has 40 items on it, you don't
have a productivity problem. You have a prioritization problem
disguised as a volume problem.

---

A full task manager feels like progress. It isn't. It's procrastination
with better aesthetics. The hard work is deciding what to delete —
not what app to put the rest in.

---

The question that changed how I work:
"If I could only finish 3 things this week and they had to matter,
what are they?"

That's it. That's the system.
```

---

**LinkedIn post** — 1,621 characters, no Markdown, hook within first 210 characters

```
Three years. That's how long I optimized my task manager before
realizing I was solving the wrong problem.

Not because the system was bad. The system was fine. I had
color-coded tags, recurring reviews, nested projects. It looked
impressive. It was just very organized noise.

Here's what most productivity advice gets wrong: it treats execution
as the bottleneck. So you get frameworks, apps, and templates — all
designed to help you do more, faster. But doing more faster is only
valuable if what you're doing matters.

The real constraint isn't systems. It's clarity.

When you don't know what actually matters, a better task manager
just gives you a more polished list of the wrong things to do.
You feel productive. You're not making progress.

The shift that helped me wasn't a new tool. It was a single,
uncomfortable constraint: if I could only finish three things this
week and they had to genuinely move something forward, what are they?

Everything else becomes noise the moment you answer that honestly.

→ Clarity first. Systems second.
→ Delete before you organize.
→ A shorter list you actually trust beats a complete list you avoid.

What's one thing on your list right now that you know, deep down,
shouldn't be there?
```

---

Both outputs pass compliance. The thread stays within 280 characters per tweet with no links in the body. The LinkedIn post uses no Markdown formatting and the hook lands within the first 210 characters.

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

## Built for

Solo creators, indie makers, and developer-writers who publish regularly across platforms. If you're writing blog posts, threads, newsletters, and scripts yourself — and spending more time reformatting than writing — this is for you.

If you have a content team with a CMS and a scheduling tool, you probably want something with a dashboard.

---

## Brand voice (optional)

After your first output, content-wand can learn your writing style — and remember it across every session, every platform. The same brief that produces neutral copy without a profile produces output that sounds distinctly like you with one.

First run always generates in a clean, neutral voice. After delivery, content-wand offers to set up your profile.

A 5-question interview takes ~5 minutes. Question 1 — writing samples — carries 70% of the profile weight. Confidence scores as HIGH (≥3,000 sample words across ≥2 content types), MED, or LOW (<1,500 words). Low-confidence profiles are flagged and applied conservatively.

The profile saves to `.content-wand/brand-voice.json` in your project. It stores extracted patterns only — tone axes, sentence style, vocabulary level, opening patterns, structural patterns, and platform-specific notes. Never your raw writing, fetched URLs, or personal data.

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

- **Routing loads first, not last.** All mode detection and routing logic appears in the first 50 lines of SKILL.md. LLMs follow mid-document instructions less reliably than early-document ones — a documented failure mode for long prompts ("Lost in the Middle" — MIT/TACL 2024). Position is architecture.

- **Platform specs load once, not per-platform.** In a 9-platform ATOMIZE run, re-reading spec constraints for each platform wastes context. Specs are read once before the generation loop and held in active context for all platforms.

- **Brand voice is never a gate.** The first output always runs without a voice profile. Setup is offered after delivery, never before. Gating content behind an interview would make first-time use feel like homework.

- **Sub-skills communicate via structured delimiter blocks** (`---BLOCK-NAME-START---`), not prose. If there's no delimiter, it's not a handoff — this prevents output from one sub-skill being misread as input instructions by the next.

- **NOT contracts name rationalizations, not just prohibitions.** Instead of "don't do X," each NOT contract names the specific excuse the model might use to justify doing X anyway — making it much harder to rationalize around the rule.

- **Two-pass validation per platform.** Pass 1 checks hard constraints (character limits, link placement rules, format requirements) — these are `compliance: fail` conditions that block saving. Pass 2 checks quality heuristics (hook strength, CTA clarity, engagement design) — these are `quality_flags` warnings, self-corrected silently where possible.

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
