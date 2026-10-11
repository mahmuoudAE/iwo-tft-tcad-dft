You are an independent reviewer of a Silvaco ATLAS campaign design. Read-only sandbox: do not modify any file, do not run deckbuild.exe, scripts/run_atlas.py or scripts/run_campaign.py, do not use the network. Reading files and doing arithmetic in python3 is fine.

Files (relative to the working directory IWO_PHYSICS_CONSTRAINED_MODEL_V1):
- analysis_2026-10-10_campaign/CAMPAIGN_DESIGN.md  (the design to review)
- analysis_2026-10-10_campaign/campaign_matrix.json and make_campaign_matrix.py (the run list and its generator)
- inputs it merges: analysis_2026-10-10_campaign/DFT_TO_TCAD.md, dft_inputs.json, GENERATOR_AUDIT.md, codex_design.md (your own earlier design)
- scripts/build_iwo_decks.py (deck generator), config/iwo_material_model_v2.yaml, config/solver.yaml
- analysis_2026-10-06_extraction/extraction.py and run_extraction.py (registered extraction)

Answer, concisely (at most ~1200 words), with a verdict per item: OK / FIX (say exactly what) / RISK (say what to watch):
1. Are the two "exact profiling" claims correct for THIS deck: (a) a change of the front INTERFACE QF (y = 0, x = 0..24 um, gate under the whole x range) is an exact rigid shift of I_D(V_G) at V_D = 0.7 V with Pd S/D volumes on top and air above the channel; (b) I_D is exactly proportional to MUN for constant mobility and for IGZO.TOKYO in electron-only drift-diffusion with continuous DEFECTS? Point out any term that breaks exactness (e.g. fringe fields under the contacts, mobility-dependent trap occupancy, tunnelling).
2. Model ON/OFF choices and the disagreement table (section 2): any choice you think is wrong, and why.
3. Labels: any parameter mislabelled (COMPUTED / MEASURED / LITERATURE / FITTED / ASSUMED), any fitted quantity presented as validation.
4. Arithmetic: check the start values (mu_inf 100.0, ell 7.25 nm, MUN 12.98/40.26/60.54), quasi-2D NC300 1.373e19 at 2 nm, FN constants (F.AE 3.50e-6 / 1.03e-5 A/V^2, F.BE 9.97e7 / 3.97e7 V/cm), stage counts summing to 177 + 23 reserve = 200.
5. Gate-leakage test (section 7): is the verdict rule quantitative and fair? Is the worst-case oxide set sensible? Will QTNLSC.EL/FNORD actually inject from the Conductor-region gate in this deck?
6. The 10-run minimum set: would you change any entry?
7. Anything that would waste launches or make a stage uninterpretable.
Do not restate the design. Only give findings.
