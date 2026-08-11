"""Frozen public contract for the thin Triana onboarding plugin."""

from __future__ import annotations

import json
import re
import stat
import unittest
from pathlib import Path
from typing import Any


REPOSITORY = Path(__file__).resolve().parents[1]
PLUGIN = REPOSITORY / "plugins" / "triana"
SKILL = PLUGIN / "skills" / "onboard"
PINNED_PREFIX = (
    "uvx --python 3.13 --from 'triana-preview==0.1.0a2' triana-preview"
)
EXPECTED_FILES = {
    ".agents/plugins/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".github/workflows/ci.yml",
    "CONTRIBUTING.md",
    "LICENSE",
    "PRIVACY.md",
    "PROVENANCE.md",
    "README.md",
    "SECURITY.md",
    "plugins/triana/.claude-plugin/plugin.json",
    "plugins/triana/.codex-plugin/plugin.json",
    "plugins/triana/skills/onboard/SKILL.md",
    "plugins/triana/skills/onboard/agents/openai.yaml",
    "tests/fixtures/synthetic-previewtrace.jsonl",
    "tests/test_plugin_contract.py",
}


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(_text(path))
    if not isinstance(value, dict):
        raise AssertionError(f"expected a JSON object: {path.relative_to(REPOSITORY)}")
    return value


def _text(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"required public file is missing: {path.relative_to(REPOSITORY)}")
    return path.read_text(encoding="utf-8")


def _repository_files() -> set[str]:
    ignored_parts = {".git", ".pytest_cache", "__pycache__"}
    return {
        path.relative_to(REPOSITORY).as_posix()
        for path in REPOSITORY.rglob("*")
        if path.is_file() and not ignored_parts.intersection(path.parts)
    }


