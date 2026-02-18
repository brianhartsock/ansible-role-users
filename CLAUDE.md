# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `brianhartsock.users` (a fork of `weareinteractive.users`), an Ansible role that manages Linux users, groups, SSH keys, and authorized keys. It targets Ubuntu, Debian, and CentOS (EL 7). Requires Ansible >= 2.4.

## Commands

### Install Dependencies
```
uv sync
```

### Lint (all hooks)
```
uv run pre-commit run --all-files
```
Runs yamllint, ansible-lint, and flake8 via pre-commit. Individual linters:
```
uv run yamllint .
uv run ansible-lint
uv run flake8
```

### Lint Config Notes
- `.ansible-lint` skips `yaml` rules (handled by yamllint) and excludes `.venv`
- `.yamllint` uses ansible-lint recommended settings with 160-char line limit and forbids implicit/explicit octal values
- `.flake8` excludes `.venv`

### CI (GitHub Actions)
- **Lint job** (`ci.yml`): runs yamllint, ansible-lint, and flake8 on every push/PR to `master`
- **Molecule job** (`ci.yml`): runs `molecule test` with Docker (Ubuntu 22.04 jammy, Ubuntu 24.04 noble) after lint passes
- **Release job** (`release.yml`): imports the role to Ansible Galaxy via `ansible-galaxy role import` when a GitHub release is published

### Molecule
- Single scenario: `molecule/default/molecule.yml`
- Driver: Docker
- Platforms: `ubuntu:22.04` (jammy), `ubuntu:24.04` (noble)
- Verifier: testinfra

## Architecture

### Task Flow
`tasks/main.yml` imports `manage.yml`, which orchestrates the full workflow:
1. Creates the primary group (`users_group`) and secondary groups (`users_groups`)
2. Loops over `users` list, including `manage_user.yml` per user
3. `manage_user.yml` creates the user (via `ansible.builtin.user`) then imports `manage_user_home.yml` to configure home directory, SSH keys, authorized keys, and dotfiles
4. Removes users listed in `users_remove`

### Per-User Properties
Each user in the `users` list is a dict with `username` (required) and optional overrides. Per-user properties (e.g., `group`, `home_mode`, `ssh_key`) override role-level defaults (e.g., `users_group`, `users_home_mode`). The fallback pattern is: `user.<property> | default(users_<property>)`.

### Key Conventions
- Uses `ansible.builtin.user` and `ansible.builtin.group` with fully qualified collection names
- Task names include the username: `"Adding user '{{ user.username }}' to the system"`
- Loop variable for user iteration is `user` (set via `loop_control.loop_var`)
- SSH private key tasks use `no_log: true`
- All tasks are tagged with `users` and `users-manage`

## Development Workflow

Follow this workflow for all code changes.

```
Code → Document → Verify → Code Review
  ^                              |
  └──── fix issues ──────────────┘
```

### 1. Code

Make the implementation changes. Use FQCNs, name all tasks, and follow the patterns in existing task files.

### 2. Document

Update README.md and CLAUDE.md to reflect any changes to variables, platforms, commands, or architecture. If the ansible plugin is installed, use the `documentator` agent.

### 3. Verify

Run linters (yamllint, ansible-lint, flake8), pre-commit hooks, and molecule tests. All checks must pass before proceeding. If the ansible plugin is installed, use the `verifier` agent.

### 4. Code Review

Review the changes for Ansible best practices, idempotency, security, cross-platform correctness, and test coverage. If the ansible plugin is installed, use the `code-reviewer` agent.

### 5. Iterate

If verification or code review flags issues, fix them and repeat from step 2. Continue until all checks pass and the review is clean.
