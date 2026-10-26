"""Offline V1.3 SHA/metadata evidence preflight security regression suite."""

import importlib.util
from pathlib import Path
import unittest


MODULE = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "bridge_evidence.py"
spec = importlib.util.spec_from_file_location("bridge_evidence", MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

REPO = "example/my-app"
PR = 12
TESTED = "a" * 40
REPORT = "b" * 40
PATH = ".ai-collab/reports/PR-12-aaaaaaa-a1.md"


def event(action="synchronize", fork=False, draft=False, handoff=True):
    repo = "other/fork" if fork else REPO
    return {"action": action, "repository": {"full_name": REPO},
            "pull_request": {
                "number": PR, "state": "open", "draft": draft,
                "head": {"repo": {"full_name": repo}, "sha": REPORT},
                "base": {"repo": {"full_name": REPO}},
                "body": ("[AI_DEV_BRIDGE_HANDOFF]\n"
                         "[/AI_DEV_BRIDGE_HANDOFF]" if handoff else "no handoff")}}


def report(tested=TESTED, attempt=1, tests="PASS", exit_code="0",
           overall="PASS", failure="NONE", command="python3 -m unittest"):
    return "\n".join((
        "[WORKBUDDY_EXECUTION_REPORT]",
        "Protocol: 1.3",
        "Repository: " + REPO,
        "PR: https://github.com/{}/pull/{}".format(REPO, PR),
        "Attempt: " + str(attempt),
        "Tested Commit SHA: " + tested,
        "Environment: Windows; Python 3.13",
        "Build: N/A",
        "Tests: " + tests,
        "Test command: " + command,
        "Test exit code: " + exit_code,
        "Failure category: " + failure,
        "Overall: " + overall,
        "Deployment: NOT ATTEMPTED",
        "Evidence: real exit codes reported by WorkBuddy",
        "",
    ))


def files(name=PATH):
    return [{"filename": name, "status": "added"}]


def compare(items=None):
    return {"status": "ahead", "files": files() if items is None else items}


class FakeApi:
    def __init__(self, file_list=None, content=None, comparison=None):
        self.file_list = file_list if file_list is not None else files()
        self.content = content if content is not None else report()
        self.comparison = comparison if comparison is not None else compare()
        self.calls = []

    def pr_files(self, number):
        self.calls.append("files")
        return self.file_list

    def report(self, sha, path):
        self.calls.append("report")
        return self.content

    def compare(self, sha, head):
        self.calls.append("compare")
        return self.comparison


class EvidenceGateTests(unittest.TestCase):
    def test_valid_report_only_lineage(self):
        result = gate.inspect_event(event(), REPO, FakeApi())
        self.assertEqual(result["state"], "EVIDENCE_READY")
        self.assertEqual(result["tested_sha"], TESTED)
        self.assertIn("NOT proof", gate.summary(result))

    def test_waiting_is_not_test_pass(self):
        result = gate.inspect_event(event(), REPO, FakeApi(file_list=[]))
        self.assertEqual(result["state"], "WAITING_FOR_REPORT")
        self.assertNotIn("PASS", gate.summary(result))

    def test_fork_is_skipped_without_api(self):
        api = FakeApi()
        self.assertEqual(gate.inspect_event(event(fork=True), REPO, api)["state"], "SKIPPED")
        self.assertEqual(api.calls, [])

    def test_draft_is_skipped(self):
        self.assertEqual(gate.inspect_event(event(draft=True), REPO, FakeApi())["state"], "SKIPPED")

    def test_missing_handoff_is_skipped(self):
        self.assertEqual(gate.inspect_event(event(handoff=False), REPO, FakeApi())["state"], "SKIPPED")

    def test_removed_report_is_not_used(self):
        api = FakeApi(file_list=[{"filename": PATH, "status": "removed"}])
        self.assertEqual(gate.inspect_event(event(), REPO, api)["state"], "WAITING_FOR_REPORT")

    def test_legacy_name_for_old_protocol(self):
        self.assertEqual(gate.get_report_name(PR, ".ai-collab/reports/PR-12-aaaaaaa.md"), ("aaaaaaa", 1))

    def test_fake_report_path_rejected(self):
        self.assertIsNone(gate.get_report_name(PR, ".ai-collab/reports/PR-11-aaaaaaa-a1.md"))
        self.assertIsNone(gate.get_report_name(PR, ".ai-collab/reports/PR-12-aaaaaaa-a0.md"))

    def test_mismatched_sha_prefix_rejected(self):
        with self.assertRaisesRegex(gate.EvidenceError, "Tested SHA"):
            gate.parse_report(report(tested="c" * 40), REPO, PR, PATH)

    def test_missing_full_sha_rejected(self):
        with self.assertRaisesRegex(gate.EvidenceError, "Tested SHA"):
            gate.parse_report(report(tested="a" * 7), REPO, PR, PATH)

    def test_duplicate_field_rejected(self):
        with self.assertRaisesRegex(gate.EvidenceError, "Duplicate"):
            gate.parse_report(report() + "Overall: PASS\n", REPO, PR, PATH)

    def test_missing_field_rejected(self):
        with self.assertRaisesRegex(gate.EvidenceError, "Missing fields"):
            gate.parse_report(report().replace("Test command: python3 -m unittest\n", ""),
                              REPO, PR, PATH)

    def test_tests_pass_exit_code_inconsistent(self):
        with self.assertRaisesRegex(gate.EvidenceError, "Tests PASS"):
            gate.parse_report(report(exit_code="1"), REPO, PR, PATH)

    def test_overall_pass_when_test_fail_rejected(self):
        with self.assertRaisesRegex(gate.EvidenceError, "Overall PASS"):
            gate.parse_report(report(tests="FAIL", exit_code="1"), REPO, PR, PATH)

    def test_report_fail_can_still_be_structurally_verified(self):
        parsed = gate.parse_report(report(tests="FAIL", exit_code="1",
                                         overall="FAIL", failure="TEST"), REPO, PR, PATH)
        self.assertEqual(parsed["overall"], "FAIL")
        self.assertEqual(gate.inspect_event(
            event(), REPO, FakeApi(content=report(
                tests="FAIL", exit_code="1", overall="FAIL",
                failure="TEST")))["state"], "EVIDENCE_READY")

    def test_blocked_is_not_pass(self):
        parsed = gate.parse_report(report(tests="BLOCKED", exit_code="NOT RUN",
                                         overall="BLOCKED", failure="PERMISSION"),
                                   REPO, PR, PATH)
        self.assertEqual(parsed["overall"], "BLOCKED")

    def test_report_only_compare_required(self):
        modified = files() + [{"filename": "src/main.cpp", "status": "modified"}]
        with self.assertRaisesRegex(gate.EvidenceError, "Substantive"):
            gate.inspect_event(event(), REPO, FakeApi(comparison=compare(modified)))

    def test_wrong_ancestor_compare_rejected(self):
        with self.assertRaisesRegex(gate.EvidenceError, "not verifiably"):
            gate.inspect_event(event(), REPO, FakeApi(comparison={
                "status": "diverged", "files": files()}))

    def test_report_must_be_new_after_tested_sha(self):
        with self.assertRaisesRegex(gate.EvidenceError, "not actually added"):
            gate.inspect_event(event(), REPO, FakeApi(comparison=compare([
                {"filename": ".ai-collab/reports/PR-12-aaaaaaa-a0.md", "status": "added"}])))

    def test_modified_report_between_shas_rejected(self):
        with self.assertRaisesRegex(gate.EvidenceError, "not actually added"):
            gate.inspect_event(event(), REPO, FakeApi(comparison=compare([
                {"filename": PATH, "status": "modified"}])))

    def test_oversized_report_rejected(self):
        with self.assertRaisesRegex(gate.EvidenceError, "32 KiB"):
            gate.parse_report(report() + ("X" * 35000), REPO, PR, PATH)

    def test_duplicate_attempt_report_files_rejected(self):
        with self.assertRaisesRegex(gate.EvidenceError, "Ambiguous"):
            gate.choose_latest_report(files() + [{
                "filename": ".ai-collab/reports/PR-12-ccccccc-a1.md", "status": "added"
            }], PR)

    def test_no_real_run_in_summary(self):
        state = gate.inspect_event(event(), REPO, FakeApi())
        rendered = gate.summary(state)
        self.assertIn("NOT proof of execution", rendered)

    def test_newer_attempt_selected(self):
        path2 = ".ai-collab/reports/PR-12-aaaaaaa-a2.md"
        choice = gate.choose_latest_report(files() + [{"filename": path2, "status": "added"}], PR)
        self.assertEqual(choice, path2)


    def test_valid_windows_crlf_report(self):
        data = gate.parse_report(report().replace("\n", "\r\n"), REPO, PR, PATH)
        self.assertEqual(data["overall"], "PASS")

    def test_build_pass_with_failed_build_exit_is_invalid(self):
        broken = report().replace(
            "Build: N/A", "Build: PASS\nBuild command: make\nBuild exit code: 1"
        )
        with self.assertRaisesRegex(gate.EvidenceError, "Build PASS"):
            gate.parse_report(broken, REPO, PR, PATH)

    def test_build_pass_without_execution_details_is_invalid(self):
        with self.assertRaisesRegex(gate.EvidenceError, "Build PASS"):
            gate.parse_report(report().replace("Build: N/A", "Build: PASS"),
                              REPO, PR, PATH)

    def test_build_only_success_with_tests_na(self):
        valid = report(tests="N/A", exit_code="N/A", command="N/A").replace(
            "Build: N/A", "Build: PASS\nBuild command: make test\nBuild exit code: 0"
        )
        data = gate.parse_report(valid, REPO, PR, PATH)
        self.assertEqual(data["build"], "PASS")
        self.assertEqual(data["tests"], "N/A")
        self.assertEqual(data["overall"], "PASS")

    def test_all_checks_na_cannot_claim_success(self):
        invalid = report(tests="N/A", exit_code="N/A", command="N/A")
        with self.assertRaisesRegex(gate.EvidenceError, "Overall PASS"):
            gate.parse_report(invalid, REPO, PR, PATH)

    def test_failed_build_cannot_claim_overall_success(self):
        invalid = report().replace(
            "Build: N/A", "Build: FAIL\nBuild command: make\nBuild exit code: 2"
        )
        with self.assertRaisesRegex(gate.EvidenceError, "Overall PASS"):
            gate.parse_report(invalid, REPO, PR, PATH)

    def test_build_field_is_required(self):
        invalid = report().replace("Build: N/A\n", "")
        with self.assertRaisesRegex(gate.EvidenceError, "Missing fields"):
            gate.parse_report(invalid, REPO, PR, PATH)

    def test_build_blocked_with_zero_exit_rejected(self):
        invalid = report(tests="BLOCKED", exit_code="NOT RUN",
                         overall="BLOCKED", failure="PERMISSION").replace(
            "Build: N/A", "Build: BLOCKED\nBuild command: tool\nBuild exit code: 0"
        )
        with self.assertRaisesRegex(gate.EvidenceError, "Build BLOCKED"):
            gate.parse_report(invalid, REPO, PR, PATH)

    def test_not_run_tests_cannot_be_overall_pass_even_with_build_pass(self):
        invalid = report(tests="NOT RUN", exit_code="NOT RUN",
                         command="NOT RUN").replace(
            "Build: N/A", "Build: PASS\nBuild command: make\nBuild exit code: 0"
        )
        with self.assertRaisesRegex(gate.EvidenceError, "Overall PASS"):
            gate.parse_report(invalid, REPO, PR, PATH)



if __name__ == "__main__":
    unittest.main()
