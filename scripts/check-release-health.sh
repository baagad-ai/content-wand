#!/usr/bin/env bash
# =============================================================================
# check-release-health.sh — content-wand release health check
#
# Prints a PASS/WARN/FAIL report for each release-readiness criterion.
# This script is INFORMATIONAL ONLY — it always exits 0 and never blocks.
# Designed to be called from a git pre-push hook or run manually.
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Resolve repo root (works whether called from hook or manually)
# ---------------------------------------------------------------------------
REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || git rev-parse --show-toplevel)"

# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------
PASS=0
WARN=0
FAIL=0

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
pass() { echo "  ✅ $1"; PASS=$((PASS + 1)); }
warn() { echo "  ⚠️  $1"; WARN=$((WARN + 1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL + 1)); }

section() { echo ""; echo "$1"; }

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         content-wand Release Health Check               ║"
echo "╚══════════════════════════════════════════════════════════╝"

# ===========================================================================
# 1. Required Files
# ===========================================================================
section "📁 Required Files"

# README.md exists
if [[ -f "$REPO_ROOT/README.md" ]]; then
    pass "README.md exists"
else
    fail "README.md missing"
fi

# README.md does NOT contain "Status: In development"
if [[ -f "$REPO_ROOT/README.md" ]]; then
    if grep -qi "Status: In development" "$REPO_ROOT/README.md"; then
        warn 'README.md still contains "In development" — update before release'
    else
        pass 'README.md does not contain "In development"'
    fi
fi

# README.md contains badge markers (img.shields.io)
if [[ -f "$REPO_ROOT/README.md" ]]; then
    if grep -q "img.shields.io" "$REPO_ROOT/README.md"; then
        pass "README.md has badges (img.shields.io)"
    else
        warn "README.md has no badge markers (img.shields.io) — consider adding status badges"
    fi
fi

# LICENSE exists
if [[ -f "$REPO_ROOT/LICENSE" ]]; then
    pass "LICENSE exists"
else
    fail "LICENSE missing — required for open-source releases"
fi

# CHANGELOG.md exists and has a version entry (not just [Unreleased])
if [[ -f "$REPO_ROOT/CHANGELOG.md" ]]; then
    pass "CHANGELOG.md exists"
    # A version entry looks like ## [1.2.3] — any semver-like bracket, not [Unreleased]
    if grep -qP '##\s+\[\d+\.\d+' "$REPO_ROOT/CHANGELOG.md" 2>/dev/null || \
       grep -qE '##[[:space:]]+\[[0-9]+\.[0-9]+' "$REPO_ROOT/CHANGELOG.md"; then
        VERSION_ENTRY=$(grep -oE '\[[0-9]+\.[0-9]+[^]]*\]' "$REPO_ROOT/CHANGELOG.md" | head -1)
        pass "CHANGELOG.md has version entry $VERSION_ENTRY"
    else
        fail "CHANGELOG.md has no version entry — add a release section like ## [1.0.0]"
    fi
else
    fail "CHANGELOG.md missing"
fi

# CONTRIBUTING.md exists
if [[ -f "$REPO_ROOT/CONTRIBUTING.md" ]]; then
    pass "CONTRIBUTING.md exists"
else
    fail "CONTRIBUTING.md missing"
fi

# CODE_OF_CONDUCT.md exists
if [[ -f "$REPO_ROOT/CODE_OF_CONDUCT.md" ]]; then
    pass "CODE_OF_CONDUCT.md exists"
else
    fail "CODE_OF_CONDUCT.md missing"
fi

# SECURITY.md exists
if [[ -f "$REPO_ROOT/SECURITY.md" ]]; then
    pass "SECURITY.md exists"
else
    fail "SECURITY.md missing"
fi

# SUPPORT.md exists
if [[ -f "$REPO_ROOT/SUPPORT.md" ]]; then
    pass "SUPPORT.md exists"
else
    fail "SUPPORT.md missing"
fi

# .gitignore exists and contains ".content-wand/"
if [[ -f "$REPO_ROOT/.gitignore" ]]; then
    pass ".gitignore exists"
    if grep -q "\.content-wand/" "$REPO_ROOT/.gitignore"; then
        pass '.gitignore contains ".content-wand/"'
    else
        fail '.gitignore does not contain ".content-wand/" — local cache may be committed'
    fi
else
    fail ".gitignore missing"
fi

# .github/ISSUE_TEMPLATE/config.yml exists
if [[ -f "$REPO_ROOT/.github/ISSUE_TEMPLATE/config.yml" ]]; then
    pass ".github/ISSUE_TEMPLATE/config.yml exists"
else
    fail ".github/ISSUE_TEMPLATE/config.yml missing"
fi

