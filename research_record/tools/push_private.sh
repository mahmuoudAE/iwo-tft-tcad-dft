#!/bin/bash
# usage (WSL "Ubuntu"): bash tools/push_private.sh "commit subject" ["body"]
#
# Commits anything new in the PRIVATE research repo, then pushes, but ABORTS in any of these cases:
#   - no remote is set;
#   - the remote GitHub repo is publicly visible;
#   - a secret-like string is found in the unpushed range;
#   - a file larger than 50 MB is in the unpushed range.
# Never prints credentials.
cd "/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)/iwo-tft-research-private" || exit 1

URL=$(git remote get-url origin 2>/dev/null)
if [ -z "$URL" ]; then echo "no remote 'origin' - create the private repo on GitHub first (HUM-002)"; exit 2; fi
SLUG=$(echo "$URL" | sed -E 's#(https://github.com/|git@github.com:)##; s#\.git$##')
CODE=$(curl -s -o /dev/null -w '%{http_code}' "https://api.github.com/repos/$SLUG")
if [ "$CODE" = "200" ]; then echo "ABORT: github.com/$SLUG is PUBLIC (unauthenticated API returns 200). Make it private first."; exit 5; fi
if [ "$CODE" != "404" ]; then echo "ABORT: cannot confirm that github.com/$SLUG is private (HTTP $CODE). Try again later."; exit 6; fi
echo "visibility check passed: unauthenticated API returns 404 for $SLUG (private)"

AN=$(git log -1 --format='%an' 2>/dev/null); AE=$(git log -1 --format='%ae' 2>/dev/null)
git add -A
if ! git diff --cached --quiet; then
  git -c user.name="$AN" -c user.email="$AE" commit -q -m "$1

${2:+$2

}Co-Authored-By: Claude <noreply@anthropic.com>"
fi

if git rev-parse --verify -q origin/main >/dev/null; then RANGE="origin/main..HEAD"; else RANGE="HEAD"; fi
echo "unpushed commits:"; git log --oneline $RANGE

# Secret scan (--root covers the first push). grep -a: without it, a binary-looking patch (e.g. a PDF that git
# shows as text) makes grep print only "binary file matches" and the scan silently passes. Only a count is
# printed, never the matched text.
# (bracketed letters stop the pattern from matching its own source text)
# key pattern = the PEM/OpenSSH header every real key carries; plain prose about "the private key" does not match
PAT='password\s*[:=]|ghp[_][A-Za-z0-9]{20}|github[_]pat[_]|BEGIN [A-Z ]*PRIVATE[ ]KEY|key[t]ab|verification[ ]code|token\s*[:=]\s*\S{12}'
HITS=$(git log -p --root $RANGE | LC_ALL=C grep -a -E '^\+' | LC_ALL=C grep -a -c -i -E "$PAT")
if [ "${HITS:-0}" != "0" ]; then echo "SECRET SCAN: $HITS suspicious added line(s) - not pushing (text not shown). Files at HEAD:"; LC_ALL=C git grep -l -a -i -E "$PAT" HEAD -- | head -5; exit 3; fi

BIG=$(git ls-files | while read -r f; do [ -f "$f" ] && s=$(stat -c %s "$f") && [ "$s" -gt 52428800 ] && echo "$s $f"; done)
if [ -n "$BIG" ]; then echo "FILE > 50 MB - not pushing:"; echo "$BIG"; exit 4; fi

echo "checks clean"
GIT_TERMINAL_PROMPT=0 git push -u origin main 2>&1 | grep -v -i CRLF | tail -3
echo "push rc=${PIPESTATUS[0]}"
git status -sb | head -1
