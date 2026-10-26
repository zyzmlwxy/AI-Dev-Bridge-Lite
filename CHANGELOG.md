# Changelog

## [Unreleased] — V1.2 GitHub-native notification candidate

- Optional `pull_request`-based GitHub Actions notifications for same-repository, non-draft PRs with a handoff block.
- Evidence-based `CODE_READY` (WorkBuddy next) and `REVIEW_PENDING` (ChatGPT next) comments, deduplicated by notification kind and exact PR head SHA.
- GitHub compare classifies report-only commits conservatively: only added, immutable, correctly named reports qualify. No automatic PASS or VERIFIED.
- Offline standard-library Python regression tests including draft/fork restrictions, duplicate suppression and mixed changes.
- Retains standalone `AGENTS.md` and V1.1 manual mode; no background AI wakeup, external hosting, or autonomous deployment.
- **Pending** GitHub Actions permission/notification smoke test and independent WorkBuddy execution evidence.
## 1.1.0 — 2026-10-26

- Standardized task states: READY, CODE_READY, TESTING, REVIEW_PENDING, FIX_REQUIRED, BLOCKED, VERIFIED, AWAITING_APPROVAL, DONE.
- Added concise `[AI_DEV_BRIDGE_HANDOFF]` blocks in PR descriptions so a user can hand off by PR link instead of copying a large prompt.
- Defined retry attempts, immutable execution report naming, failure categories, duplicate suppression and a human escalation after three failed attempts.
- Required ChatGPT to discover report files/comments from the PR itself and verify tested SHA against report/metadata commits.
- Preserved the V1.0 single-file `AGENTS.md` installation path; no scheduler, service, GitHub Action or autonomous agent invocation.
- Acceptance evidence: WorkBuddy completed three real Git + SSH attempts: Attempt 1 `FAIL` (intentional fixture), Attempt 2 `FAIL` (CRLF working-tree mismatch), Attempt 3 `PASS` (committed-HEAD checks). ChatGPT verified each reported tested SHA against the corresponding report-only commit. Build was N/A; no deployment occurred.
- Released as public main branch content after explicit user approval. This entry is **not** a claim that a GitHub Release or Git tag was created.

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

### Current integration test limitation (V1.2 candidate)

GitHub CI ran the Python syntax check and **18/18 tests passed**. However, the real notification job received **HTTP 403** when attempting to create a PR comment. Automatic GitHub comment delivery is **BLOCKED** pending approved repository/workflow permissions; this is not a released or verified feature. The V1.1 manual PR link handoff remains supported.
