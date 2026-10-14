#!/bin/bash
# Run this YOURSELF in a WSL terminal (Claude never handles keys):
#   wsl -d Ubuntu -- bash "/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)/iwo-tft-research-private/tools/set_gemini_key.sh"
# Stores your Gemini API key for tools/gemini_advise.py in ~/.config/iwo/gemini_key (mode 600, outside the repo).
# The key is read with hidden input and never printed. It also records whether billing is enabled on the key's
# Cloud project: without that confirmation gemini_advise.py runs only the connection test and sends no research data
# (free-tier prompts may be used by Google to improve its products; paid-tier prompts are not).
set -e
umask 077
mkdir -p "$HOME/.config/iwo"
read -r -s -p "Paste your Gemini API key (input is hidden), then press Enter: " K; echo
if [ "${#K}" -lt 30 ]; then echo "That is too short to be an API key. Nothing was saved."; exit 1; fi
case "$K" in AIza*) ;; *) echo "Note: Google API keys usually start with 'AIza'. Saving anyway.";; esac
printf '%s' "$K" > "$HOME/.config/iwo/gemini_key"; chmod 600 "$HOME/.config/iwo/gemini_key"; unset K
read -r -p "Is billing enabled on this key's Cloud project (paid tier)? Type yes or no: " B
if [ "$B" = "yes" ]; then
  date -u +%FT%TZ > "$HOME/.config/iwo/gemini_billing_confirmed"
  echo "Saved. Billing confirmation recorded. You can tell Claude the key is set."
else
  rm -f "$HOME/.config/iwo/gemini_billing_confirmed"
  echo "Saved WITHOUT billing confirmation: only the connection test will run, no research data will be sent."
fi
