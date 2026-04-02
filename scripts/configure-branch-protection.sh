#!/usr/bin/env bash
set -euo pipefail

REPO="brianhartsock/ansible-role-users"
BRANCH="master"
REQUIRED_CHECKS=("Lint" "Molecule")

CHECK_ONLY=false
if [[ "${1:-}" == "--check" ]]; then
    CHECK_ONLY=true
fi

echo "Repository: $REPO"
echo "Branch: $BRANCH"
echo "Required checks: ${REQUIRED_CHECKS[*]}"
echo ""

# Fetch current branch protection
CURRENT=$(gh api "repos/$REPO/branches/$BRANCH/protection" 2>/dev/null || echo "none")

if [[ "$CURRENT" == "none" ]]; then
    echo "Status: No branch protection rules configured."
    echo ""

    if $CHECK_ONLY; then
        echo "Missing checks: ${REQUIRED_CHECKS[*]}"
        echo "Run without --check to configure branch protection."
        exit 0
    fi
else
    echo "Current branch protection:"
    EXISTING_CHECKS=$(echo "$CURRENT" | jq -r '.required_status_checks.contexts // [] | .[]' 2>/dev/null || echo "")

    if [[ -n "$EXISTING_CHECKS" ]]; then
        echo "  Required status checks:"
        echo "$EXISTING_CHECKS" | while read -r check; do
            echo "    - $check"
        done
    else
        echo "  No required status checks."
    fi
    echo ""

    # Check for missing checks
    MISSING=()
    for check in "${REQUIRED_CHECKS[@]}"; do
        if ! echo "$EXISTING_CHECKS" | grep -qx "$check"; then
            MISSING+=("$check")
        fi
    done

    if [[ ${#MISSING[@]} -eq 0 ]]; then
        echo "All required checks are configured."
        exit 0
    fi

    echo "Missing checks: ${MISSING[*]}"

    if $CHECK_ONLY; then
        echo "Run without --check to configure branch protection."
        exit 0
    fi
fi

echo "Configuring branch protection..."

# Build the checks array for the API
CHECKS_JSON=$(printf '%s\n' "${REQUIRED_CHECKS[@]}" | jq -R . | jq -sc '[.[] | {context: ., app_id: -1}]')

gh api "repos/$REPO/branches/$BRANCH/protection" \
    --method PUT \
    --input - <<EOF
{
  "required_status_checks": {
    "strict": false,
    "checks": $CHECKS_JSON
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF

echo ""
echo "Verifying configuration..."

UPDATED=$(gh api "repos/$REPO/branches/$BRANCH/protection/required_status_checks" 2>/dev/null)
echo "Required status checks after update:"
echo "$UPDATED" | jq -r '.checks[] .context' | while read -r check; do
    echo "  - $check"
done

echo ""
echo "Branch protection configured successfully."
