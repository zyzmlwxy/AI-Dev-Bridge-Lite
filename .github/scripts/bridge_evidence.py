#!/usr/bin/env python3
"""V1.3 GitHub-native execution report preflight.

Verifies format and Git history only. It does not run a project's commands,
confirm a report's honesty, approve a PR, or wake an external AI agent.
"""

import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


SHA = re.compile(r"^[0-9a-f]{40}$")
ACTUAL_STATUS = re.compile(r"^(PASS|FAIL|BLOCKED|N/A|NOT RUN|UNKNOWN)(?:\s+\(.*\))?$")
PR_EVENTS = frozenset(("opened", "reopened", "edited", "ready_for_review", "synchronize"))
REQUIRED = (
    "Protocol", "Repository", "PR", "Attempt", "Tested Commit SHA",
    "Build", "Tests", "Test command", "Test exit code", "Failure category", "Overall"
)
FAILURES = frozenset(("NONE", "CODE", "TEST", "ENVIRONMENT", "PERMISSION", "UNKNOWN"))
MAX_REPORT_BYTES = 32768
MAX_PAGES = 10


class EvidenceError(Exception):
    """Malformed, stale or unverifiable report evidence."""


def report_pattern(pr_number):
    return re.compile(
        r"^\.ai-collab/reports/PR-{}-([0-9a-f]{{7}})(?:-a([1-9][0-9]*))?\.md$".format(
            pr_number
        )
    )


def get_report_name(pr_number, filename):
    match = report_pattern(pr_number).fullmatch(filename or "")
    if not match:
        return None
    return (match.group(1), int(match.group(2)) if match.group(2) else 1)


def status(value):
    match = ACTUAL_STATUS.fullmatch(value.strip())
    return match.group(1) if match else None


