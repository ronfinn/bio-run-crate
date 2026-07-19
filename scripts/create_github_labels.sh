#!/usr/bin/env bash
#
# create_github_labels.sh
#
# Create or update the GitHub labels used by the bio-run-crate backlog.
#
# Idempotent: uses `gh label create --force`, which creates a label if it does
# not exist and updates its colour/description if it does. Running this script
# repeatedly never creates duplicates and never deletes existing labels.
#
# Safe by design:
#   - never prints authentication tokens
#   - never reads .env, credentials, keys or local Claude configuration
#   - does not delete or rename existing GitHub content
#
set -euo pipefail

# --- Preflight ---------------------------------------------------------------

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI ('gh') is not installed. See https://cli.github.com/" >&2
  exit 1
fi

# Discard gh auth status output so no token-related detail is ever printed.
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
echo "Creating or updating labels..."

# --- Labels ------------------------------------------------------------------
# Format: "name|colour|description"
# Colours are six-character hexadecimal values without a leading '#'.

labels=(
  "type:feature|1d76db|New functionality or capability"
  "type:documentation|0075ca|Documentation-only change"
  "type:testing|fbca04|Tests, fixtures, or CI checks"
  "type:security|b60205|Security or privacy-related work"
  "area:project|5319e7|Project charter, governance, meta"
  "area:cli|006b75|Command-line interface"
  "area:data-model|0e8a16|Manifest and data models"
  "area:examples|c2e0c6|Synthetic example data"
  "area:validation|1d76db|Validation rules and engine"
  "area:reporting|5319e7|JSON and Markdown reports"
  "area:ro-crate|0052cc|RO-Crate package generation"
  "area:nf-prov|006b75|nf-prov crate import and enrichment"
  "area:profiles|0e8a16|Modality-specific profiles"
  "area:ci|bfdadc|Continuous-integration setup"
  "area:tutorial|c5def5|Tutorials and walkthroughs"
  "area:demo|d4c5f9|Demonstration and release preparation"
  "priority:P0|b60205|Must-have for v0.1.0"
  "priority:P1|d93f0b|Should-have; not blocking v0.1.0"
  "priority:P2|fbca04|Nice-to-have; later"
  "release:v0.1.0|0e8a16|Targeted for the v0.1.0 release"
)

count=0
for entry in "${labels[@]}"; do
  IFS='|' read -r name colour description <<<"${entry}"
  gh label create "${name}" \
    --color "${colour}" \
    --description "${description}" \
    --force >/dev/null
  echo "  created/updated: ${name}"
  count=$((count + 1))
done

echo "Done. ${count} labels created or updated."
