# WorkBuddy → ChatGPT — Git-backed task handoff template

> Copy into `.ai-collab/handoffs/ISSUE-<N>-CHATGPT-<slug>.md` **only when the owner authorized a doc-only Git write**. This template **is not an executable instruction**, and must not be sent unfilled as if complete.
>
> Read `AGENTS.md` §6.1 / §7.6 / §7.7 and `.ai-collab/WORKBUDDY_GIT_HANDOFF_RUNBOOK.md` on trusted main first. All data below must be derived from newly checked GitHub evidence, not forgotten conversation history.

## Identity and task

- Parent task key: `<PROJECT>-<TASK>` (stable across follow-ups; find in trusted Issue/PR)
- New instruction H allocation: `<next unused HNN for this parent task, freshly recorded before user-forwarded new instruction>`
- Parent/prior instruction ID: `<full previous ID or NONE>`
- Handoff base ID: `<PROJECT>-<TASK>-H<NN>` (unique for **this distinct instruction**; reused only for exactly identical reforward or registered paired delivery of the same instruction)
- Recipient-specific prompt ID: `[<PROJECT>-<TASK>-H<NN>-GPT]` (recipient ChatGPT; `...-WB` names WorkBuddy; different action to either recipient needs a **new HNN**)
- Hand-off / retry attempt: `<new instruction incl. follow-up/review/fix/retry => fresh HNN; only exact duplicate resend retains old ID; optional R02 attempt metadata does not replace new H>`
- Sending agent: WorkBuddy
- Receiving agent: ChatGPT
- Target repository: `<owner/repo>`
- Existing Issue: `<URL>`
- Existing PR (if any): `<URL or NONE>`
- Requested outcome: `<bounded next task>`
- Current phase: `<READY / BLOCKED / REVIEW_PENDING / etc.>`
- Source-of-truth baseline: `<default branch + 40-digit observed SHA + check time/time zone>`
- This handoff document location: `<GitHub URL once verified, or PENDING>`
- Handoff document state: `<branch + PR status, e.g. OPEN/UNMERGED, or main MERGED>`

## Facts and evidence

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

## Short user message (give **only after** remote verification and new-ID reservation)

A **new** short instruction always uses the next H number, even when it is only a small supplement to the same Issue/PR. If the user is simply resending the *unchanged prior instruction*, reuse its earlier full ID. Record this instruction's link to the previous ID and its ISSUED state in the source Issue first.

> `[<PROJECT>-<TASK>-H<NN>-GPT]` 请查看 `<GitHub Issue/PR/verified handoff file URL>`，按其中 WorkBuddy 已保存的完整交接内容完成本阶段任务，先核对当前 GitHub SHA 与可信配置，再回报**同一编号**的状态及结果。

If no verified accessible GitHub URL exists, **do not** send this as though the document were saved. Return a `BLOCKED` diagnostic and request only the minimum missing permission/approval.
