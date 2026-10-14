# IWO Mission Control (local, read-only dashboard)

One page that shows the whole project state:

- **ATLAS TCAD (campaign C10):**
  - the launch ledger and launch budget (total cap, C10 cap of 200, reserve);
  - progress per stage, plan entries and the S1 rule verdicts;
  - post-run checks and the NC-audit status;
  - the active run, with live point progress, Vg, a partial I-V curve, timeout ETA and Windows process detection;
  - the next plan and its stop rules.
- **CERN (lxplus HTCondor):**
  - jobs by kind and status, with GPUs and GPU memory;
  - one pipeline row per structure: ML → QC → collect → RELAX segments → FINAL, with retries and FAILED/DAG FAILED flags;
  - force-check (val) jobs, recent history, AFS quota and a sparkline history.
- **ML melt-quench:** the 22 specs, QC passes and failures, rejections and their replacement seeds.
- **Codex monitor:** the work-chat timeline (verdicts, and whether each Claude decision is pending or decided), the autodigest loops and their next wake, the writer lock and any send in flight.
- **Hypothesis register:** whether it is frozen, the freeze prerequisites, the hypotheses with priority and status, and pending amendments.
- **Ledgers:** decisions, open tasks, claim counts and whether the current-state page is stale.
- **Git:** for both repos, the last commit, the dirty count and the unpushed count.
- **Deadlines:** the CERN deadlines.
- **Alerts:** a list derived from all of the above, ranked crit, warn, info.

## Start

- **Windows:** double-click `start_dashboard.cmd`. It starts the server in WSL Ubuntu in a minimised window, then opens <http://localhost:8765>. Close that window to stop the server.
- **WSL:** run `python3 server.py`. Options:
  - `--port N`, or the `IWO_DASH_PORT` environment variable. The default is 8765. The server refuses to start if the port is taken.
- **One-shot:** run `python3 server.py --once --out sample_status.json`. Add `--no-cern` to skip CERN. This runs every collector once, writes the JSON and exits. It does not append to `history.jsonl`.
- **Claude preview:** the `iwo-dashboard` entry in `IWO_ATLAS_Model_claude/.claude/launch.json`.

The server must run inside WSL, because it uses the WSL SSH master `~/.ssh/cm-cern`, and WSL `/proc` for the Codex loops.

## API (GET only)

| Route | Returns |
|---|---|
| `/` | `index.html`. Other files served: `app.js`, `app.css`, `style.css`, `favicon.*`, and flat files in `static/` (html/js/css/svg/png/ico/woff2/json). |
| `/api/status` | Aggregated JSON: `schema, version, generated_utc, server, atlas, cern, ml, codex, register, ledger, git, meta, alerts, alert_counts, history`. Each collector is `{ok, updated_utc, updated_epoch, error, duration_s, age_s, data}`. `history` holds the CERN points of the last 24 h (a time window, at most 600 points). `cern.data.snapshot_age_s` is the age of the shown CERN data at the time of the request. |
| `/api/refresh` | Re-runs the local collectors and returns the status. It is skipped if a local collection is running or finished less than 5 s ago; this is checked under the collection lock, so concurrent refreshes give one collection. Needs the header `X-IWO-Refresh: 1` (the page sends it; with curl add `-H "X-IWO-Refresh: 1"`). Cross-site requests (an `Origin` other than this server, or `Sec-Fetch-Site` other than `same-origin`/`none`) get 403. |
| `/api/refresh?cern=1` | Also refreshes CERN. Refused with 429 if a CERN query is running or the last one started less than 120 s ago. |
| `/api/history?hours=H&max=N` | The in-memory CERN history for the longer sparkline ranges: `{hours, max, n_total, n, generated_epoch, points[]}`. `hours` is clamped to 0.25–744 (default 24) and `max` to 10–1000 points (default 600, evenly thinned, newest kept). It reads memory only, never the disk or CERN. |

Every other route returns 404.

## Frontend (`index.html`)

One self-contained page: inline CSS and vanilla JS, no external scripts, fonts or CDNs, so it works offline. Every value is inserted with `textContent`; nothing uses `innerHTML`.

- **Top bar:** UTC and server-local clocks, countdowns to the next deadline, the CERN target (15 Oct) and CERN end (21 Oct), health pills (SSH master, HTCondor run/idle/held, ATLAS, Codex loop, C10 budget, register), data freshness, the Refresh button (`/api/refresh?cern=1`; a 429 is shown as a polite "ask again in N s"), and a theme toggle (auto, dark, light).
- **Alerts strip:** always visible, crit first. Collapsed, it shows every crit alert plus enough warnings to make two lines. Expanded, it shows everything, with an info filter. New warn/crit alerts are announced through `aria-live`, and the source tag opens the matching tab.
- **Tabs:**
  - **Overview:** KPI tiles, a per-structure swimlane (ML → QC → collect → relax segments → final SCF), the CERN window timeline, next actions ("waiting on you" and pipeline attention), the ATLAS stage bar and budget gauge, and the latest Codex exchange.
  - **CERN DFT:** connection and snapshot details, a history chart (queue, relaxations, GPUs, GPU memory, AFS quota over 6 h, 24 h, 3 d or all), a sortable and filterable structures table, jobs by kind, validation jobs, recent completions, failed directories and the full condor_q table.
  - **ML structures:** the summary with breakdowns, the spec list with QC and the rejections with their replacement seeds.
  - **ATLAS C10:** the active-run banner (progress, elapsed, timeout, rate ETA, live partial I-V) or the idle state, the S0–S7 stepper, the budget, the measured vs ATLAS transfer curve, runs, plan entries (sim vs exp), rule verdicts, post-run checks, the next plan with pre-registered expectations, the NC audit, Windows processes, and plans and stop rules.
  - **Codex & register:** the monitor (loops, next digest, writer lock, sends in flight, session, log), the exchange timeline (pending decisions highlighted, "awaits your go" flagged), the hypothesis board, the freeze checklist and the amendments.
  - **Ledger & git:** decisions, people-dependent items, the task queue, claims, both repos, collector health and server info.
