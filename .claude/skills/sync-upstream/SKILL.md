---
name: sync-upstream
description: >
  This skill should be used when the user asks to "sync with upstream",
  "merge upstream changes", "check upstream for updates", "pull from upstream",
  "compare with upstream", "fetch upstream", or mentions syncing, merging, or
  pulling from the upstream repository (weareinteractive/ansible-users).
---

# Sync Upstream

Synchronize the local fork with the upstream repository
(`git@github.com:weareinteractive/ansible-users.git`). This skill handles
adding the remote, fetching, comparing, and merging with user approval at
each step.

## Workflow

### Step 1: Ensure Upstream Remote Exists

Check if the `upstream` remote is already configured:

```
git remote -v
```

If `upstream` is not listed, add it:

```
git remote add upstream git@github.com:weareinteractive/ansible-users.git
```

### Step 2: Fetch Upstream

Fetch the latest state from upstream:

```
git fetch upstream
```

### Step 3: Compare Differences

Determine the current branch name, then run these comparisons:

1. **Commit divergence** - Count commits ahead/behind:
   ```
   git rev-list --count HEAD..upstream/master
   git rev-list --count upstream/master..HEAD
   ```

2. **Upstream commit log** - Show commits not yet in local:
   ```
   git log --oneline HEAD..upstream/master
   ```

3. **Diff stat** - Show files changed upstream since the fork point:
   ```
   git diff --stat HEAD...upstream/master
   ```

4. **Potential conflicts** - Identify files modified in both branches since
   the merge base:
   ```
   git diff --name-only $(git merge-base HEAD upstream/master)..HEAD
   git diff --name-only $(git merge-base HEAD upstream/master)..upstream/master
   ```
   Cross-reference both lists. Files appearing in both were modified on each
   side and may produce merge conflicts.

Present a clear summary to the user including:
- Number of upstream commits to merge
- Number of local-only commits
- The upstream commit log
- The file-level diff stat
- Any files likely to conflict

If upstream has **zero** new commits, report that the fork is up to date and
stop here.

### Step 4: Prompt Before Merging

Use `AskUserQuestion` to ask the user whether to proceed with the merge.
Include the option to view full diffs of specific files before deciding. Do
**not** merge without explicit user approval.

If the user wants to inspect specific changes first, show them with:
```
git diff HEAD...upstream/master -- <file>
```

### Step 5: Merge

Once the user approves, merge upstream into the current branch:

```
git merge upstream/master
```

Do **not** use `--squash` or `--rebase` unless the user requests it.

### Step 6: Handle Conflicts

If the merge produces conflicts:

1. Run `git diff --name-only --diff-filter=U` to list conflicted files.
2. For each conflicted file:
   - Read the file and show the conflict markers to the user.
   - Ask the user how to resolve (keep ours, keep theirs, or manual edit).
   - Apply the resolution and stage the file with `git add`.
3. After all conflicts are resolved, complete the merge with `git commit`
   (use the default merge commit message unless the user specifies otherwise).

### Step 7: Verify

After a successful merge, run `git log --oneline -5` to confirm the merge
commit and summarize what was merged.
