# RE3 N64 — Codex network access setup

## Important
A repository file cannot grant network permissions or bypass a host's command sandbox. This `.codex/config.toml` **requests** network access for `workspace-write` sandbox mode only where Codex accepts project-local configuration and the host permits it. A higher-priority policy or cloud environment restriction wins.

## Installation
Copy `.codex/config.toml` into the repository root, preserving the `.codex/` directory. Do not replace an existing config without merging settings.

## Cloud Codex
Open Codex environment settings for the RE3-N64-Port environment. Enable internet access for the environment if offered, select an appropriate allowed-domain policy, and restart the task/environment. GitHub repository checkout is usually managed by Codex; don't assume manually cloning the same repo is necessary.

## Local Codex CLI
Network access is controlled by the selected sandbox and approval policy. If allowed, use workspace-write with network access. Never turn off the sandbox or run with unrestricted permissions solely to fix a clone failure.

## Diagnostics for Codex
1. Print `pwd` and `git remote -v` (do not print credential-bearing remote URLs).
2. Check whether the repository is already checked out (`git status`). If so, do not clone again.
3. Check DNS/HTTPS access to `github.com` and any dependency hosts with approved commands.
4. If blocked, report the exact command and error, and request environment network permission. Do not loop retries.
5. After access is available, run host tests, then N64 build checks.

## Security
Do not commit GitHub tokens, Google Drive OAuth tokens, Dropbox keys, ROM/ISO images or private credentials. Prefer pinned dependencies and minimal network allowlists.
