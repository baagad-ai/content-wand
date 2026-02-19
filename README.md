# content-wand

[![Version](https://img.shields.io/github/v/release/baagad-ai/content-wand)](https://github.com/baagad-ai/content-wand/releases/latest) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> Turn any content into platform-ready posts — or transform it between formats — with Writing Style matching and AI-pattern removal on every output.

---

## Install

```bash
npx skills add baagad-ai/content-wand
```

Works with Claude Code, Codex, Gemini CLI, GitHub Copilot, and more. No dependencies, no build step.

---

## Use

```
/content-wand [paste content, URL, or describe a topic]
```

Natural language works — just describe what you want:

```
/content-wand atomize this article for Twitter and LinkedIn: [paste]

/content-wand https://example.com/article → newsletter and podcast notes

/content-wand repurpose this transcript into a blog post: [paste]

/content-wand write about "why most productivity systems fail" → TikTok script
```

Or skip the slash command and talk to Claude directly:

> "Turn this podcast transcript into a Twitter thread and email newsletter"
> "Take my rough notes and make a LinkedIn post"

---

## Two modes

**Atomize** — one piece of content → multiple platform formats at once.

```
blog post → Twitter/X thread + LinkedIn post + Email newsletter
           + Instagram carousel + YouTube Shorts + TikTok script
           + Threads post + Bluesky post + Podcast talking points
```

**Repurpose** — transform between content types.

```
Podcast transcript   → Blog post
Twitter thread       → LinkedIn article
Rough notes          → Newsletter issue
Blog post            → Email course
Case study           → Template
Interview transcript → Twitter thread
```

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

## 9 platforms

| Platform | What you get | Key constraint |
|----------|-------------|----------------|
| Twitter/X | Full thread — hook tweet + 4–8 body tweets | 280 chars/tweet; links go in reply, not body |
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

| Input | What happens |
|-------|-------------|
| Pasted text | Classified and processed directly |
| URL | Fetched, extracted, classified |
| Transcript | Re-ordered from non-linear structure; key themes extracted |
| Notes | Core concept identified; gaps surfaced if too sparse |
| Topic | 3–5 web searches run; content synthesized from results |

---

## Writing Style

content-wand learns how you write — once — and applies it automatically from then on. The same brief that produces neutral output without a style produces output that sounds like you wrote it with one.

**First-time users** are offered Writing Style setup before generation, not after. One-time setup (~3 minutes), remembered forever.

**Returning users** have their style applied automatically. Single saved style: silent auto-apply. Multiple saved styles: smart suggestion with rationale shown, you confirm or pick.

**Multiple styles** — create as many as you need. Writing for yourself, for a client, for a brand? Each gets its own named style. Names come from your own words, not abstract labels.

A 3-question interview (2 optional extras) captures your style. Writing samples carry 70% of the weight. Confidence scores as HIGH (≥3,000 sample words across ≥2 content types), MED, or LOW. Low-confidence styles are flagged.

Styles work across every project automatically — no per-project setup.

To manage: say "show my writing styles", "update my [name] style", or "delete my [name] style".

---

## Humanizer

Every output — with or without a Writing Style — passes through a humanizer before delivery. It removes detectable AI writing patterns using a research-backed pattern library (FSU/Max Planck, GPTZero, Wikipedia's AI writing guide).

Three passes:

1. **Lexical scrub** — replaces 80+ AI-flagged words and phrases (leverage, pivotal, tapestry, seamless, it's worth noting...)
2. **Structural rewrites** — fixes em dash overuse, rule-of-threes syndrome, significance signposting, forced balanced arguments, uniform sentence length, passive voice detachment
3. **Writing Style shaping** — if a style is active, shapes the cleaned output to match your documented patterns

Platform-specific rules apply last: Twitter gets no em dashes and forced contractions; LinkedIn loses the inspirational closers; TikTok scripts use spoken rhythm instead of written grammar.

After delivery: *"Cleaned N AI writing patterns."* Ask "what did you change?" for a breakdown.

---

## Who it's for

Solo creators, indie makers, and developer-writers who publish regularly across platforms. If you're writing blog posts, threads, newsletters, and scripts yourself — and spending more time reformatting than writing — this is for you.

Also works for agencies and ghostwriters who create content for clients. The Writing Style interview has a fork for capturing someone else's voice — all questions adapt to the brand or client instead of you personally.

If you have a content team with a CMS and a scheduling tool, you probably want something with a dashboard.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — platform spec updates, new platform support, edge case handling, and humanizer pattern improvements are all welcome. Read the conventions before opening a PR.

---

Prajwal Mishra — [@baagad_ai](https://x.com/baagad_ai) · [MIT License](LICENSE)
