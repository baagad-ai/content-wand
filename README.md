# content-wand

> Turn any content into platform-native formats or transform between content types — with optional brand voice matching.

**Status:** In development. See `docs/plans/2026-02-18-content-wand.md` for implementation plan.

## What It Does

**ATOMIZE mode** — Take 1 piece of content → up to 6 platform-native formats:
- Twitter/X thread
- LinkedIn post
- Email newsletter
- Instagram carousel script
- YouTube Shorts script
- Podcast talking points

**REPURPOSE mode** — Transform between content types:
- Podcast transcript → Blog post
- Twitter thread → LinkedIn article
- Rough notes → Newsletter issue
- Blog post → Email course
- Case study → Template
- (and more)

## Works With Any Input
- Pasted text (blog post, essay, article)
- URLs (fetches the content)
- Transcripts (podcast, video, interview)
- Rough notes or bullet points
- Just a topic idea (researches and writes)

## Optional Brand Voice
On first use, content-wand generates content in a clean generic voice. After your first output, it offers to learn your voice — a 5-question interview that takes 2 minutes and saves a local profile for all future use.

## Installation

```bash
# Clone into your skills directory
git clone https://github.com/baagad-ai/content-wand ~/.claude/skills/content-wand

# Or for Codex CLI
git clone https://github.com/baagad-ai/content-wand ~/.codex/skills/content-wand
```

## Usage

```
/content-wand [your content or URL]
```

Or just describe what you want: "Turn this podcast transcript into a Twitter thread and LinkedIn post."

## Author
Prajwal Mishra — [@baagad_ai](https://x.com/baagad_ai)
