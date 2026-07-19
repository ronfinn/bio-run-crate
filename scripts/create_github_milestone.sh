#!/usr/bin/env bash
#
# create_github_milestone.sh
#
# Create the 'v0.1.0' GitHub milestone if it does not already exist.
#
# The GitHub CLI has no dedicated top-level milestone command, so this uses
# `gh api` against the repository's milestones endpoint.
#
# Idempotent: the script first lists all existing milestones (open and closed)
# and skips creation if one with the exact title 'v0.1.0' is already present.
# It never deletes or renames existing milestones.
#
# Safe by design:
#   - never prints authentication tokens
#   - never reads .env, credentials, keys or local Claude configuration
#
set -euo pipefail

MILESTONE_TITLE="v0.1.0"
MILESTONE_DESCRIPTION="First tagged release: minimal validating CLI and RO-Crate 1.2 generation."

# --- Preflight ---------------------------------------------------------------

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI ('gh') is not installed. See https://cli.github.com/" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: 'gh' is not authenticated. Run 'gh auth login' first." >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: current directory is not a Git repository." >&2
  exit 1
fi

REPO="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
if [[ -z "${REPO}" ]]; then
  echo "ERROR: could not determine the current GitHub repository." >&2
  exit 1
fi

echo "Repository: ${REPO}"

# --- Idempotency check -------------------------------------------------------
# List every milestone title (open and closed) and look for an exact match.

exists="no"
while IFS= read -r title; do
  if [[ "${title}" == "${MILESTONE_TITLE}" ]]; then
    exists="yes"
    break
  fi
done < <(gh api "repos/${REPO}/milestones?state=all" --jq '.[].title')

if [[ "${exists}" == "yes" ]]; then
  echo "Skipping: milestone '${MILESTONE_TITLE}' already exists."
  exit 0
fi

# --- Create ------------------------------------------------------------------

gh api "repos/${REPO}/milestones" \
  -f title="${MILESTONE_TITLE}" \
  -f state="open" \
  -f description="${MILESTONE_DESCRIPTION}" >/dev/null

echo "Created milestone '${MILESTONE_TITLE}'."