# .github/workflows/publish.yml exists and does NOT contain "create-release@v1"
if [[ -f "$REPO_ROOT/.github/workflows/publish.yml" ]]; then
    pass ".github/workflows/publish.yml exists"
    if grep -q "create-release@v1" "$REPO_ROOT/.github/workflows/publish.yml"; then
        fail 'publish.yml uses deprecated "create-release@v1" — replace with softprops/action-gh-release or similar'
    else
        pass 'publish.yml does not use deprecated "create-release@v1"'
    fi
else
    fail ".github/workflows/publish.yml missing"
fi

# .github/workflows/stale.yml exists
if [[ -f "$REPO_ROOT/.github/workflows/stale.yml" ]]; then
    pass ".github/workflows/stale.yml exists"
else
    warn ".github/workflows/stale.yml missing — consider adding stale issue management"
fi

# ===========================================================================
# 2. CHANGELOG hygiene
# ===========================================================================
section "📋 CHANGELOG"

if [[ -f "$REPO_ROOT/CHANGELOG.md" ]]; then
    # Has [Unreleased] section
    if grep -q "\[Unreleased\]" "$REPO_ROOT/CHANGELOG.md"; then
        pass "Has [Unreleased] section (good practice for ongoing changes)"
    else
        warn "No [Unreleased] section in CHANGELOG.md — good practice to track upcoming changes"
    fi

    # Last version entry has a date in format YYYY-MM-DD or — YYYY-MM-DD
    LAST_VERSION_LINE=$(grep -oE '##[[:space:]]+\[[0-9]+\.[0-9]+[^]]*\][^$]*' "$REPO_ROOT/CHANGELOG.md" | head -1 || true)
    if [[ -n "$LAST_VERSION_LINE" ]]; then
        if echo "$LAST_VERSION_LINE" | grep -qE '[0-9]{4}-[0-9]{2}-[0-9]{2}'; then
            DATE_FOUND=$(echo "$LAST_VERSION_LINE" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
            pass "Last version entry has a date ($DATE_FOUND)"
        else
            warn "Last version entry in CHANGELOG.md has no date — add YYYY-MM-DD for traceability"
        fi
    else
        warn "Could not parse a version line from CHANGELOG.md"
    fi
else
    warn "Skipping CHANGELOG hygiene checks — CHANGELOG.md not found"
fi

# ===========================================================================
# 3. Git Health
# ===========================================================================
section "🔀 Git Health"

# Current branch is main
CURRENT_BRANCH=$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
if [[ "$CURRENT_BRANCH" == "main" ]]; then
    pass "On main branch"
else
    warn "Not on main branch (currently on '$CURRENT_BRANCH') — releases should be cut from main"
fi

# No uncommitted changes
UNCOMMITTED=$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
if [[ "$UNCOMMITTED" -eq 0 ]]; then
    pass "No uncommitted changes"
else
    warn "${UNCOMMITTED} uncommitted change(s) — consider committing or stashing before push"
fi

# Local is not ahead of origin (no unpushed commits)
UNPUSHED=$(git -C "$REPO_ROOT" rev-list "origin/${CURRENT_BRANCH}..HEAD" 2>/dev/null | wc -l | tr -d ' ' || echo "0")
if [[ "$UNPUSHED" -eq 0 ]]; then
    pass "Local branch is in sync with origin (no unpushed commits)"
else
    warn "${UNPUSHED} unpushed commit(s) ahead of origin/${CURRENT_BRANCH}"
fi

# ===========================================================================
# 4. Security
# ===========================================================================
section "🔒 Security"

# .content-wand/ is in .gitignore
if [[ -f "$REPO_ROOT/.gitignore" ]] && grep -q "\.content-wand/" "$REPO_ROOT/.gitignore"; then
    pass ".content-wand/ is in .gitignore (local cache protected)"
else
    fail ".content-wand/ is NOT in .gitignore — local cache could be committed accidentally"
fi

# No *.env files in the repo (tracked by git)
ENV_FILES=$(git -C "$REPO_ROOT" ls-files '*.env' 2>/dev/null | wc -l | tr -d ' ')
if [[ "$ENV_FILES" -eq 0 ]]; then
    pass "No .env files tracked by git"
else
    fail "${ENV_FILES} .env file(s) are tracked by git — remove them and add to .gitignore"
fi

# ===========================================================================
# Summary
# ===========================================================================
echo ""
echo "══════════════════════════════════════════════════════════"
printf "  Summary: %d passed, %d warnings, %d failures\n" "$PASS" "$WARN" "$FAIL"
echo "  This script is informational — no action was taken."
echo "══════════════════════════════════════════════════════════"
echo ""

# Always exit 0 — this script is informational only.
exit 0
