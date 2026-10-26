# AI Dev Bridge Lite

**A single-file, GitHub-based collaboration protocol for ChatGPT and WorkBuddy. No server required.**

[简体中文](README.md) · [Quick start](#quick-start) · [Workflow](#workflow)

AI Dev Bridge Lite is not an autonomous agent platform. It is a portable `AGENTS.md` protocol that defines responsibilities and durable handoffs between two AI-assisted development environments:

- **ChatGPT** plans, writes code, opens pull requests, reviews implementation, and validates reports.
- **WorkBuddy** accesses an authorized local environment, builds and runs tests, checks real results, and reports evidence.
- **GitHub** stores issues, pull requests, source code, commit SHAs, execution reports, and concise project state.

It requires no background daemon, database, webhook, or local installation for the GitHub-web user. Both assistants still need authorized repository access, and the user triggers each task.

## Quick start

1. Create a GitHub repository at `https://github.com/new` (Private is fine).
2. Copy [AGENTS.md](AGENTS.md) into the **root of your project repository**. On GitHub: `Add file → Create new file → AGENTS.md`. Do not overwrite existing project rules; merge them by pull request when necessary.
3. Send this to ChatGPT:

   > Open my repository `https://github.com/OWNER/REPO`, read `AGENTS.md`, inspect existing project conventions, and initialize only the missing `.ai-collab/PROJECT_CONFIG.md` and `.ai-collab/PROJECT_STATUS.md` files in a new branch and pull request. Do not overwrite files, merge, or deploy. Give me the PR link and a WorkBuddy handoff instruction.

4. Send this to WorkBuddy:

   > Connect to `https://github.com/OWNER/REPO` as the execution agent. Read `AGENTS.md` and the current task PR, verify its exact commit SHA, run real builds/tests in the authorized local environment, and report actual exit codes. If the connector cannot access a private repository or post a PR comment, use an existing authorized Git + SSH configuration and write a sanitized report under `.ai-collab/reports/` in the same PR branch. Do not change main, install software without permission, merge, or deploy.

## V1.1: One PR link for each handoff

V1.1 adds consistent task states, a short PR handoff card, numbered test attempts, failure categories, and safe retry instructions to the original single-file protocol. No daemon, external database, or automatic agent-to-agent wake-up is added.

- ChatGPT records requirements, acceptance checks, and real build/test commands in a `[AI_DEV_BRIDGE_HANDOFF]` block in the PR description.
- Send WorkBuddy only **"Execute this PR: https://github.com/OWNER/REPO/pull/12"**. It must read `AGENTS.md` and the PR, resolve the latest full head SHA, run the authorized checks, and write a sanitized report.
- Send ChatGPT only **"Review this PR: https://github.com/OWNER/REPO/pull/12"**. It should locate the latest report from PR comments or changed files, verify the tested SHA and the later report commit, and decide the next state.
- Failures are classified as `CODE`, `TEST`, `ENVIRONMENT`, `PERMISSION` or `UNKNOWN`. Actual code/test fixes need a new head SHA and a retest; missing tools/permissions become `BLOCKED`. Report filenames contain an attempt number to preserve history.
- If a task still fails after three execution attempts, request human review rather than performing unbounded retries.

The V1.1 handoff was exercised in three real WorkBuddy Git + SSH attempts: an intentional failed fixture check, a real Windows CRLF mismatch, then a successful committed-HEAD check, with separate reports and verified SHAs. This is a protocol acceptance drill (build N/A), not a production build or autonomous retry.

The new protocol is still contained in the same root-level `AGENTS.md`. An Issue/PR and user-started AI conversations remain the coordination mechanism.

## V1.2: optional GitHub-native PR notifications

The V1.1 single-file flow remains fully supported. V1.2 offers an **opt-in** GitHub Actions workflow that leaves comments on eligible same-repository, non-draft PRs with an `[AI_DEV_BRIDGE_HANDOFF]` block:

- `CODE_READY` for an eligible PR or substantive source/configuration change. Next actor: WorkBuddy.
- `REVIEW_PENDING` when a commit adds **only immutable, correctly named execution report files**. Next actor: ChatGPT.
- Duplicate comments for the same event type and exact PR head SHA are suppressed. Notifications do not assert test success or start either AI.

To opt in, copy `.github/workflows/ai-dev-bridge-notify.yml` and `.github/scripts/bridge_notify.py` into the target repository, review their permissions and enable GitHub Actions PR-comment rights (workflow-local `contents: read`, `issues: write`, and `pull-requests: write` token permissions). The notifier uses Python's standard library and repository-local GitHub APIs; no backend server or webhook receiver is needed. Draft and fork PRs are deliberately skipped. Repositories that cannot grant comment permissions can continue using the manual V1.1 handoff.

Run local offline checks in this repo with `python3 -m unittest discover -s tests -p 'test_bridge_notify.py' -v`. **Actual V1.2 evidence:** WorkBuddy on Windows 11 / Python 3.13.14 and GitHub CI independently passed 18/18 tests and syntax checks; GitHub Actions posted real `CODE_READY` and report-only `REVIEW_PENDING` bot comments and demonstrated same-SHA notification deduplication. The original HTTP 403 was resolved with the repository owner's approval to change **only the workflow's** `pull-requests` permission to `write`, not the repository-wide default. See [PR #7 verification](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/pull/7#issuecomment-6407513665). No autonomous agent start, project build or production deployment was verified.

## V1.3: automatic report-evidence preflight

V1.3 adds an **optional, read-only** GitHub Actions check for execution reports. It consumes no custom secrets and never executes report-provided commands. The existing single-file `AGENTS.md` flow and V1.2 PR comments remain usable without it.

- `WAITING_FOR_REPORT`: no newly added WorkBuddy report was found. Not test PASS.
- `EVIDENCE_READY`: report metadata and Git compare lineage are consistent, including a complete tested SHA and a report-only change from tested code to current PR HEAD. This is **not a verification that tests really ran**.
- `EVIDENCE_INVALID`: missing or inconsistent metadata, invalid SHA, stale tested revision, or substantive changes after the tested SHA; investigate and retest where needed.

Opt in by reviewing and adding `.github/workflows/ai-dev-bridge-evidence.yml` and `.github/scripts/bridge_evidence.py`. The GitHub token requires only `contents: read` and `pull-requests: read`. Offline tests for this repository are in `tests/test_bridge_evidence.py`; that suite is optional when installing only the two runtime files into a different project. **Verified V1.3.0 evidence:** WorkBuddy tested the repaired source on Windows 11 / Python 3.13.14 (syntax exit 0, **33/33** evidence regressions and **18/18** V1.2 compatibility tests exit 0), then pushed a report-only commit. GitHub Actions returned `EVIDENCE_READY` after comparing the exact tested SHA with the report commit, and GitHub's bot published `REVIEW_PENDING`. Four original PR code-review findings were addressed and re-tested. See [PR #11 acceptance](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/pull/11#issuecomment-6409808855). The gate verifies report metadata and Git lineage, not the truth of execution claims or autonomous agent invocation.

GitHub checks and comments do not start WorkBuddy or ChatGPT, approve PRs, or deploy software. V1.3 reduces evidence-checking effort, not the need for the user to start assistants.

## Workflow

```text
Request → ChatGPT task/PR → WorkBuddy tests exact SHA
       → GitHub report → ChatGPT verifies evidence → User approves
```

Reports must distinguish **Tested Commit SHA** from the later **Report Commit SHA**. If code changes after testing, retest the affected areas. Never mark unrun tests as passing. The `AGENTS.md` file does not automatically wake up either assistant.

## GitHub access and SSH fallback

A connected GitHub integration may still lack private repository read or write permissions. WorkBuddy can fall back to a previously authorized local Git + SSH setup; it must request approval before creating keys, installing software, or changing persistent configuration. When port 22 is blocked, GitHub [documents SSH over port 443](https://docs.github.com/en/authentication/troubleshooting-ssh/using-ssh-over-the-https-port). Verify server host keys and never upload private keys.

If PR comments are unavailable, WorkBuddy can commit only a sanitized report file in the same PR branch, e.g. `.ai-collab/reports/PR-12-abcdef0.md`. Neither a successful clone nor an authenticated connector guarantees PR comment or push rights; check them separately.

## Safety and limitations

Deployment is **disabled by default** and requires explicit authorization, a target commit, backups and rollback. Do not expose private repository content, secrets, personal agent state, credentials or raw sensitive logs. Existing project rules take precedence when they impose stronger constraints.

The protocol has been exercised in private-repository handoffs, a Windows C++11 direct-build smoke test with eight passing cases, and an independent second-repository bootstrap. This does not prove universal compatibility, autonomous scheduling or production deployment safety. Each new project needs its own permission and test validation.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and the [MIT license](LICENSE).
