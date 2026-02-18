# content-wand Public Release Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ship content-wand as a polished, discoverable, and trustworthy open-source GitHub release that makes a strong first impression on any developer who lands on the repo.

**Architecture:** No code changes — this plan is entirely about repo health, documentation quality, discoverability, and the release mechanics (tag, GitHub Release, public visibility).

**Tech Stack:** gh CLI, git, Markdown, GitHub Actions, Shields.io badges.

**Roles taken:** Open Source Maintainer · Technical Writer · DevOps Engineer · Product Manager

**Prerequisite check:** Run all tasks from `/Users/prajwalmishra/Desktop/Experiments/skills/content-wand-github`.

---

## Audit Summary — Current State vs. Release Standard

| Area | Current | Required |
|------|---------|----------|
| Repo visibility | **Private** | Public |
| README | Minimal stub (55 lines, no badges, no visuals, "In development") | Full human-facing doc |
| CODE_OF_CONDUCT.md | **Missing** | Required |
| SUPPORT.md | **Missing** | Recommended |
| .github/ISSUE_TEMPLATE/config.yml | **Missing** | Prevents blank issues |
| v1.0.0 git tag | **Not created** | Required for CHANGELOG link to work |
| GitHub topics | 10 topics, missing Claude-native + new platforms | 15-20 focused topics |
| GitHub Actions publish.yml | Uses deprecated `actions/create-release@v1` | `softprops/action-gh-release@v2` |
| docs/plans/ | Internal implementation notes, public-facing | Archive or reframe |
| CONTRIBUTING.md | References internal plan doc path for testing | Remove private path reference |
| Homepage field | Points to repo itself | Link to README anchor or remove |

---

## Task 1: Security History Scan

**Files:** Read-only audit, no edits.

**Purpose:** Verify no credentials, tokens, or secrets exist anywhere in git history before making the repo public. This is the single most important pre-publish step.

**Step 1: Scan git log for common secret patterns**

```bash
cd /Users/prajwalmishra/Desktop/Experiments/skills/content-wand-github
git log --all --oneline --full-history -- "*.env" "*.pem" "*.key" "credentials*" "secrets*" "*token*" "*password*"
```

Expected: No output (no such files in history).

**Step 2: Search all committed content for API key patterns**

```bash
git log --all -p | grep -iE "(api_key|secret|token|password|NPM_TOKEN|GITHUB_TOKEN)\s*[:=]\s*[a-zA-Z0-9_\-]{10,}" | grep -v "secrets\." | grep -v "\${{" | head -40
```

Expected: Zero matches containing real values (template references like `${{ secrets.NPM_TOKEN }}` are fine).

**Step 3: Check .gitignore covers all sensitive output paths**

Verify `.gitignore` already contains:
- `.content-wand/brand-voice.json` ✓
- `.DS_Store` ✓
- `node_modules/` ✓
- `.worktrees/` ✓

**Step 4: Confirm no docs/plans content references real credentials**

```bash
grep -r "token\|password\|secret\|api_key" /Users/prajwalmishra/Desktop/Experiments/skills/content-wand-github/docs/ --include="*.md" -i
```

Expected: No hits, or only contextual references (not actual values).

**If any secret is found:** Stop immediately. Rotate the credential, then purge history with `git filter-repo` before proceeding.

---

## Task 2: Archive docs/plans/ — Make Internal Notes Non-Confusing

**Files:**
- Modify: `CONTRIBUTING.md`
- Create: `docs/plans/README.md`

**Problem:** `docs/plans/` contains two implementation plan files that are internal dev notes. They are harmless but confusing to external contributors — one is referenced in CONTRIBUTING.md as a test case source.

**Step 1: Create an index file that frames the docs as architecture history**

Create `docs/plans/README.md`:

```markdown
# Architecture Decisions & Implementation Notes

These documents record the design decisions made during content-wand's development.
They are public for transparency — they explain *why* the architecture is the way it is,
not just *what* it does.

| Document | Purpose |
|----------|---------|
| [2026-02-18-content-wand.md](./2026-02-18-content-wand.md) | Original implementation plan — core design constraints and their sources |
| [2026-02-18-enterprise-upgrade.md](./2026-02-18-enterprise-upgrade.md) | v1.0.0 enterprise upgrade — 40 audit fixes, rationale |
```

**Step 2: Update CONTRIBUTING.md testing instructions**

Remove the specific internal plan file path reference. Change the testing instruction from:

