#!/usr/bin/env bash
set -euo pipefail

API="${API:-https://git.seonology.com/api/v1}"
TOK="${TOK:-}"
SPEC="${1:-$(dirname "$0")/gitea-settings.json}"

if [ -z "$TOK" ]; then
  echo "error: TOK is empty. Export a Gitea token before running this script." >&2
  exit 1
fi

for command_name in jq curl; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "error: $command_name is required" >&2
    exit 1
  }
done

REPO="$(jq -r '.repo' "$SPEC")"
OWNER="${REPO%%/*}"
NAME="${REPO##*/}"
REPO_BODY="$(jq -c '{description: .description, website: .website} + .units + .merge' "$SPEC")"
TOPIC_BODY="$(jq -c '{topics: .topics}' "$SPEC")"

curl -fsS -X PATCH -H "Authorization: token $TOK" -H 'Content-Type: application/json' -d "$REPO_BODY" "$API/repos/$OWNER/$NAME" >/dev/null
curl -fsS -X PUT -H "Authorization: token $TOK" -H 'Content-Type: application/json' -d "$TOPIC_BODY" "$API/repos/$OWNER/$NAME/topics" >/dev/null
curl -fsS -H "Authorization: token $TOK" "$API/repos/$OWNER/$NAME" | jq '{full_name,description,website,private,default_branch,has_issues,has_wiki,has_projects,has_pull_requests,has_releases,has_packages,has_actions,has_code,allow_merge_commits,allow_squash_merge,allow_rebase,default_merge_style,default_delete_after_merge: .default_delete_branch_after_merge}'
curl -fsS -H "Authorization: token $TOK" "$API/repos/$OWNER/$NAME/topics" | jq '.topics'
