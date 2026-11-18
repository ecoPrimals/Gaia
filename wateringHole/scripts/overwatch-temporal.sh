#!/usr/bin/env bash
# DEPRECATION: Target replacement is membrane temporal.cascade / gate.check:
#   membrane gate.check --json [--pull]
# Partially replaced by primalSpring temporal_cascade.sh + graph.execute("sync_diverge").
#
# overwatch-temporal.sh — Gate-agnostic Forgejo-level temporal check
#
# Queries all Forgejo orgs, compares remote HEAD SHAs against local clones,
# and reports divergences. Requires only curl + python3 (or jq). No SSH needed
# for the check phase (Forgejo HTTPS API is public/read).
#
# Can be run from ANY gate with a local ecoPrimals workspace clone.
#
# Usage:
#   overwatch-temporal.sh                  # human-readable table
#   overwatch-temporal.sh --json           # machine-readable JSON
#   overwatch-temporal.sh --pull           # also pull diverged repos
#   overwatch-temporal.sh --json --pull    # both
#
# Environment:
#   ECOPRIMAL_ROOT   Override workspace root (default: auto-detect via .gate file)
#   FORGEJO_URL      Override Forgejo base URL (default: https://git.primals.eco)

set -euo pipefail

FORGEJO_URL="${FORGEJO_URL:-https://git.primals.eco}"
ORGS=("ecoPrimals" "sporeGarden" "syntheticChemistry" "protoKarya")
SEARCH_DIRS=("primals" "gardens" "springs" "infra" "protists")

FLAG_JSON=false
FLAG_PULL=false

for arg in "$@"; do
    case "$arg" in
        --json) FLAG_JSON=true ;;
        --pull) FLAG_PULL=true ;;
        --help|-h)
            echo "Usage: overwatch-temporal.sh [--json] [--pull]"
            echo ""
            echo "Gate-agnostic Forgejo temporal check. Compares remote HEAD"
            echo "against local clones across all ecosystem orgs."
            echo ""
            echo "  --json   Output machine-readable JSON"
            echo "  --pull   Pull diverged repos after checking"
            echo ""
            echo "Environment:"
            echo "  ECOPRIMAL_ROOT   Workspace root (auto-detected via .gate)"
            echo "  FORGEJO_URL      Forgejo base URL (default: git.primals.eco)"
            exit 0
            ;;
        *) echo "Unknown flag: $arg" >&2; exit 1 ;;
    esac
done

find_workspace_root() {
    if [ -n "${ECOPRIMAL_ROOT:-}" ]; then
        echo "$ECOPRIMAL_ROOT"
        return
    fi
    local dir="$PWD"
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/.gate" ]; then
            echo "$dir"
            return
        fi
        dir="$(dirname "$dir")"
    done
    echo "ERROR: Cannot find workspace root (.gate file). Set ECOPRIMAL_ROOT." >&2
    exit 1
}

ROOT="$(find_workspace_root)"
GATE="$(cat "$ROOT/.gate" 2>/dev/null || echo "unknown")"

find_local_dir() {
    local repo="$1"
    for base in "${SEARCH_DIRS[@]}"; do
        local candidate="$ROOT/$base/$repo"
        if [ -d "$candidate/.git" ]; then
            echo "$candidate"
            return
        fi
    done
    echo ""
}

get_forgejo_repos() {
    local org="$1"
    curl -sf "$FORGEJO_URL/api/v1/orgs/$org/repos?limit=50" 2>/dev/null || echo "[]"
}

diverged_count=0
ok_count=0
not_cloned_count=0
total_count=0
results=()

