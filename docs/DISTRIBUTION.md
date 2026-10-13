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

## Channels

Findings from marketplace research dated 2026-10-13. Terms change, so confirm them before listing.

| Channel | Pays creators | Notes |
|---|---|---|
| Cursor marketplace | No | Publisher terms require open-source, permissive licences and forbid charging. Reach only. |
| Anthropic directory, skills.sh, SkillsMP | No | Free indexes. Anthropic scans each version, rejects over-broad hooks and undisclosed network calls, and checks that the description matches behaviour. |
| Agensi, SkillHQ, AgentPowers, MyClaude | Yes (roughly 70% to 92% creator share, varying) | Review each one's scan rules, payout terms and exclusivity. |
| Direct (Gumroad, Lemon Squeezy, Polar) | Yes | Full control of price and licence. You handle support and refunds. |

Marketplaces rely on traceability and scanning rather than copy protection. A licence check that phones home would conflict with content-wand's no-telemetry position and with directory rules on undisclosed network calls, so there is none.

## Scans to run before submitting

These tools were not run as part of the 2.0.0 build. Run them and publish the reports.

- A skill security scanner such as Cisco skill-scanner or Snyk Agent Scan.
- `claude plugin validate --strict` for the plugin layout. It does not catch every frontmatter error, so keep `tests/test_repo.py` in the gate.
- `skills-ref validate` (the reference validator) against `skills/content-wand/`.

Expect reviewers to look hardest at hooks, shell use and network calls. The README, `SECURITY.md` and `compatibility` frontmatter disclose all three.

## Decisions you must make before selling

1. **What is paid.** The repository is MIT, so anyone may legally copy and resell it. Sell something that is not simply the text: a Pro pack of extra references, templates and evals kept in a separate proprietary repository, signed data feeds, support, or client-ready services. Do not remove the MIT core from the public repository without checking the rights below.
2. **Rights to relicense.** Confirm that every contributor agreed to the licence change you want. Review `references/ai-patterns.md`, which lists research and a Wikipedia article among its sources. It contains pattern lists and original wording, not copied text, but confirm that with a quick read before a commercial release.
3. **Distributor terms.** Exclusivity, payout split, refunds, update obligations, liability, and who is merchant of record. The distributor was not identified in this research, so compare their offer against the table above.
4. **Entity, tax and trademark.** The name "content-wand" and any logo.
5. **Support promise.** Response times and which hosts you support.

## Licensing and support

The repository is MIT licensed. If a distributor requires a different commercial licence, decide that before listing and keep the licence field in `SKILL.md`, the manifests and `LICENSE` consistent. Support routes are in `SUPPORT.md` and security reporting is in `SECURITY.md`.

## Listing assets worth preparing

- A 60 second recording of one source becoming three platform outputs, then the review packet.
- A before and after of a flagged unsupported claim.
- The `check_release.py` output and `SHA256SUMS`.
- A one-page summary of the security model from `SECURITY.md`.
