# AI Dev Bridge Lite — PROJECT_CONFIG

Status: **fail-closed baseline; execution disabled**

**Machine-readable source of truth:** `.ai-collab/PROJECT_CONFIG.json` is authoritative for executor parsing. This Markdown file is the human-readable explanation and must be kept consistent with the JSON. The executor must parse and validate JSON strictly; it must not scrape this Markdown table to obtain execution settings. If the JSON is missing, invalid, has an unsupported schema version, contains unknown safety-critical values, or conflicts with this document, execution is `BLOCKED`.

This file is intended to be read from the trusted base branch (`main`) only. A candidate PR must not use changes it proposes to this file to authorize its own execution. This configuration becomes trusted policy only after review and merge.

## Configuration

| Key | Value | Meaning |
|---|---|---|
| `schema_version` | `1` | Configuration contract version |
| `repository_allowlist` | `zyzmlwxy/AI-Dev-Bridge-Lite` | Exact repository allowed for task discovery |
| `base_branch` | `main` | Only this base branch is eligible |
| `required_opt_in_label` | `ai-bridge:execute` | Explicit task opt-in; not an execution grant by itself |
| `execution_enabled` | `false` | Hard stop: no project command may run |
| `workspace_profile` | `UNCONFIGURED` | No local workspace is approved yet |
| `allowed_commands` | `[]` | Empty allowlist: no project command is authorized |
| `working_directory` | `UNCONFIGURED` | Must be configured and verified before execution |
| `command_timeout_seconds` | `60` | Conservative default; applies only after explicit enablement |
| `writable_paths` | `.ai-collab/reports/` | Report-only path after separately approved execution; no source writes |
| `report_contract` | `V1.3` | Must satisfy the V1.3 evidence/report gate |
| `retry_policy` | `NO_AUTOMATIC_RETRY` | Uncertain or failed runs require reconciliation and human approval |
| `deployment` | `DISABLED` | No deployment, release, or merge authorization |
| `executor_profile` | `SINGLE_ACTIVE_EXECUTOR` | Current MVP operational profile |
| `multi_executor_mode` | `DEFERRED` | Not prohibited by the protocol; requires separate validation before enablement |

## Tool resolution

- Do not modify system or user `PATH` automatically.
- A future local runner may use explicitly configured absolute executable paths after verifying that the binaries exist and reporting their versions.
- Tool paths are machine-local settings and must not be committed to this public repository.
- Missing tools, ambiguous paths, an unapproved workspace, a dirty worktree, or an unknown configuration value must fail closed.

## Enablement requirements

Changing `execution_enabled` to `true` is not sufficient by itself. The owner must separately review and approve:
1. a dedicated clean workspace checked out at an exact source SHA;
2. a non-empty exact command allowlist and working directory;
3. tool executable paths and bounded timeouts;
4. single-flight behavior for the scheduled task;
5. a harmless pilot command and its evidence/report procedure.

Until those requirements are met and the owner explicitly authorizes the pilot, outcomes may include discovery/claim states, but no project command may execute.
