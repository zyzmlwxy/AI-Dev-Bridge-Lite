# Issue #21 — WorkBuddy reverse Git handoff demonstration

**Owner request:** Let WorkBuddy independently persist its *own* detailed instructions to Git, and relay only a short URL prompt to the human for ChatGPT. This file exists precisely so a **new WorkBuddy chat with no remembered Git/SSH commands** can reconstruct the procedure.

**Target:** `zyzmlwxy/AI-Dev-Bridge-Lite` · [Issue #21](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/issues/21)  
**Receiving agent:** WorkBuddy · **Next agent:** ChatGPT  
**Trust boundary:** Always reread `main` `AGENTS.md`, `.ai-collab/PROJECT_CONFIG.json`, this Issue and current HEAD; this file is just the task specification.

## Task, sequential phases and allowed operations

### Step 0 — recover without any old conversation (read-only)

Read **trusted `main`**:
- `AGENTS.md` §6.1 and §7.6
- `.ai-collab/WORKBUDDY_GIT_HANDOFF_RUNBOOK.md` (includes Git command examples, Git+SSH over 443 reconstruction, safe push/read-back and PR procedure)
- `.ai-collab/handoffs/TEMPLATE-WORKBUDDY-TO-CHATGPT.md`
- `.ai-collab/PROJECT_CONFIG.json`, `.ai-collab/PROJECT_STATUS.md`, Issue #21, actual main SHA and open PRs

Identify which steps are facts `VERIFIED`, only old `USER_REPORTED`, `UNKNOWN` or `BLOCKED`.

### Step 1 — verify *actual* write capability without side effects

Use an available **authenticated** GitHub connector to check Git read/write support; if it returns `auth-required`, don't pretend it can write. Locate Git in the current WorkBuddy environment as shown in the runbook; use last documented Git+SSH over 443 path only after bounded, read-only re-verification and host-key validation. Do not assume this session runs on the same machine as the old successful probe.

If the selected WorkBuddy session only has unauthenticated public web access, the Git executable isn't accessible or the intended local worktree doesn't exist, **stop and return BLOCKED**, reporting what permission/environment is missing. Do not install, clone, reset credentials or modify SSH/PATH/firewall.

### Step 2 — doc-only write demonstration (requires explicit owner authorization)

**Only after the user explicitly instructs you to perform this scoped doc-only demonstration and you have a verified, pre-approved existing clean documentation worktree or supported authenticated GitHub connector:**

- In the **same** public framework repository, inspect Issue #21 and existing doc-only PRs; reuse owned work if available; otherwise create **one new independent branch** named `docs/workbuddy-handoff-proof-21` from the verified current `main` (if that exact branch name is already owned by another task, STOP and reconcile rather than overwrite).
- Create **only one** new file `.ai-collab/handoffs/ISSUE-21-CHATGPT-WORKBUDDY-PROOF.md` based on the template. Populate it with actual, sanitized evidence of how you recovered Git access, actual scope of write authorization, current main SHA, what was verified, and the next ChatGPT acceptance task. Do not put credentials or local machine paths in a **public** repo.
- Inspect `git diff --cached` / connector diff so **only this single file** is staged. Make a normal commit (no amend/force), push **only this branch**, read back the actual full remote SHA, and verify the file exists through the web/connector.
- Create a PR from this branch to `main` if available (documentation-only); otherwise provide the verified branch-file link and clearly say the PR was not created. **Do not merge** the PR. Do not touch `PROJECT_CONFIG.json`, the WorkBuddy scheduler or any project/source/build/test file.
- If no Git or connector write permission, stop at Step 1 with `BLOCKED`. The purpose of this test is **real**, not simulated, write-back capability.

This is a **manual Git documentation handoff**, not a scheduled executor task. The trusted execution policy stays `execution_enabled=false`, `allowed_commands=[]`, workspace UNCONFIGURED, deployment DISABLED. This test does **not** approve Stage B of Issue #19 or any local project command.

### Step 3 — user-facing response (make it short)

If read-back succeeded, return a very short message, e.g.:

> 请 ChatGPT 验收 Issue #21 的 WorkBuddy→ChatGPT Git 交接：<已验证的 GitHub PR 或文档链接>。详细信息已写入 Git，本次未合并或执行项目命令。

Also include the full remote commit SHA as a separate single line of evidence, **not a long prompt**. If any step failed, respond `BLOCKED：Git 交接文件未成功提交或核实远端；<精简脱敏原因>` and do not claim success.

## ChatGPT acceptance checks (after WorkBuddy result)

1. Confirm the resulting branch and PR (if any) actually exist and the pushed HEAD matches the WorkBuddy report.
2. Compare parent/source SHA and diff; **only the allowed handoff file was added**; no code/config/secret leaks.
3. Confirm the receiver can open the handoff file through GitHub and its facts are classified by evidence quality.
4. Check **correctness of one-line human relay prompt**; a new ChatGPT session needs no previous chat history.
5. Confirm auto-executor/Stage B guards unchanged. Merge requires separate explicit owner approval.

**Status before test:** Documentation procedure prepared; **WorkBuddy write-back not yet tested**.
