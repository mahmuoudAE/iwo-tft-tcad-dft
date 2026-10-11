You are an independent reviewer of a code change to a Silvaco ATLAS 5.28 deck generator. Read-only sandbox: do not modify any
file, do not run deckbuild.exe, scripts/run_atlas.py or scripts/run_campaign.py, do not use the network. Reading files and
running python3 for arithmetic or for importing scripts/build_iwo_decks.py to build deck TEXT (it contains no subprocess call)
is fine.

Working directory: IWO_PHYSICS_CONSTRAINED_MODEL_V1. Files:
- analysis_2026-10-10_campaign/implementation_2026-10-10.diff: unified diff of scripts/build_iwo_decks.py, scripts/run_atlas.py,
  scripts/run_campaign.py (the change under review).
- config/physics_options.yaml (new, all options OFF), config/iwo_material_model_v3.yaml (new model file).
- analysis_2026-10-10_campaign/sample_decks/*.in and sample_decks/extra/*.in (generated decks), sample_decks/NEW_STATEMENTS.md.
- analysis_2026-10-10_campaign/GENERATOR_AUDIT.md (syntax audit the change must follow), CAMPAIGN_DESIGN.md, campaign_matrix.json.
- The ATLAS 5.28 manual as text: report_latex_full/tools/atlas_manual_pages.txt (search with grep; "===== PDF PAGE N =====" markers).
- Installed example decks: /mnt/c/sedatools/examples/deckbuild/4.2.5.R/ (tft/tftex21, diode/diodeex10, diode/diodeex12,
  quantum/quantumex05, quantum/quantumex20, eprom/eprmex01, organic/organicex04, solar/solarex18).

Answer concisely (at most ~1000 words), with a verdict per item: OK / FIX (say exactly what) / RISK (what to watch on the first run):
1. OFF = unchanged: with every option OFF, can any path of the diff change the generated text of an existing V1/V2 deck
   (transfer, ID-VD output mode)? (The author's harness says 48/48 identical; look for paths it would not exercise.)
2. Syntax of every NEW statement in the sample decks against the manual/examples: MATERIAL region=3/4 affinity eg300 me.tunnel;
   CONTACT ... qtunn.cmass; MODELS qtnlsc.el qtnl.derivs / fnord f.ae f.be / itat.sc.el / bqp.n bqp.ngamma bqp.nalpha bqp.qdir;
   DOPING region=4 uniform tat.trap ... acceptor sign sigp e.level; LOG ... j.tun; extract ifn."gate";
   MOBILITY material=IWO igzo.tokyo mun mup tmun tmup igzo.gamma0 igzo.tgamma igzo.ncrit;
   CONTACT name=source workfun surf.rec barrier e.tunnel me.tunnel ^ins.ohmic; MATERIAL ... arichn / ml mt1 mt2 continuing the
   IWO MATERIAL statement; same-name ELECTRODE volumes; MATERIAL region=8 mun. Flag anything misspelt, on the wrong statement,
   or in an order ATLAS would reject (e.g. MOBILITY after SOLVE INIT, DOPING after MATERIAL).
3. Physics/geometry of the separate ungated strip deck (sample_decks/S2-14_*_strip.in) and of the in-solver strip
   (sample_decks/extra/S6-27_*.in): is every point of the rectangular domain covered by a region, do the electrodes/regions
   make sense, is the Neumann bottom (no gate) a fair "ungated" model, any obvious solver trap?
4. run_atlas.execute_strip and the run_campaign "strip" branch: any bug (KCL rule, ratio, missing file, RUN_INDEX row,
   resume)? Is adding this mode a change of semantics for existing plans?
5. Labels in config/iwo_material_model_v3.yaml and config/physics_options.yaml: any value mislabelled (COMPUTED / MEASURED /
   LITERATURE / FITTED / ASSUMED / CALCULATED / MODEL), or a fitted value presented as validation?
6. Anything else that would waste a launch (the campaign has at most 200 sequential launches).
