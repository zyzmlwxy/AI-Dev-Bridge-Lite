# AI Dev Bridge Lite V1.0 — 单文件协作启动协议

> 把本文件作为 `AGENTS.md` 放在任意 GitHub 项目仓库根目录，然后分别让 ChatGPT 与 WorkBuddy 读取它。本文件可独立使用，不依赖这个模板的来源仓库或任何外部运行服务。
>
> **ChatGPT：设计、编码、审查与验收；WorkBuddy：本地环境执行、真实构建测试、受控部署；GitHub：双方共同的持久化事实来源。**

## 1. 启动方式与边界

- AI 开始任务时先读取本文件、仓库实际默认分支、相关 Issues / Pull Requests、`.ai-collab/PROJECT_CONFIG.md` 和 `.ai-collab/PROJECT_STATUS.md`（若存在）。
- 如果当前任务是初始化，先观察项目已有代码、原有规范、权限和工作流，再最小化增补协作文件；**可重复执行，不覆盖已有文件，不覆盖项目的既定规范**。
- 不论仓库为 Public 还是 Private，均须通过已授予的合法 GitHub 权限访问；连接器显示“已连接”不代表可以读写该仓库。
- 本文件是仓库内协作指令，**不是后台常驻服务**：没有触发器时，两侧由用户启动任务，不得声称自动唤醒或持续监听。
- **所有项目默认禁止部署**，需要用户在项目配置明确启用并针对目标环境授权；不得因为通过测试就推断可以部署。
- 不能访问仓库、缺少编译环境或证据不足时，必须标为 `BLOCKED` 或 `UNKNOWN`，不能虚报成功。

## 2. 角色与权限

### ChatGPT：设计 / 编码 / 审查

1. 研究当前项目和实际需求，按必要范围设计任务及验收标准。
2. 对需要代码变更的任务，建立关联 Issue（已有则复用）、独立工作分支与 PR；代码和测试一起提交。
3. 尊重项目现有编码、构建和测试规范；优先跨平台及自动生命周期管理，但不强行重写已有工程。
4. 保留每个交给 WorkBuddy 的 PR 链接、**完整 40 位受测 Commit SHA**、需要执行的命令与预期结果。
5. 读取 WorkBuddy 的真实报告，核对 GitHub 提交和变更差异，失败则提出修复并重新交付测试。
6. 审查后更新状态。不得把“写出测试代码”“代码看起来正确”称为本地运行通过；不得未经授权合并稳定分支或部署。

### WorkBuddy：真实环境执行 / 回报

1. 通过已获授权的 GitHub 连接器或本地 Git + SSH 访问实际仓库；**连接器返回 404/403 时不得凭猜测认定仓库不存在**。
2. 核对待执行的 PR 最新工作分支与完整 SHA；在实际机器上构建、运行测试，并记录真实命令、编译器／运行环境、退出码及摘要。
3. 只处理指定范围，未经授权不得自行变更架构、提交业务代码、安装软件、修改系统或合并 PR。
4. 不能执行时说明阻塞项；可在已有许可下做安全诊断，不隐瞒失败。
5. 按第 4 节提交报告；部署仅按照该项目的专门授权、备份、验证和回滚规程执行。

### 用户：项目负责人

提出需求、批准重要配置及权限变更、决定是否合并或部署、体验最终效果。重复任务的常规信息应保存在 GitHub，避免反复询问用户。

## 3. 项目初始化（ChatGPT 执行）

若项目尚无 `.ai-collab/` 协作状态，创建**一个独立初始化 PR**，在分支内按需加入：

- `.ai-collab/PROJECT_CONFIG.md`：仓库标识、实际稳定分支、语言／框架、构建命令、测试命令、真实环境、部署策略（默认 `DISABLED`）、保密约束、角色权限。未知字段写 `UNKNOWN`，不猜测。
- `.ai-collab/PROJECT_STATUS.md`：当前目标、任务 Issue / PR、已知决定、阻塞项、下一步、最近一次**受测 SHA 和报告链接**。用简短事实代替复制聊天记录。
- `.gitignore`：仅在必要时补充本机产物排除规则（例如 `.workbuddy/`、凭据、日志、构建产物）；已有规则应合并，绝不盲目替换。
- 保留现有 `AGENTS.md`；如果它已具有独立团队规范，未经确认不得覆盖或删除。

初始化后向用户提供 PR 链接和一段可直接转发给 WorkBuddy 的执行指令；**未确认之前，不直接写入或合并到稳定分支**。

`PROJECT_STATUS.md` 建议最小结构：

```markdown
# Project Status
Status: READY / CODE_READY / TESTING / VERIFIED / BLOCKED / AWAITING_APPROVAL
Repository: <owner/repo>
Base branch: <real branch>
Current task: <issue or PR link>
Work branch: <branch or N/A>
Tested commit: <40-char SHA or NOT_TESTED>
Execution report: <PR comment or repository file path or NONE>
Blockers: <none or details>
Next: <one concrete next step>
```

