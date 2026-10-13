# Architecture

content-wand separates what a model is good at (writing, judgement) from what code is good at (counting, checking, storing, guarding). The skill is one orchestrator, a set of on-demand references, and one deterministic program.

```
User / agent host
   |  reads
   v
SKILL.md (routing, hard rules, 9-step workflow, < 500 lines)
   |  loads when a step needs it
   v
references/*.md    platform craft, specs, formats, security, use cases
   |  calls
   v
scripts/cw.py ---> cwlib/*   validate, claims, scan, ingest, styles, output, specs, updater
   ^
   |  guards (only when installed as a plugin and the skill is active)
hooks/hooks.json ---> run-hook.sh ---> hook_main.py ---> cwlib/hooks.py
```

## Design decisions

| Decision | Reason |
|---|---|
| One skill, not a chain of sub-skills | v1 passed text between sub-skills in one context window, which added tokens and ambiguity but no isolation. One orchestrator with references loaded on demand is cheaper and easier to test. |
| Deterministic CLI for anything checkable | Models miscount characters, forget numbers and skip steps. Code gives repeatable limits checks, claims ledgers and storage. |
| Python standard library only | Nothing to install, nothing to audit in a dependency tree, works wherever Python 3.9+ exists. |
| Progressive disclosure | Only the description is always in context. The body loads on trigger. References load per step. |
| Works without hooks | Hooks exist on few hosts. Every guard also exists as an instruction or CLI check. Hooks make them harder to skip. |
| Data separate from code | Platform facts change faster than logic. They live in `data/` with kind, date and source. |

## Components

### SKILL.md

Frontmatter uses portable fields only. The description names triggers and exclusions. The body contains the hard rules and the workflow: preflight, intake, style, strategy, drafting, specificity and fidelity edit, checks, review packet, publishing and spec refresh. Everything else is a reference link.

### References

`platform-specs.md` is rendered from `data/platform-specs.json` by `scripts/maintainer/render_specs.py`. A test fails if they drift. Other references: `platform-writer`, `writer-guide`, `repurpose`, `humanizer`, `writing-style`, `style-schema`, `output-formats`, `use-cases`, `review-and-publish`, `security`, `spec-refresh`, `tool-map`, `disclosure`, `ai-patterns`.

### cw.py and cwlib

| Module | Responsibility |
|---|---|
| `validate`, `textstats` | Platform checks (weighted X length, hashtags, subject lines, slide counts, Shorts duration from word count and pace). |
| `claims` | Extracts quotes, numbers, money, percentages, multiples and URLs, compares with the source. |
| `ingest`, `urlguard`, `scan` | Pinned-DNS fetch, redirect rechecks, hidden-text stripping, injection scan, structural token neutralisation, file boundary. |
| `styles` | Writing Style schema 1.3, validation, forbidden data, atomic writes. |
| `output` | Output folders, validated saves, metadata, review status, review packet. |
| `links` | UTM parameters and link checks. |
| `specs` | Loads shipped data plus local overrides, freshness, source allow-list, proposal validation, snapshots and rollback. |
| `updater`, `ed25519` | Signed feed check, pure-Python Ed25519 verification (RFC 8032 vectors tested), downgrade protection, pending store. |
| `session`, `hooks` | Session marker, audit log, hook handlers. |
| `jsonio`, `paths` | Atomic JSON writes with owner-only permissions, state paths. |

All commands print one JSON document and use fixed exit codes (`0` ok, `1` error, `3` compliance failure, `4` human decision needed), so an agent never has to parse prose.

## Hook lifecycle

1. `SessionStart` and `UserPromptExpansion` (and a `Skill` call for content-wand) write a session marker with the working directory and start time.
2. Every other hook starts at `hook_main.py`, which checks the marker before importing the guard logic. A session that never used the skill pays only a small start-up cost.
3. `PreToolUse` classifies the call (fetch, write, shell, connector) and returns allow, ask or deny with a short reason.
4. `PostToolUse` scans fetched text for injection and validates platform files written under `content-output/`.
5. `Stop` blocks finishing when platform files saved in this session have no validation record, with a time slack for coarse filesystem clocks.
6. Each decision is appended to the audit log with tool name, host and reason only.

Any exception inside a hook exits 0 with no decision. A guard that crashes must not stop the user's work.

### Publish gate

For a tool that looks like publishing (connector names and verbs such as post, publish, tweet, send, schedule), the hook extracts the outgoing text and compares it with approved outputs in this session's `content-output/`. It is allowed only if the text matches an approved file and every outgoing URL (apart from API hosts) already appears in that approved text. Appending a link to approved text is denied. Anything else is denied with the reason.

### Host compatibility

| Host | Skill | `cw.py` | Hooks |
|---|---|---|---|
| Claude Code | Yes | Yes | Yes, through `hooks/hooks.json` |
| Cursor | Yes | Yes | No. The manifest sets `"hooks": {}` so the Claude format is not misread. `preflight` reports `prompt-only`. |
| Codex, Gemini CLI, Copilot, OpenCode | Yes | Yes | No |
| claude.ai upload | Yes (skill zip) | Where code execution is available | No |

`references/tool-map.md` maps capability names (fetch, write, shell) to each host's tool names and gives the fallback when a tool is missing.

## Spec freshness and the updater

```
data/platform-specs.json  --(local approved changes)--> state/specs-overrides.json
        ^                                                   |
        | release                                           | snapshot per apply -> specs rollback
        |
feed/specs-feed.json + .sig  --check-remote (opt-in, 24h, one host)--> pending --apply-remote (user yes)
agent research + proposal.json --validate-proposal (code) --> apply (user yes)
```

Validation rules for a change: the source URL must be on the platform's official allow-list for `hard` and `policy` facts, the quote must contain the proposed value, the type must match the existing fact, and the date must be plausible. Secondary sources are allowed only for `algorithm` and `heuristic` facts and are marked as such.

Feed rules: size cap, one allow-listed host, same-host redirects only, Ed25519 signature check, `data_version` must not be older than the installed floor, and the result is only ever stored as pending.

## Testing

| Layer | Where | What |
|---|---|---|
| Unit and integration | `tests/test_cwlib.py`, `test_security.py`, `test_updater.py` | Logic, a local HTTP server for ingest, RFC 8032 vectors, tamper and downgrade cases. |
| Hooks | `tests/test_hooks.py` | Activation, SSRF, publish gate, secret paths, stop hook, fail-open. |
| Repository | `tests/test_repo.py` | Line budget, frontmatter, link integrity, spec drift, standard-library-only imports, secret scan. |
| Evals | `evals/` | Compliance, claims, injection, humanizer and trigger corpora, plus a manual model protocol. |
| Release gate | `scripts/check_release.py` | All of the above plus reproducible archives and archive contents. |

## Extending

- **New platform.** Add facts to `data/platform-specs.json` with sources, re-render the reference, add a validator branch, a craft section in `platform-writer.md`, tests and eval cases.
- **New hook rule.** Add it in `cwlib/hooks.py` with a test in `tests/test_hooks.py` that covers both the block and the allowed neighbour case.
- **New injection pattern.** Add it to `scan.py` and a case to `evals/data/injection.json`. Add a benign neighbour to avoid false positives.
