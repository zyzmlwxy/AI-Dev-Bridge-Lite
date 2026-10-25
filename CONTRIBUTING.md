# Contributing / 贡献指南

Thanks for helping improve AI Dev Bridge Lite.

欢迎贡献文档修正、兼容性验证及经过脱敏的使用案例。

## Scope / 范围

Useful contributions include:
- Better onboarding for browser-only GitHub users.
- Clearer Git + SSH setup and permission troubleshooting.
- Cross-platform, reproducible handoff report examples.
- Security hardening and corrections to the `AGENTS.md` protocol.

Please open an Issue before proposing major architectural changes. This is intentionally a **minimal, no-server** protocol; daemon-based automation belongs in separately scoped proposals.

## Pull requests

1. Create a small, focused branch and pull request.
2. Explain what was changed and how it was checked.
3. Do not claim tests ran unless you include actual execution evidence.
4. Keep user-specific configuration, private URLs, machine paths and credentials out of commits.
5. Preserve compatibility with a standalone root-level `AGENTS.md` file.
6. If adding a new required file, explain why the one-file onboarding path remains intact.

## Responsible disclosure / 安全问题

Do not disclose credentials or private project details through public Issues. Follow [SECURITY.md](SECURITY.md).
