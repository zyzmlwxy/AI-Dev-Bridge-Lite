"""Offline V1.2 classification and idempotence tests (no GitHub API calls)."""

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "bridge_notify.py"
spec = importlib.util.spec_from_file_location("bridge_notify", MODULE_PATH)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

REPO = "example/my-app"
SHA1 = "a" * 40
SHA2 = "b" * 40
PR = 42
HANDOFF = (
    "[AI_DEV_BRIDGE_HANDOFF]\n"
    "Protocol: 1.1\n"
    "PR: https://github.com/example/my-app/pull/42\n"
    "[/AI_DEV_BRIDGE_HANDOFF]\n"
)


def event(action="opened", *, fork=False, draft=False, body=HANDOFF):
    headrepo = "another/fork" if fork else REPO
    result = {
        "action": action,
        "repository": {"full_name": REPO},
        "pull_request": {
            "number": PR,
            "draft": draft,
            "body": body,
            "head": {"repo": {"full_name": headrepo}, "sha": SHA2},
            "base": {"repo": {"full_name": REPO}},
        },
    }
    if action == "synchronize":
        result.update({"before": SHA1, "after": SHA2})
    return result


class FakeApi:
    def __init__(self, files=None, duplicate=False):
        self.files = files
        self.duplicate = duplicate
        self.posts = []
        self.compares = 0

    def compare(self, before, after):
        self.compares += 1
        assert (before, after) == (SHA1, SHA2)
        return self.files

    def already_notified(self, number, marker):
        assert number == PR
        assert SHA2 in marker
        return self.duplicate

    def post_comment(self, number, content):
        self.posts.append((number, content))


class NotificationTests(unittest.TestCase):
    def test_open_pr_creates_workbuddy_notification(self):
        api = FakeApi()
        result = bridge.process(event(), REPO, api)
        self.assertIn("POSTED: CODE_READY", result)
        self.assertEqual(len(api.posts), 1)
        self.assertIn("Next actor: WorkBuddy", api.posts[0][1])
        self.assertIn(SHA2, api.posts[0][1])

    def test_draft_is_ignored(self):
        api = FakeApi()
        self.assertIn("SKIPPED", bridge.process(event(draft=True), REPO, api))
        self.assertEqual(api.posts, [])

    def test_fork_is_ignored(self):
        api = FakeApi()
        self.assertIn("SKIPPED", bridge.process(event(fork=True), REPO, api))
        self.assertEqual(api.posts, [])

    def test_missing_handoff_is_ignored(self):
        api = FakeApi()
        self.assertIn("SKIPPED", bridge.process(event(body="hello"), REPO, api))
        self.assertEqual(api.posts, [])

    def test_duplicate_marker_prevents_comment(self):
        api = FakeApi(duplicate=True)
        self.assertIn("DUPLICATE", bridge.process(event(), REPO, api))
        self.assertEqual(api.posts, [])

    def test_report_only_sync_notifies_chatgpt(self):
        api = FakeApi(files=[{
            "filename": ".ai-collab/reports/PR-42-aaaaaaa-a1.md",
            "status": "added",
        }])
        result = bridge.process(event("synchronize"), REPO, api)
        self.assertIn("POSTED: REVIEW_PENDING", result)
        self.assertEqual(api.compares, 1)
        self.assertIn("Next actor: ChatGPT", api.posts[0][1])
        self.assertIn("NOT verified test success", api.posts[0][1])

    def test_legacy_v10_report_is_accepted(self):
        items = [{"filename": ".ai-collab/reports/PR-42-bbbbbbb.md", "status": "added"}]
        decision = bridge.classify(event("synchronize"), REPO, items)
        self.assertEqual(decision[0], "REVIEW_PENDING")

    def test_wrong_number_report_not_accepted(self):
        items = [{"filename": ".ai-collab/reports/PR-43-aaaaaaa-a1.md", "status": "added"}]
        self.assertEqual(bridge.classify(event("synchronize"), REPO, items)[0], "CODE_READY")

    def test_modified_report_not_accepted(self):
        items = [{"filename": ".ai-collab/reports/PR-42-aaaaaaa-a1.md", "status": "modified"}]
        self.assertEqual(bridge.classify(event("synchronize"), REPO, items)[0], "CODE_READY")

    def test_report_and_source_change_notifies_workbuddy(self):
        items = [
            {"filename": ".ai-collab/reports/PR-42-aaaaaaa-a1.md", "status": "added"},
            {"filename": "src/parser.cpp", "status": "modified"},
        ]
        self.assertEqual(bridge.classify(event("synchronize"), REPO, items)[0], "CODE_READY")

    def test_empty_compare_skips(self):
        api = FakeApi(files=[])
        self.assertIn("SKIPPED", bridge.process(event("synchronize"), REPO, api))
        self.assertEqual(api.posts, [])

    def test_missing_compare_blocks_without_guess(self):
        with self.assertRaises(bridge.NotificationError):
            bridge.classify(event("synchronize"), REPO)

    def test_mismatched_after_sha_blocks(self):
        e = event("synchronize")
        e["after"] = SHA1
        with self.assertRaises(bridge.NotificationError):
            bridge.process(e, REPO, FakeApi(files=[]))

    def test_invalid_head_sha_blocks(self):
        e = event()
        e["pull_request"]["head"]["sha"] = "not-a-sha"
        with self.assertRaises(bridge.NotificationError):
            bridge.classify(e, REPO)

    def test_dry_run_does_not_post(self):
        api = FakeApi()
        output = bridge.process(event(), REPO, api, dry_run=True)
        self.assertIn("DRY_RUN:", output)
        self.assertEqual(api.posts, [])

    def test_handoff_body_is_never_executed_or_echoed(self):
        api = FakeApi()
        e = event(body=HANDOFF + "\nmalicious $(rm -rf /) text")
        bridge.process(e, REPO, api)
        self.assertNotIn("rm -rf", api.posts[0][1])

    def test_disabled_action_skipped(self):
        self.assertIn("SKIPPED", bridge.process(event("closed"), REPO, FakeApi()))

    def test_only_exact_report_filename(self):
        self.assertFalse(bridge.report_filename(".ai-collab/reports/PR-42-aaaaaaa-a0.md", PR))
        self.assertFalse(bridge.report_filename("../PR-42-aaaaaaa-a1.md", PR))
        self.assertTrue(bridge.report_filename(".ai-collab/reports/PR-42-aaaaaaa-a1.md", PR))


if __name__ == "__main__":
    unittest.main()
