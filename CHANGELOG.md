# Changelog

All notable changes to content-wand are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.0.0] — 2026-02-18

### Added

**Core skill suite (5 files)**
- `SKILL.md` orchestrator — routing table top-loaded in first 50 lines ("Lost in the Middle" mitigation); 7-step ATOMIZE/REPURPOSE pipeline; 7 explicit edge cases
- `content-ingester-SKILL.md` — 5 input types (paste, url, transcript, notes, topic); WebFetch for URLs; WebSearch for topic-only; 7-entry fallback table; strict NOT contract
- `brand-voice-extractor-SKILL.md` — READ/SETUP dual-mode; samples-first mini-interview (5 questions max, Q1 weighted 70%); opt-in `.content-wand/brand-voice.json` persistence; schema-validated on read; voice authenticity framework; staleness detection; NEVER anti-patterns section
- `platform-writer-SKILL.md` — 2-pass validation (hard compliance + quality heuristics) for all 9 platforms; hook selection framework; pre-generation thinking check; LOW confidence voice handling; TikTok/Threads/Bluesky pass 1 + pass 2 checks
- `repurpose-transformer-SKILL.md` — 4-class distance logic (DIRECT / COMPRESS / EXPAND / STRUCTURAL); 12-word Repurposable Core Test pre-flight check; COMPRESS anchors to 3 strongest ideas; explicit EXPAND NEVER list

**Reference files**
- `references/platform-specs.md` — 2026-current algorithm intelligence for 9 platforms; mandatory staleness check header
- `references/brandvoice-schema.md` — approved JSON schema; confidence scoring rubric; 5 security constraints; migration rules
- `references/platform-writer-guide.md` — hook-to-content-shape mapping; quality anti-patterns

**Platforms supported**
- Twitter/X thread, LinkedIn post, Email newsletter, Instagram carousel script, YouTube Shorts script, Podcast talking points, TikTok script, Threads post, Bluesky post

**Community and repo**
- GitHub issue templates (bug report, feature request)
- PR template
- CONTRIBUTING.md with skill file rules and NOT contract conventions
- SECURITY.md with security model and brand voice file constraints
- MIT License

### Architecture decisions

- "Lost in the Middle" mitigation: routing instructions top-loaded in lines 1–50 of SKILL.md
- Brand voice is never a gate: first output always generated without voice; setup offered after
- Structured handoff blocks (`---BLOCK-NAME-START---`/`---BLOCK-NAME-END---`) prevent inter-sub-skill ambiguity
- All NOT contracts name specific rationalizations, not just prohibitions
- Brand voice file: opt-in, schema-validated on read, never stores raw content or credentials
- platform-specs.md loaded once before the generation loop (not per-platform), preventing redundant token use
- Pre-transformation check: repurpose-transformer validates a repurposable core concept exists before any work begins
- VOICE-PROFILE block re-emitted verbatim by orchestrator to ensure downstream sub-skills receive it even in long sessions

[Unreleased]: https://github.com/baagad-ai/content-wand/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/baagad-ai/content-wand/releases/tag/v1.0.0
