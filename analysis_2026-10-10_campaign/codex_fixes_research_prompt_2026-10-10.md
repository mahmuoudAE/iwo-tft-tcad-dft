You are a read-only research assistant for a Silvaco ATLAS 5.28 TCAD deck generator (working directory
IWO_PHYSICS_CONSTRAINED_MODEL_V1). The author is fixing review findings and needs FACTS from the installed manual text
and example decks, not opinions.

=== HARD RULES (read-only) ===
- Do not modify, create or delete any file. Do not use the network.
- NEVER launch Silvaco: do not run deckbuild.exe, scripts/run_atlas.py, scripts/run_campaign.py, or anything under /mnt/c/sedatools/exe.
- Do NOT execute any Windows executable (*.exe, including the Windows Python venv) through WSL interop. Linux python3 has no
  NumPy/PyYAML; use it only for arithmetic or plain-text parsing. grep, sed -n, awk, find are fine.
- Report only what you verified. Cite the manual line number in report_latex_full/tools/atlas_manual_pages.txt and the
  nearest preceding "===== PDF PAGE N =====" marker, or the example file path. If you cannot verify, write UNVERIFIED.

Sources: report_latex_full/tools/atlas_manual_pages.txt (ATLAS 5.28 user manual text); installed examples under
/mnt/c/sedatools (search *.in / *.out / *.log / *.str text files only); this project's run outputs under results/runs/*/deckbuild.out
(V1/V2 runs, no tunnelling/BQP/IGZO options were ever active in them).

Device: bottom gate. Conductor gate (TiN, workfunction 4.7 eV) / HfO2 15 nm (eps 19.57, region 4) / Al2O3 2 nm (eps 9.0,
region 3) / IWO semiconductor (user.material) / Pd source-drain. Generator code: scripts/build_iwo_decks.py campaign_options().

Questions (answer each in <= 150 words, numbered):

Q1 FNORD field location. Manual around lines 13000-13060 (and the FNORD/F.AE/F.BE text near PDF p.288). At which interface
   and in which material is the field E in J = F.AE E^2 exp(-F.BE/E) evaluated (gate-electrode/insulator, or each
   insulator-SEMICONDUCTOR segment)? Is there any per-region or per-material F.AE/F.BE, or only the MODELS-level pair? For a
   series HfO2/Al2O3 stack with only the Al2O3 touching the semiconductor, is it correct that E_Al2O3 = (eps_HfO2/eps_Al2O3) E_HfO2
   (D continuity, no oxide charge), so that to reproduce J(E_HfO2) with the HfO2-barrier constants one needs
   F.AE' = F.AE / r^2, F.BE' = r * F.BE, r = 19.57/9.0 = 2.1744? State any manual text that contradicts this. Also: does
   FNORD with a Conductor/electrode gate add the current to the gate terminal (self-consistent), and is the current direction
   for V_G < 0 (electron injection from gate into the oxide) covered, or only semiconductor-to-gate?

Q2 TAT.POISSON. Manual around line 14541 (PDF p.323) and the ITAT / TAT.TRAP / DOPING text (PDF p.320-327). Exact syntax
   to switch off the trap charge in Poisson (statement and parameter, e.g. MODELS ^TAT.POISSON?), its default, and whether
   ITAT.SC.EL still computes and collects the trap-assisted tunnelling current when it is off. Is any trap-occupancy quantity
   available for OUTPUT/SAVE/PROBE/LOG (name it), so the charged-oxide electrostatic shift could be quantified instead?

Q3 Positive identification in the run output (deckbuild.out = the ATLAS stdout with "ATLAS>" echoed statements). For each
   of QTNLSC.EL, FNORD, ITAT.SC.EL, BQP (bqp.n), IGZO.TOKYO (MOBILITY material=... igzo.tokyo): does the manual or any
   installed example output (*.out/*.log text under /mnt/c/sedatools) show a NON-echoed line or table entry that ATLAS
   prints when the model is active (e.g. a REGIONAL MODEL FLAGS row name, a REGIONAL MOBILITY MODEL SUMMARY model title,
   an extra iteration-table column such as a quantum-potential variable, a "Tunneling" header)? Quote the exact string and
   where you found it. Look at results/runs/run_0040_13p2_recal_dos384_13p2/deckbuild.out lines 237-433 for the table formats
   this ATLAS build prints. If nothing is documented, write UNVERIFIED for that model.

Q4 LOG j.tun. What names do the tunnelling current columns get in the .log file (e.g. "Itnl", "Jtnl", per electrode?) and
   are they readable from the DeckBuild-format log text? Manual reference only; UNVERIFIED if not documented.

Q5 Anything in the same manual sections that says FNORD, QTNLSC.EL and ITAT.SC.EL cannot be combined, or that ITAT
   requires a specific METHOD / carriers setting (the decks use "method newton trap maxtraps=10 ... carriers=1 electrons").

Finish with a short "Facts for the author" list (one line each, with citation).
