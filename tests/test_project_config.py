"""Contract tests for the repository's fail-closed machine-readable config.

These tests validate configuration shape and safe defaults only. They do not
execute project commands or enable the WorkBuddy runner.
"""
import json
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPOSITORY_ROOT / ".ai-collab" / "PROJECT_CONFIG.json"
CONFIG_DOC_PATH = REPOSITORY_ROOT / ".ai-collab" / "PROJECT_CONFIG.md"

EXPECTED_KEYS = {
    "schema_version",
    "repository_allowlist",
    "base_branch",
    "required_opt_in_label",
    "execution_enabled",
    "workspace_profile",
    "workspace_root",
    "allowed_commands",
    "working_directory",
    "command_timeout_seconds",
    "writable_paths",
    "report_contract",
    "retry_policy",
    "deployment",
    "executor_profile",
    "multi_executor_mode",
}


class ProjectConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
            cls.config = json.load(config_file)

    def test_config_has_exact_supported_keys(self):
        self.assertIsInstance(self.config, dict)
        self.assertEqual(set(self.config.keys()), EXPECTED_KEYS)

    def test_schema_version_is_supported_integer(self):
        self.assertIs(type(self.config["schema_version"]), int)
        self.assertEqual(self.config["schema_version"], 1)

    def test_repository_and_base_branch_are_explicit(self):
        self.assertEqual(
            self.config["repository_allowlist"],
            ["zyzmlwxy/AI-Dev-Bridge-Lite"],
        )
        self.assertEqual(self.config["base_branch"], "main")
        self.assertEqual(
            self.config["required_opt_in_label"],
            "ai-bridge:execute",
        )

    def test_execution_is_fail_closed_by_default(self):
        self.assertIs(self.config["execution_enabled"], False)
        self.assertEqual(self.config["allowed_commands"], [])
        self.assertEqual(self.config["workspace_profile"], "UNCONFIGURED")
        self.assertIsNone(self.config["workspace_root"])
        self.assertIsNone(self.config["working_directory"])
        self.assertEqual(self.config["deployment"], "DISABLED")

    def test_human_readable_policy_mirrors_safety_critical_values(self):
        with CONFIG_DOC_PATH.open("r", encoding="utf-8") as doc_file:
            markdown = doc_file.read()

        expected_rows = (
            '| `repository_allowlist` | `["zyzmlwxy/AI-Dev-Bridge-Lite"]` |',
            "| `execution_enabled` | `false` |",
            "| `workspace_profile` | `UNCONFIGURED` |",
            "| `workspace_root` | `null` |",
            "| `allowed_commands` | `[]` |",
            "| `working_directory` | `null` |",
            '| `writable_paths` | `[".ai-collab/reports/"]` |',
            "| `deployment` | `DISABLED` |",
        )

        for row in expected_rows:
            with self.subTest(row=row):
                self.assertIn(row, markdown)

    def test_timeout_is_a_bounded_positive_integer(self):
        timeout = self.config["command_timeout_seconds"]
        self.assertIs(type(timeout), int)
        self.assertGreaterEqual(timeout, 1)
        self.assertLessEqual(timeout, 3600)

    def test_writable_paths_are_report_only(self):
        self.assertEqual(
            self.config["writable_paths"],
            [".ai-collab/reports/"],
        )
        self.assertEqual(self.config["report_contract"], "V1.3")
        self.assertEqual(self.config["retry_policy"], "NO_AUTOMATIC_RETRY")

    def test_executor_profile_keeps_future_extension_possible(self):
        self.assertEqual(
            self.config["executor_profile"],
            "SINGLE_ACTIVE_EXECUTOR",
        )
        self.assertEqual(self.config["multi_executor_mode"], "DEFERRED")


if __name__ == "__main__":
    unittest.main()