> "paste the skill into Claude and run at least one scenario from the test cases in `docs/plans/2026-02-18-content-wand.md`"

To:

> "paste the skill into Claude and run at least one full scenario (ATOMIZE with a real article URL, or REPURPOSE from transcript → newsletter). Paste the output in your PR."

**Step 3: Commit**

```bash
git add docs/plans/README.md CONTRIBUTING.md
git commit -m "docs: add plans index, remove internal path reference from CONTRIBUTING"
```

---

## Task 3: Add Missing Community Health Files

**Files:**
- Create: `CODE_OF_CONDUCT.md`
- Create: `SUPPORT.md`
- Create: `.github/ISSUE_TEMPLATE/config.yml`

**Why:** GitHub's Community Health checklist requires CODE_OF_CONDUCT.md. Without it, the repo shows as incomplete on the Insights → Community tab, which signals poor maintainship. SUPPORT.md reduces noisy "how do I use this" Issues.

**Step 1: Create CODE_OF_CONDUCT.md**

Standard Contributor Covenant v2.1 (the open source default — do not invent a custom one):

```markdown
# Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, caste, color, religion, or sexual
identity and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment:

- Demonstrating empathy and kindness toward other people
- Being respectful of differing opinions, viewpoints, and experiences
- Giving and gracefully accepting constructive feedback
- Accepting responsibility and apologizing to those affected by our mistakes
- Focusing on what is best not just for us as individuals, but for the overall community

Examples of unacceptable behavior:

- The use of sexualized language or imagery, and sexual attention or advances of any kind
- Trolling, insulting or derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without their explicit written permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
prajwal@baagad.ai. All complaints will be reviewed and investigated promptly
and fairly.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org),
version 2.1, available at https://www.contributor-covenant.org/version/2/1/code_of_conduct.html.
```

**Step 2: Create SUPPORT.md**

```markdown
# Getting Support

## Quick answers

Check the [README](./README.md) — most questions about installation, usage, and brand voice setup are answered there.

## Something isn't working

[Open an issue](https://github.com/baagad-ai/content-wand/issues/new?template=bug_report.md) with the bug report template. Include your input type, mode, and what Claude actually did.

## Feature ideas

[Open a feature request](https://github.com/baagad-ai/content-wand/issues/new?template=feature_request.md) or start a [Discussion](https://github.com/baagad-ai/content-wand/discussions).

## Direct contact

For security issues: prajwal@baagad.ai (see [SECURITY.md](./SECURITY.md))
For everything else: [@baagad_ai on X](https://x.com/baagad_ai)
```

**Step 3: Create .github/ISSUE_TEMPLATE/config.yml**

This disables blank issues and forces users to pick a template:

```yaml
blank_issues_enabled: false
contact_links:
  - name: Ask a question
    url: https://github.com/baagad-ai/content-wand/discussions
    about: For usage questions and how-to help, please use Discussions.
```

**Step 4: Commit**

```bash
git add CODE_OF_CONDUCT.md SUPPORT.md .github/ISSUE_TEMPLATE/config.yml
git commit -m "docs: add CODE_OF_CONDUCT, SUPPORT, and issue template config"
```

---

## Task 4: Fix and Harden GitHub Actions

**Files:**
- Modify: `.github/workflows/publish.yml`
- Create: `.github/workflows/stale.yml`

**Problem:** `actions/create-release@v1` is deprecated and unmaintained. It also lacks the `permissions:` block, which is a security concern for Actions running in public repos.

**Step 1: Rewrite publish.yml**

Replace the entire file with:

```yaml
name: Publish

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write   # needed to create GitHub Releases

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'

      - name: Publish to npm
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body: |
            See [CHANGELOG.md](https://github.com/baagad-ai/content-wand/blob/main/CHANGELOG.md) for changes in this release.
          generate_release_notes: true
```

Note: `softprops/action-gh-release@v2` is the maintained successor to `actions/create-release@v1`. The `generate_release_notes: true` flag automatically pulls merged PRs and new contributors into release notes.

**Step 2: Create .github/workflows/stale.yml**

```yaml
name: Mark Stale Issues

on:
  schedule:
    - cron: '0 0 * * 1'  # Every Monday

permissions:
  issues: write
  pull-requests: write

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v9
        with:
          stale-issue-message: >
            This issue has been inactive for 60 days. If it is still relevant,
            leave a comment and it will stay open.
          close-issue-message: >
            Closing due to inactivity. Reopen if this is still relevant.
          days-before-stale: 60
          days-before-close: 14
          exempt-issue-labels: 'pinned,security,good first issue'
```

