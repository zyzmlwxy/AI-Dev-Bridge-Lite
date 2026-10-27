# AI Dev Bridge Lite V1.3 — 单文件协作启动协议

> 把本文件作为 `AGENTS.md` 放在任意 GitHub 项目仓库根目录，然后分别让 ChatGPT 与 WorkBuddy 读取它。本文件可独立使用，不依赖这个模板的来源仓库或任何外部运行服务。
>
> **ChatGPT：设计、编码、审查与验收；WorkBuddy：本地环境执行、真实构建测试、受控部署；GitHub：双方共同的持久化事实来源。**

## 1. 启动方式与边界

- AI 开始任务时先读取本文件、仓库实际默认分支、相关 Issues / Pull Requests、`.ai-collab/PROJECT_CONFIG.json`（若存在）、`.ai-collab/PROJECT_CONFIG.md` 和 `.ai-collab/PROJECT_STATUS.md`（若存在）。若两种配置文件同时存在，JSON 是自动化执行器的机器可读权威配置，Markdown 仅用于解释；JSON 缺失、无效、版本不支持或与安全策略说明冲突时，必须对执行 fail closed。
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

- `.ai-collab/PROJECT_CONFIG.md`：供人审查的项目配置说明，包含仓库标识、稳定分支、构建／测试命令、环境、部署策略（默认 `DISABLED`）、保密约束和角色权限。未知字段写 `UNKNOWN`，不猜测。
- `.ai-collab/PROJECT_CONFIG.json`（自动执行场景）：机器可读的权威配置；严格校验 schema 版本和字段类型。仅当项目启用自动执行时需要；不能用 Markdown 文本替代机器校验。 本仓库通过 `tests/test_project_config.py` 校验配置键、类型、关闭执行的安全默认值及 Markdown 说明的一致性；该测试由证据预检工作流执行。
- `.ai-collab/PROJECT_STATUS.md`：当前目标、任务 Issue / PR、已知决定、阻塞项、下一步、最近一次**受测 SHA 和报告链接**。用简短事实代替复制聊天记录。
- `.gitignore`：仅在必要时补充本机产物排除规则（例如 `.workbuddy/`、凭据、日志、构建产物）；已有规则应合并，绝不盲目替换。
- 保留现有 `AGENTS.md`；如果它已具有独立团队规范，未经确认不得覆盖或删除。

初始化后向用户提供 PR 链接和一段可直接转发给 WorkBuddy 的执行指令；**未确认之前，不直接写入或合并到稳定分支**。

`PROJECT_STATUS.md` 建议最小结构：