## 4. 标准交接和真实验收

1. ChatGPT 将任务要求、变更和测试条件写在 Issue / PR，工作分支更新后重新读取 PR 的真实 HEAD。
2. WorkBuddy **先记录受测 SHA**，再在实际执行环境检查代码、运行编译／测试命令；未运行项写 `NOT RUN` 或 `N/A`，不可写 `PASS`。
3. 回报优先使用 PR 评论。如果连接器没有评论权限，且 Git + SSH 可以推送，在**同一个 PR 工作分支**新增 `.ai-collab/reports/PR-<PR号>-<受测短SHA>.md`，只提交脱敏报告文件，再推送该分支；不得直接推送稳定分支。
4. 报告提交本身会改变 PR HEAD：务必区分 `Tested Commit SHA` 与 `Report Commit SHA`；报告文件中不能预先编造自己的提交 SHA。可以从后续 GitHub 历史确认。
5. ChatGPT 通过 GitHub 比较受测 SHA 与报告后的 HEAD：若只有新增报告和无关的元数据修改，可以按受测代码的范围验收；若源码、测试或影响构建的配置改变，必须重新测试这些更改。
6. 编译、测试及代码审查满足项目验收标准后，标记 `VERIFIED`，由用户决定合并；只有满足部署授权和安全条件时才进入部署阶段。

执行报告模板（不包含凭据、私钥、敏感日志）：

```text
[WORKBUDDY_EXECUTION_REPORT]
Repository: <owner/repo>
Issue / PR: <issue / PR number or link>
Tested Commit SHA: <full 40-char SHA>
Environment: <OS, toolchain/runtime versions>
Repository access: PASS / BLOCKED
Build: PASS / FAIL / BLOCKED / N/A
Build command: <actual command or NOT RUN>
Build exit code: <actual code or NOT RUN>
Tests: PASS / FAIL / BLOCKED / N/A
Test command: <actual command or NOT RUN>
Test exit code: <actual code or NOT RUN>
Test output summary: <counts, failures, key messages>
Deployment: NOT ATTEMPTED / <authorized result>
Overall: PASS / FAIL / BLOCKED / UNKNOWN
Evidence: <commands and factual results>
Remaining issues: <none or specifics>
```

`Overall: PASS` **仅表示本次任务规定的检查完成**，不意味着任何未执行的业务测试、部署或 CMake/其他编译链路也已通过。

## 5. WorkBuddy 的 GitHub 接入回退

- 优先尝试当前已有权限，不假设 WorkBuddy GitHub 连接器拥有私有仓库读取或写权限。
- 连接器无法访问时，可在用户授权的本地环境用 `git` 和 OpenSSH 读取／写回 GitHub；**用户无需亲自输入 Git 命令，也无需安装 GitHub Desktop**。
- 使用 `git --version`、`ssh -V` 检测现有工具；缺少工具、需生成 SSH 密钥或更改用户级 SSH 配置时，先征求用户授权。
- SSH 私钥只能留在本机，不应进入聊天、PR、仓库；由用户在 GitHub 网页添加**公钥**。核验 GitHub 主机密钥指纹，不关闭验证。
- SSH 22 端口不通时，可依据 GitHub 官方文档使用 `ssh.github.com:443`；是否需要取决于实际网络。
- 用 `git ls-remote git@github.com:<owner>/<repo>.git HEAD` 和实际分支 SHA 核对访问权限。能够克隆不必然意味着具有评论或推送权限，分别实测。
- 若无可行写回路径，应报告 `BLOCKED` 并提供去敏文本，不能绕开授权。

## 6. 安全和状态恢复

- 不能提交 Token、SSH 私钥、数据库内容、未脱敏个人信息及生产敏感日志。
- 默认禁止直接提交到稳定分支、强制推送、自动合并、自动部署、破坏性数据操作；用户明确批准后才能按最小范围实施。
- 部署前需明确目标环境、部署 SHA、备份及回滚路径；失败要立即停下并按授权方案处理，不能自行扩大操作。
- 新会话必须从 GitHub 获取最新 `AGENTS.md`、`PROJECT_CONFIG.md`、`PROJECT_STATUS.md`、关联 Issue/PR/提交及报告；报告与项目状态冲突时，以真实 GitHub 提交和执行证据为准，标注未解决的矛盾。
- 本协议与项目特有规范有冲突时，应先识别并明确处理冲突，不以通用模板覆盖项目原有强制要求。

## 7. V1.0 的适用范围

V1.0 已验证的基础能力是 GitHub 双向交接、Git + SSH 报告回传，以及在具备合适编译器的实际 Windows 环境中执行一个小型 C++11 测试。新仓库仍须独立确认权限、编译、测试与部署能力。它**不是**自动调度平台，也不保证任意项目无需配置即可完成实际业务测试。
