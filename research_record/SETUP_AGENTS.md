# Setting up Claude Code and Codex to work together on the IWO project

The first time takes about one hour. Steps 1–3 and 6 are yours; everything else is already in this repository.

## How it works

```
                 YOU  (decide, approve, push)
                  │   one command per step:  tools\relay.ps1 -Task RQ-xxx ...
                  ▼
  Claude Code ──writes──►  iwo-tft-research-private  ◄──writes── Codex
  (owner of evidence,       one folder, Git = record           (independent reviewer,
   ATLAS/DFT preparation)                                       hypotheses, designs)
```

- Both agents work in the **same folder**. There are no two copies to keep in sync.
- They never run at the same time. The relay runs them one after the other.
- Each agent writes only in its own area:
  - Codex: `codex/` and `handoffs/CODEX_TO_CLAUDE.md`;
  - Claude: `claude/`, its handoff file, the ledger and the queue.

  The relay reverts anything else an agent touches.
- The relay commits; nobody pushes. ATLAS launches and CERN actions always need your approval.
- Astra (in ChatGPT) stays manual: you attach files and paste its answer back.

---

## Step 1. Install Git for Windows (5 min)

Until now git ran only inside WSL. The two command-line tools expect git on Windows.

```bash
winget install --id Git.Git -e
```

Close the terminal, open a new one, and check:

```bash
git --version
```

The repository's `.gitattributes` keeps LF line endings, so the WSL scripts keep working.

## Step 2. Install the two command-line tools (5 min)

Node.js is already installed (`C:\nodejs`). Use `npm.cmd` rather than `npm`. This avoids PowerShell's script-execution policy without changing any system setting.

```bash
npm.cmd install -g @anthropic-ai/claude-code
```

```bash
npm.cmd install -g @openai/codex
```

Check both:

```bash
claude --version
```

```bash
codex --version
```

If a command is "not recognized", the npm global folder is missing from PATH. Run `npm.cmd prefix -g` to see that folder, add it to your user PATH, then reopen the terminal.

## Step 3. Sign in to each tool (you do this; never paste passwords or keys into a chat)

- **Claude:** run `claude` in a terminal, type `/login`, finish the sign-in in the browser, then type `/exit`. It uses your Claude subscription.
- **Codex:** run `codex login` and finish the sign-in in the browser with your ChatGPT account. Then run `codex` once inside this folder, answer **yes** when it asks whether to trust the folder, and exit.

## Step 4. Check the tools and the flags the relay uses (5 min)

```bash
cd "C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\iwo-tft-research-private"
```

```bash
git status
```

You should see `On branch main` and `nothing to commit, working tree clean`.

```bash
claude --help
```

Look for `--permission-mode`, `--allowedTools`, `--add-dir`, `--max-turns` and `--output-format`.

```bash
codex exec --help
```

Look for `--sandbox`, `--cd`, `--output-last-message` and `--profile`, and check that a prompt of `-` is read from stdin.

If any of these flags is missing in your version, tell Claude: the relay needs a one-line change.

## Step 5. The Claude Code project configuration (already in the repo)

| File | What it does |
|---|---|
| `CLAUDE.md` | Rules, paths and your preferences. Loaded automatically in every Claude session in this folder. |
| `.claude/agents/evidence-auditor.md` | Re-derives every quoted number from the raw files |
| `.claude/agents/atlas-runner.md` | ATLAS decks and runs: budget check, stepped sweeps, solver pitfalls, never launches without your go |
| `.claude/agents/dft-cern.md` | Quantum ESPRESSO and CERN, with your account rules |
| `.claude/agents/figure-maker.md` | Figures in your Origin-like style, with honest captions |
| `.claude/agents/ledger-keeper.md` | Keeps the ledger, current state and task queue consistent |
| `.claude/commands/status.md` | `/status`: the project state in 15 lines |
| `.claude/commands/handoff.md` | `/handoff RQ-xxx`: writes the handoff, audits its numbers, updates the record, commits locally |
| `.claude/commands/register.md` | `/register REG-001 title`: drafts a prediction registration |
| `.claude/commands/review.md` | `/review RQ-xxx`: Claude reviews a Codex task (assessment first, then verdicts) |
| `.claude/hooks/guard.py` and `.claude/settings.json` | Safety hook: blocks a raw `git push` and any change to `data_private/raw/`; asks you before ATLAS launches and CERN actions |