```markdown
# Project Status
Status: READY / CODE_READY / TESTING / REVIEW_PENDING / FIX_REQUIRED / BLOCKED / VERIFIED / AWAITING_APPROVAL / DONE
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

### 6.1 上下文丢失恢复清单（ChatGPT 与 WorkBuddy 均必须遵守）

上下文、会话记忆或本地工作记录可能丢失。**不得要求对方仍记得旧聊天，也不得把“忘记了”当成此前能力不存在的证据。** GitHub 是可共享的持久化事实来源；恢复时按以下顺序操作：

1. **重新读取事实：** 从默认分支读取本文件、`.ai-collab/PROJECT_CONFIG.json`、`.ai-collab/PROJECT_CONFIG.md`、`.ai-collab/PROJECT_STATUS.md`；再读取关联 Issue/PR、最新 HEAD、提交差异、Reviews、Checks/Actions 和最近的执行报告。不得使用旧聊天中的 SHA、PR 状态或记忆覆盖当前 GitHub 状态。
2. **先查已完成工作：** 对照最新差异和报告，确认哪些工作已经完成、哪些失败、哪些只是设计、哪些尚未运行。已有任务优先复用现有 Issue/PR；不要重复创建、重做已完成工作或假称旧操作成功。
3. **区分证据等级：** 明确标记 `VERIFIED`（有可核验命令/结果/时间/SHA）、`USER_REPORTED`（用户提供但尚无本轮独立验证）、`UNKNOWN`、`BLOCKED`。记录最后已知成功的环境、方法和下一步；上下文丢失后不得将 `USER_REPORTED` 伪装成已实测，也不得无故降格为“不可能”。
4. **重新探测旧能力，而非从零配置：** 对曾可用的 SSH、工具路径、共享目录或网络连接，先检查已记录的脱敏证据，并在相同机器/账号/配置条件下重试原有连接方式。采用有超时、只读、最小副作用的探测；记录本轮实际结果。若环境已经变化，明确标出差异。
5. **失败时先诊断、后申请变更：** 保留退出码和脱敏错误摘要，区分 DNS/网络、认证、权限、工具缺失、路径/工作区等问题。不得因为一次失败就重建密钥、修改 SSH 配置、PATH、防火墙或远程服务；任何有副作用的修复先确认授权。
6. **把经验写回 GitHub：** 在关联 Issue/PR 或 `.ai-collab/PROJECT_STATUS.md` 记录事实、证据链接、最后验证时间、未解决风险和唯一明确的下一步。仅记录必要的脱敏信息；不得提交密码、Token、私钥、私网地址、真实用户名或敏感日志。机器本地路径、SSH alias 和凭据仍由本地配置保存，GitHub 只记录可安全公开的别名/占位符及验证结论。

**既有能力恢复原则：** 如果用户或历史记录表明某项外部能力曾经可用，但当前会话没有新证据，应保留原有证据等级，先检查已记录的脱敏验证信息，再在相同执行环境中以有界超时、只读、最小副作用的方式重新探测。不要因上下文丢失就要求用户重新配置，也不能把旧成功直接说成本轮已验证。若失败，先记录退出码与脱敏错误并诊断原因；任何有副作用的修复都须另行授权。具体业务系统的连接恢复应在对应业务项目中跟进，不应混入本通用协作框架项目。
- 本协议与项目特有规范有冲突时，应先识别并明确处理冲突，不以通用模板覆盖项目原有强制要求。

## 7. V1.1：标准化任务状态与低摩擦交接

本节是 V1.0 的兼容扩展。**仍只需复制本 AGENTS.md 即可启用**；下述状态文本和交接块直接放在已有的 Issue、PR 和状态文件中，不要求安装新的工具或创建外部服务。

### 7.1 任务标识和状态

- 一个 Issue 代表一项需求，一个关联 PR 代表一次待审代码／配置变更；已有 Issue / PR 时先复用，不为了“重新开始”重复创建。
- `.ai-collab/PROJECT_STATUS.md` 是**项目当前状态摘要**，不是详细日志；多个并行任务必须分别保留自己的 Issue / PR 状态和受测 SHA，不得混写。
- 统一任务状态（只表示有证据支持的阶段，不表示 AI 在后台实时运行）：

| 状态 | 含义 | 下一步责任方 |
| --- | --- | --- |
| `READY` | 需求、范围和验收标准已确认 | ChatGPT 编码／准备 PR |
| `CODE_READY` | PR 已含待执行变更及可核对的 HEAD | WorkBuddy 领取执行 |
| `TESTING` | WorkBuddy 已明确接手某个受测 SHA；不是推测其正在运行 | WorkBuddy 执行 |
| `REVIEW_PENDING` | 执行报告已写回 GitHub，尚待核查 | ChatGPT 检查证据 |
| `FIX_REQUIRED` | 真实失败或验收不满足，需修改并重新提交 | ChatGPT 修复 |
| `BLOCKED` | 权限、工具、环境或外部依赖阻止执行，需说明解除条件 | 指定责任人 |
| `VERIFIED` | ChatGPT 已根据实际证据验收**指定代码 SHA** | 用户审核 |
| `AWAITING_APPROVAL` | 技术验收已完成，等待用户合并／发布决定 | 用户 |
| `DONE` | 已完成授权的合并及本任务验收；部署另算 | 无 |

- 常规路径：`READY → CODE_READY → TESTING → REVIEW_PENDING → VERIFIED → AWAITING_APPROVAL → DONE`。
- 报告 FAIL 或技术复核失败：`TESTING/REVIEW_PENDING → FIX_REQUIRED → CODE_READY`。**每次修复源码、测试或影响构建的配置，都要生成新的待测 SHA，重新执行受影响测试。**
- 权限或环境不足：`READY/CODE_READY/TESTING → BLOCKED`；解除阻塞后回到可核对的上一阶段，不把权限恢复等同于测试通过。
- 新 HEAD 仅包含 WorkBuddy 的去敏报告时，可以在核对差异后继续审查原受测 SHA；**任意其他实质变更不得自动继承之前的 PASS**。
- 未真正观察到执行中信息时，仍记 `CODE_READY`；不得因为发出指令就擅自写 `TESTING`。状态更新由 ChatGPT 根据 GitHub 已存在的证据完成；WorkBuddy 只需按第 7.3 节写回报告。

### 7.2 一段式 PR 交接卡

ChatGPT 创建或更新 PR 时，在 **PR 描述中**加入下列可复制的最小交接块，并填写真实值；已有交接块则就地更新，不反复追加旧版本：

```text
[AI_DEV_BRIDGE_HANDOFF]
Protocol: 1.1
Issue: <Issue URL or N/A>
PR: <full PR URL>
Scope: <bounded task description>
Acceptance: <specific passing checks>
Build: <real command, N/A or UNKNOWN>
Tests: <real command, N/A or UNKNOWN>
Deployment: DISABLED
[/AI_DEV_BRIDGE_HANDOFF]
```

- 用户向 WorkBuddy 发 **“执行此 PR：<PR URL>”** 即可；WorkBuddy 必须读取仓库根目录 `AGENTS.md`、PR 描述和当前分支内容，再自行查询**最新实际完整 40 位 HEAD SHA**。PR 描述、聊天里的旧 SHA 只是线索，不能当成最新状态。
- 任务要求已经存在于仓库时不要重复向用户询问命令、链接和文件名。`UNKNOWN` 命令需先调查或回报 `BLOCKED`，不可假装执行。
- WorkBuddy 报告写回后，用户可向 ChatGPT 发送 **“验收此 PR：<PR URL>”**；ChatGPT 应主动检查 PR 文件差异、报告文件和评论，优先从 GitHub 发现最新报告，**不要求用户再次手动提供报告路径**。若连接器确实无法列出或读取报告，明确说明限制后才索取补充信息。
- 新会话中的两个 AI 均从此 PR、`AGENTS.md` 和状态文件恢复上下文，不使用某次旧聊天中的 SHA 替代实时远端引用。

### 7.3 报告格式、尝试次数和去重

WorkBuddy 在每次独立执行后写回如下报告。`Attempt` 是此 PR 第几次执行（从 1 开始）；相同 SHA 因真实环境问题重试也要增加 Attempt 并说明原因：

```text
[WORKBUDDY_EXECUTION_REPORT]
Protocol: 1.1
Repository: <owner/repo>
PR: <PR URL>
Attempt: <positive integer>
Tested Commit SHA: <actual full 40-char SHA>
Environment: <OS, toolchain/runtime versions>
Build: PASS / FAIL / BLOCKED / N/A / NOT RUN
Build command: <actually executed command or NOT RUN>
Build exit code: <actual integer or NOT RUN>
Tests: PASS / FAIL / BLOCKED / N/A / NOT RUN
Test command: <actually executed command or NOT RUN>
Test exit code: <actual integer or NOT RUN>
Test output summary: <measured counts, failures or N/A>
Failure category: NONE / CODE / TEST / ENVIRONMENT / PERMISSION / UNKNOWN
Deployment: NOT ATTEMPTED
Overall: PASS / FAIL / BLOCKED / UNKNOWN
Evidence: <actual evidence, sanitized>
Retry reason: <NONE or why the same SHA is tested again>
Remaining issues: <NONE or precise blockers>
```

- 首选 PR 评论；若无评论权限但有 Git + SSH 推送权限，则在**相同 PR 工作分支**新增 `.ai-collab/reports/PR-<PR号>-<受测短SHA>-a<Attempt>.md`，只写去敏报告，不上传二进制或原始敏感日志。
- 为兼容 V1.0，原有 `PR-<PR号>-<受测短SHA>.md` 仍可读取；后续新报告优先使用含 Attempt 的命名。
- 提交报告前应检查相同 PR/SHA/Attempt 的报告是否已存在；已存在则**不要覆盖或重复推送**，先检查是否已正确回传。需要重新执行时递增 Attempt，保留失败证据。
- 报告文本中 **Tested Commit SHA** 指实际检查的源代码提交；报告的 **Report Commit SHA** 应由 ChatGPT 在随后核对 GitHub 历史得出，不允许在报告里伪造未产生的提交。
- WorkBuddy 既不能评论也不能推送时只返回 `BLOCKED` 与去敏错误，不尝试越权写入。只给用户一份可复制的报告，不能宣称“已提交到 GitHub”。
- `PASS` 要求所有本轮明确规定的必要检查都有真实证据。`N/A`（不适用）、`NOT RUN`（没执行）、`BLOCKED`（执行条件不足）必须区分。

### 7.4 失败修复与重测

1. ChatGPT 阅读**最新有效报告**和之前的失败尝试，核实 `Tested Commit SHA`、变更列表、退出码、失败类别；证据不足时置 `UNKNOWN/BLOCKED`，不猜测根因。
2. `CODE` 或 `TEST` 类问题由 ChatGPT 在同一任务 PR 工作分支做**最小范围修复**，增加必要回归用例，更新 PR 的交接块和状态为 `CODE_READY`；WorkBuddy 对**新 SHA** 重新构建／测试。
3. `ENVIRONMENT` / `PERMISSION` 问题优先标记 `BLOCKED`，描述需要的工具或授权，不让 ChatGPT 为绕过环境问题而随意修改业务源码，也不擅自安装工具。
4. 同一个 PR 若已连续 3 次尝试仍无法满足验收，默认升级为人工复核；用户可决定继续、缩小任务范围或停止。**本规则不是后台自动重试器**。
5. 每轮报告保留历史；ChatGPT 在更新 `PROJECT_STATUS.md` 时只写当前结果、最新受测 SHA、报告位置和明确下一动作，不复制整份日志。
6. 如果 WorkBuddy 上传报告时发现 PR HEAD 已因其他来源改变，应仍准确记录实际受测 SHA；ChatGPT 检查冲突和变更，必要时中止验收并要求基于新 HEAD 重新测试。
7. 不得在没有用户明确批准时合并稳定分支、部署生产环境、重置或删除其他人的分支。

### 7.5 状态文件的最小任务字段

已有项目状态格式可继续使用，但建议将当前任务摘要规范为以下 Markdown 文本；不用外置 JSON 数据库：

```text
Protocol: 1.1
Status: <one state from 7.1>
Current task: <Issue URL>
PR: <PR URL>
Working branch: <branch>
Tested commit: <full SHA or NOT_TESTED>
Latest report: <path / PR comment / NONE>
Attempt: <integer / 0>
Last result: PASS / FAIL / BLOCKED / UNKNOWN / NOT RUN
Next actor: ChatGPT / WorkBuddy / USER
Next action: <single concrete step>
Deployment: DISABLED
```

以上字段只是仓库内的可读事实索引，不构成 AI 间实时锁或自动任务队列。并发任务须使用独立的 Issue / PR，由 ChatGPT 主动核查 HEAD，**禁止并发强推**。


### 7.6 通过 Git 引用转交指令（用户只复制一句话）

当 ChatGPT 或 WorkBuddy 需要**通过用户**把任务交给另一方，而任务包含较长的范围、步骤、受测 SHA、验收标准、权限或风险说明时，默认采用 **“详细交接文件入 Git + 简短引用提示词”**，避免让用户反复复制大段说明：

1. **先查已有记录：** 优先复用对应项目仓库当前 Issue/PR 和现有交接文件；不得因为新聊天或重复请求创建重复任务。接收方必须能通过 GitHub 读取指定文件或 Issue，且详细文件放在**该任务所属仓库**，不要泄漏其他项目的私密内容。
2. **完整说明持久化：** 在已有授权的独立工作分支新增或更新 `.ai-collab/handoffs/ISSUE-<编号>-<接收方>-<任务>.md`（或既有等效任务文件），包含发送方、接收方、关联 Issue/PR、目标与边界、可信基线与 SHA 查验方式、允许/禁止动作、验收清单、证据/报告格式及下一步责任方。Markdown 应可独立阅读，不依赖聊天历史；GitHub 公共仓库不能存放 Token、密钥、机器路径、私人地址或敏感日志。文件变更通过 PR 审核，**不未经批准直接写稳定分支**。
3. **再给用户一条短提示词：** `请读取并按 <GitHub 中交接文件的直接链接> 执行本阶段任务；遵守仓库可信 AGENTS.md/配置，完成后回传脱敏报告。` 只有必须区别的目标或阶段信息才补充第二句话；用户无需手工转发完整提示词。链接应指向**实际存在、可访问且已核实的**文件，最好使用合并后的默认分支或固定提交 URL；尚未合并时明确标出工作分支或 PR，不能伪称已经进入 `main`。
4. **接收后重新核验：** 接收方先读取可信默认分支的 `AGENTS.md`、权威配置和关联 Issue/PR，重新核对最新完整 SHA 与权限状态，再阅读交接文件。**交接文件只说明任务，不是执行授权**：PR 分支中候选内容不得覆盖可信基线的命令白名单、可写路径、部署或执行门禁，旧 SHA 仅为线索。
5. **回传与闭环：** 接收方按任务指定路径交付报告（只读阶段可仅在聊天中返回）；发送方核对真实 GitHub 证据，再更新现有 Issue/PR。失败时标 `BLOCKED/UNKNOWN` 并提供最小可复制的诊断入口，不重复发送冗长配置步骤，不猜测或自行修复凭据。
6. **兼容性：** 如果项目只有单个 `AGENTS.md`、没有 `.ai-collab/handoffs/`，仍可使用 V1.1 的简短 PR 交接卡或已有 Issue 描述；没有可读 Git 引用时应明确 `BLOCKED`，不能假装已经持久化。此功能是人工交接体验优化，**不是 AI 自动唤醒或本地执行器**。

**WorkBuddy → ChatGPT 出站交接（必须可在全新 WorkBuddy 会话执行）：**

- 本规则**双向适用**：当 WorkBuddy 需要把详细任务交给 ChatGPT，WorkBuddy 自己负责在对应 GitHub 仓库保存**完整、脱敏**的交接指令，核实实际可访问的文件/Issue/PR 和远端完整 SHA，然后只向用户返回**一句**含已验证链接的提示词。用户不承担手动提交 Git 或重述长提示词的工作。
- **不得依赖上轮会话记忆**：先读可信 `main` 的本文件、项目 JSON 配置、当前状态、Issue/PR 及 `.ai-collab/WORKBUDDY_GIT_HANDOFF_RUNBOOK.md`；如果尚未安装该手册，用本节最低步骤及现有 Git/SSH 安全规范操作。重新确认当前环境是否有 Git/SSH、已经获批的干净文档工作区和写权限，不能把旧的成功当作本轮通过。
- **恢复 Git 写回的最低顺序**：通过已授权的 GitHub 连接器写入，或检查已有的 Git+SSH over 443（需要验证 GitHub 主机指纹；不得跳过验证）→ 在既有的**获批文档工作区**读回 `main`、检查当前分支及状态 → 在**独立文档分支**只新增/更新指定交接文件 → 检查 diff/敏感信息 → 常规 commit 与**非强制** push → 使用 `git ls-remote` / GitHub 再次核对实际远端分支 SHA 与文件可读性 → 创建/关联 PR（若具备权限）并回传短链接。**具体 PowerShell/Git 命令、Windows 路径探测、连接器 `auth-required` 回退、无权限时的 BLOCKED 处理**在 `.ai-collab/WORKBUDDY_GIT_HANDOFF_RUNBOOK.md` 中完整记录；不得要求新会话自行猜命令或重配 SSH 密钥/PATH。
- **写入权限须另行成立**：已有只读任务（例如 Issue #19 Stage A）、未批准的工作区、无写权限、私有仓库无法分享给接收方，都不能自动升级为“可创建分支/提交”。Git 文档工作流**不是** `PROJECT_CONFIG.json` 的自动命令执行白名单，也不许可本地项目构建、部署、合并 `main`、强推、安装或破坏性操作。没有获批写入条件时只报 `BLOCKED`，不虚构 Git 链接、PR 或已成功推送。
- **模板与可复现验证**：`.ai-collab/handoffs/TEMPLATE-WORKBUDDY-TO-CHATGPT.md` 提供完整交接结构；[Issue #21](https://github.com/zyzmlwxy/AI-Dev-Bridge-Lite/issues/21) 和 `.ai-collab/handoffs/ISSUE-21-WORKBUDDY-REVERSE-HANDOFF-PROBE.md` 可用于独立的、经授权的纯文档回传验证。**规范存在 ≠ WorkBuddy 写回已实测**；实测前应标记 `NOT TESTED`。

**最短可复制格式：** `执行任务：<已验证的 GitHub 文件 URL>。按其中的边界操作并回传结果。`


## 8. V1.1 的适用范围

V1.1 保留已验证的 V1.0 双向 GitHub 交接、Git + SSH 报告回传与 C++11 冒烟测试基础；新增规范化任务状态、简短交接和有证据的失败重试约定。**新增规则只有通过独立执行端验证后才可声称经过实测**。没有自动调度、后台互相唤醒或已验证的生产部署功能。


## 9. V1.2：可选 GitHub 原生通知（人工仍负责启动 AI）

V1.2 与 V1.1 **完全兼容**：复制本文件至任意项目根目录，即可继续使用手动 PR 链接交接。新增自动通知为**可选增强**，不是单文件启动的先决条件。

### 9.1 什么会自动发生

- 如项目负责人主动启用本仓库示例中的 `.github/workflows/ai-dev-bridge-notify.yml` 和 `.github/scripts/bridge_notify.py`，GitHub Actions 可在同仓库 PR 的 `opened` / `reopened` / `edited` / `ready_for_review` / `synchronize` 事件后检查其交接卡；Draft、Fork 和缺少交接卡的 PR 必须跳过。
- **`CODE_READY`**：打开、重新打开、编辑合格 PR，或实际 PR HEAD 变更不是“仅新增执行报告”时，将带 HEAD SHA 的 `[AI_DEV_BRIDGE_NOTIFICATION]` 评论写入 PR。下一位处理者：WorkBuddy。
- **`REVIEW_PENDING`**：在一次 `synchronize` 提交中，若 GitHub 比对证实变更**全部是新增的、命名正确的执行报告文件**，写入同样格式的通知评论。下一位处理者：ChatGPT。它仅意味着报告候选已到，**不是** Tests PASS、VERIFIED 或审查通过。
- 通知由 `<!-- AI_DEV_BRIDGE_V1_2_NOTIFY kind=... sha=... -->` 标记按事件种类和完整 SHA 去重，已有通知不可重复刷屏。报告必须继续区分真实受测 SHA 和报告提交 SHA；通知不得替代 WorkBuddy 执行证据。
- 此流程依赖已启用的 GitHub Actions、仓库允许 `issues: write` 的 GitHub Actions Token 和 PR 评论权限。若权限不足，工作流应失败并记录实际 403/BLOCKED；不得悄悄声称已发出通知。

### 9.2 对用户与 AI 的意义

- 用户在 GitHub 订阅或关注该 PR 时，可以收到正常的 GitHub 评论通知。GitHub 是否实际推送到移动端取决于用户的 GitHub 通知设置。
- WorkBuddy 和 ChatGPT 仍**不会因 GitHub 评论自动启动**；用户仍需要主动打开这两个 AI 或由独立的、明确授权的集成进行调用。在没有直接接入的监听器时，绝不宣传为全自动多 Agent。
- WorkBuddy 应从 `CODE_READY` 通知中的 PR URL 获取实际 PR 最新 HEAD 并按 V1.1 运行，而不是信任评论作为已执行证明。ChatGPT 应从 `REVIEW_PENDING` 通知自行读取报告和 GitHub compare、实际审核后才能置 VERIFIED。
- 同一仓库的工作流属于可选安装文件，不允许 PR 的文字内容当作 shell 命令执行，不允许对外部 Fork 使用写 Token，不允许自动合并或部署。

### 9.3 使用与迁移

1. V1.1 用户：无须安装任何东西，继续依靠单文件 `AGENTS.md` 和 PR 链接人工交接。
2. 希望 GitHub 自动写交接通知的项目：由负责人审核后**额外复制**本仓库的 `.github/workflows/ai-dev-bridge-notify.yml` 与 `.github/scripts/bridge_notify.py`，按自身仓库 Actions 权限设置启用，确认 GitHub Actions 允许评论。
3. 在项目的 PR 描述中继续维护 V1.1 的 `[AI_DEV_BRIDGE_HANDOFF]` 块。通知成功只意味着 GitHub 评论已创建；AI 实际执行仍独立验收。
4. 单仓库安全验证见 `tests/test_bridge_notify.py`（离线用例）和 `tests/V1.2_ACCEPTANCE.md`（真实 GitHub / WorkBuddy 验收）。任何未运行测试必须写 N/A / NOT RUN，不得虚报。

### 9.4 范围界限

- 不包含后台任务队列、WorkBuddy/ChatGPT API 直连、定时自动唤醒或无人审批的循环重试。
- GitHub 工作流仅对当前有权限的仓库 PR 发布评论，不跨仓库发送私有源代码或日志。
- GitHub Actions 执行路径与 V1.1 单文件手动路径互相独立； Actions 失败时仍可以按 V1.1 手动交接。
- 在 GitHub 实际跑通通知和 WorkBuddy 的独立真实检查之前，V1.2 只能标为候选，不能称作端到端实测成功。

## 10. V1.3：可选的 GitHub 自动执行证据预审

V1.3 在 V1.2 自动评论基础上，提供**可选、只读**的 GitHub Actions 报告证据检查。核心的 `AGENTS.md` 单文件接入仍可脱离 Actions 独立工作，不增加守护进程、Webhook 接收服务、长期令牌或 AI 自动唤醒。

### 10.1 两种状态与其含义

- `WAITING_FOR_REPORT`：PR 里没有新增符合命名规则的 WorkBuddy 报告。表示等待 WorkBuddy 执行，**不是**任何测试结果的 PASS。
- `EVIDENCE_READY`：自动检测找到带独立 Attempt 编号的报告，检查报告字段、完整受测 SHA、命令/退出码及 Git 提交谱系；从 `Tested Commit SHA` 到报告提交 HEAD 只能新增报告文件，任何业务代码、测试或配置变化都会阻止沿用旧的验证。
- `EVIDENCE_INVALID`：元数据不完整、SHA 不匹配、受测 SHA 非当前 HEAD 的可验证祖先、报告提交后存在代码变更、或自述测试结论与退出码不一致时，Actions 检查退出非零，要求人重新核对或在新 HEAD 上重测。
- `EVIDENCE_READY` **仅表示报告的格式与 Git 谱系可信**，不表示执行输出真实、测试通过、代码安全、已批准、已由 ChatGPT 审核。真正 `VERIFIED` 必须依照 V1.1 流程由 ChatGPT 检查证据。

### 10.2 新增组件及权限

- 可选复制 `.github/workflows/ai-dev-bridge-evidence.yml` 与 `.github/scripts/bridge_evidence.py`；由 GitHub Actions `pull_request` 在同仓库非 Draft PR 上执行。
- 工作流只需要 `contents: read` 和 `pull-requests: read`，与 V1.2 通知脚本的写权限独立；**不得改为** `pull_request_target`，也不得执行报告中声称的 shell 命令。
- 报告遵守 V1.1 的 `.ai-collab/reports/PR-<PR号>-<受测SHA前7位>-a<Attempt>.md` 命名和 `[WORKBUDDY_EXECUTION_REPORT]` 字段约定；旧版没有 Attempt 后缀的报告仍可识别为 Attempt 1，但必须包含足够的元数据。
- 自动检查通过后会在 GitHub Actions 的 Job Summary 输出待处理对象、受测 SHA、报告提交 SHA、下一位处理者；用户和 ChatGPT 可从 PR Checks 查看，而非复制一整份报告。
- 同一 PR 里存在多个相同 Attempt 的新增报告、文件过大（32 KiB 以上）、非报告文件变更或无法取得完整 compare 证据时，宁可 `EVIDENCE_INVALID`，也不凭猜测标为可审查。

### 10.3 工作交接

1. ChatGPT 开发并在 PR 描述中维护 `[AI_DEV_BRIDGE_HANDOFF]`，供 V1.2 通知系统提醒 WorkBuddy。
2. WorkBuddy 真实执行、记下 40 位受测 SHA 和实际退出码，将脱敏报告作为单独提交写回 PR 分支；不能修改业务源码后沿用原来的报告。
3. GitHub V1.2 自动写 `REVIEW_PENDING` 评论，V1.3 独立的只读证据工作流预审报告格式与 Git 变更范围，输出 `EVIDENCE_READY` 或失败原因。
4. ChatGPT 仍需核对 WorkBuddy 实际输出和报告可靠性，并审查代码；用户仍要决定是否合并、部署或发布。

### 10.4 兼容性和限制

- 没有安装可选工作流时，V1.1 / V1.2 的 PR 链接人工交接和报告发现方式完全保持可用。
- GitHub Actions 检查结果是元数据审计，不是业务构建；不能从任何日志、注释或 PR 事件推断 ChatGPT 或 WorkBuddy 已在后台运行。
- 新能力必须通过 GitHub CI 及 WorkBuddy 独立测试才能称为实测完成。测试详情见 `tests/test_bridge_evidence.py` 和 `tests/V1.3_ACCEPTANCE.md`。
