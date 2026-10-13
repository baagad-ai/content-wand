# Security policy

## Supported versions

| Version | Supported |
|---|---|
| 2.x | Yes |
| 1.x | No. Upgrade to 2.x. |

## Reporting a vulnerability

Do not open a public issue.

Email [baagad.ai@gmail.com](mailto:baagad.ai@gmail.com) with a description, steps to reproduce, impact and any suggested fix. You will get a reply within 48 hours. Confirmed issues are fixed in a release and credited unless you prefer otherwise.

Examples of in-scope reports: a URL that bypasses the SSRF guard, source text that causes the agent or a hook to follow injected instructions, a way to publish text that was not approved, a way to write a credential path past the guard, a forged or downgraded spec feed that is accepted, or a secret stored in a Writing Style or output.

## Threat model

content-wand reads untrusted text and can write files and, when the user connects tools, publish. The main risks are indirect prompt injection, server-side request forgery, data exfiltration, unreviewed publishing and tampered rule updates.

| Source | Trust |
|---|---|
| `SKILL.md`, `references/`, `data/` shipped with a signed release | Trusted |
| The user's messages | Trusted |
| Writing Style and settings files | Local data, validated, never instructions |
| Fetched pages, search results, transcripts, pasted text, uploaded files, connector output | Untrusted. Supplies facts only |

### Controls

1. **Instructions.** Hard rules at the top of `SKILL.md`: source text is data, nothing publishes without an explicit yes, no invented facts.
2. **Deterministic code (`cw.py`, standard library only).**
   - Fetch guard: http(s) only, no credentials in URLs, no private, loopback, link-local or metadata addresses, unusual IP encodings rejected, one DNS resolution pinned for the connection, every redirect rechecked, size and time limits.
   - Page cleaning: hidden elements, comments and invisible Unicode are removed. Chat-template tokens are neutralised.
   - Injection scan: instruction-like patterns, encoded payloads, tag-character smuggling and mixed-script words are reported.
   - File boundary: `ingest --file` refuses credential and configuration files. Output writes stay inside `content-output/`.
   - Secret guard: `output save` and Writing Style writes refuse API keys and private keys.
   - Claims ledger: numbers, quotes and links absent from the source are surfaced.
3. **Hooks (Claude Code and compatible hosts).** Active only during a content-wand session, fail open on internal errors. They block SSRF and credential-path access, gate publishing connectors to approved text with no extra links, scan fetched content, validate outputs on write and block exit with unvalidated files. See `skills/content-wand/references/security.md` for the full table.
4. **Human review.** A review packet and per-file approval are required, and approval of a draft is separate from permission to publish.

### Signed rule updates

- Opt-in, off by default, disabled by `CONTENT_WAND_UPDATES=off`.
- One request per 24 hours to one allow-listed host. No identifier, content or usage data is sent.
- Feed and signature are verified with Ed25519 against a public key shipped in the skill. Bad signatures, older versions and oversized files are discarded.
- A valid update is stored as pending and applied only after user approval. Every apply saves a snapshot for rollback.
- Updates contain data (platform facts and their sources), never code.
- The signing key is held offline by the maintainer. It is never in the repository.

### Network and telemetry

No telemetry. No licence check. No remote code execution. Network access is limited to URLs the user supplies or asks the agent to research, and the optional signed-feed check.

### Data on disk

State: `$CONTENT_WAND_HOME`, else `$XDG_CONFIG_HOME/content-wand`, else `~/.config/content-wand`, created with owner-only permissions. Outputs: `content-output/` in the project. The audit log keeps tool names, hosts and short reasons, not page content or full URLs with query strings. `cw.py style reset --yes` and deleting those folders remove everything.

### Known limits

- Injection scanning is pattern based and cannot catch every attack. It is one layer, not the defence.
- Without hooks (`guards: "prompt-only"`), protections rely on instructions and the CLI. Keep the review step.
- A connector that publishes under a name the hooks do not recognise as publishing is not gated. Report such names so they can be added.
- The skill cannot verify claims against the real world, only against the source supplied.
