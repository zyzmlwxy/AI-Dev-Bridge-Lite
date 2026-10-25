# Security Policy / 安全说明

AI Dev Bridge Lite is a **workflow specification**, not a hosted service. It cannot independently grant access, enforce sandboxing, run tests or protect production credentials. Operators remain responsible for configuring permissions and reviewing commands.

## Supported scope

The current public release is a documentation-led V1.x protocol. Security corrections to access, reporting, privacy and deployment guidance are in scope.

## Reporting vulnerabilities

Do **not** put private keys, access tokens, proprietary source code, production logs or exploit details in a public Issue. Contact the repository maintainer through their GitHub profile or an appropriate private reporting channel if one is enabled. No private reporting channel or response SLA is implied by this file.

## Key safeguards

- GitHub App/OAuth access and SSH push permissions should be scoped to the required repositories.
- Never send or commit private SSH keys or GitHub Personal Access Tokens in prompts or reports.
- Verify SSH host keys; do not bypass identity checks.
- Prefer isolated PR branches, review and full tested-commit SHA verification.
- Treat model-generated commands as untrusted until reviewed for the target machine.
- Do not run destructive commands or deploy production systems without explicit operator approval, backups, and a workable rollback plan.
- Strip sensitive environment details from execution reports before they are committed to a shared or public repository.
- Existing project-specific security policies override this general guide when stricter.