**Step 3: Commit**

```bash
git add .github/workflows/publish.yml .github/workflows/stale.yml
git commit -m "ci: replace deprecated create-release action, add stale workflow, add permissions block"
```

---

## Task 5: Update CHANGELOG.md — Reflect Real History

**Files:**
- Modify: `CHANGELOG.md`

**Problem:** The current 1.0.0 entry is the initial build only. It does not reflect the 40-issue audit fix, the enterprise upgrade (185 net insertions), the 7 skill-judge issues fixed, or any of the work done after initial build. The CHANGELOG should be a faithful record.

**Step 1: Rewrite CHANGELOG.md**

```markdown
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
```

**Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: expand CHANGELOG to reflect full 1.0.0 feature set and architecture decisions"
```

---

## Task 6: README Overhaul — Human-First Design

**Files:**
- Modify: `README.md`

**This is the highest-impact task.** The current README is 55 lines with no badges, no visuals, minimal installation instructions, and "Status: In development." A public release README must be the product's front door.

**Design principles:**
- Lead with value, not mechanics
- Answer "what is this?" in 10 seconds
- Show concrete examples before explaining architecture
- Badges provide trust signal at a glance
- Every section heading is a scannable decision point for the reader

**Target structure:**

```markdown
# content-wand

[Badges row]

> One-line pitch

[What problem this solves — 2 sentences max]

## Modes

[Two-column: ATOMIZE | REPURPOSE with examples]

## Platforms

[Table: Platform | What you get | Key constraint]

## Works with any input

[Table: Input type | Example | How Claude handles it]

## Optional: Brand Voice

[3-sentence explanation + what gets saved]

## Installation

[bash block]

## Usage

[4 real examples covering major use cases]

## How it works

[Architecture: orchestrator → sub-skills → reference files]

## Contributing

[One paragraph + link]

## License
```

**Step 1: Write the full new README.md**

```markdown
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

```
One blog post → Twitter thread + LinkedIn post + Email newsletter + Instagram carousel + YouTube Shorts script + Podcast talking points
```

**REPURPOSE** — Transform between content types.

```
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

To reset: delete `.content-wand/brand-voice.json`. That's it.

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
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: complete README overhaul — badges, platform table, architecture, usage examples"
```

---

## Task 7: Update GitHub Repository Metadata

**Files:** No file edits — this uses the `gh` CLI to update GitHub settings.

**Step 1: Update repository topics**

```bash
gh api repos/baagad-ai/content-wand \
  --method PATCH \
  --field topics[]="claude" \
  --field topics[]="claude-code" \
  --field topics[]="claude-skill" \
  --field topics[]="claude-skills" \
  --field topics[]="ai-skill" \
  --field topics[]="prompt-engineering" \
  --field topics[]="anthropic" \
  --field topics[]="content-repurposing" \
  --field topics[]="content-atomization" \
  --field topics[]="brand-voice" \
  --field topics[]="social-media-automation" \
  --field topics[]="twitter-thread" \
  --field topics[]="linkedin-post" \
  --field topics[]="newsletter" \
  --field topics[]="solopreneur" \
  --field topics[]="developer-tools" \
  --field topics[]="llm-tools" \
  --field topics[]="tiktok" \
  --field topics[]="content-creation"
```

**Step 2: Update homepage to point to the README anchor**

```bash
gh api repos/baagad-ai/content-wand \
  --method PATCH \
  --field homepage="" \
  --field has_wiki=false \
  --field has_projects=false
```

Setting homepage to empty is better than pointing to the repo itself (a circular link).

**Step 3: Commit**

No commit needed — these are GitHub API calls, not file changes.

---

## Task 8: Create the v1.0.0 Annotated Tag and GitHub Release

**Files:** No file edits — git and gh CLI operations.

**Why annotated tags, not lightweight:** Annotated tags are full Git objects with metadata. They are the correct choice for releases — `git describe` works with them, and they show up in `git tag -v`.

**Step 1: Create the annotated tag locally**

```bash
cd /Users/prajwalmishra/Desktop/Experiments/skills/content-wand-github
git tag -a v1.0.0 -m "Release v1.0.0 — full skill suite for 9 platforms with brand voice, 2-pass validation, and enterprise-grade edge case handling"
```

**Step 2: Push the tag**