check_org() {
    local org="$1"
    local repos_json
    repos_json="$(get_forgejo_repos "$org")"

    local repo_names
    repo_names="$(echo "$repos_json" | python3 -c "
import sys, json
repos = json.load(sys.stdin)
for r in repos:
    print(r['name'])
" 2>/dev/null)" || return

    for repo in $repo_names; do
        total_count=$((total_count + 1))

        local default_branch
        default_branch="$(echo "$repos_json" | python3 -c "
import sys, json
repos = json.load(sys.stdin)
for r in repos:
    if r['name'] == '$repo':
        print(r.get('default_branch', 'main'))
        break
" 2>/dev/null)" || default_branch="main"

        local remote_sha
        remote_sha="$(curl -sf "$FORGEJO_URL/api/v1/repos/$org/$repo/branches/$default_branch" 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('commit', {}).get('id', 'UNKNOWN')[:12])
" 2>/dev/null)" || remote_sha="UNKNOWN"

        local local_dir
        local_dir="$(find_local_dir "$repo")"

        local local_sha="NOT_CLONED"
        local local_base=""
        if [ -n "$local_dir" ]; then
            local_sha="$(cd "$local_dir" && git rev-parse HEAD 2>/dev/null | cut -c1-12)" || local_sha="ERROR"
            local_base="${local_dir#$ROOT/}"
        fi

        local status
        if [ "$local_sha" = "NOT_CLONED" ]; then
            status="NOT_CLONED"
            not_cloned_count=$((not_cloned_count + 1))
        elif [ "$remote_sha" = "UNKNOWN" ]; then
            status="UNKNOWN"
        elif [ "$remote_sha" = "$local_sha" ]; then
            status="OK"
            ok_count=$((ok_count + 1))
        else
            status="DIVERGED"
            diverged_count=$((diverged_count + 1))
        fi

        results+=("$org|$repo|$default_branch|$remote_sha|$local_sha|$local_base|$status")

        if [ "$FLAG_PULL" = true ] && [ "$status" = "DIVERGED" ] && [ -n "$local_dir" ]; then
            (
                cd "$local_dir"
                git branch --set-upstream-to="origin/$default_branch" "$default_branch" 2>/dev/null || true
                git pull --rebase --quiet 2>/dev/null
            )
            if [ "$FLAG_JSON" = false ]; then
                echo "  PULLED: $org/$repo"
            fi
        fi
    done
}

if [ "$FLAG_JSON" = false ]; then
    echo "overwatch-temporal: Forgejo sweep from $GATE"
    echo "  workspace: $ROOT"
    echo "  forgejo:   $FORGEJO_URL"
    echo "  orgs:      ${ORGS[*]}"
    echo ""
fi

for org in "${ORGS[@]}"; do
    check_org "$org"
done

if [ "$FLAG_JSON" = true ]; then
    python3 -c "
import json, sys

results = []
for line in sys.argv[1:]:
    parts = line.split('|')
    results.append({
        'org': parts[0],
        'repo': parts[1],
        'branch': parts[2],
        'remote_sha': parts[3],
        'local_sha': parts[4],
        'local_path': parts[5],
        'status': parts[6]
    })

output = {
    'gate': '$GATE',
    'workspace': '$ROOT',
    'forgejo': '$FORGEJO_URL',
    'total': $total_count,
    'ok': $ok_count,
    'diverged': $diverged_count,
    'not_cloned': $not_cloned_count,
    'repos': results
}
print(json.dumps(output, indent=2))
" "${results[@]}"
else
    if [ "$diverged_count" -gt 0 ]; then
        echo "DIVERGED ($diverged_count):"
        for r in "${results[@]}"; do
            IFS='|' read -r org repo branch remote local path status <<< "$r"
            if [ "$status" = "DIVERGED" ]; then
                echo "  $org/$repo ($branch)  remote=$remote  local=$local  [$path]"
            fi
        done
        echo ""
    fi

    if [ "$not_cloned_count" -gt 0 ]; then
        echo "NOT CLONED ($not_cloned_count):"
        for r in "${results[@]}"; do
            IFS='|' read -r org repo branch remote local path status <<< "$r"
            if [ "$status" = "NOT_CLONED" ]; then
                echo "  $org/$repo ($branch)  remote=$remote"
            fi
        done
        echo ""
    fi

    echo "--- SUMMARY ---"
    echo "  Total:      $total_count repos across ${#ORGS[@]} orgs"
    echo "  OK:         $ok_count"
    echo "  Diverged:   $diverged_count"
    echo "  Not cloned: $not_cloned_count"
    echo "  Gate:       $GATE"

    if [ "$diverged_count" -eq 0 ] && [ "$not_cloned_count" -eq 0 ]; then
        echo ""
        echo "ALL REPOS CONVERGED."
    fi
fi