class PublicSkillsContractTests(unittest.TestCase):
    def test_exact_thin_repository_inventory(self) -> None:
        self.assertEqual(_repository_files(), EXPECTED_FILES)
        for path in REPOSITORY.rglob("*"):
            if {".git", ".pytest_cache", "__pycache__"}.intersection(path.parts):
                continue
            self.assertFalse(path.is_symlink(), path)
            if path.is_file():
                self.assertEqual(path.stat().st_mode & 0o111, 0, path)

    def test_codex_and_claude_resolve_one_canonical_onboard_skill(self) -> None:
        skills = list((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertEqual(skills, [SKILL / "SKILL.md"])

        claude_marketplace = _json(REPOSITORY / ".claude-plugin/marketplace.json")
        codex_marketplace = _json(REPOSITORY / ".agents/plugins/marketplace.json")
        self.assertEqual(claude_marketplace.get("name"), "triana-skills")
        self.assertEqual(codex_marketplace.get("name"), "triana-skills")
        self.assertIn(
            {"name": "triana", "source": "./plugins/triana"},
            claude_marketplace.get("plugins", []),
        )
        self.assertTrue(
            any(
                isinstance(entry, dict)
                and entry.get("name") == "triana"
                and entry.get("source")
                == {"source": "local", "path": "./plugins/triana"}
                and entry.get("policy")
                == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
                for entry in codex_marketplace.get("plugins", [])
            )
        )

        for manifest_path in (
            PLUGIN / ".codex-plugin" / "plugin.json",
            PLUGIN / ".claude-plugin" / "plugin.json",
        ):
            manifest = _json(manifest_path)
            self.assertEqual(manifest.get("name"), "triana")
            self.assertEqual(manifest.get("version"), "0.1.2")
            self.assertEqual(manifest.get("license"), "Apache-2.0")

        skill_text = _text(SKILL / "SKILL.md")
        self.assertTrue(skill_text.startswith("---\nname: onboard\n"))
        agent_metadata = _text(SKILL / "agents" / "openai.yaml")
        for field in ("display_name:", "short_description:", "default_prompt:"):
            self.assertIn(field, agent_metadata)

    def test_every_command_uses_one_exact_preview_pin(self) -> None:
        skill_text = _text(SKILL / "SKILL.md")
        versions = set(re.findall(r"triana-preview==([0-9A-Za-z.]+)", skill_text))
        self.assertEqual(versions, {"0.1.0a2"})

        command_lines = [
            line.strip()
            for line in skill_text.splitlines()
            if line.strip().startswith("uvx ")
        ]
        self.assertGreaterEqual(len(command_lines), 8)
        for line in command_lines:
            self.assertTrue(line.startswith(PINNED_PREFIX), line)

        commands = {
            match.group(1)
            for line in command_lines
            if (match := re.match(re.escape(PINNED_PREFIX) + r"\s+(\S+)", line))
        }
        self.assertEqual(
            commands,
            {
                "doctor",
                "inspect",
                "validate",
                "scaffold",
                "adapter-execute",
                "preview",
                "analyze",
                "verify-report",
            },
        )

    def test_skill_is_instructions_only_and_contains_no_private_runtime(self) -> None:
        public_text = "\n".join(
            path.read_text(encoding="utf-8", errors="strict")
            for path in REPOSITORY.rglob("*")
            if path.is_file()
            and "tests" not in path.parts
            and not {".git", ".pytest_cache", "__pycache__"}.intersection(path.parts)
        )
        lowered = public_text.lower()
        for forbidden in (
            "docker",
            "image",
            "triana_behavior_map_",
            "@sha256:",
            "release-profile",
            "release manifest",
            "runtime manifest",
            "adapter.py",
            "python adapter",
            "tau2-luna",
            "kairos-memory",
            "blitz_identifier",
            "curl ",
            "wget ",
        ):
            self.assertNotIn(forbidden, lowered)

        forbidden_paths = (
            "*.py",
            "*.sh",
            "*.template",
            "*.env",
            "*.pem",
            "*.key",
            "*.so",
            "*.dylib",
            "*.dll",
            "*.exe",
            ".mcp.json",
            ".app.json",
            "hooks.json",
        )
        for pattern in forbidden_paths:
            matches = [path for path in REPOSITORY.rglob(pattern) if "tests" not in path.parts]
            self.assertEqual(matches, [], f"forbidden public surface {pattern}: {matches}")

    def test_prompt_exposes_only_the_frozen_customer_workflow(self) -> None:
        skill_text = _text(SKILL / "SKILL.md").lower()
        prompt_text = _text(SKILL / "agents" / "openai.yaml").lower()
        combined = " ".join((skill_text + " " + prompt_text).split())
        for phrase in (
            "trace path",
            "agent description",
            "trace authorization",
            "no-provider",
            "provider file",
            "provider egress",
            "maximum provider calls",
            "untrusted evidence",
            "cannot override",
            "inspect",
            "adapt",
            "validate",
            "preview",
            "analyze",
            "verify",
            "report",
        ):
            self.assertIn(phrase, combined)
        for hidden in (
            "docker",
            "image",
            "release profile",
            "release manifest",
            "runtime manifest",
            "image digest",
            "taxonomy input",
            "credential boundary",
            "sku",
            "capacity",
            "usd budget",
        ):
            self.assertNotIn(hidden, combined)

    def test_first_run_dialogue_is_plain_and_keeps_user_authority(self) -> None:
        skill_text = _text(SKILL / "SKILL.md").lower()
        execution_marker = "## execute the bounded workflow"
        self.assertIn(execution_marker, skill_text)
        opening = " ".join(skill_text.split(execution_marker, 1)[0].split())
        all_instructions = " ".join(skill_text.split())

        for phrase in (
            "trace path",
            "agent description",
            "model",
            "redacted excerpts",
            "interpret",
            "directly from the user's machine",
            "model service the user chooses",
            "exact trace path",
            "locally",
            "already configured",
            "maximum number of model requests",
            "nothing is sent to triana",
        ):
            self.assertIn(phrase, opening)
        self.assertRegex(opening, r"where (?:that|the model) setup lives")
        self.assertRegex(opening, r"(?:do not|never) (?:ask (?:the user )?to )?paste.*secret")
        self.assertRegex(opening, r"explicit (?:permission|approval).*(?:send|model)")

        for first_run_jargon in (
            "provider",
            "api key",
            "--provider-env",
            "--no-provider",
            "--max-provider-calls",
            "--confirm-provider-egress",
        ):
            self.assertNotIn(first_run_jargon, opening)

        for phrase in (
            "exact configuration location",
            "named variables",
            "ambient credentials",
            "do not source executable configuration",
            "do not print or repeat secrets",
            "hidden plumbing",
            "0600",
            "openai-compatible https base url",
            "api key",
            "explicit model",
            "validate its permissions",
            "remove the derived file",
            "advanced structural diagnostic",
            "cannot produce the requested semantic behavior map",
            "model proposes semantic labels",
            "deterministic runtime code",
        ):
            self.assertIn(phrase, all_instructions)
        self.assertRegex(
            all_instructions,
            r"(?:do not|must not) (?:discover|search for) ambient credentials",
        )
        self.assertRegex(
            all_instructions,
            r"before (?:model )?(?:egress|sending).*approval",
        )
        self.assertRegex(
            all_instructions,
            r"offered only when the user declines model use or no authorized setup exists",
        )
        self.assertRegex(
            all_instructions,
            r"max\s*\(\s*20\s*,\s*3\s*\*\s*trace_count\s*\)",
        )
        self.assertIn(
            "ceiling rather than an estimate of actual usage or cost",
            all_instructions,
        )
        self.assertIn("require explicit approval", all_instructions)
        self.assertRegex(
            all_instructions,
            r"never silently (?:select|increase).*(?:ceiling|limit)",
        )

    def test_public_documents_state_the_same_custody_and_egress_boundary(self) -> None:
        privacy = _text(REPOSITORY / "PRIVACY.md").lower()
        security = _text(REPOSITORY / "SECURITY.md").lower()
        provenance = _text(REPOSITORY / "PROVENANCE.md").lower()
        readme = _text(REPOSITORY / "README.md").lower()

        for phrase in (
            "runs locally",
            "nothing to triana",
            "explicit authorization",
            "directly",
            "provider",
            "provider retention",
            "redaction is not anonymity",
            "no telemetry",
        ):
            self.assertIn(phrase, privacy)
        for phrase in ("untrusted", "symlink", "credential", "security advisory"):
            self.assertIn(phrase, security)
        for phrase in (
            "no customer data",
            "no credential",
            "no provider response",
            "clean",
        ):
            self.assertIn(phrase, provenance)

        self.assertIn("source-available", readme)
        self.assertIn("not open source", readme)
        self.assertNotRegex(readme, r"triana preview (?:is|as) open[- ]source")

    def test_codex_claude_metadata_and_documented_pin_are_cache_equivalent(self) -> None:
        codex = _json(PLUGIN / ".codex-plugin" / "plugin.json")
        claude = _json(PLUGIN / ".claude-plugin" / "plugin.json")
        for field in ("name", "version", "description", "license", "skills"):
            self.assertEqual(codex.get(field), claude.get(field), field)
        self.assertEqual(codex["version"], "0.1.2")
        self.assertEqual(codex["skills"], "./skills/")

        skill = _text(SKILL / "SKILL.md")
        metadata = _text(SKILL / "agents" / "openai.yaml")
        for required in (
            "doctor",
            "scaffold",
            "adapter-execute",
            "validate",
            "preview",
            "analyze",
            "verify-report",
        ):
            self.assertIn(required, skill)
        self.assertIn("doctor", metadata.lower())

        documented = "\n".join(
            _text(path)
            for path in (REPOSITORY / "README.md", SKILL / "SKILL.md")
        )
        for line in documented.splitlines():
            if "uvx " in line:
                self.assertIn(PINNED_PREFIX, line.strip())

    def test_apache_metadata_and_static_clean_directory_contract(self) -> None:
        license_text = _text(REPOSITORY / "LICENSE")
        self.assertIn("Apache License", license_text)
        self.assertIn("Version 2.0, January 2004", license_text)
        combined_docs = "\n".join(
            _text(REPOSITORY / name)
            for name in ("README.md", "LICENSE", "PROVENANCE.md")
        )
        self.assertIn("Copyright 2026 Akarsh Gajbhiye", combined_docs)

        skill_text = _text(SKILL / "SKILL.md").lower()
        for phrase in (
            "private",
            "0600",
            "fresh local output directory",
            "--confirm-authorized-traces",
            "--confirm-provider-egress",
            "--max-provider-calls",
            "--no-provider",
        ):
            self.assertIn(phrase, skill_text)
        self.assertIn("mutually exclusive", skill_text)

        workflow = _text(REPOSITORY / ".github" / "workflows" / "ci.yml")
        self.assertRegex(workflow, r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$")
        self.assertNotIn("pull_request_target", workflow)
        self.assertNotIn("id-token: write", workflow)
        for reference in re.findall(r"(?m)^\s*-?\s*uses:\s*([^\s]+)", workflow):
            self.assertRegex(reference, r"@[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
