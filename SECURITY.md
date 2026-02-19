# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Email: [baagad.ai@gmail.com](mailto:baagad.ai@gmail.com)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fix

You'll receive a response within 48 hours. If the issue is confirmed, a patch will be released and you'll be credited unless you prefer otherwise.

## Security model

content-wand is a Claude Agent Skill — it runs inside Claude's context window. The main security surface is the brand voice file:

### `.content-wand/brand-voice.json`

- **Opt-in only** — the file is never written without explicit user confirmation
- **Schema-validated on read** — any file with unknown keys is rejected outright, not parsed
- **Never stores raw content** — only extracted patterns (tone axes, style descriptors); never raw writing samples, URL-fetched text, credentials, or personal information
- **Project-scoped** — stored at `.content-wand/brand-voice.json` relative to the project, not in home or system directories
- **User-deletable** — deleting the file is the complete reset mechanism; no other cleanup required

## Known Architectural Constraints

### The Lethal Trifecta

content-wand simultaneously satisfies three properties that, in combination, create a structurally exploitable attack surface for prompt injection:

1. **Access to private data** — reads and writes `.content-wand/brand-voice.json` (personal voice data); writes files to `content-output/`
2. **Exposure to untrusted content** — fetches content from user-supplied URLs and WebSearch results
3. **Ability to communicate externally** — uses WebFetch and WebSearch

When all three are present, a sufficiently sophisticated prompt injection in fetched content could in theory instruct the skill to read and exfiltrate brand-voice data. This is an architectural property of content-wand's design, not a flaw that can be patched away.

**Mitigations in place:**
- Trust boundary model in SKILL.md — explicit rules for what external content can and cannot control
- Behavioral injection detection in content-ingester — heuristic scanning of fetched content
- Security sections in all sub-skills — reinforce that raw_text is data, not instructions
- Schema validation + string field scanning in brand-voice-extractor READ mode
- Delimiter guard preventing fake block injection

**Mitigations that are NOT in place (by design):**
- Cryptographic content signing (would require external infrastructure)
- LLM-independent deterministic injection detection (not possible in a pure markdown skill)
- Full trifecta elimination (would require removing core features)

**User recommendation:** Treat content-wand like any tool that processes untrusted web content. Do not use it on URLs you do not trust. The brand-voice.json file is local to your project — add `.content-wand/` to `.gitignore`.

---

### What this skill does NOT do

- It does not make network requests except via Claude's built-in WebFetch/WebSearch tools (used for URL fetching and topic research)
- It does not execute code during skill operation. The repository contains utility scripts (`assets/generate-pdf.js`, `assets/launch-slideshow.html`) for manual use only — these are not loaded or executed by Claude.
- It does not access files outside the project directory (content-output/ and .content-wand/ are project-relative)
- It does not transmit data to external services

### Recommended `.gitignore` entry

If you use content-wand in a version-controlled project, add:

```
.content-wand/
content-output/
```
