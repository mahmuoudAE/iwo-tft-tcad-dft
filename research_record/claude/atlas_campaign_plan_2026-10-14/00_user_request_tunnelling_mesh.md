# User request 2026-10-14 ~15Z: include the tunnelling mesh (QTX.MESH / QTY.MESH) in the campaign plan

Facts gathered (main session, before integration):
- ATLAS 5.28 manual (atlas_manual_pages.txt l.13505-13507): T(E) by transfer matrix on a stepwise potential; fine mesh along the tunnelling direction recommended.
- l.13660-13676 "Mesh Considerations": QTNLSC is quasi-1D on slices through the insulator. For an Atlas-built mesh slicing is automatic (locally perpendicular to each semiconductor-oxide segment; SHAPEOX alternative). QTX.MESH/QTY.MESH are described as the option for Athena/DevEdit meshes; the QT mesh must enclose the insulator and not overextend; tunnelling along y by default (QTUNN.DIR 0). Table 3-130 parameters NODE, LOCATION, X, RATIO, SPACING.
- 2004 manual (atlas_user_manual_740p.txt l.8730-8757, 27757): same statements.
- Project history: build_iwo_decks.py option gate_tunnelling.qt_mesh=1 (qt_slice_um 0.2, qt_point_nm 0.5) reproduces the run_0063..0066 form. run_0062: automatic slicing ran out of memory at the old 2 GB limit. run_0065: a QT mesh flush with the oxide faces was ignored ("must enclose oxide"). run_0066: on the rectangular QT mesh the tunnel current was booked to the electrodes only; drift-diffusion currents bit-identical to run_0061/0065 (no continuity coupling), KCL failed. Registered form since run_0067: automatic slicing.
- S2-11 (run_0076 vs run_0067, oxide y-mesh x0.5, automatic slicing): registered FAIL, resolved |I_G| changed up to 2.86 dec (0.315 dec at -3 V).

To integrate: a tunnelling-mesh convergence branch, e.g. (i) automatic-slice series with a further uniform oxide refinement, and/or (ii) QT-mesh series (point spacing 0.5 -> 0.25 nm, slice spacing 0.2 -> 0.1 um) used only as an I_G magnitude/convergence cross-check (not self-consistent, KCL known to fail), with launch cost, memory risk (32-bit ~30k nodes), the amendment needed (result-informed, after S2-11), Codex + manual check, and what each outcome can claim.
