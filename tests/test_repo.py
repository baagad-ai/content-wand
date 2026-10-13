"""Repository integrity: the skill spec, generated files, manifests and version agreement."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import unittest

from helpers import REPO, SCRIPTS, SKILL

from cwlib import __version__  # noqa: E402

ALLOWED_FRONTMATTER = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert match, "SKILL.md must start with YAML frontmatter"
    fields: dict = {}
    current = None
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and current is not None:
            key, _, value = line.strip().partition(":")
            fields[current][key] = value.strip().strip('"')
        else:
            key, _, value = line.partition(":")
            value = value.strip()
            if value == "":
                fields[key] = {}
                current = key
            else:
                fields[key] = value.strip('"')
                current = None
    return fields, text[match.end():]


class SkillSpec(unittest.TestCase):
    def setUp(self) -> None:
        self.fm, self.body = frontmatter(SKILL / "SKILL.md")
        self.text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_frontmatter_is_spec_only(self) -> None:
        self.assertEqual(set(self.fm) - ALLOWED_FRONTMATTER, set())
        for required in ("name", "description"):
            self.assertIn(required, self.fm)

    def test_name_matches_folder_and_format(self) -> None:
        self.assertEqual(self.fm["name"], SKILL.name)
        self.assertRegex(self.fm["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(self.fm["name"]), 64)

    def test_description_limits(self) -> None:
        d = self.fm["description"]
        self.assertLessEqual(len(d), 1024)
        self.assertGreater(len(d), 150)
        self.assertRegex(d, r"(?i)use when")

    def test_compatibility_and_metadata(self) -> None:
        self.assertLessEqual(len(self.fm["compatibility"]), 500)
        self.assertEqual(self.fm["metadata"]["version"], __version__)

    def test_body_budget(self) -> None:
        self.assertLess(len(self.text.splitlines()), 500)

    def test_every_reference_is_linked_and_exists(self) -> None:
        refs = sorted(p.name for p in (SKILL / "references").glob("*.md"))
        for name in refs:
            self.assertIn(f"`{name}`", self.text, f"{name} is not mentioned in SKILL.md")
        for name in re.findall(r"`references/([\w.-]+\.md)`", self.text):
            self.assertTrue((SKILL / "references" / name).exists(), name)

    def test_script_paths_in_skill_exist(self) -> None:
        for rel in set(re.findall(r"python3 (scripts/[\w./-]+\.py)", self.text)):
            self.assertTrue((SKILL / rel).exists(), rel)

    def test_every_cw_subcommand_used_in_docs_exists(self) -> None:
        help_text = subprocess.run([sys.executable, str(SCRIPTS / "cw.py"), "--help"], capture_output=True, text=True).stdout
        commands = set(re.findall(r"\{([a-z,-]+)\}", help_text)[0].split(","))
        docs = [SKILL / "SKILL.md", *(SKILL / "references").glob("*.md")]
        for doc in docs:
            for cmd in re.findall(r"cw\.py ([a-z][a-z-]+)", doc.read_text(encoding="utf-8")):
                self.assertIn(cmd, commands, f"{doc.name} mentions unknown command '{cmd}'")

    def test_no_stale_v1_vocabulary(self) -> None:
        stale = ("content-ingester", "platform-writer-SKILL", "brandvoice-schema", "VOICE-PROFILE", "CONTENT-OBJECT", "~/.claude/content-wand/styles")
        for doc in [SKILL / "SKILL.md", *(SKILL / "references").glob("*.md")]:
            body = doc.read_text(encoding="utf-8")
            for word in stale:
                if doc.name == "writing-style.md" and word == "~/.claude/content-wand/styles":
                    continue
                self.assertNotIn(word, body, f"{doc.name} still contains '{word}'")

    def test_no_retired_claims_are_stated_as_fact(self) -> None:
        data = json.loads((SKILL / "data" / "platform-specs.json").read_text())
        self.assertTrue(data.get("retired_claims"))
        body = "\n".join(p.read_text(encoding="utf-8") for p in (SKILL / "references").glob("*.md") if p.name != "platform-specs.md")
        for phrase in ("suppress 50", "reduce reach 50", "13.5x", "60-second limit", "Shorts are limited to 60", "maximum 1 link"):
            self.assertNotIn(phrase.lower(), body.lower(), phrase)


class Generated(unittest.TestCase):
    def test_platform_specs_markdown_is_in_sync(self) -> None:
        proc = subprocess.run([sys.executable, str(SCRIPTS / "maintainer" / "render_specs.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_ai_patterns_json_is_in_sync(self) -> None:
        proc = subprocess.run([sys.executable, str(SCRIPTS / "maintainer" / "build_ai_patterns.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class Packaging(unittest.TestCase):
    def load(self, rel: str):
        return json.loads((REPO / rel).read_text(encoding="utf-8"))

    def test_versions_agree(self) -> None:
        for rel in (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json", "package.json"):
            self.assertEqual(self.load(rel)["version"], __version__, rel)

    def test_marketplace_entry_matches_plugin(self) -> None:
        m = self.load(".claude-plugin/marketplace.json")
        p = self.load(".claude-plugin/plugin.json")
        self.assertEqual(m["plugins"][0]["name"], p["name"])
        self.assertEqual(m["plugins"][0]["source"], "./")

    def test_hooks_manifest_points_at_real_script(self) -> None:
        hooks = self.load("hooks/hooks.json")["hooks"]
        self.assertEqual(set(hooks), {"SessionStart", "UserPromptExpansion", "PreToolUse", "PostToolUse", "Stop"})
        handlers = {"session_start", "user_prompt_expansion", "pre_tool_use", "post_tool_use", "stop"}
        seen = set()
        for event, groups in hooks.items():
            for group in groups:
                for h in group["hooks"]:
                    self.assertEqual(h["type"], "command")
                    self.assertIn("${CLAUDE_PLUGIN_ROOT}/skills/content-wand/scripts/run-hook.sh", h["command"])
                    self.assertLessEqual(h["timeout"], 30)
                    seen.add(h["command"].split()[-1])
        self.assertEqual(seen, handlers)
        self.assertTrue((SCRIPTS / "run-hook.sh").exists())

    def test_hook_matchers_are_valid_regexes(self) -> None:
        for groups in self.load("hooks/hooks.json")["hooks"].values():
            for group in groups:
                if "matcher" in group:
                    re.compile(group["matcher"])

    def test_scripts_use_only_the_standard_library(self) -> None:
        stdlib = set(sys.stdlib_module_names)
        local = {"cwlib"} | {p.stem for p in SCRIPTS.glob("*.py")}
        for path in SCRIPTS.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module.split(".")[0]]
                for n in names:
                    self.assertTrue(n in stdlib or n in local, f"{path.name} imports non-stdlib module {n}")

    def test_no_obfuscation_or_dynamic_execution(self) -> None:
        banned = re.compile(r"\b(eval|exec)\(|__import__\(|compile\(|marshal\.|pickle\.|base64\.b64decode\([^)]*\)\s*\)\s*\)\s*$")
        for path in SCRIPTS.rglob("*.py"):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if banned.search(line) and "re.compile" not in line:
                    self.fail(f"{path.name}:{lineno}: {line.strip()}")

    def test_network_calls_are_confined(self) -> None:
        allowed = {"ingest.py", "updater.py", "urlguard.py"}
        pattern = re.compile(r"\b(urllib\.request|http\.client|socket\.create_connection|requests\.|urlopen)\b")
        for path in (SCRIPTS / "cwlib").glob("*.py"):
            if pattern.search(path.read_text(encoding="utf-8")):
                self.assertIn(path.name, allowed, f"{path.name} opens network connections")

    def test_no_secrets_committed(self) -> None:
        secret = re.compile(r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|content-wand-feed\.secret)")
        for path in SKILL.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".md", ".json", ".sh", ".b64"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                for m in secret.finditer(text):
                    if path.name == "feed.py" or "test" in path.name:
                        continue
                    self.fail(f"{path.relative_to(REPO)} contains {m.group(0)[:20]}")


if __name__ == "__main__":
    unittest.main()
