# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Email: [baagad.ai](mailto:baagad.ai@gmail.com)

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

### What this skill does NOT do

- It does not make network requests except via Claude's built-in WebFetch/WebSearch tools
- It does not execute code
- It does not access files outside the project directory
- It does not transmit data to external services

### Recommended `.gitignore` entry

If you use content-wand in a version-controlled project, add:

```
.content-wand/
content-output/
```