**Test (2 min).** Open a new Claude Code session in this folder (Step 8) and ask:
1. "run git push". It must be refused with a message about the push scripts.
2. "/status". It must print a short summary and change nothing.

The hook was tested on 16 cases (blocked, asked and allowed commands, including commit messages that contain the word "push").

## Step 6. The Codex configuration (5 min)

Copy the settings file. If `%USERPROFILE%\.codex\config.toml` already exists, merge the lines by hand instead.

```bash
Copy-Item "config\codex\config.toml.example" "$env:USERPROFILE\.codex\config.toml"
```

It defines:
- the default: write only inside the folder, ask before anything else, no network, high reasoning;
- `review`: no questions asked, writes only inside the folder;
- `readonly`: never writes.

**Optional:** copy the prompts into Codex's prompt folder so they appear in Codex's slash-command menu.

```bash
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\prompts"
```

```bash
Copy-Item prompts\0*.md "$env:USERPROFILE\.codex\prompts\"
```

**Test (2 min).** This only reads:

```bash
codex exec --sandbox read-only --cd . "Read AGENTS.md and list, in order, the files it tells you to read. Change nothing."
```

**If Codex fails on Windows** (sandbox errors), run it inside WSL instead:
1. In WSL Ubuntu, install Node and Codex.
2. Run `codex login` there.
3. Add `-CodexInWsl` to every relay command.

## Step 7. Dry-run the relay (2 min)

The relay is `tools\relay.ps1`. `-ExecutionPolicy Bypass` applies to this one process only; it changes no system setting.

```bash
pwsh -ExecutionPolicy Bypass -File tools\relay.ps1 -Task RQ-001 -Owner claude -Step full -DryRun
```

It prints the exact commands and prompts for all four agent runs, and runs nothing.

### What each step does

| Step | Agent | Commits |
|---|---|---|
| `-Step own` | The owner does the task and writes a handoff (Part A evidence, Part B interpretation). | 1 |
| `-Step review` | The other agent writes (a) an independent assessment from Part A only, committed first, then (b) its verdicts after reading Part B. | 2 |
| `-Step respond` | The owner answers every objection: accepted, partially accepted, evidence disagrees, or unresolved. | 1 |
| `-Step full` | own, then review, then respond; then it stops. | 4 |

### Checks after every agent run
- If the agent made commits itself, they are undone.
- Files outside the agent's area are reverted.
- If the public repository changed, the relay stops.
- If the agent failed, the relay stops and leaves its work uncommitted for you to inspect.

### Guarantees
- The relay never pushes and never loops.
- It refuses to start if the folder has uncommitted changes.

Prompts, final answers and a run summary are kept in `relay_logs/<run>/`. Full transcripts (`*.stream.log`) are kept on disk but not committed.

## Step 8. The first real cycle: RQ-001, mobility and SS definitions (about 30–60 min of agent time)

1. Run the owner step:

   ```bash
   pwsh -ExecutionPolicy Bypass -File tools\relay.ps1 -Task RQ-001 -Owner claude -Step own
   ```

2. Read the new handoff at the top of `handoffs/CLAUDE_TO_CODEX.md` and the files in `claude/evidence/RQ-001/`. If it is poor, stop here and tell Claude what is wrong in a normal chat.
3. Run the review:

   ```bash
   pwsh -ExecutionPolicy Bypass -File tools\relay.ps1 -Task RQ-001 -Owner claude -Step review
   ```

4. Read `codex/independent_reviews/RQ-001_independent_assessment.md` and `RQ-001_review.md`.
5. Run the response:

   ```bash
   pwsh -ExecutionPolicy Bypass -File tools\relay.ps1 -Task RQ-001 -Owner claude -Step respond
   ```

6. Decide:
   - **They agree:** record the decision in `05_DECISION_LOG.md`.
   - **They still disagree:** give Astra `prompts/05_ASTRA_ARBITRATION.md` with the files it lists.
7. Push when you choose, by telling Claude "push the private repo".

Once you trust the loop, `-Step full` does steps 1, 3 and 5 in one go. Even then, read the handoff before you act on the review.

