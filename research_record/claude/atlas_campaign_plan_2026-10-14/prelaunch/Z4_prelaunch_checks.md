# Z4 pre-launch checks (2026-10-15, no launch)

Package root: IWO_PHYSICS_CONSTRAINED_MODEL_V1 (cwd). Interpreter: IWO_ATLAS_Model_claude\.venv\Scripts\python.exe.
Env: IWO_MODEL_FILE=config/iwo_material_model_v3.yaml; IWO_ATLAS_VIEWERS, IWO_ATLAS_JOB unset. Nothing appended to config/sealed_runs.json.
Shell: PowerShell. All values below COMPUTED (tool output of this session).

| # | Command | Exit | Key output line | Verdict |
|---|---|---|---|---|
| 1 | `python -I -B analysis_2026-10-10_campaign/regress_sealed_aware.py` | 0 | `identical 60; unexpected differences 0` | PASS |
| 2 | `python -B analysis_2026-10-10_campaign/make_campaign_configs.py --check` | 0 | `plans verified: 185 matrix entries in 7 stage plans (4 runnable, 54 entries) + 5 templates; verbatim and in matrix order: YES; ...` | PASS |
| 3a | `Get-FileHash analysis_2026-10-10_campaign/score_register.py -Algorithm SHA256` | 0 | `c0f28bb942508a81a0f59b4a4c1e720bbfdbe8d9466d7e002476d64dcc10b55a` (starts c0f28bb9) | PASS |
| 3b | `python -B analysis_2026-10-10_campaign/score_register.py selftest` | 0 | `90/90 ok` | PASS |
| 4 | `git rev-parse --verify '1375164^{commit}'`; `git diff --stat 1375164 -- scripts` | 0 / 0 | commit 1375164b3ab861450f7d910f4e421975a0c63397; diff --stat empty; `git status --short scripts` empty | PASS |
| 5 | `python -I -B analysis_2026-10-10_campaign/prelaunch_gate_a41.py` | 4 | `NOTHING TO LAUNCH: both A41 runs have started (rerun run_0076, S0-02-DOS2 run_0077). Do not invoke the plan again.` | Expected: exit 4 = DIAGb plan exhausted (gate docstring l.6-7). Gate scope is config/campaign_C10_DIAGb.json only; no other A41 gate script exists in analysis_2026-10-10_campaign/. |
| 6 | `tasklist /FO CSV /NH \| Select-String 'deckbuild\|dbascii\|atlas\|tonyplot\|athena\|devedit'`; `Get-CimInstance Win32_Process -Filter "Name like 'python%'" \| ? CommandLine -match 'run_atlas\|run_campaign'` | 0 | no matches in either list | PASS |

Notes
- Run 1-5 first attempt with `-I` for items 2 and 3b failed (exit 1, `ModuleNotFoundError: campaign_tools` / `campaign_extract`): `-I` drops the script directory from sys.path. Rerun without `-I` (the documented usage, score_register.py l.135) passed. The plan's Z4 does not prescribe `-I` for these two.
- Item 1 also printed the per-sealed-run equality lines (all True); sealed directories not opened (wrapper's own handling).
- `git status` shows results/RUN_INDEX.csv modified vs HEAD and pre-existing changes under inputs/astra_*; none made by this session.
- A41 gate prints `RUN_INDEX: 77 distinct run ids (max run_0077), c10 17`.
- Z4 rule for launch time: append each state-only DIAG run to config/sealed_runs.json once its STARTED row exists (plan §2.0 Z4, l.184). Not done now.
