# content-wand

[![Version](https://img.shields.io/github/v/release/baagad-ai/content-wand)](https://github.com/baagad-ai/content-wand/releases/latest) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> Turn one source into review-ready, platform-native content. Limits are checked in code, every claim is traced to the source, and nothing is published without human approval.

content-wand is an [Agent Skill](https://agentskills.io) for Claude Code, Codex, Gemini CLI, Cursor, GitHub Copilot, OpenCode and other hosts that read `SKILL.md`. It has no runtime dependencies beyond Python 3.9+ (standard library only).

---

## What you get

| Need | How content-wand handles it |
|---|---|
| Turn a blog, transcript, notes or URL into posts | One source in, many platform-native outputs out (X, LinkedIn, newsletter, Instagram carousel, YouTube Shorts, TikTok, Threads, Bluesky, podcast outline). |
| Stay inside platform limits | `cw.py validate` checks each draft against `data/platform-specs.json`. Every fact is typed (`hard`, `policy`, `algorithm`, `heuristic`), dated and sourced. |
| Avoid invented numbers and quotes | The claims ledger lists every quote, number, price, percentage, multiple and link in the output and flags the ones that are not in the source. |
| Sound like you | A saved Writing Style is applied to drafts. A final edit pass removes generic phrasing and restores specifics. It does not try to evade AI detectors. |
| Stay safe with untrusted pages | URLs are fetched through an SSRF-safe path, hidden text is stripped, the text is scanned for injected instructions, and instruction-like text never changes the workflow. |
| Keep a human in charge | A review packet and per-file approval come before any publish step. Approving a draft does not authorise posting it. |
| Keep rules current | Platform facts carry review windows. `preflight` reports stale ones. Updates arrive by release, by an opt-in signed feed, or by an agent refresh that is validated in code and approved by you. |

---

## Install

### Any host that supports Agent Skills

```bash
npx skills add baagad-ai/content-wand
```

or copy `skills/content-wand/` into your agent's skills folder (for example `~/.claude/skills/content-wand/`).

### Claude Code plugin (skill plus guard hooks)

```
/plugin marketplace add baagad-ai/content-wand
/plugin install content-wand@content-wand
```

The plugin adds hooks that run only while the skill is active. See [Hooks](#hooks).

### Cursor

The repository includes `.cursor-plugin/plugin.json`. Cursor receives the skill and the `cw.py` checks. Claude Code style hooks are not loaded there, so `preflight` reports `guards: "prompt-only"` and the skill applies its rules in the instructions and through the CLI.

---

## Use

```
/content-wand turn this article into a LinkedIn post and an X thread: [paste or URL]
```

Natural language works too:

> "Repurpose this podcast transcript into a newsletter and three pull-quotes."
> "Make an Instagram carousel from these notes, in my voice."
> "Give me five hook variants for this launch post."
> "Build a two-week content calendar from this article."
> "Does my draft stay faithful to this source? Check the numbers."

Twelve ready-made workflows are in [`references/use-cases.md`](skills/content-wand/references/use-cases.md): platform bundles, hook variants, media bundles, release-notes kits, case study packs, calendars, UTM links and client styles.

### The workflow

1. **Preflight.** One call reports Python, state, guards, stale rules and the saved style.
2. **Intake.** Pasted text, a file, or a URL fetched through `ingest`.
3. **Style.** Use a saved Writing Style or offer a short interview once. Declining is remembered.
4. **Strategy.** Choose the repurposable core and the hook for each platform.
5. **Drafting.** Platform-native drafts, written one at a time.
6. **Specificity and fidelity edit.** Four passes: lexical, structural, specificity, voice.
7. **Checks.** `validate` for limits and `claims` for facts. Failures are fixed before you see the draft.
8. **Review packet.** You approve, reject or edit each file.
9. **Publish (optional).** Only approved text, only on request, only through the publish gate.

---

## Human-in-the-loop points

| Point | What the human decides |
|---|---|
| Style interview | Whether to create a Writing Style at all. |
| Flagged URL | Whether to fetch an address that looks unusual. |
| Unsupported claim | Whether to remove it, source it, or knowingly accept it (`--accept-unsupported-claims`, recorded in the packet). |
| Review packet | Approval or rejection per file. |
| Publishing | A separate, explicit request to post, with the final text shown. |
| Rule updates | Every spec change, signed or researched, is shown and applied only after a yes. |
| Style and settings changes | State-changing `cw.py` commands ask for confirmation when hooks are active. |

---

## Hooks

Installed as a Claude Code plugin, content-wand adds hooks that act only while the skill is active in the session. Other work is untouched. Hooks fail open: an internal error never blocks you.

| Event | Behaviour |
|---|---|
| `SessionStart`, `UserPromptExpansion`, `Skill` use | Mark the skill as active. |
| `PreToolUse` on fetch | Deny private, loopback and metadata addresses. Ask for unusual ones. |
| `PreToolUse` on writes | Deny writes to credential and agent configuration paths. |
| `PreToolUse` on shell | Deny credential reads. Ask before network commands and before state-changing `cw.py` commands. |
| `PreToolUse` on publishing connectors | Allow only text that matches an approved output. Deny extra links. |
| `PostToolUse` on fetch and search | Scan returned text for injected instructions. |
| `PostToolUse` on writes in `content-output/` | Validate the platform file immediately. |
| `Stop` | Block finishing while saved platform files lack a validation record. |

Review the decisions any time with `python3 skills/content-wand/scripts/cw.py audit tail`.

---

## CLI reference

Run from the skill folder: `python3 scripts/cw.py <command>`. Each command prints one JSON document. Exit codes: `0` ok, `1` error, `3` compliance failure (nothing saved), `4` a human decision is needed.

| Command | Purpose |
|---|---|
| `preflight` | Report environment, guards, stale rules and the saved style in one call. |
| `session start|info` | Create or inspect the session marker used by hooks. |
| `check-url URL` | Test a URL against the SSRF policy without fetching. |
| `ingest --url U | --file F` | Fetch or read a source into cleaned, scanned text. |
| `scan [--sanitize] [file]` | Scan text for injection patterns and hidden characters. |
| `validate PLATFORM [file]` | Check a draft against platform limits. |
| `validate-dir DIR` | Validate every platform file in an output folder. |
| `lint-ai [file]` | List AI-pattern findings in a draft. |
| `claims --source S --output O` | List claims in the output that the source does not support. |
| `utm URL --platform P --campaign C` | Add consistent UTM parameters. |
| `style list|read|write|validate|delete|rename|decline|reset` | Manage Writing Styles. |
| `pref get|set` | Read or change preferences. |
| `output new|save|meta|review|status|packet` | Create output folders, save validated files, record review, build the review packet. |
| `specs status|show|sources|validate-proposal|apply|rollback|check-remote|pending|apply-remote|discard-remote` | Inspect and update platform rules. |
| `audit tail` | Show recent hook decisions. |

---

## Keeping platform rules current

All limits live in `data/platform-specs.json`. Each fact has a kind, a verification date and a source.

| Kind | Review window |
|---|---|
| `hard` | 90 days |
| `policy` | 60 days |
| `algorithm` | 30 days |
| `heuristic` | 180 days |

Updates reach users three ways:

1. **Release.** New versions ship new data.
2. **Signed feed (opt-in).** `pref set update_check on` allows one request per day to a fixed host. The feed is verified with Ed25519, refuses downgrades, is stored as pending, and is applied only after you approve. No identifier or content is sent. `CONTENT_WAND_UPDATES=off` disables it.
3. **Agent refresh.** The agent reads official sources, writes a proposal with an exact quote, and code validates the proposal before you approve it.

Applied updates live in a local override file with snapshots, so `specs rollback` undoes them. Details: [`references/spec-refresh.md`](skills/content-wand/references/spec-refresh.md).

---

## Security and privacy

- Source text is data. It cannot change the rules, tools, files or steps.
- No telemetry, no licence check, no remote code. Updates carry data only.
- The network is used only to fetch a URL you provided and, if you enabled it, a daily signed-feed check.
- State is stored under `$CONTENT_WAND_HOME`, `$XDG_CONFIG_HOME/content-wand` or `~/.config/content-wand` with owner-only permissions. Outputs go to `content-output/` in your project.
- `cw.py style reset --yes` deletes saved settings and styles.

Full model: [`SECURITY.md`](SECURITY.md) and [`references/security.md`](skills/content-wand/references/security.md).

---

## Repository layout

```
skills/content-wand/        the distributable skill
  SKILL.md                  orchestrator (under 500 lines)
  references/               loaded on demand: platform craft, specs, security, formats
  data/                     platform specs, AI patterns, updater config
  scripts/cw.py             deterministic CLI; scripts/cwlib/ holds the logic
  scripts/hook_main.py      hook entry point; run-hook.sh is the portable wrapper
  scripts/maintainer/       publisher tools (not used at runtime)
hooks/hooks.json            Claude Code plugin hooks
.claude-plugin/             plugin and marketplace manifests
.cursor-plugin/             Cursor plugin manifest
evals/                      deterministic evals and the manual eval protocol
tests/                      unit, hook, security, updater and repository tests
scripts/                    package.py (release archives), check_release.py (release gate)
docs/                       architecture and distribution guides
```

---

## Develop and release

```bash
python3 -m unittest discover -s tests   # 126 tests
python3 evals/run_evals.py              # deterministic evals
python3 scripts/check_release.py        # full release gate
python3 scripts/package.py              # build dist/ archives with SHA256SUMS
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/DISTRIBUTION.md`](docs/DISTRIBUTION.md).

---

## License

MIT. See [`LICENSE`](LICENSE).