```bash
git push origin v1.0.0
```

**Step 3: Create the GitHub Release via CLI**

```bash
gh release create v1.0.0 \
  --title "v1.0.0 — Initial Release" \
  --notes "$(cat <<'EOF'
## content-wand v1.0.0

Turn any content into platform-native formats — or transform between content types — with optional brand voice matching.

### What's included

- **ATOMIZE mode**: 1 piece of content → up to 9 platform-native formats
- **REPURPOSE mode**: Transform between content types (transcript → newsletter, thread → article, etc.)
- **Brand voice**: Optional 5-question interview, opt-in JSON persistence, schema-validated
- **9 platforms**: Twitter/X, LinkedIn, Email newsletter, Instagram carousel, YouTube Shorts, Podcast, TikTok, Threads, Bluesky
- **2-pass validation**: Hard compliance check + quality heuristics per platform
- **2026 algorithm intelligence**: Platform specs current as of February 2026

See [CHANGELOG.md](https://github.com/baagad-ai/content-wand/blob/main/CHANGELOG.md) for full architecture decisions.

### Installation

\`\`\`bash
git clone https://github.com/baagad-ai/content-wand ~/.claude/skills/content-wand
\`\`\`
EOF
)"
```

**Step 4: Verify the release appears on GitHub**

```bash
gh release view v1.0.0
```

Expected: Release page shows with title, body, and the v1.0.0 tag linked.

---

## Task 9: Push All Commits and Make Repo Public

**Files:** No file edits — git push and GitHub API.

**Step 1: Push all commits from Tasks 2–6**

```bash
cd /Users/prajwalmishra/Desktop/Experiments/skills/content-wand-github
git push origin main
```

Expected: All commits from Tasks 2-6 pushed successfully.

**Step 2: Make the repository public**

```bash
gh api repos/baagad-ai/content-wand \
  --method PATCH \
  --field private=false
```

**IMPORTANT:** This is irreversible without paid plan limits. Verify the security scan in Task 1 passed before running this command.

**Step 3: Verify public visibility**

```bash
gh api repos/baagad-ai/content-wand --jq '.visibility'
```

Expected: `"public"`

**Step 4: Enable Discussions (GitHub UI — cannot be done via API with standard token)**

Go to: https://github.com/baagad-ai/content-wand/settings → Features → Enable Discussions.

---

## Task 10: Post-Release Verification Checklist

Run through every item and confirm:

**Repository health**
- [ ] `gh api repos/baagad-ai/content-wand --jq '.visibility'` → `"public"`
- [ ] `gh release view v1.0.0` → Release exists with notes
- [ ] `git tag -l` → `v1.0.0` present
- [ ] `gh api repos/baagad-ai/content-wand --jq '.topics'` → 15+ topics
- [ ] `gh api repos/baagad-ai/content-wand --jq '.homepage'` → empty or correct URL

**Files present**
- [ ] `README.md` — badges visible, no "In development" status line
- [ ] `LICENSE` — MIT
- [ ] `CHANGELOG.md` — `[1.0.0]` entry complete with link at bottom
- [ ] `CONTRIBUTING.md` — no reference to internal plan path
- [ ] `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1
- [ ] `SECURITY.md` — security model documented
- [ ] `SUPPORT.md` — created
- [ ] `.gitignore` — covers all necessary paths
- [ ] `.github/ISSUE_TEMPLATE/config.yml` — blank issues disabled
- [ ] `.github/workflows/publish.yml` — uses `softprops/action-gh-release@v2`
- [ ] `.github/workflows/stale.yml` — created

**Content quality**
- [ ] README renders correctly on GitHub (check badges, tables, code blocks)
- [ ] All links in README resolve (LICENSE, CONTRIBUTING.md, docs/plans/)
- [ ] CHANGELOG links at bottom resolve (compare URLs and release tag URL)
- [ ] Issue templates render correctly in the GitHub UI

**Functional test**
- [ ] Clone from public URL works: `git clone https://github.com/baagad-ai/content-wand /tmp/test-clone`
- [ ] Skill loads in Claude Code: `/content-wand` invocation works

---

## Execution Notes

**Dependency order:** Tasks must run in sequence (1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10). Task 1 is a gate — if secrets are found, stop and fix before proceeding. Task 9 (make public) must be last.

**Commits:** Each task has its own commit. Do not batch tasks into a single commit.

**The README in Task 6 is the highest-value task** — allocate the most review time here. This is what every visitor sees first.