**Tasks owned by Codex** (RQ-005, RQ-007): use `-Owner codex`. Codex works first, Claude reviews, Codex responds.

## Step 9. Working interactively (when you want to talk)

**Claude.** In the desktop app, open a new Code session:
1. Set the working folder to `iwo-tft-research-private`.
2. Add `IWO_PHYSICS_CONSTRAINED_MODEL_V1` as a folder.
3. Paste `prompts/01_NEW_CLAUDE_CHAT.md` the first time.
4. Start later sessions with `/status`, and finish a task with `/handoff RQ-xxx`.

**Codex.** Open the same folder (with `codex`, or its desktop or IDE app). Run one session per task and paste the matching prompt.

**Rules:**
- **One chat per task, not per role.** The roles live in the configuration and the memory lives in the repository. Close a chat when its handoff is committed.
- **Never let Claude and Codex work in the same folder at the same moment.** They would overwrite each other's files. The relay guarantees this; in interactive use it is up to you.

## Step 10. Optional: a direct line from Claude to Codex (quick second opinions only)

Codex can run as a tool-server inside Claude Code. Check the exact subcommand name in `codex --help` first (it is `mcp-server` in current versions):

```bash
claude mcp add codex -- codex mcp-server
```

Then, in a Claude chat: "ask Codex whether ...".

Use this for quick checks only, never for the central reviews. Through this line Claude chooses what Codex sees, so the review is not independent.

## Step 11. Astra (manual)

- **Hypotheses:** paste `prompts/03_ASTRA_HYPOTHESES.md` with its three attachments. Save the answer as `codex/hypothesis_tests/RQ-006_astra_hypotheses.md`.
- **Arbitration:** paste `prompts/05_ASTRA_ARBITRATION.md`. Save the answer as `decisions/30_DAY_RESEARCH_DECISION.md`.
- Ask Claude to commit the saved answers.

---

## What protects you

| Risk | Protection |
|---|---|
| Something is pushed by accident | The hook blocks a raw `git push`. The relay never pushes. The push scripts refuse a public target and scan for secrets. |
| ATLAS licence or budget used without your consent | The hook asks you. In relay (headless) mode nobody can answer, so it is refused. |
| A CERN job is submitted without your consent | Same as ATLAS. Passwords and 2FA codes are never handled by an agent. |
| Codex edits Claude's files, or the other way round | The relay reverts them and lists them in the commit message and the run summary. |
| An agent edits the charter or the decision log | Reverted: only you edit those. |
| The public repository is changed during a relay run | The relay stops and tells you. |
| Raw data are edited | The hook blocks it. |
| Holdout data leak into calibration | The fab keeps holdouts until a registration is timestamped (charter §7). |
| A runaway loop | One step per command; `full` is at most four agent runs, then it stops. |

## Cost and efficiency

- **Agent runs per step:**

  | Step | Agent runs |
  |---|---|
  | own | 1 |
  | review | 2 |
  | respond | 1 |

  A full cycle is 4 runs; on a typical task, plan for about an hour of agent time.
- **Reasoning level:** keep Codex at high. Use your highest level (xHigh) only for Astra's arbitration.
- **Keep handoffs short.** Part A is a table of numbers with file paths. The reviewer reads the files, not prose.
- **Do not run a second cycle** on the same task before you have read the first.

## Troubleshooting

| Problem | Fix |
|---|---|
| `claude` or `codex` is "not recognized" | Reopen the terminal. Run `npm.cmd prefix -g` and add that folder to your user PATH. |
| "running scripts is disabled" | Use `npm.cmd`, and start the relay with `pwsh -ExecutionPolicy Bypass -File ...` |
| Relay: "working tree not clean" | Check `git status`. Commit or discard your own edits first. |
| Relay: "no handoff for RQ-xxx" | Run `-Step own` first. |
| Codex sandbox errors on Windows | Use Codex in WSL Ubuntu and add `-CodexInWsl`. |
| An agent "changed nothing" | Read `relay_logs/<run>/<step>.final.md`; the task entry may be unclear. Clarify it in `04_TASK_QUEUE.yaml`. |
| The hook does not fire | Check that `python --version` works in a terminal, and that `.claude/settings.json` exists in this folder. |
| A flag is "unknown" | Your tool version differs. Tell Claude the exact message and it will adjust `tools/relay.ps1`. |
