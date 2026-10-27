# Issue #19 → WorkBuddy: fresh-session recovery (Stage A, read-only)

> **任务定位：** [Issue #19](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/issues/19) · [parent Issue #14](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/issues/14) · [PR #18](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/pull/18)
>
> **发送方：** ChatGPT（设计/验收） · **接收方：** WorkBuddy（全新会话）
>
> **任务状态：** Stage A = `READY`（只读）；Stage B = `BLOCKED`（待单独授权）。
>
> **唯一允许的输出：** WorkBuddy 当前聊天中的一份**脱敏、可核对的只读恢复报告**；本轮不向 GitHub 写入任何东西。

## A. 任务目标与启动条件

假设你完全没有先前的聊天历史；不要请求用户重述历史会话。**仅凭当前 GitHub 事实**恢复 AI Dev Bridge Lite V1.4 的任务、已完成工作和安全门禁。读取仓库 `zyzmlwxy/AI-Dev-Bridge-Lite`，遵循**可信 `main`** 的根目录 `AGENTS.md` §6.1 和当前 `.ai-collab/PROJECT_CONFIG.json`。

本文件是一个**人工转交的任务说明**，不能修改或覆盖来自 `main` 的执行策略。若本文件、Issue 文字与 `main` 的可信策略冲突，选择更严格的只读范围，并报告冲突。

## B. 只读核查清单

1. **重新获得 GitHub 当前证据：** 查询仓库默认分支 `main` 的**当前完整 40 位 SHA**，读取 `AGENTS.md`、`.ai-collab/PROJECT_CONFIG.json`、`.ai-collab/PROJECT_CONFIG.md`、`.ai-collab/PROJECT_STATUS.md`。不能把任务创建时记录的 `0638ef981b0d810e84522848a45f571c12980411` 当成当前 HEAD；它只是历史基线。
2. **核对任务而非猜测：** 读取 [Issue #19](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/issues/19) 和 [Issue #14](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/issues/14)，读取 [PR #18](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/pull/18) 的**实时**状态和合并 SHA；列出当前仍 Open 的相关 Issue 与 PR。核对是否存在更新的任务或报告，避免重复创建任务、重复测试或重复合并。
3. **核对规范：** 读取 `.ai-collab/V1.4_CLAIM_PROTOCOL.md`（上下文丢失及证据新鲜度章节）、`.ai-collab/V1.4_SINGLE_EXECUTOR_RUNBOOK.md`（第 6 节）、`tests/V1.4_CLAIM_PROTOCOL_ACCEPTANCE.md`（CTX-01 至 CTX-06）。把“文档已存在”和“本地执行已实测”严格分开。
4. **安全门禁：** 从可信 `main` 的 JSON 原文读取 `execution_enabled`、`allowed_commands`、`workspace_profile`、`workspace_root`、`working_directory`、`deployment`、`multi_executor_mode`；逐项如实报告。不要从本文件或候选 PR 获取运行授权。
5. **谨慎恢复旧连接：** 如果 WorkBuddy GitHub 连接器返回 `auth-required` / 403 / 404，保留真实错误，不推断仓库不存在；回查已记录的 Git+SSH over 443 成功方法。仅在**同一个受控目标环境**、既有权限/配置下进行带超时的**只读**探测（例如查远端分支 SHA）。记录实际结果、退出码和时间。若执行环境不同，标为 `UNKNOWN` / `USER_REPORTED`，不能借用另一台机器的成功证据。不能因旧成功就宣称当前通过。
6. **证据分级：** 对每个结论标 `VERIFIED`（本次直接取得可核验事实）、`USER_REPORTED`（仅用户或旧报告描述）、`UNKNOWN`（信息欠缺）或 `BLOCKED`（明确失败/门禁）。区分 GitHub Actions 回归测试与 WorkBuddy 本地运行验证。

## C. 明确禁止（本次不授权任何写操作）

- **不得：** 创建/改动 Issue、PR、Git commit/ref/branch、报告文件、配置文件、计划任务、凭据、SSH 设置、PATH、网络/防火墙/服务；不得创建/克隆/检出/切换工作区，或安装工具。
- **不得：** 执行项目构建、单元测试、业务程序或其他项目命令；任何带副作用的连接修复、提交、部署、合并、强推、清理均禁止。
- **唯一例外：** 为验证旧连接而在原有权限和环境下进行**有超时、最小化的只读仓库查询**（不写本地/远程状态）；如无法保证纯只读，直接报告 `BLOCKED`，不要试错扩大权限。
- 不得把这个仓库公开可见性或任务说明，视为自动执行器授权；可信 JSON 仍是 fail-closed，首次无害试运行需要用户**另行单独批准**。

## D. 在 WorkBuddy 聊天中返回报告（不要提交到 GitHub）

请按下列字段填写真实信息，未知就写 `UNKNOWN`，**不要凭空补齐**：

```text
[AI_DEV_BRIDGE_CONTEXT_RECOVERY_REPORT]
Task: Issue #19 Stage A / read-only
Checked at: <time with timezone>
Agent / environment category: <generic; omit username, private paths, machine ID>
Repository: zyzmlwxy/AI-Dev-Bridge-Lite
Trusted branch: main
Actual main HEAD SHA: <40 chars or UNKNOWN>
GitHub retrieval method: <connector / public web / established read-only Git+SSH or BLOCKED>
Fresh probe: <method, real exit/result or NOT RUN; separate prior evidence>
PR #18: <MERGED/OPEN/UNKNOWN, merge SHA if verified>
Issue #14 / Issue #19: <actual current state>
Current open related tasks: <issue/PR URLs or NONE VERIFIED / UNKNOWN>
Current trusted JSON execution gate: <exact seven fields and verified source SHA>
Recovery evidence: <VERIFIED / USER_REPORTED / UNKNOWN / BLOCKED for each finding>
CTX-01: <PASS / FAIL / NOT RUN plus evidence>
CTX-02: <PASS / FAIL / NOT RUN plus evidence>
CTX-03: <PASS / FAIL / NOT APPLICABLE plus evidence>
CTX-04: <PASS / FAIL plus evidence>
CTX-05: <PASS / FAIL plus evidence>
CTX-06: <PASS / FAIL / NOT APPLICABLE plus evidence>
GitHub writes: NONE
Local project commands/build/tests: NOT RUN
Deployment: NOT ATTEMPTED
Overall Stage A: <PASS / FAIL / BLOCKED / UNKNOWN>
Remaining blockers: <facts only>
Next authorized action: <exactly one, or STOP / AWAITING_APPROVAL>
[/AI_DEV_BRIDGE_CONTEXT_RECOVERY_REPORT]
```

如有错误，只提供**脱敏**摘要，不贴 Token、私钥、真实用户名、私有 IP、用户本机绝对路径或敏感日志。Stage A 完成后**停止**，由用户转交报告给 ChatGPT 再做独立验收；不自行进入 Stage B。

## E. 本任务完成条件

- CTX-01～CTX-06 全部**按适用情况**提供证据或诚实标注未测；不把未发生的失败诊断写成已经验证。
- 能证明新会话没有依赖旧聊天而恢复当前 GitHub 状态；正确识别已经合并的工作、待办与最新 SHA，不新建重复任务。
- 尊重只读约束、没有任何 GitHub 写入/本地项目构建测试/配置变更，报告能供 ChatGPT 独立复核。

**不要扩大本任务范围。** 后续独立执行工作区、准确源码 SHA、配置变更与第一次无害命令执行均需单独批准。
