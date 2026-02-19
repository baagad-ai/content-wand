# content-wand

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> A Claude skill that turns any content into platform-ready posts — or transforms it between formats — with Writing Style matching and an AI-pattern humanizer that runs on every output.

You paste a blog post, drop a URL, or say "write about X." content-wand outputs platform-native content for up to 9 platforms. Each output passes a two-pass validation check: hard constraints first (character limits, link rules, format requirements), quality heuristics second (hook strength, CTA clarity, engagement design). Then a humanizer runs a final pass on every output to strip AI writing patterns before delivery. It never guesses at your platform specs — they're kept current and loaded fresh each run.

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

Also works for agencies and ghostwriters who create content for clients. The Writing Style interview has a fork for capturing someone else's voice — all questions adapt to the brand or client instead of you personally.

If you have a content team with a CMS and a scheduling tool, you probably want something with a dashboard.

---

## Writing Style

content-wand learns how you write — once — and applies it automatically from then on. The same brief that produces neutral output without a style produces output that sounds like you wrote it with one.

**First-time users** are offered Writing Style setup before generation, not after. One-time setup (~3 minutes), remembered forever.

**Returning users** have their style applied automatically. Single saved style: silent auto-apply. Multiple saved styles: smart suggestion with rationale shown, you confirm or pick.

**Multiple styles** — create as many as you need. Writing for yourself, for a client, for a brand? Each gets its own named style. Names come from your own words, not abstract labels.

A 3-question interview (2 optional extras) captures your style. Writing samples carry 70% of the weight. Confidence scores as HIGH (≥3,000 sample words across ≥2 content types), MED, or LOW. Low-confidence styles are flagged.

Styles save globally to `~/.claude/content-wand/styles/` — they work across every project automatically. No per-project setup.

To manage: say "show my writing styles", "update my [name] style", or "delete my [name] style".

---

## Humanizer

Every output — with or without a Writing Style — passes through a humanizer before delivery. It removes detectable AI writing patterns using a research-backed pattern library (FSU/Max Planck, GPTZero, Wikipedia's AI writing guide).

Three passes:
1. **Lexical scrub** — replaces 80+ AI-flagged words and phrases (leverage, pivotal, tapestry, seamless, it's worth noting...)
2. **Structural rewrites** — fixes em dash overuse, rule-of-threes syndrome, significance signposting, forced balanced arguments, uniform sentence length, passive voice detachment
3. **Voice application** — if a Writing Style is active, shapes the cleaned output to match your documented patterns

Platform-specific rules apply last: Twitter gets no em dashes and forced contractions; LinkedIn loses the inspirational closers; TikTok scripts use spoken rhythm instead of written grammar.

After delivery: *"Cleaned N AI writing patterns."* Ask "what did you change?" for a breakdown.

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

content-wand is an orchestrated Claude skill — one entry point, five specialized sub-skills, four reference files:

```
content-wand (SKILL.md)
│
├── content-ingester           Classifies input, fetches URLs, runs WebSearch for topics
├── writing-style-extractor    Reads or captures Writing Style; contextual interview; named styles
├── repurpose-transformer      Classifies transformation distance; DIRECT/COMPRESS/EXPAND/STRUCTURAL logic
├── platform-writer            Generates output; 2-pass validation per platform
├── humanizer                  Final pass: removes AI patterns; applies Writing Style shaping
│
└── references/
    ├── platform-specs.md      Hard constraints + algorithm signals, 9 platforms, Feb 2026
    ├── brandvoice-schema.md   Writing Style JSON schema v1.2 + validation + migration rules
    ├── ai-patterns.md         AI writing pattern library for humanizer (80+ patterns, 7 categories)
    └── platform-writer-guide.md  Hook framework + quality anti-patterns
```

**Design decisions worth knowing:**

- **Routing loads first, not last.** All mode detection and routing logic appears in the first 50 lines of SKILL.md. LLMs follow mid-document instructions less reliably than early-document ones — a documented failure mode for long prompts ("Lost in the Middle" — MIT/TACL 2024). Position is architecture.

- **Platform specs load once, not per-platform.** In a 9-platform ATOMIZE run, re-reading spec constraints for each platform wastes context. Specs are read once before the generation loop and held in active context for all platforms.

- **Writing Style is offered before generation, not after.** First-time users get one clear offer before any output is produced. The first output they see has their voice in it, not a generic draft. Returning users have their style applied silently. The setup-after-delivery pattern from v1.0 caused first-timers to form a negative first impression before being offered the improvement.

- **Writing Style is global, not project-scoped.** Styles live at `~/.claude/content-wand/styles/` — they work in every project, every session. The old `.content-wand/brand-voice.json` pattern required re-setup per project.

- **The humanizer always runs.** Every output passes through AI pattern removal before delivery, regardless of whether a Writing Style is active. Output that passes hard compliance checks can still read as obviously AI-generated — the humanizer closes that gap using a research-backed pattern library.

- **Sub-skills communicate via structured delimiter blocks** (`---BLOCK-NAME-START---`), not prose. If there's no delimiter, it's not a handoff — this prevents output from one sub-skill being misread as input instructions by the next.

- **NOT contracts name rationalizations, not just prohibitions.** Instead of "don't do X," each NOT contract names the specific excuse the model might use to justify doing X anyway — making it much harder to rationalize around the rule.

- **Two-pass validation per platform.** Pass 1 checks hard constraints (character limits, link placement rules, format requirements) — these are `compliance: fail` conditions that block saving. Pass 2 checks quality heuristics (hook strength, CTA clarity, engagement design) — these are `quality_flags` warnings, self-corrected silently where possible.

---

## Files in this repo

| File | Purpose |
|------|---------|
| `SKILL.md` | Orchestrator — entry point, mode detection, routing, Writing Style state |
| `content-ingester-SKILL.md` | Input classification + URL fetch + topic research |
| `writing-style-extractor-SKILL.md` | Writing Style read/capture; contextual interview; named styles |
| `platform-writer-SKILL.md` | Platform-native generation with 2-pass validation |
| `repurpose-transformer-SKILL.md` | Type-to-type transformation with distance classification |
| `humanizer-SKILL.md` | Final-pass AI pattern removal — lexical, structural, Writing Style shaping |
| `references/platform-specs.md` | Platform constraints + algorithm signals (Feb 2026) |
| `references/brandvoice-schema.md` | Writing Style JSON schema v1.2 + validation + migration |
| `references/ai-patterns.md` | AI writing pattern library — 80+ patterns across 7 categories |
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
