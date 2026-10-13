# Tool map

`SKILL.md` names capabilities, not tools. Use the host's tool for each. If the host has no matching tool, use the fallback.

| Capability | Claude Code | Codex | Gemini CLI | Cursor | GitHub Copilot | OpenCode | Fallback |
|---|---|---|---|---|---|---|---|
| Run a shell command | `Bash` | shell | `run_shell_command` | `Shell` | shell | `bash` | Follow the steps by hand and say the automatic checks did not run. |
| Read a file | `Read` | shell read | `read_file` | `Read` | view | `read` | Ask the user to paste it. |
| Write a file | `Write`, `Edit` | `apply_patch` | `write_file`, `replace` | `Write`, `StrReplace` | edit, create | `write`, `edit` | Show the text in chat and ask the user to save it. |
| Fetch a URL | `WebFetch` | hosted web or shell | `web_fetch` | `WebFetch` | web fetch tool | `webfetch` | Use `cw.py ingest --url` if a shell exists, otherwise ask the user to paste the text. |
| Search the web | `WebSearch` | `web_search` | `google_web_search` | `WebSearch` | web search tool | `websearch` | Ask the user for source material. |
| Ask the user a question | ask in chat or the host question tool | ask in chat | ask in chat | ask in chat or question tool | ask in chat | `question` | Plain chat question. |

Tool names change between versions. Treat this as a guide and use whatever the host provides.

## Prefer `cw.py ingest` over a built-in fetch tool when a shell is available

It resolves the address once, blocks internal ranges, strips hidden text and scans for injected instructions in the same step. Built-in fetch tools return page text as the model would see it, with hidden text included on some hosts.

On Claude Code, WebFetch calls are also screened by the hooks when the plugin is installed.

## Hook support by host

| Host | Hooks | What content-wand does |
|---|---|---|
| Claude Code | Yes (plugin `hooks/hooks.json`) | Full guard set, see `security.md`. |
| Cursor | Different schema | The plugin ships the skill only. Prompt-only mode, and `preflight` activates the scripted checks. |
| Codex, Gemini CLI, Copilot, Windsurf, Kiro, Droid | Different schemas | Not shipped. Prompt-only mode. |
| OpenCode, Amp, Cline | Plugin systems | Not shipped. Prompt-only mode. |

The hook scripts read Claude Code's event format. Adapting them to another host means translating that host's event JSON, and nothing else in the skill depends on hooks.

Where there are no hooks, `preflight` reports `guards: "prompt-only"`. The scripts still do all counting, validation and claims checks, because the skill calls them directly.

## Where the skill is installed from

The folder is the same everywhere. The common locations are `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, `.gemini/skills/` and the user-level equivalents. Run the scripts relative to this skill's folder.

## Cloud and sandboxed runs

State in the home directory may not persist between runs. If `preflight` cannot write the state directory, say that Writing Styles and settings will not be saved, and offer to keep a style file in the project (`.content-wand/`). Set `CONTENT_WAND_HOME` to that folder.
