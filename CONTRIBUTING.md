# Contributing to content-wand

Thank you for helping improve content-wand. Open an issue first for anything larger than a small fix.

## Setup

Python 3.9 or newer. There are no packages to install: the runtime and the tests use only the standard library.

```bash
python3 -m unittest discover -s tests   # unit, hook, security, updater and repository tests
python3 evals/run_evals.py              # deterministic evals
python3 scripts/check_release.py        # everything above plus packaging checks
```

All three must pass before a pull request is ready.

## What helps most

- **Platform rule corrections** with an official source URL and a verification date.
- **New eval cases** for a bug you found (a failing case first, then the fix).
- **New platform or format support**, with a validator entry, spec data, a craft section and evals.
- **Injection and SSRF test cases**, especially bypasses.
- **Clearer instructions** that make agents behave more consistently across hosts.

## What does not fit

- Runtime dependencies, network calls that carry user content, telemetry, or remote code.
- Features that publish without the review gate.
- Detector-evasion claims or features.
- Storing raw source text or contact details in Writing Styles.

## Design rules

| Rule | Why |
|---|---|
| `SKILL.md` stays under 500 lines and holds routing, hard rules and the workflow. Detail goes in `references/` one level deep. | Agents load the body whenever the skill triggers. Long bodies cost every run. |
| Frontmatter uses only `name`, `description`, `license`, `compatibility`, `metadata`. | These are portable across hosts. The description says what the skill does and when to use it, and names what it is not for. |
| Anything that can be counted or checked belongs in `cw.py`, not in prose. | Models miscount. Code does not. |
| Platform limits live only in `data/platform-specs.json`. After editing it, run `python3 skills/content-wand/scripts/maintainer/render_specs.py` so `references/platform-specs.md` matches. | One source of truth. `tests/test_repo.py` fails on drift. |
| Every `hard` or `policy` fact needs an official `source`. Secondary facts need a `note`. | Prevents folklore from becoming a rule. |
| Hooks fail open and stay inactive unless the skill is active. | A guard must never break unrelated work. |
| Denials and warnings are specific and short. | Users and agents act on clear reasons. |
| Untrusted text is never executed, followed or echoed into outputs. | See `references/security.md`. |

## Changing AI-pattern data

Edit `data/ai-patterns.json` through `scripts/maintainer/build_ai_patterns.py` and keep `references/ai-patterns.md` in sync. Add a case to `evals/data/humanizer.json` for each new pattern.

## Changing the update feed

Only the maintainer signs feeds. Use `scripts/maintainer/feed.py` as described in `docs/DISTRIBUTION.md`. Never commit a secret key.

## Pull requests

1. Branch from `main`.
2. Add tests or evals for behaviour you change.
3. Update `CHANGELOG.md` under `[Unreleased]`.
4. Fill in the pull request template.
5. For changes to workflow instructions, include the manual eval results described in `evals/README.md`.

## Conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
