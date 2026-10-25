# Changelog

## 1.0.0 — Initial public release

- Portable single-file `AGENTS.md` bootstrap protocol.
- ChatGPT / WorkBuddy roles with GitHub Issue and PR handoff.
- Real build/test execution reports with exact tested commit SHA.
- Git + SSH fallback when connectors cannot access private repositories or write PR comments.
- Cross-session recovery via `.ai-collab/PROJECT_CONFIG.md` and `.ai-collab/PROJECT_STATUS.md`.
- Browser-only onboarding and bilingual guides.
- Default-deny production deployment and no autonomous scheduler.

### Validation notes

The collaboration workflow has been exercised in private GitHub repositories, including a basic C++11 smoke test built with g++ and eight passing test cases. An independent second repository completed the single-file bootstrap and report handoff. These observations are limited to those environments; project-specific build and deployment support is not guaranteed.

### Known limitations

- Some GitHub connectors do not have private-repository access or comment permissions.
- Git + SSH requires an authorized local runtime and, for some environments, one-time public-key enrollment.
- No background automation or cross-agent wake-up is provided.
- Additional build generators, including one Windows CMake default-generator path, were not fully validated.