def parse_report(body, repository, number, filename):
    if not isinstance(body, str) or len(body.encode("utf-8")) > MAX_REPORT_BYTES:
        raise EvidenceError("Report is missing or larger than 32 KiB")
    lines = body.splitlines()  # Handles both LF and Windows CRLF.
    if not lines or lines[0] != "[WORKBUDDY_EXECUTION_REPORT]":
        raise EvidenceError("Missing report header on first line")
    name_info = get_report_name(number, filename)
    if name_info is None:
        raise EvidenceError("Report name does not match PR")
    fields = {}
    for line in lines[1:]:
        if not line or line.startswith(" ") or line.startswith("\t"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key in REQUIRED or key in ("Build command", "Build exit code"):
            if key in fields:
                raise EvidenceError("Duplicate report field: " + key)
            fields[key] = value.strip()
    missing = [key for key in REQUIRED if not fields.get(key)]
    if missing:
        raise EvidenceError("Missing fields: " + ", ".join(missing))
    if fields["Repository"] != repository:
        raise EvidenceError("Report repository mismatch")
    expected_url = "https://github.com/{}/pull/{}".format(repository, number)
    if fields["PR"].rstrip("/") != expected_url:
        raise EvidenceError("Report PR mismatch")
    try:
        attempt = int(fields["Attempt"])
    except ValueError as exc:
        raise EvidenceError("Attempt must be numeric") from exc
    if attempt < 1 or attempt != name_info[1]:
        raise EvidenceError("Attempt does not match report filename")
    tested_sha = fields["Tested Commit SHA"]
    if not SHA.fullmatch(tested_sha) or tested_sha[:7] != name_info[0]:
        raise EvidenceError("Tested SHA must be full and match report filename")
    if not re.fullmatch(r"1\.[1-9][0-9]*", fields["Protocol"]):
        raise EvidenceError("Unsupported protocol version")
    build = status(fields["Build"])
    tests = status(fields["Tests"])
    overall = status(fields["Overall"])
    if build is None or tests is None or overall is None:
        raise EvidenceError("Unknown Build, Tests or Overall status")
    if fields["Failure category"] not in FAILURES:
        raise EvidenceError("Unknown failure category")

    def check_result(label, state, command, code):
        # Check only declared evidence. This is syntactic consistency, not
        # verification that WorkBuddy truly executed the declared command.
        if state == "PASS":
            if (not command or command in ("N/A", "NOT RUN", "UNKNOWN")
                    or code != "0"):
                raise EvidenceError(
                    "{} PASS requires actual command and exit code 0".format(label)
                )
        elif state == "FAIL":
            if not command or command in ("N/A", "NOT RUN", "UNKNOWN"):
                raise EvidenceError("{} FAIL requires actual command".format(label))
            try:
                numeric = int(code)
            except ValueError as exc:
                raise EvidenceError(
                    "{} FAIL requires a numeric exit code".format(label)
                ) from exc
            if numeric == 0:
                raise EvidenceError(
                    "{} FAIL conflicts with exit code 0".format(label)
                )
        elif state in ("N/A", "NOT RUN"):
            if code not in ("", "NOT RUN", "N/A"):
                raise EvidenceError(
                    "{} {} contradicts execution exit code".format(label, state)
                )
        elif state == "BLOCKED":
            # Execution might not have started, or might have exited with a
            # concrete failure; never accept a contradictory zero exit.
            if code not in ("", "NOT RUN", "N/A"):
                try:
                    numeric = int(code)
                except ValueError as exc:
                    raise EvidenceError(
                        "{} BLOCKED has invalid exit code".format(label)
                    ) from exc
                if numeric == 0:
                    raise EvidenceError(
                        "{} BLOCKED conflicts with exit code 0".format(label)
                    )

    check_result("Build", build,
                 fields.get("Build command", ""),
                 fields.get("Build exit code", ""))
    check_result("Tests", tests,
                 fields["Test command"], fields["Test exit code"])

    if overall == "PASS":
        if (build not in ("PASS", "N/A")
                or tests not in ("PASS", "N/A")
                or (build != "PASS" and tests != "PASS")
                or fields["Failure category"] != "NONE"):
            raise EvidenceError(
                "Overall PASS is inconsistent with applicable Build/Tests/Failure category"
            )
    if overall == "BLOCKED" and fields["Failure category"] == "NONE":
        raise EvidenceError("Overall BLOCKED must state failure category")
    return {"tested_sha": tested_sha, "attempt": attempt,
            "build": build, "tests": tests, "overall": overall,
            "category": fields["Failure category"]}


def choose_latest_report(files, number):
    """Select latest added report in PR diff; never use removed or modified files."""
    matching = []
    for item in files:
        info = get_report_name(number, item.get("filename", ""))
        if info and item.get("status") == "added":
            matching.append((info[1], item["filename"]))
    if not matching:
        return None
    matching.sort()
    if len(matching) >= 2 and matching[-1][0] == matching[-2][0]:
        raise EvidenceError("Ambiguous latest Attempt; manual review required")
    return matching[-1][1]


def audit_report(event, repository, files, body, compare):
    """Pure evidence inspection; compare is GitHub tested_sha..head response."""
    pr = event.get("pull_request") or {}
    number = pr.get("number")
    head = pr.get("head", {}).get("sha")
    if type(number) is not int or number < 1 or not isinstance(head, str) or not SHA.fullmatch(head):
        raise EvidenceError("Invalid PR number or head SHA")
    filename = choose_latest_report(files, number)
    if filename is None:
        return {"state": "WAITING_FOR_REPORT", "next": "WorkBuddy",
                "message": "No new immutable WorkBuddy report added in this PR"}
    info = parse_report(body, repository, number, filename)
    if info["tested_sha"] == head:
        raise EvidenceError("Tested SHA equals report HEAD; report commit must be separate")
    if not isinstance(compare, dict) or compare.get("status") != "ahead":
        raise EvidenceError("Tested SHA is not verifiably an ancestor of report HEAD")
    changes = compare.get("files")
    if not isinstance(changes, list) or not changes:
        raise EvidenceError("No complete Git compare file evidence")
    if len(changes) >= 300:
        raise EvidenceError("Compare may be truncated at 300 files")
    if not any(x.get("filename") == filename and x.get("status") == "added" for x in changes):
        raise EvidenceError("Latest report not actually added after tested SHA")
    for item in changes:
        if (item.get("status") != "added"
                or get_report_name(number, item.get("filename", "")) is None):
            raise EvidenceError("Substantive change after tested SHA: retest new HEAD")
    return {"state": "EVIDENCE_READY", "next": "ChatGPT",
            "filename": filename, "tested_sha": info["tested_sha"],
            "head": head, "attempt": info["attempt"],
            "tests_reported": info["tests"], "overall_reported": info["overall"],
            "message": "Format and report-only ancestry verified; test truth NOT verified"}


class GitHubReadApi:
    """Read-only REST helper, never prints tokens or raw reports."""

    def __init__(self, repository, token, url="https://api.github.com"):
        if not token:
            raise EvidenceError("Missing Actions token")
        self.repository = repository
        self.token = token
        self.url = url.rstrip("/")

    def get(self, endpoint):
        request = urllib.request.Request(
            "{}/repos/{}/{}".format(self.url, self.repository, endpoint),
            headers={
                "Authorization": "Bearer " + self.token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "ai-dev-bridge-evidence-v1.3",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise EvidenceError("GitHub read {} HTTP {}".format(endpoint.split("?")[0], exc.code)) from exc
        except urllib.error.URLError as exc:
            raise EvidenceError("GitHub read unavailable") from exc

    def pr_files(self, number):
        files = []
        for page in range(1, MAX_PAGES + 1):
            block = self.get("pulls/{}/files?per_page=100&page={}".format(number, page))
            if not isinstance(block, list):
                raise EvidenceError("GitHub PR files response is not a list")
            files.extend(block)
            if len(block) < 100:
                return files
        raise EvidenceError("PR file listing too long for safe audit")

    def report(self, sha, filename):
        quoted = urllib.parse.quote(filename, safe="/")
        item = self.get("contents/{}?ref={}".format(quoted, sha))
        if item.get("encoding") != "base64":
            raise EvidenceError("Expected base64 report content")
        if item.get("size", MAX_REPORT_BYTES + 1) > MAX_REPORT_BYTES:
            raise EvidenceError("Report too large")
        try:
            content = base64.b64decode(item["content"], validate=False)
            if len(content) > MAX_REPORT_BYTES:
                raise EvidenceError("Report too large")
            return content.decode("utf-8")
        except (ValueError, UnicodeError, KeyError) as exc:
            raise EvidenceError("Report decode failure") from exc

    def compare(self, tested, head):
        if not SHA.fullmatch(tested) or not SHA.fullmatch(head):
            raise EvidenceError("Invalid SHA in compare")
        return self.get("compare/{}...{}".format(tested, head))


def actionable_event(event, repository):
    pr = event.get("pull_request") or {}
    if event.get("action") not in PR_EVENTS:
        return False
    if event.get("repository", {}).get("full_name") != repository:
        return False
    if pr.get("draft") or pr.get("state") not in (None, "open"):
        return False
    if pr.get("head", {}).get("repo", {}).get("full_name") != repository:
        return False
    if pr.get("base", {}).get("repo", {}).get("full_name") != repository:
        return False
    body = pr.get("body") or ""
    return ("[AI_DEV_BRIDGE_HANDOFF]" in body
            and "[/AI_DEV_BRIDGE_HANDOFF]" in body)


def inspect_event(event, repository, api):
    if not actionable_event(event, repository):
        return {"state": "SKIPPED", "next": "NONE",
                "message": "Only open, same-repo non-draft PRs with a handoff are eligible"}
    number = event["pull_request"]["number"]
    head = event["pull_request"]["head"]["sha"]
    if not isinstance(head, str) or not SHA.fullmatch(head):
        raise EvidenceError("PR SHA must be full 40-char hex")
    files = api.pr_files(number)
    filename = choose_latest_report(files, number)
    if filename is None:
        return audit_report(event, repository, files, None, None)
    body = api.report(head, filename)
    info = parse_report(body, repository, number, filename)
    compare = api.compare(info["tested_sha"], head)
    return audit_report(event, repository, files, body, compare)


def summary(info):
    # The diagnostic is derived from validated enums, numbers and filenames,
    # never from arbitrary raw report body or shell commands.
    state = info["state"]
    if state == "WAITING_FOR_REPORT":
        return "State: WAITING_FOR_REPORT. Next: WorkBuddy. No report audited."
    if state == "SKIPPED":
        return "State: SKIPPED. No write or execution performed."
    return ("State: EVIDENCE_READY. Next: ChatGPT. Report: {}. "
            "Attempt: {}. Tested: {}. Report commit HEAD: {}. "
            "Self-reported Tests: {}. Self-reported Overall: {}. "
            "This is metadata/Git preflight, NOT proof of execution or approval.").format(
                info["filename"], info["attempt"], info["tested_sha"],
                info["head"], info["tests_reported"], info["overall_reported"])


def write_summary(text):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("## AI Dev Bridge V1.3 evidence preflight\n\n")
            handle.write(text + "\n\n")


def main():
    try:
        repository = os.environ["GITHUB_REPOSITORY"]
        with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as src:
            event = json.load(src)
        api = GitHubReadApi(repository, os.environ["GH_TOKEN"],
                            os.environ.get("GITHUB_API_URL", "https://api.github.com"))
        result = inspect_event(event, repository, api)
        msg = summary(result)
        print(msg)
        write_summary(msg)
        return 0
    except (EvidenceError, OSError, KeyError, ValueError) as exc:
        # Truncate and sanitize exceptions before writing to public run logs.
        message = "EVIDENCE_INVALID: " + str(exc)[:250]
        print(message, file=sys.stderr)
        try:
            write_summary(message + "\nNext: ChatGPT/WorkBuddy must investigate and retest if code changed.")
        except OSError:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
