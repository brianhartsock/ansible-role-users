# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `weareinteractive.users`, an Ansible role that manages Linux users, groups, SSH keys, and authorized keys. It targets Ubuntu, Debian, and CentOS (EL 7). Requires Ansible >= 2.4.

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
- `.ansible-lint` skips `yaml` rules (handled by yamllint) and excludes `./meta/readme.yml` and `.venv`
- `.yamllint` uses ansible-lint recommended settings with 160-char line limit and forbids implicit/explicit octal values
- `.flake8` excludes `.venv`

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
