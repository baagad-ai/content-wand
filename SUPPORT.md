# Getting support

## Quick answers

- Installation, commands and workflows: [`README.md`](README.md).
- Twelve ready-made workflows: [`skills/content-wand/references/use-cases.md`](skills/content-wand/references/use-cases.md).
- Something looks wrong with limits or rules: run `python3 scripts/cw.py preflight` from the skill folder and check `specs`. Platform rules can change faster than releases, see [`references/spec-refresh.md`](skills/content-wand/references/spec-refresh.md).

## Diagnose a problem

```bash
python3 scripts/cw.py preflight     # environment, guards, stale rules, style state
python3 scripts/cw.py audit tail    # recent hook decisions (Claude Code plugin)
```

`guards: "prompt-only"` means hooks are not active on this host. That is normal outside Claude Code.

## Report a bug

[Open an issue](https://github.com/baagad-ai/content-wand/issues/new?template=bug_report.md). Include the host and version, the `preflight` output, the prompt, and what happened. Remove private content first.

## Request a feature

[Open a feature request](https://github.com/baagad-ai/content-wand/issues/new?template=feature_request.md).

## Security issues

Do not use public issues. See [`SECURITY.md`](SECURITY.md).

## Commercial and distributor questions

See [`docs/DISTRIBUTION.md`](docs/DISTRIBUTION.md). Contact: [@baagad_ai on X](https://x.com/baagad_ai).
