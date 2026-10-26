#!/usr/bin/env python3
"""Optional GitHub-native V1.2 handoff notifications.

Runs on same-repository pull_request events only. No project code or
untrusted PR body is executed; an event is a prompt for human/agent review,
never an assertion that a task passed tests or that an agent was awakened.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request


HANDOFF = re.compile(
    r"(?m)^\[AI_DEV_BRIDGE_HANDOFF\]\s*$[\s\S]*?"
    r"^\[/AI_DEV_BRIDGE_HANDOFF\]\s*$"
)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
ACTIONS = frozenset(("opened", "reopened", "edited", "ready_for_review", "synchronize"))


class NotificationError(Exception):
    """An API or event state prevented a trustworthy notification."""


def report_filename(filename, pr_number):
    """Match only immutable, appropriately numbered V1.0/V1.1 report paths."""
    pattern = (
        r"\.ai-collab/reports/PR-" + str(pr_number)
        + r"-[0-9a-f]{7}(?:-a[1-9][0-9]*)?\.md"
    )
    return re.fullmatch(pattern, filename) is not None


def classify(event, repository, changed_files=None):
    """Return (event_kind, head_sha, pr_number) or None.

    The changed_files list comes from comparing the two actual PR head SHAs,
    not the entire diff against the base branch. Each item has filename/status.
    """
    pr = event.get("pull_request")
    action = event.get("action")
    if not isinstance(pr, dict) or action not in ACTIONS:
        return None
    if event.get("repository", {}).get("full_name") != repository:
        return None
    if pr.get("base", {}).get("repo", {}).get("full_name") != repository:
        return None
    if pr.get("head", {}).get("repo", {}).get("full_name") != repository:
        return None  # never handle forks using a write-capable token
    if pr.get("draft"):
        return None
    if not HANDOFF.search(pr.get("body") or ""):
        return None

    number = pr.get("number")
    sha = pr.get("head", {}).get("sha")
    if type(number) is not int or number <= 0 or not isinstance(sha, str):
        raise NotificationError("Missing valid PR number or head SHA")
    if not SHA40.fullmatch(sha):
        raise NotificationError("PR head SHA must be 40 lowercase hex chars")

    if action == "synchronize":
        if changed_files is None:
            raise NotificationError("Missing compare evidence for synchronize")
        if not changed_files:
            return None
        report_only = all(
            item.get("status") == "added"
            and report_filename(item.get("filename", ""), number)
            for item in changed_files
        )
        kind = "REVIEW_PENDING" if report_only else "CODE_READY"
    else:
        kind = "CODE_READY"

    return kind, sha, number


def marker(kind, sha):
    return "<!-- AI_DEV_BRIDGE_V1_2_NOTIFY kind={} sha={} -->".format(kind, sha)


def comment_body(kind, sha, number, repository):
    url = "https://github.com/{}/pull/{}".format(repository, number)
    if kind == "REVIEW_PENDING":
        actor = "ChatGPT"
        instruction = "Review this PR: " + url
        meaning = ("Report-only Git change detected. This indicates a candidate "
                   "execution report, NOT verified test success.")
    else:
        actor = "WorkBuddy"
        instruction = "Execute this PR: " + url
        meaning = ("An eligible PR handoff or substantive change was detected. "
                   "No local build/test has been performed by this notification.")
    return "\n".join((
        marker(kind, sha),
        "[AI_DEV_BRIDGE_NOTIFICATION]",
        "Protocol: 1.2",
        "Event: " + kind,
        "PR: " + url,
        "Head Commit SHA: " + sha,
        "Next actor: " + actor,
        "Action: " + instruction,
        "Note: " + meaning,
        "[/AI_DEV_BRIDGE_NOTIFICATION]",
        "",
        "GitHub comment only; agents are NOT automatically started. "
        "Read the actual PR and AGENTS.md before acting.",
    ))


class GitHubApi:
    """Minimal GitHub REST client; uses only ephemeral GitHub Actions token."""

    def __init__(self, repository, token, api_url="https://api.github.com"):
        if not token:
            raise NotificationError("Missing GH_TOKEN")
        self.repository = repository
        self.token = token
        self.api_url = api_url.rstrip("/")

    def request(self, path, method="GET", data=None):
        url = "{}/repos/{}/{}".format(
            self.api_url, self.repository, path.lstrip("/")
        )
        payload = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=payload, method=method, headers={
            "Authorization": "Bearer " + self.token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ai-dev-bridge-lite-v1.2",
        })
        if payload is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            # Diagnostic details are restricted to GitHub's structured error
            # message and accepted permissions; never print headers, tokens,
            # the request payload, or any untrusted raw response body.
            try:
                error_data = json.loads(exc.read(2048).decode("utf-8"))
                message = error_data.get("message", "")
            except (ValueError, UnicodeError, OSError):
                message = ""
            if not isinstance(message, str):
                message = ""
            safe_message = "".join(
                c for c in message[:200]
                if c.isalnum() or c in " .,:;_-/()"
            )
            accepted = exc.headers.get("X-Accepted-GitHub-Permissions", "")
            if not isinstance(accepted, str):
                accepted = ""
            safe_permissions = "".join(
                c for c in accepted[:160]
                if c.isalnum() or c in " =,;_-"
            )
            raise NotificationError(
                "GitHub API {} {} returned HTTP {}; message={}; "
                "accepted_permissions={}".format(
                    method, path, exc.code,
                    safe_message or "UNAVAILABLE",
                    safe_permissions or "NOT_REPORTED",
                )
            ) from exc
        except urllib.error.URLError as exc:
            raise NotificationError("GitHub API unavailable: " + str(exc.reason)) from exc

    def compare(self, before, after):
        if not SHA40.fullmatch(before) or not SHA40.fullmatch(after):
            raise NotificationError("Compare requires exact 40-hex SHA values")
        payload = self.request("compare/{}...{}".format(before, after))
        if payload.get("too_large") or payload.get("status") != "ahead":
            raise NotificationError("Cannot classify non-linear or oversized compare")
        if payload.get("commits") is None or payload.get("files") is None:
            raise NotificationError("Missing GitHub compare evidence")
        return payload["files"]

    def already_notified(self, number, event_marker):
        # Bounded pagination: if older pages exceed the bound, prefer failing
        # safely to producing an unverified duplicate notification.
        for page in range(1, 11):
            comments = self.request(
                "issues/{}/comments?per_page=100&page={}".format(number, page)
            )
            if any(event_marker in (comment.get("body") or "") for comment in comments):
                return True
            if len(comments) < 100:
                return False
        raise NotificationError("PR comment history too long for safe deduplication")

    def post_comment(self, number, content):
        return self.request(
            "issues/{}/comments".format(number), method="POST", data={"body": content}
        )


def process(event, repository, api, dry_run=False):
    action = event.get("action")
    pr = event.get("pull_request") or {}
    if action not in ACTIONS:
        return "SKIPPED: unsupported event"
    if not isinstance(pr, dict):
        return "SKIPPED: missing PR"

    changed = None
    if action == "synchronize":
        # First enforce basic PR scope without allowing a report classification
        # to issue an API call on a fork or draft.
        if (event.get("repository", {}).get("full_name") != repository
                or pr.get("head", {}).get("repo", {}).get("full_name") != repository
                or pr.get("base", {}).get("repo", {}).get("full_name") != repository
                or pr.get("draft")
                or not HANDOFF.search(pr.get("body") or "")):
            return "SKIPPED: not eligible"
        before = event.get("before")
        after = event.get("after")
        if not isinstance(before, str) or not isinstance(after, str):
            raise NotificationError("Missing exact before/after for synchronize")
        if pr.get("head", {}).get("sha") != after:
            raise NotificationError("PR head and event after SHA disagree")
        changed = api.compare(before, after)

    decision = classify(event, repository, changed)
    if decision is None:
        return "SKIPPED: not eligible or no changes"
    kind, sha, number = decision
    token = marker(kind, sha)
    if not dry_run and api.already_notified(number, token):
        return "DUPLICATE: {} {}".format(kind, sha)
    content = comment_body(kind, sha, number, repository)
    if dry_run:
        return "DRY_RUN:\n" + content
    api.post_comment(number, content)
    return "POSTED: {} for PR #{} ({})".format(kind, number, sha)


def write_actions_summary(message):
    """Record a human-readable status even when PR comment permissions fail."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as stream:
        stream.write("## AI Dev Bridge Lite V1.2 notification\n\n")
        stream.write(message.replace("\n", "  \n") + "\n\n")
        stream.write(
            "A GitHub Actions notification is NOT proof that WorkBuddy "
            "or ChatGPT was automatically started or that tests passed.\n"
        )


def main():
    try:
        path = os.environ["GITHUB_EVENT_PATH"]
        repository = os.environ["GITHUB_REPOSITORY"]
        with open(path, encoding="utf-8") as stream:
            event = json.load(stream)
        dry_run = "--dry-run" in sys.argv[1:]
        api = GitHubApi(
            repository,
            os.environ.get("GH_TOKEN", "dry-run-token" if dry_run else ""),
            os.environ.get("GITHUB_API_URL", "https://api.github.com"),
        )
        result = process(event, repository, api, dry_run=dry_run)
        print(result)
        write_actions_summary(result)
    except (NotificationError, KeyError, ValueError, OSError) as exc:
        status = "BLOCKED: {}".format(exc)
        print(status, file=sys.stderr)
        try:
            write_actions_summary(status)
        except OSError:
            pass
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
