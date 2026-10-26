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

The new protocol is still contained in the same root-level `AGENTS.md`. An Issue/PR and user-started AI conversations remain the coordination mechanism.

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
