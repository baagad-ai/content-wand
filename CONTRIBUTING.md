# Contributing to content-wand

Thank you for helping improve content-wand.

## What we're looking for

- **New platform support** — additional output formats (Substack, Medium, etc.)
- **Platform spec updates** — algorithm changes, new character limits, format changes
- **Humanizer pattern improvements** — new AI writing patterns to detect and fix; better replacements; platform-specific rules
- **Edge case handling** — inputs or failure modes not yet addressed
- **NOT contract improvements** — tighter prohibitions with named rationalizations
- **Quality heuristic improvements** — better signals for what makes content actually good

## What we're not looking for

- Adding complexity for its own sake
- Breaking the core architecture (orchestrator + sub-skills + reference files)
- Changes that violate the Writing Style security constraints
- Reverting the Writing Style interview to a post-generation gate — this is intentional UX design

## How to contribute

1. **Open an issue first** for anything beyond a small fix — describe what you want to change and why before writing code.

2. **Fork and branch** — create a branch from `main`.

3. **Follow the skill file conventions:**
   - Valid YAML frontmatter on every SKILL.md file
   - NOT contracts must name specific rationalizations Claude might use, not just state prohibitions
   - Handoff blocks use exact delimiters: `---BLOCK-NAME-START---` / `---BLOCK-NAME-END---`
   - Fallback behavior must be explicit for every failure mode
   - User-facing messages must never contain file paths, technical terms (JSON, schema, validation), or security jargon

4. **Update CHANGELOG.md** under `[Unreleased]` before submitting.

5. **Test manually** — paste the skill into Claude and run at least one full scenario (ATOMIZE with a real article URL, or REPURPOSE from transcript → newsletter). Paste the output in your PR.

6. **Open a PR** using the PR template.

## Skill file rules

These are non-negotiable:

| Rule | Why |
|------|-----|
| Routing instructions in first 50 lines of SKILL.md | "Lost in the Middle" (MIT/TACL 2024): LLM attention degrades for content in the middle of long documents |
| Writing Style offered before generation for first-timers | First impression matters. Generic first output creates a negative anchor. |
| Max 3 required + 2 optional Writing Style questions | Research ceiling before abandonment spikes |
| No raw content stored in Writing Style files | Security constraint — extract patterns only |
| Sub-skills communicate via structured blocks only | Prevents inter-sub-skill ambiguity. Note: this is a discipline convention, not a platform-enforced constraint — all sub-skills run in the same context window. The block protocol creates functional separation; contributors must enforce it manually. |
| Humanizer always runs | Every output must pass AI pattern removal before delivery — no exceptions, no flags |
| No technical jargon in user-facing messages | Users should never see file paths, JSON, "schema validation", or security terminology |

## Code of conduct

Be direct, specific, and constructive. We value precision over politeness.
