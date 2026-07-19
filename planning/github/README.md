# GitHub backlog bootstrap

This directory is the version-controlled source of truth for the project's
GitHub backlog: its labels, its `v0.1.0` milestone, and its Milestone 0 issues.
The issue text lives here as Markdown; three scripts under `scripts/` push it to
GitHub with the [`gh`](https://cli.github.com/) CLI.

The whole system is **auditable** (everything is in git) and **idempotent**
(every script is safe to run repeatedly — it never creates duplicates and never
deletes or renames existing GitHub content).

## Layout

```
planning/github/
  README.md            # this file
  issues.tsv           # maps body files -> title, labels, milestone
  issues/              # one Markdown body per issue (01..15)
scripts/
  create_github_labels.sh
  create_github_milestone.sh
  create_github_issues.sh
```

`issues.tsv` is tab-separated with four columns:

| Column | Meaning |
|--------|---------|
| `body_file` | filename under `planning/github/issues/` |
| `title` | exact GitHub issue title |
| `labels` | comma-separated label names |
| `milestone` | milestone title (`v0.1.0`) |

## Prerequisites

- `gh` is installed and authenticated (`gh auth login`).
- You are inside a clone of this repository whose GitHub remote is the intended
  target. Each script confirms the target with
  `gh repo view --json nameWithOwner --jq '.nameWithOwner'`.

The scripts never print authentication tokens and never read `.env`,
credentials, keys, or local Claude configuration.

## How the scripts work

### 1. `scripts/create_github_labels.sh`
Creates or updates every label used by the backlog using
`gh label create --force`. Because `--force` is an upsert (create if missing,
update colour/description if present), the script is inherently idempotent.

### 2. `scripts/create_github_milestone.sh`
Creates the `v0.1.0` milestone. GitHub CLI has no dedicated milestone command,
so it uses `gh api`. It first lists all existing milestones (open and closed)
and **skips creation if a milestone titled exactly `v0.1.0` already exists**.

### 3. `scripts/create_github_issues.sh`
Reads `issues.tsv`, snapshots every existing issue title (open and closed) once,
and creates only the issues whose exact title is not already present. Each new
issue is created with `gh issue create --body-file`, all of its labels, an
assignment to `@me`, and the `v0.1.0` milestone. Existing issues are reported as
skipped.

## Order of operations

Run the scripts in this order — issues reference both labels and the milestone,
so those must exist first:

```bash
./scripts/create_github_labels.sh
./scripts/create_github_milestone.sh
./scripts/create_github_issues.sh
```

## Safe to rerun

All three scripts are idempotent:

- **Labels** — `gh label create --force` upserts; rerunning just refreshes them.
- **Milestone** — skipped if a milestone titled `v0.1.0` already exists.
- **Issues** — skipped if an issue with the exact title already exists.

No script deletes, closes, or renames existing content. Rerunning after a
partial run simply fills in whatever is missing.

## Verifying the result

```bash
# Labels
gh label list

# Milestone (should list "v0.1.0")
gh api repos/:owner/:repo/milestones --jq '.[].title'

# Issues in the milestone (open + closed)
gh issue list --state all --milestone v0.1.0
```

Rerun any script and confirm it reports "skipping" and creates nothing new.

## Adding another issue later

1. Create a new body file, e.g. `planning/github/issues/16-my-topic.md`,
   following the section structure used by the existing issues
   (`## Problem`, `## Scope`, `## Out of scope`, `## Acceptance criteria` ending
   with the common checklist).
2. Append one tab-separated row to `issues.tsv`:
   `16-my-topic.md<TAB>My issue title<TAB>type:feature,area:cli,priority:P1,release:v0.1.0<TAB>v0.1.0`
3. If the row uses a new label, add it to `scripts/create_github_labels.sh` and
   rerun that script.
4. Rerun `./scripts/create_github_issues.sh`. Existing issues are skipped; only
   the new one is created.
