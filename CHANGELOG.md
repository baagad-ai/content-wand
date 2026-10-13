# Changelog

All notable changes to content-wand are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [2.0.0] - 2026-10-13

A ground-up rebuild into a single production-grade skill with a deterministic core, guard hooks and a verified rule-update path. Breaking: the layout and the sub-skill files from 1.x are gone.

### Added

- **`cw.py` deterministic toolkit** (Python 3.9+, standard library only): `preflight`, `ingest`, `scan`, `validate`, `validate-dir`, `lint-ai`, `claims`, `utm`, `style`, `pref`, `output`, `specs`, `audit`. One JSON document per command and fixed exit codes.
- **Platform validator** driven by `data/platform-specs.json`: weighted X length, hashtag and link rules, subject lines, carousel slide counts, Shorts duration and more. Facts are typed (`hard`, `policy`, `algorithm`, `heuristic`), dated and sourced, with review windows reported by `preflight`.
- **Claims ledger**: quotes, numbers, money, percentages, multiples and links in outputs are compared with the source, and unsupported ones block review unless the user accepts them knowingly.
- **Human-in-the-loop review**: review packet, per-file approve/reject, recorded overrides, and a separate explicit step for publishing.
- **Guard hooks** for Claude Code (`hooks/hooks.json`): SSRF and credential-path denial, publish gate with approved-text matching and extra-link detection, prompt-injection scan of fetched content, validation of written outputs, and a stop gate. Hooks run only while the skill is active, fail open and write an audit log.
- **Safe ingestion**: DNS-pinned fetch with redirect rechecks, hidden-text stripping, invisible Unicode removal, injection scan, chat-template token neutralisation and a local file boundary.
- **Signed spec updates**: opt-in daily check, Ed25519 verification (pure Python, RFC 8032 vectors tested), downgrade protection, pending-then-approve flow, snapshots and rollback. An agent-researched refresh path validates official sources and exact quotes in code.
- **Writing Style 1.3** with validation, forbidden-data rules, migration of legacy styles and an interview that can be declined once and remembered.
- **New references**: output formats, twelve use-case workflows, review and publish, security, spec refresh, tool map per host, disclosure policies.
- **Packaging**: reproducible skill and plugin archives with `SHA256SUMS` and a file manifest (`scripts/package.py`), plus `scripts/check_release.py` as the release gate.
- **Plugin manifests** for Claude Code (plugin and marketplace) and Cursor.
- **Tests and evals**: 126 tests covering logic, hooks, security, the updater and repository invariants, deterministic eval suites, and a manual model-in-the-loop protocol.
- **Documentation**: README, `SECURITY.md` threat model, `docs/ARCHITECTURE.md`, `docs/DISTRIBUTION.md`, `evals/README.md`.
- GitHub Actions workflow that runs the release gate on supported Python versions.

### Changed

- `SKILL.md` is now a 210-line orchestrator with spec-compliant frontmatter and a trigger description that names exclusions. Detail moved to `references/` and loads on demand.
- The humanizer is now a four-pass specificity and fidelity edit. It no longer claims to defeat AI detectors.
- Platform facts moved out of prose into data and are rendered into `references/platform-specs.md`.
- State moved to `$CONTENT_WAND_HOME` or `~/.config/content-wand` with owner-only permissions. Legacy styles are migrated with `style migrate-legacy`.

### Removed

- The 1.x sub-skill files (`content-ingester`, `platform-writer`, `repurpose-transformer`, `humanizer`, `writing-style-extractor` as separate `SKILL.md` files) and the shell release-health script. Their content now lives in `skills/content-wand/references/` and `scripts/check_release.py`.

### Security

- Source text can no longer change workflow, tools or outputs. See `SECURITY.md`.
- Closed a publish-gate gap where extra links could ride along with approved text.
- Neutralised chat-template tokens in ingested text.


## [1.1.0] — 2026-02-19

### Added

- **`writing-style-extractor-SKILL.md`** — replaces `brand-voice-extractor-SKILL.md` with a full UX overhaul:
  - Agency/client fork at the start of every SETUP session — all interview questions adapt to the brand or client
  - 3 required + 2 optional questions (down from 5 required); progress indicators on each question
  - Session context anchoring — interview references the platform and content type you're generating right now
  - Style naming derived from user's own Q2+Q3 words, not abstract metaphors
  - Plain-language messages throughout — no JSON, schema, or file path jargon exposed to users
- **`humanizer-SKILL.md`** — new final-pass sub-skill that runs after every generation, no exceptions:
  - 3-pass system: lexical scrub → structural rewrites → voice application
  - Research-backed pattern library (FSU/Max Planck arxiv:2412.11385, GPTZero vocabulary research, Wikipedia Signs of AI Writing guide, MDPI stylometric research 2025)
  - Platform-specific rules: Twitter bans em dashes and forced formality; LinkedIn bans inspirational closers; TikTok uses spoken rhythm
- **`references/ai-patterns.md`** — comprehensive AI writing pattern reference loaded by the humanizer:
  - Tier 1 banned words/phrases (80+) with context-aware exceptions
  - Tier 2 contextual words for judgment-based replacement
  - Filler phrase deletion rules
  - Opening/closing cliché removal
  - Structural pattern fixes: em dash overuse, rule-of-threes, significance signposting, forced balance, uniform sentence length, passive voice detachment, bullet obsession
  - Tonal marker fixes: false intimacy, excessive positivity, corporate inspirational tone
  - Full substitution quick-reference table
- **Writing Style management commands** in orchestrator: list, create, update, delete, rename, inspect styles — triggered by natural language ("show my writing styles", "delete my [name] style")
- **Global Writing Style storage** — styles now saved to `~/.claude/content-wand/styles/` with a `config.json` index; no per-project setup required

### Changed

- **Writing Style** (formerly "brand voice") — terminology updated throughout:
  - All user-facing messages use "Writing Style" — no "brand voice", "profile", or "voice DNA"
  - First-time users offered setup **before** generation (was: after delivery); first output can have style applied from day one
  - Single saved style: auto-applied silently with one-line confirmation
  - Multiple saved styles: smart suggestion with rationale shown, user confirms or picks
  - 30-day declined state in `config.json` — users who skip are not prompted again for 30 days
  - Interview: 3 required + 2 optional questions; each question includes why it's being asked
- **Schema v1.2** — `references/brandvoice-schema.md` updated:
  - Added `style_name`, `style_for` (own|client), `client_name` fields
  - Updated file location to `~/.claude/content-wand/styles/[name].json`
  - `config.json` structure documented
  - Migration path from old `.content-wand/brand-voice.json` files
  - All user-facing rejection messages use plain language only
- **SKILL.md** pipeline:
  - STEP 0 added: checks Writing Style state before anything else
  - STEP 1.5 added: Writing Style offer/apply/skip logic
  - STEP 4.5 added: humanizer invocation between generation and delivery
  - STEP 5: one-time nudge at bottom of output only for first-time skippers (not for declined users)
  - STEP 6: simplified to staleness refresh only
  - STEP 7: updated save path and config.json management

### Removed

- **`brand-voice-extractor-SKILL.md`** — replaced by `writing-style-extractor-SKILL.md`

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

[Unreleased]: https://github.com/baagad-ai/content-wand/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/baagad-ai/content-wand/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/baagad-ai/content-wand/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/baagad-ai/content-wand/releases/tag/v1.0.0
