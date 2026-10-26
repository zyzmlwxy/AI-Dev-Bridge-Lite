# Changelog

## [Unreleased] — V1.3 evidence-gated handoff candidate

- Opt-in read-only GitHub Actions preflight for immutable WorkBuddy reports, with `WAITING_FOR_REPORT`, `EVIDENCE_READY` and fail-safe `EVIDENCE_INVALID` status.
- Parse essential execution metadata and actual recorded exit codes, validate full tested SHA against report filename and linked PR.
- Confirm with GitHub commit comparison that only report files were added after the tested SHA; prevent silently inheriting evidence after source/test/config changes.
- Python standard-library implementation and offline malformed-report / non-ancestor / mixed-diff regression tests.
- Preserve V1.1 single-file manual onboarding and V1.2 native PR comment notifications, without external services or autonomous agent starts.
- **Pending:** GitHub Actions live evidence workflow, WorkBuddy independent run/report and ChatGPT SHA verification. Not a released or approved version.

## 1.2.0 — 2026-10-26

- Optional `pull_request`-based GitHub Actions notifications for same-repository, non-draft PRs with a handoff block.
- Evidence-based `CODE_READY` (WorkBuddy next) and `REVIEW_PENDING` (ChatGPT next) comments, deduplicated by notification kind and exact PR head SHA.
- GitHub compare classifies report-only commits conservatively: only added, immutable, correctly named reports qualify. No automatic PASS or VERIFIED.
- Offline standard-library Python regression tests including draft/fork restrictions, duplicate suppression and mixed changes.
- Retains standalone `AGENTS.md` and V1.1 manual mode; no background AI wakeup, external hosting, or autonomous deployment.
- **Verified:** WorkBuddy Windows 11 / Python 3.13.14 syntax and 18/18 unit tests exit 0, GitHub CI 18/18 PASS; real `github-actions[bot]` `CODE_READY` and `REVIEW_PENDING` comments; same-SHA notification deduplication. Both WorkBuddy reports preserved, with Attempt 2 tested SHA distinct from the report-only commit.
## 1.1.0 — 2026-10-26

- Standardized task states: READY, CODE_READY, TESTING, REVIEW_PENDING, FIX_REQUIRED, BLOCKED, VERIFIED, AWAITING_APPROVAL, DONE.
- Added concise `[AI_DEV_BRIDGE_HANDOFF]` blocks in PR descriptions so a user can hand off by PR link instead of copying a large prompt.
- Defined retry attempts, immutable execution report naming, failure categories, duplicate suppression and a human escalation after three failed attempts.
- Required ChatGPT to discover report files/comments from the PR itself and verify tested SHA against report/metadata commits.
- Preserved the V1.0 single-file `AGENTS.md` installation path; no scheduler, service, GitHub Action or autonomous agent invocation.
- Acceptance evidence: WorkBuddy completed three real Git + SSH attempts: Attempt 1 `FAIL` (intentional fixture), Attempt 2 `FAIL` (CRLF working-tree mismatch), Attempt 3 `PASS` (committed-HEAD checks). ChatGPT verified each reported tested SHA against the corresponding report-only commit. Build was N/A; no deployment occurred.
- Released in public main and via the `v1.1.0` GitHub Tag / Release; the GitHub Release was published separately after merge.

## 1.0.0 — Initial public release

- Portable single-file `AGENTS.md` bootstrap protocol.
- ChatGPT / WorkBuddy roles with GitHub Issue and PR handoff.
- Real build/test execution reports with exact tested commit SHA.
- Git + SSH fallback when connectors cannot access private repositories or write PR comments.
- Cross-session recovery via `.ai-collab/PROJECT_CONFIG.md` and `.ai-collab/PROJECT_STATUS.md`.
- Browser-only onboarding and bilingual guides.
- Default-deny production deployment and no autonomous scheduler.

### Validation notes

The collaboration workflow has been exercised in private GitHub repositories, including a basic C++11 smoke test built with g++ and eight passing test cases. An independent second repository completed the single-file bootstrap and report handoff. These observations are limited to those environments; project-specific build and deployment support is not guaranteed.

### Known limitations

- Some GitHub connectors do not have private-repository access or comment permissions.
- Git + SSH requires an authorized local runtime and, for some environments, one-time public-key enrollment.
- No background automation or cross-agent wake-up is provided.
- Additional build generators, including one Windows CMake default-generator path, were not fully validated.

### V1.2 permission diagnostic (resolved)

The first GitHub notification jobs returned `HTTP 403 Resource not accessible by integration` despite `issues: write`. Following explicit user approval, granting the **single notification workflow** `pull-requests: write` resolved the error. Actual bot comments for both notification states were verified on [PR #7](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/pull/7); no repository-wide permission setting was changed and no PAT was used. V1.1 manual handoff remains fully supported.
