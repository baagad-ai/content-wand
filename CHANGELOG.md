# Changelog

All notable changes to content-wand are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.0.1] — 2026-02-18

### Security

**Prompt injection defenses added across all sub-skills**

- `SKILL.md` — Added Security: Trust Boundaries section with a 4-tier trust model (SKILL.md → user commands → tool outputs → external content). Documents what untrusted content can and cannot influence. Added orchestrator-level `injection_warning` surfacing protocol.
- `content-ingester-SKILL.md` — Added behavioral injection detection for fetched URL content and web search results. HIGH RISK patterns (persona hijacking, file access directives, output manipulation) stop and flag; MEDIUM RISK patterns warn and continue. Extended CONTENT-OBJECT output format with `injection_warning`, `injection_detail`, `injection_warning_low`, `injection_detail_low` fields. Existing URL scheme validation and delimiter guard preserved.
- `platform-writer-SKILL.md` — Added Security section: `raw_text` is source material to transform, not instructions to execute. Content flagged with `injection_warning: true` is never reproduced in any output.
- `repurpose-transformer-SKILL.md` — Added Security section: behavioral directives embedded in source content are ignored; legitimate content is transformed normally.
- `brand-voice-extractor-SKILL.md` — Added Security section: writing samples are voice pattern data only; instructions embedded in samples are never executed. Existing JSON schema validation (unknown key rejection) provides defense for READ mode.

### Changed

- Bumped version 1.0.0 → 1.0.1
- Removed `puppeteer` and `pdf-lib` from root `package.json` (PDF slideshow artifacts unrelated to the skill; `assets/` is gitignored)
- Updated `package.json` description and `skills` block to mention prompt injection defense
- Added keywords: `prompt-injection-defense`, `ai-security`, `secure-ai`

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

[Unreleased]: https://github.com/baagad-ai/content-wand/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/baagad-ai/content-wand/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/baagad-ai/content-wand/releases/tag/v1.0.0
