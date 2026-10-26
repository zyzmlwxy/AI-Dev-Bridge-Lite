# AI Dev Bridge Lite — PROJECT_STATUS

Last updated: 2026-10-27

## Current phase

**V1.4 single-executor MVP preparation — fail-closed design merged; context-recovery procedure under review; runtime preflight only.**

## Verified progress

- PR #16 verified sequential claim creation, duplicate skip, and a sequential non-fast-forward rejection using Git + SSH.
- PR #17 was squash-merged into `main` as merge commit `34b8089bfae6cfa5dec24b764c2969ac7a807fcd`. It adds the V1.4 claim protocol, acceptance matrix, single-executor runbook, and strict machine-readable configuration.
- PR #18 ([context-loss recovery](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/pull/18)) is open and adds a durable, project-agnostic recovery checklist, evidence grades, and CTX-01 through CTX-06 acceptance cases. Project-specific connection recovery is out of scope and must be handled in the relevant business project's repository.
- GitHub Actions run [#40359969450](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/actions/runs/40359969450) passed on tested commit `2200ab9720a76ce5360a4dfa7987985e97524cfe`: project-config contract tests, existing evidence-gate regression checks, and notifier offline tests. The only PR change after that tested SHA was a status-documentation update. These checks do not validate the WorkBuddy runner or execute project build/tests.
- `.ai-collab/PROJECT_CONFIG.json` is the trusted-base machine-readable configuration source of truth; `.ai-collab/PROJECT_CONFIG.md` is its human explanation.
- The config deliberately remains fail-closed: `execution_enabled=false`, `allowed_commands=[]`, `workspace_profile=UNCONFIGURED`, `deployment=DISABLED`.
- The last reported environment probe found Git/Python usable via explicit executable paths, while PowerShell PATH resolution did not find Git and `python` resolved to a Microsoft Store stub. Do not change global/user `PATH` automatically.
- The inspected checkout was on the PR #16 conflict-candidate branch, not an approved execution workspace. Do not use it to run project tasks.

## Current execution gate

- `execution_enabled`: **false**
- `allowed_commands`: **empty**
- `workspace_profile`: **UNCONFIGURED**
- `workspace_root` / `working_directory`: **null**
- `deployment`: **DISABLED**
- Multi-executor concurrency testing: **deferred**, not an MVP blocker.

No WorkBuddy-local project command, build/test, deployment, PATH mutation, or scheduled-task change has been authorized or performed in this phase. GitHub Actions results are configuration/evidence regression checks only.

## Next steps

1. Review and merge PR #18 (context-loss recovery policy) when ready.
2. WorkBuddy rereads current GitHub state and resumes the next task authorized by the relevant project. For any previously available capability with missing fresh evidence, apply the generic re-probe procedure in the runbook; track business-specific connectivity in that business project's repository.
3. Designate a separate, clean execution workspace at an explicitly approved source SHA; do not reuse the PR #16 conflict-candidate checkout.
4. Configure and verify exact executable paths, working directory, timeout, and a narrowly scoped command allowlist without changing global `PATH`.
5. Verify single-flight behavior and report-only evidence handling.
6. Obtain separate user authorization for one harmless pilot command and preserve the actual command/output/exit-code evidence.

## Context recovery contract

On every fresh ChatGPT or WorkBuddy session, reread `AGENTS.md`, trusted-base config JSON/Markdown, this status file, related Issues/PRs, latest commits/reviews/checks, and the latest execution report. GitHub evidence wins over chat memory. Record durable facts with one of `VERIFIED`, `USER_REPORTED`, `UNKNOWN`, or `BLOCKED`; preserve sanitized known-good methods and failures so neither side assumes the other remembers prior work. Never commit credentials, private keys, private IPs, usernames, machine-local secret paths, or sensitive logs.

No automatic source editing, merge, release, or deployment is authorized by this status file.
