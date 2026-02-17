# Changelog

All notable changes to content-wand will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.0.0] — 2026-02-18

### Added
- **Orchestrator** (`SKILL.md`) — mode detection table top-loaded in first 50 lines; 7-step ATOMIZE/REPURPOSE flow; 7 edge cases handled
- **content-ingester** sub-skill — classifies 5 input types (paste, url, transcript, notes, topic); WebFetch for URLs; WebSearch for topic-only inputs; strict NOT contract
- **brand-voice-extractor** sub-skill — READ/SETUP dual-mode; samples-first mini-interview (5 questions max, Q1 weighted 70%); opt-in `.content-wand/brand-voice.json` persistence; schema validation on read
- **platform-writer** sub-skill — 2-pass validation (hard constraint compliance + quality heuristics) for all 6 platforms; status emits per format
- **repurpose-transformer** sub-skill — 4-class distance logic (DIRECT / COMPRESS / EXPAND / STRUCTURAL); COMPRESS anchors to 3 strongest ideas
- **platform-specs** reference — 2026-current hard constraints, algorithm signals, and quality heuristics for Twitter/X, LinkedIn, Email Newsletter, Instagram Carousel, YouTube Shorts, Podcast Talking Points
- **brandvoice-schema** reference — approved JSON schema, confidence scoring rubric, security constraints (5 prohibited content types), validation rules

### Architecture decisions
- "Lost in the Middle" mitigation: routing instructions top-loaded in lines 1–50 of SKILL.md
- Brand voice is never a gate: first output always generated without voice; setup offered after
- Structured handoff blocks (`---BLOCK-NAME-START---`/`---BLOCK-NAME-END---`) prevent inter-sub-skill ambiguity
- All NOT contracts name specific rationalizations, not just prohibitions
- Brand voice file: opt-in, schema-validated on read, never stores raw content or credentials

[1.0.0]: https://github.com/baagad-ai/content-wand/releases/tag/v1.0.0
