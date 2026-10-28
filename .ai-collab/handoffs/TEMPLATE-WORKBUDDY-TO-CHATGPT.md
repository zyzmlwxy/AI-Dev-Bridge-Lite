# WorkBuddy → ChatGPT — Git-backed task handoff template

> Copy into `.ai-collab/handoffs/ISSUE-<N>-CHATGPT-<slug>.md` **only when the owner authorized a doc-only Git write**. This template **is not an executable instruction**, and must not be sent unfilled as if complete.
>
> Read `AGENTS.md` §6.1 / §7.6 / §7.7 and `.ai-collab/WORKBUDDY_GIT_HANDOFF_RUNBOOK.md` on trusted main first. All data below must be derived from newly checked GitHub evidence, not forgotten conversation history.

## Identity and task

- Handoff base ID: `<PROJECT>-<TASK>-H<NN>` (registered in the project's existing Issue/PR log; same base ID for both agents)
- Recipient-specific prompt ID: `[<PROJECT>-<TASK>-H<NN>-GPT]` (the receiver is ChatGPT; pair with `...-WB` when applicable)
- Hand-off / retry attempt: `<first dispatch / same-ID reforward / explicitly authorized -R02>`
- Sending agent: WorkBuddy
- Receiving agent: ChatGPT
- Target repository: `<owner/repo>`
- WorkBuddy local-only private-state file (PATH ONLY; relative to verified project root): `.ai-local/workbuddy/private.json` — **never** attach or paste the file contents, real absolute path, credentials or environment dumps to GitHub/ChatGPT
- WorkBuddy locally observed private-state status (sanitized; `USER_REPORTED` to ChatGPT): `<PRESENT / ABSENT / UNKNOWN / BLOCKED / NOT_CHECKED>`; file must be under an authorized worktree and ignored/untracked before any write
- Existing Issue: `<URL>`
- Existing PR (if any): `<URL or NONE>`
- Requested outcome: `<bounded next task>`
- Current phase: `<READY / BLOCKED / REVIEW_PENDING / etc.>`
- Source-of-truth baseline: `<default branch + 40-digit observed SHA + check time/time zone>`
- This handoff document location: `<GitHub URL once verified, or PENDING>`
- Handoff document state: `<branch + PR status, e.g. OPEN/UNMERGED, or main MERGED>`

## Facts and evidence

> GitHub can validate this project's **relative-path contract** but **cannot independently read WorkBuddy's private local file or validate its contents**. Local file presence/access/security status is from WorkBuddy's sanitized report; do not call it GitHub VERIFIED. Credential-store references remain local only; no secret values in handoff.


- Dispatch status on source Issue/PR: `<ISSUED / ACKED / IN_PROGRESS / PASS / FAIL / BLOCKED>`; latest evidence link `<URL>`; **never rerun side effects after PASS for the same ID**.


| Fact / claim | Evidence grade | Direct source / real output | Checked at |
|---|---|---|---|
| `<task progress>` | `VERIFIED/USER_REPORTED/UNKNOWN/BLOCKED` | `<GitHub link or sanitized evidence>` | `<time>` |
| `<tested source SHA vs current HEAD>` | `...` | `...` | `...` |
| `<environment capability / SSH or Git>` | `...` | `<sanitized read-only probe, not raw secrets>` | `...` |

- Actual actions performed and effect: `<specific commands and exit codes ONLY if already authorized, else NOT RUN>`.
- Tested commit SHA: `<full 40-character SHA or NOT_TESTED>`
- Report commit SHA: `<different full SHA or NONE>`
- Current PR HEAD: `<full 40-character SHA or UNKNOWN>`
- Known blockers, failures and retry risk: `<precise, sanitized>`
- Existing task/PR already completed: `<yes/no/unknown, evidence>`

## Next recipient task

- **ChatGPT should do:** `<one actionable scoped next step>`
- **ChatGPT must not do:** `<no merge/deploy/execution/... as appropriate>`
- Owner approvals already explicitly granted: `<verifiable authorization and scope or NONE>`
- Owner approvals still required: `<precise gate>`
- Acceptance / validation: `<testable evidence criteria; don't upgrade reported facts to VERIFIED>`
- Next actor once checked: `<ChatGPT / WorkBuddy / USER>`

## Commit/read-back facts (WorkBuddy only; fill AFTER real GitHub read-back)

- Local doc-only commit SHA: `<full SHA or NO_COMMIT>`
- Remote branch/ref + observed remote SHA: `<ref and SHA or NOT_VERIFIED>`
- PR URL and status: `<URL and OPEN/MERGED, or PR_NOT_CREATED>`
- File URI ChatGPT can read: `<verified URL or BLOCKED>`
- No unrelated file changes / credential leaks: `<VERIFIED with diff or UNKNOWN>`

## Short user message (give **only after** remote verification)

> `[<PROJECT>-<TASK>-H<NN>-GPT]` 请查看 `<GitHub Issue/PR/verified handoff file URL>`，按其中 WorkBuddy 已保存的完整交接内容完成本阶段任务，先核对当前 GitHub SHA 与可信配置，再回报**同一编号**的状态及结果。

**Private-data rule:** Git/GitHub may carry only the project-relative pointer `.ai-local/workbuddy/private.json` and a sanitized status. Never fill this template with the contents of that local file or any real machine-specific path. See trusted `AGENTS.md` §6.2 and the WorkBuddy runbook §1.1.

If no verified accessible GitHub URL exists, **do not** send this as though the document were saved. Return a `BLOCKED` diagnostic and request only the minimum missing permission/approval.
