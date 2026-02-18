# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `weareinteractive.users`, an Ansible role that manages Linux users, groups, SSH keys, and authorized keys. It targets Ubuntu, Debian, and CentOS (EL 7). Requires Ansible >= 2.4.

## Commands

### Install Dependencies
```
uv sync
```

### Lint
```
make lint
```
Runs `uv run ansible-lint .` (excludes `./meta/readme.yml` and `.venv` per `.ansible-lint` config).

### Test (Docker-based)
```
make ubuntu22.04   # or ubuntu20.04, ubuntu18.04, ubuntu16.04
make debian11      # or debian10, debian9, debian8
```
Tests run inside Docker containers via `ansiblecheck/ansiblecheck` images. Each target runs syntax check, playbook execution, and idempotence verification against `tests/main.yml`.

### Generate Docs
```
gem install ansible-role
make docs
```
Regenerates `README.md` from `meta/readme.yml` via `ansible-role docgen`.

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
