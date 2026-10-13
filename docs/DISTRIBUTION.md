# Distribution guide

How to prepare, verify and ship content-wand through a skill marketplace or a direct sale.

## What a buyer receives

| Artifact | Contents | Use |
|---|---|---|
| `content-wand-skill-<version>.zip` | The `content-wand/` skill folder only | Upload to claude.ai or marketplaces, or unzip into any skills directory. |
| `content-wand-plugin-<version>.zip` | Plugin layout with manifests and hooks | Claude Code and Cursor plugin installs. |
| `SHA256SUMS`, `manifest.json` | Hashes for both archives and every file | Integrity proof for distributors and buyers. |

Archives are reproducible: building twice yields identical bytes. They exclude tests, evals, docs, caches and any secret-looking file.

## Pre-release checklist

1. Run `python3 scripts/check_release.py`. It must print `release gate passed`.
2. Re-verify platform facts that `preflight` lists as stale. Cite official sources. Re-render with `scripts/maintainer/render_specs.py` and bump `data_version`.
3. Run the manual evals in `evals/README.md` on at least two model families and record the results.
4. Bump the version in `skills/content-wand/scripts/cwlib/__init__.py`, the `SKILL.md` metadata, `package.json`, `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json`. `tests/test_repo.py` fails if they differ.
5. Update `CHANGELOG.md`.
6. Build with `python3 scripts/package.py`, publish `dist/` with the tag, and give the distributor the `SHA256SUMS`.

## Enabling the signed update feed

The feed is inert until you create a signing key. Do this once, on an offline or protected machine.

```bash
python3 skills/content-wand/scripts/maintainer/feed.py keygen --out ~/.content-wand-publisher
```

It writes `content-wand-feed.secret` (mode 0600) to the output folder and the public key to `skills/content-wand/data/updater-pubkey.b64`. Commit the public key only. Keep the secret key out of the repository and out of CI logs.

For each data release:

```bash
# edit data/platform-specs.json after checking official sources, bump data_version
python3 skills/content-wand/scripts/maintainer/feed.py build --summary "Re-verified LinkedIn limits"
python3 skills/content-wand/scripts/maintainer/feed.py sign --key ~/.content-wand-publisher/content-wand-feed.secret
python3 skills/content-wand/scripts/maintainer/feed.py verify
```

Commit `feed/specs-feed.json` and `feed/specs-feed.json.sig`. Clients that opted in pick it up within 24 hours and ask their user before applying.

Rotate the key by shipping a new release with a new public key. Old clients keep working with shipped data.

## Distributor questions and answers

| Question | Answer |
|---|---|
| Does it call home? | No telemetry and no licence check. The only optional request is a daily signed-feed check, off by default, to one allow-listed host, with no identifiers. |
| Does it run remote code? | No. Updates carry data only and are verified with Ed25519. |
| What does it need? | Python 3.9+ standard library. No packages. |
| What does it write? | `content-output/` in the project and a state folder with owner-only permissions. |
| Can it post by itself? | No. Publishing needs a separate explicit request, the final text shown, and, with hooks, a match with approved text. |
| How does it handle hostile web pages? | SSRF-safe fetch, hidden-text stripping, injection scan, and rules that treat source text as data. |
| Which hosts? | Any host that supports Agent Skills. Hooks are Claude Code only. |
| How are claims about platform limits kept honest? | Typed, dated, sourced facts with review windows and a validated update path. |

## Positioning for buyers

Lead with outcomes that are checkable rather than adjectives.

- Review time drops because limits, counts and unsupported claims are checked before a person sees the draft.
- Risk is lower because nothing publishes without approval and source text cannot steer the agent.
- Output improves with use because a Writing Style is saved and applied.
- It does not promise to beat AI detectors and does not claim guaranteed reach. Say so in listings. It is both accurate and a trust signal.

## Licensing and support

The repository is MIT licensed. If a distributor requires a different commercial licence, decide that before listing and keep the licence field in `SKILL.md`, the manifests and `LICENSE` consistent. Support routes are in `SUPPORT.md` and security reporting is in `SECURITY.md`.

## Listing assets worth preparing

- A 60 second recording of one source becoming three platform outputs, then the review packet.
- A before and after of a flagged unsupported claim.
- The `check_release.py` output and `SHA256SUMS`.
- A one-page summary of the security model from `SECURITY.md`.
