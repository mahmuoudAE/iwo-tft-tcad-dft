#!/bin/bash
# usage (WSL "Ubuntu"): bash tools/push_public.sh "commit subject" ["body"]
#
# PUBLIC repo (IWO_PHYSICS_CONSTRAINED_MODEL_V1 -> github.com/mahmuoudAE/iwo-tft-tcad-dft). Standing permission: decision D-04.
# Commits anything new, then ABORTS the push if a secret-like string or a file > 50 MB is in the unpushed range.
# Never add restricted or unpublished data to this repo (charter section 8).
cd "/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)/IWO_PHYSICS_CONSTRAINED_MODEL_V1" || exit 1

AN=$(git log -1 --format='%an'); AE=$(git log -1 --format='%ae')
git add -A
if ! git diff --cached --quiet; then
  git -c user.name="$AN" -c user.email="$AE" commit -q -m "$1

${2:+$2

}Co-Authored-By: Claude <noreply@anthropic.com>"
fi

echo "unpushed commits:"; git log --oneline origin/main..HEAD

# grep -a: without it, a binary-looking patch (e.g. a PDF that git shows as text) makes grep print only
# "binary file matches" and the scan silently passes. Only a count is printed, never the matched text.
# (bracketed letters stop the pattern from matching its own source text)
PAT='password\s*[:=]|ghp[_][A-Za-z0-9]{20}|github[_]pat[_]|PRIVATE[ ]KEY|key[t]ab|verification[ ]code|token\s*[:=]\s*\S{12}'
HITS=$(git diff origin/main..HEAD | LC_ALL=C grep -a -E '^\+' | LC_ALL=C grep -a -c -i -E "$PAT")
if [ "${HITS:-0}" != "0" ]; then echo "SECRET SCAN: $HITS suspicious added line(s) - not pushing (text not shown). Files at HEAD:"; LC_ALL=C git grep -l -a -i -E "$PAT" HEAD -- | head -5; exit 3; fi

BIG=$(git diff --name-only --diff-filter=AM origin/main..HEAD | while read -r f; do [ -f "$f" ] && s=$(stat -c %s "$f") && [ "$s" -gt 52428800 ] && echo "$s $f"; done)
if [ -n "$BIG" ]; then echo "FILE > 50 MB - not pushing:"; echo "$BIG"; exit 4; fi

echo "secret scan clean; no file > 50 MB; files changed: $(git diff --name-only origin/main..HEAD | wc -l)"
GIT_TERMINAL_PROMPT=0 git push origin main 2>&1 | grep -v -i CRLF | tail -2
echo "push rc=${PIPESTATUS[0]}"
git status -sb | head -1
