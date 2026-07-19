#!/usr/bin/env bash
#
# create_github_issues.sh
#
# Create the bio-run-crate backlog issues described in planning/github/issues.tsv.
#
# The TSV is the single source of truth. Each row references a Markdown body
# file, an issue title, a comma-separated label list, and a milestone title.
#
# Idempotent: the script snapshots every existing issue title (open and closed)
# once, then creates only the issues whose exact title is not already present.
# It never edits, closes, deletes or renames existing issues.
#
# Safe by design:
#   - never prints authentication tokens
#   - never reads .env, credentials, keys or local Claude configuration
#
set -euo pipefail

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

# Resolve paths relative to the repository root so the script works from any CWD.
REPO_ROOT="$(git rev-parse --show-toplevel)"
TSV_FILE="${REPO_ROOT}/planning/github/issues.tsv"
BODY_DIR="${REPO_ROOT}/planning/github/issues"

if [[ ! -f "${TSV_FILE}" ]]; then
  echo "ERROR: issues file not found: ${TSV_FILE}" >&2
  exit 1
fi

echo "Repository: ${REPO}"
echo "Reading: ${TSV_FILE}"

# --- Snapshot existing titles (open + closed) --------------------------------
# Compare exact strings; 'gh issue list --search' is fuzzy and unsafe for this.

existing_titles="$(gh issue list --state all --limit 500 --json title --jq '.[].title')"

title_exists() {
  local needle="$1"
  # Exact, whole-line match against the snapshot.
  grep -Fxq -- "${needle}" <<<"${existing_titles}"
}

# --- Create missing issues ---------------------------------------------------

created=0
skipped=0
line_no=0

while IFS=$'\t' read -r body_file title labels milestone || [[ -n "${body_file}" ]]; do
  line_no=$((line_no + 1))

  # Skip the header row and any blank lines.
  [[ -z "${body_file}" ]] && continue
  [[ "${body_file}" == \#* ]] && continue
  [[ "${body_file}" == "body_file" ]] && continue

  body_path="${BODY_DIR}/${body_file}"
  if [[ ! -f "${body_path}" ]]; then
    echo "ERROR: body file missing for '${title}': ${body_path}" >&2
    exit 1
  fi

  if title_exists "${title}"; then
    echo "  skipping (exists): ${title}"
    skipped=$((skipped + 1))
    continue
  fi

  # Build repeated --label arguments from the comma-separated list.
  label_args=()
  IFS=',' read -ra label_list <<<"${labels}"
  for label in "${label_list[@]}"; do
    # Trim surrounding whitespace.
    label="${label#"${label%%[![:space:]]*}"}"
    label="${label%"${label##*[![:space:]]}"}"
    [[ -n "${label}" ]] && label_args+=(--label "${label}")
  done

  gh issue create \
    --title "${title}" \
    --body-file "${body_path}" \
    --milestone "${milestone}" \
    --assignee "@me" \
    "${label_args[@]}" >/dev/null

  echo "  created: ${title}"
  created=$((created + 1))
done <"${TSV_FILE}"

echo "Done. ${created} issue(s) created, ${skipped} skipped (already existed)."
