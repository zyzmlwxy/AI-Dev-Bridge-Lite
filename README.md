# AI Dev Bridge Lite

**零服务、单文件启动的 ChatGPT × WorkBuddy GitHub 开发协作协议（V1.1）。**

[English](README.en.md) · [快速开始](#快速开始) · [协作流程](#协作流程) · [安全边界](#安全边界)

## 简介

AI Dev Bridge Lite 不是又一个后台 Agent 平台，而是一套可直接复制到项目根目录的 `AGENTS.md` 协作约定：

- **ChatGPT**：需求分析、设计、编码、生成 Pull Request、代码审查和验收。
- **WorkBuddy**：本地真实构建、运行测试、查看运行结果，并提交执行报告。
- **GitHub**：双方共享代码、Issue、Pull Request、完整 Commit SHA、执行证据及跨会话状态。

**无需**自建服务、数据库、Webhook，也无需用户安装 GitHub Desktop 或本地运行初始化脚本。支持已有项目和新建项目，但新项目仍须授权两个 AI 访问仓库。默认禁止未经批准的生产部署。

## 快速开始

### 1. 在 GitHub 网页新建项目

在 `https://github.com/new` 创建仓库，可以为 Private。你可以使用一个已有项目，不必重新创建仓库。

### 2. 上传唯一启动文件

将[本仓库的 AGENTS.md](AGENTS.md)复制到**你的目标项目根目录**，文件名仍为 `AGENTS.md`。

GitHub 网页路径：进入仓库 → `Add file` → `Create new file` → 输入 `AGENTS.md` → 粘贴全文并提交。

如果目标项目已经有 `AGENTS.md`，**不要直接覆盖**。让 AI 在 PR 中提议合并协作条款。

### 3. 给 ChatGPT 发指令

> 我的 GitHub 项目是 `https://github.com/OWNER/REPO`。请通过可用的 GitHub 连接读取项目根目录的 `AGENTS.md`，遵守 AI Dev Bridge Lite 规范。先检查仓库原有规则和实际权限，在独立分支 / PR 初始化缺失的 `.ai-collab/PROJECT_CONFIG.md`、`.ai-collab/PROJECT_STATUS.md`。不要覆盖项目文件、合并稳定分支或部署。请给我初始化 PR 链接和发给 WorkBuddy 的执行任务。

### 4. 给 WorkBuddy 发指令

> 请作为 AI Dev Bridge Lite 执行端，接入 `https://github.com/OWNER/REPO`。读取根目录 `AGENTS.md` 和 ChatGPT 创建的 PR，核对最新完整 Commit SHA。使用有权限的 GitHub 访问方式读取代码、执行真实构建测试，并按协议回传结果；若连接器无法访问 Private 仓库或评论，请在已有授权下使用本机 Git + SSH，报告通过 PR 工作分支的 `.ai-collab/reports/` 文件回传。不得自行安装软件、合并稳定分支或部署。

> **不需要把用户名、密码、SSH 私钥或个人访问令牌发给 AI。** 初次 SSH 授权时用户只需在 GitHub 网页添加公钥。

## 协作流程

```text
用户提出需求
   |
ChatGPT 创建 Issue、工作分支和 PR
   |
WorkBuddy 拉取并核对指定 Commit SHA
   |
WorkBuddy 在真实环境编译、运行、检查
   |
WorkBuddy 在 PR 评论或提交报告文件
   |
ChatGPT 从 GitHub 读取证据、比较受测 SHA 和报告提交 SHA
   |
用户批准合并或部署（如果需要）
```

- 编译、测试未执行时必须写 `NOT RUN` 或 `N/A`，不能写 `PASS`。
- 连接器显示 `connected` 不等于对指定私有仓库有权限。
- 报告提交会产生新的 Commit，**受测 SHA** 与 **报告提交 SHA** 必须分别记录。
- 代码变更后要重新检查是否需要重新测试。
- `AGENTS.md` 不会自动唤醒 AI；这版仍由用户触发两侧任务。

## 私有仓库与 WorkBuddy 连接方式

WorkBuddy 的 GitHub 连接器是否能读写 Private 仓库取决于实际授权；某些环境连接器只读或返回 403 / 404。解决思路：

1. 在 WorkBuddy 实际机器上检查现有 `git --version` 与 `ssh -V`，未经许可不要安装或改配置。
2. 使用已有的 Git + SSH 授权克隆／提交指定工作分支。
3. 如果 SSH 22 端口不可用，可以按 [GitHub 官方文档](https://docs.github.com/en/authentication/troubleshooting-ssh/using-ssh-over-the-https-port)尝试 `ssh.github.com:443`；必须核验 SSH 主机密钥。
4. PR 评论不可写时，往同一 PR 分支新增 `.ai-collab/reports/PR-<号码>-<受测短SHA>.md`，只提交脱敏报告，不触碰 `main`。

首次密钥配置只提交**公钥**到 GitHub 网页，绝不提交私钥。已配置的同一账号 SSH 通道可以在具备访问权限的其他项目中复用。

## V1.1：一个 PR 链接完成交接

V1.1 在 V1.0 的单文件协作基础上，加入**标准任务状态、简短交接卡、失败分类和可追踪的重试尝试**。无需新增服务，双方仍由用户主动启动。

现在日常开发可以这样做：

1. 给 ChatGPT 提需求，由它创建 Issue、工作分支和 PR，并在 PR 描述中写入 `[AI_DEV_BRIDGE_HANDOFF]`，包含任务范围、验收标准、实际编译／测试命令。
2. 对 WorkBuddy 只需发送：**“执行此 PR：https://github.com/OWNER/REPO/pull/12”**。它按 `AGENTS.md` 自行获取最新完整 SHA，运行任务并回传报告。
3. 回来对 ChatGPT 只需发送：**“验收此 PR：https://github.com/OWNER/REPO/pull/12”**。它自行检查 PR 差异、评论与 `.ai-collab/reports/`，核对实际受测版本和报告。
4. 如果失败，按 `CODE` / `TEST` / `ENVIRONMENT` / `PERMISSION` 分类：应修代码的提交新 SHA 再测；缺权限或工具的报告 `BLOCKED`，不靠猜测处理。
5. 每次重测通过 `Attempt` 编号保留历史，避免新报告覆盖旧失败证据。通常连续 3 次未通过则请求人工复核。

<details>
<summary>PR 最小交接块示例</summary>

```text
[AI_DEV_BRIDGE_HANDOFF]
Protocol: 1.1
Issue: https://github.com/OWNER/REPO/issues/11
PR: https://github.com/OWNER/REPO/pull/12
Scope: 修复 JSON 数组解析
Acceptance: 单元测试与回归测试通过
Build: <由项目提供的真实构建命令>
Tests: <由项目提供的真实测试命令>
Deployment: DISABLED
[/AI_DEV_BRIDGE_HANDOFF]
```

</details>

**注意：**“一个 PR 链接”减少的是**人工复制指令**，不代表 WorkBuddy 和 ChatGPT 会自动互相通知。新增的 V1.1 重试约定也不是自主循环执行器。跨项目新手仍只需复制根目录的 `AGENTS.md`。

## V1.2 候选：可选的 GitHub 原生自动通知

V1.2 在 V1.1 的一链接交接之上，尝试进一步降低人工催促：由 GitHub Actions 对**同仓库、非 Draft、带 `[AI_DEV_BRIDGE_HANDOFF]` 的 PR** 自动写一条通知评论。用户若订阅 PR，可按自己的 GitHub 通知设置收到提醒。

| GitHub 事件 | PR 通知 | 下一位处理者 |
| --- | --- | --- |
| 合格 PR 创建 / 编辑 / 重新打开 | `CODE_READY` | WorkBuddy 实测 |
| PR 代码或配置变更 | `CODE_READY` | WorkBuddy 重新核对 SHA |
| PR 仅新增符合格式的执行报告文件 | `REVIEW_PENDING` | ChatGPT 核对证据 |

**通知不等于执行完成，更不会自行启动 WorkBuddy/ChatGPT。** `REVIEW_PENDING` 仅表示报告已送达，不能自动理解为 PASS/VERIFIED，仍需 ChatGPT 真正检查受测 SHA、报告提交与退出码。

### 需要额外启用的可选组件

单文件 `AGENTS.md` 依然完全支持 V1.1 人工交接。想启用自动评论通知时，仓库负责人需额外审查并复制以下两个文件到目标仓库同名路径，然后启用允许 GitHub Actions 给 PR 留言的仓库权限：

- `.github/workflows/ai-dev-bridge-notify.yml` — 使用 `pull_request`，仅在同仓库且非 Draft PR 执行。
- `.github/scripts/bridge_notify.py` — 只通过 GitHub API 查询变更和留言，依赖 Python 标准库，无需外部服务或令牌配置。

提示：仓库若限制 `GITHUB_TOKEN` 写权限，工作流可能报 403 并无法留言；不能绕过权限。对于来自 Fork 的 PR，通知任务直接跳过。可用 `python3 -m unittest discover -s tests -p 'test_bridge_notify.py' -v` 执行本仓库的离线验证用例。

这仍是开发中的 **V1.2 候选**，GitHub Actions 的实测通知效果以对应工作流和 WorkBuddy 报告为准。若 Actions 禁用，照旧按 V1.1 手动把 PR 链接交给两个 AI。
## 跨会话恢复

每次重开 ChatGPT / WorkBuddy 会话时，只需提供仓库 URL 或关联 Issue / PR，并要求读取：

```text
AGENTS.md
.ai-collab/PROJECT_CONFIG.md
.ai-collab/PROJECT_STATUS.md
本次相关 Issue、PR、执行报告
```

实时 GitHub 提交与执行证据优先于过时的状态文件。上下文可以恢复，不代表 Agent 会自动运行。

## 安全边界

- 不绕过 GitHub 权限，不公开私有仓库来替代授权。
- 不提交令牌、SSH 私钥、.env、敏感日志或本地 Agent 个人工作目录。
- 默认 PR 流程；不擅自推送 `main`、强推或合并。
- 默认不部署。正式部署前需明确授权、部署 SHA、备份和回滚方案。
- 对原项目已有的开发／代码规范和安全约束保持尊重。

## 验证状态与局限

本协议来源于两轮受控测试：**私有仓库 Git + SSH 交接/报告回传**、**Windows 环境下一项 C++11 小样例的真实编译与 8 组测试**，另在独立第二仓库完成单文件初始化和报告回传验证。

V1.1 还通过 WorkBuddy 的真实 Git + SSH 三轮交接演练：Attempt 1 检测到故意失败，Attempt 2 识别 Windows CRLF 问题，Attempt 3 对受测 Git 提交的检查均成功；全部保留真实 SHA 和报告证据。此次为协议与测试样例验证，构建为 N/A，未执行部署。

这不意味着该协议能在任何项目上自动运行，或所有语言/构建系统均已经测试。新的业务项目必须单独验证访问权限、实际工具链、构建测试、部署条件。某测试环境的 CMake 默认生成器未获得通过验证，因此不将 CMake 测试列为已验证能力。

## 参与贡献

欢迎通过 GitHub Issues 提交适配问题、文档建议和更多实测案例。参见 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [SECURITY.md](SECURITY.md)。

## 开源许可证

本项目采用 [MIT License](LICENSE)。