- **Polling:** `/api/status` every 30 s, paused while the tab is hidden. While the server is unreachable or a collector has not run yet, the page retries after 3 s, doubling up to 30 s. A response older than the data on screen is ignored. When the server is unreachable, the page keeps the last data and shows an offline banner, an `[offline]` title and a red favicon.
- **Stale CERN data:** when the SSH master is down, a refresh failed, or the snapshot is older than three CERN intervals, the HTCondor pill and the CERN tiles are marked "cached" and a banner says so.
- **Re-rendering:** a panel is rebuilt only when the data it shows changed. A rebuild waits while text is selected in the panel, the pointer is on a chart, or a list box is open (at most 2 min).
- **Persistence:** the tab (also in the URL hash), filters, sort orders, open details and the theme are kept in `localStorage` (guarded with try/catch). Scroll position, focus (every generated control has a stable id) and the chart read-out position survive each refresh.
- **Screen readers:** new warn/crit alerts and banner state changes (server unreachable, SSH master down, CERN data stale, local collectors behind) are announced once through one `aria-live` region; ticking times are never inside a live region.
- **Layout:** works down to 375 px. Wide tables scroll inside their card, and the page itself never scrolls sideways.

**Refresh cadence:**
- Local collectors: every 30 s.
- Git: every 300 s.
- CERN: 300 s after the last CERN query (a manual refresh restarts that clock). No two CERN queries are ever less than 120 s apart: the check and the query run under one lock, for the scheduled loop and the Refresh button alike. Each CERN snapshot takes about 5 s end to end.

After each good CERN snapshot taken by the running server, its counts are appended to `history.jsonl` (capped at 5000 lines) for sparklines. `--once` runs do not append.

## Safety properties

- **Read-only.** There are no write endpoints and no actions. The server only reads project files, `/proc` and the Windows process list. It writes only `history.jsonl` in this folder.
- **Does not touch:**
  - It never launches ATLAS or DeckBuild.
  - It never commits or pushes.
  - It never stops or signals any process.
- **Bound to 127.0.0.1 only.** Requests whose `Host` header is not localhost, 127.0.0.1 or [::1] are refused, as protection against DNS rebinding. Files are served from a fixed whitelist, so path traversal returns 404.
- **No cross-site triggering.** `/api/refresh` (the only route that causes work, including CERN queries) needs `X-IWO-Refresh: 1` and refuses foreign `Origin` / `Sec-Fetch-Site` values, so another web page open in the browser cannot make the server query CERN.
- **CERN access goes only through the existing SSH ControlMaster:**
  - First, `ssh -O check -o BatchMode=yes -o ControlPath=~/.ssh/cm-cern`. If that fails, nothing else is attempted, and the dashboard shows "SSH master gone, log in again" with the last good snapshot and its age.
  - The snapshot call uses `BatchMode=yes`, `ControlMaster=no`, `ProxyCommand=/bin/false`, `ConnectTimeout=10`, stdin `/dev/null`, and `GSSAPIAuthentication`, `PubkeyAuthentication`, `PasswordAuthentication` and `KbdInteractiveAuthentication` set to `no`. It runs under a 45 s timeout.
  - ssh tries the master's socket first. If the master disappeared or went stale after the check, ssh would normally fall back to a new direct connection; `ProxyCommand=/bin/false` makes that fallback fail at once, so no new TCP connection to lxplus is opened and no authentication is attempted. The dashboard never logs in and never handles passwords or 2FA. (Verified locally: with a missing socket ssh runs the proxy command and never connects; without it, it dials the host.)
  - `cern_snapshot.sh` (a manual helper; the dashboard does not call it) uses the same options, with a 15 s timeout and stdin `/dev/null` on its `-O check`.
  - The remote script, `cern_snapshot.py`, is sent as a base64 argument. It only runs `condor_q`, `condor_history` and `fs lq`, and reads files under `~/iwo_amorph`. It writes nothing on CERN.
- **Git:**
  - Calls use `--no-optional-locks` (no index refresh) and never fetch.
  - On `/mnt/c`, Windows `git.exe` is called through `/init` with `-c core.longpaths=true` for that call only. This takes 0.2 s instead of the 55 s WSL git needs to re-hash the public repo.
- **Secrets:**
  - It never reads `~/.ssh` keys, tokens, `.git-credentials`, `~/.codex/auth.json` or process environments.
  - For the Codex session it reads the session ID from `codex/work_chat/session_id.txt`, walks the file names under `~/.codex/sessions` to find the matching file, and stats that file (modification time and size). It never opens the session file, and the ID itself is not put in the API output (only `session_id_present`).
