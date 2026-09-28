# Summary of every recorded Silvaco invocation

Snapshot: 2026-09-12T13:55:21.917970+00:00. 70 invocations; 75 reserved engine stages. The current four-hour rebuild accounts for 10 invocations. Combined earlier inputs can reserve more than one engine stage.

Metrics below are recomputed from native logs where the strict full-transfer rebuild loader applies. Earlier process, probe and quantum runs have different purposes; their blank fit fields are not zero errors. Native evidence PASS is not a mesh/DOS pass or measurement-fit acceptance. All-point signed linear errors and zero counts are in the companion CSV/JSON.

| # | Run / purpose | Native outcome | Active log RMSE | Ion error |
|---|---|---|---:|---:|
|1|20260910T053330_375383_minimal [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|2|20260910T053345_024339_minimal_windows_batch [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|3|20260910T060125_349772_minimal_numbered_contacts [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|4|20260910T060145_619199_iwo_2nm_original_smoke [historical artifact not bundled]|Historical saved validation.json: LOCAL_ATLAS_SMOKE_DOS_DISABLED; not a new rebuild numerical certificate|-|-|
|5|20260910T060500_655908_2p0_full [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|6|20260910T061028_286517_2p0_smoke [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|7|20260910T061324_276828_mobility_update_check [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|8|20260910T061422_730711_mobility_region_check [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|9|20260910T061552_900597_mobility_bias_refresh_check [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|10|20260910T061640_369060_2p0_smoke [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|11|20260910T062342_462763_2p0_smoke [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|12|20260911T144631_108956_paper_athena_2nm [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|13|20260911T144832_495009_paper_native_DOS_2nm_01 [historical artifact not bundled]|INCOMPLETE: task timeout; partial output preserved|-|-|
|14|20260911T145341_407807_paper_athena_import_2nm_01 [historical artifact not bundled]|Historical saved validation.json: REAL_ATLAS_DIAGNOSTIC_NOT_CALIBRATED; not a new rebuild numerical certificate|-|-|
|15|20260911T145716_216706_paper_active_2nm_01 [historical artifact not bundled]|Historical saved validation.json: REAL_ATLAS_DIAGNOSTIC_NOT_CALIBRATED; not a new rebuild numerical certificate|-|-|
|16|20260911T145925_836281_paper_active_128_2nm_01 [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|17|20260911T145949_402807_paper_athena_ideal_support_2nm_01 [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|18|20260911T150155_078376_paper_active_80_2nm_01 [historical artifact not bundled]|Not independently rechecked as a standard full-transfer rebuild|-|-|
|19|20260911T150208_547981_paper_active_width2_2nm_01 [historical artifact not bundled]|Historical saved validation.json: REAL_ATLAS_DIAGNOSTIC_NOT_CALIBRATED; not a new rebuild numerical certificate|-|-|
|20|20260911T150513_112358_paper_active_dos2_2nm_01 [historical artifact not bundled]|INCOMPLETE: task timeout; partial output preserved|-|-|
|21|20260911T150849_876775_paper_active_mesh07_2nm_01 [historical artifact not bundled]|INCOMPLETE: task timeout; partial output preserved|-|-|
|22|20260911T153248_978780_combined_constant_probe [historical artifact not bundled]|Historical saved probe_validation.json: GENUINE_25_POINT_COMBINED_PROBE_NOT_CALIBRATION; not a new rebuild numerical certificate|-|-|
|23|20260911T153347_792827_combined_tokyo_probe [historical artifact not bundled]|Historical saved probe_validation.json: GENUINE_25_POINT_COMBINED_PROBE_NOT_CALIBRATION; not a new rebuild numerical certificate|-|-|
|24|20260911T153703_362271_combined_tokyo_full_2nm [historical artifact not bundled]|Historical saved validation.json: REAL_ATLAS_DIAGNOSTIC_NOT_CALIBRATED; not a new rebuild numerical certificate|-|-|
|25|20260911T154221_075249_combined_schottky_full_2nm [historical artifact not bundled]|Historical saved validation.json: REAL_ATLAS_DIAGNOSTIC_NOT_CALIBRATED; not a new rebuild numerical certificate|-|-|
|26|20260911T154437_705885_combined_mesh_full_2nm [historical artifact not bundled]|Historical saved validation.json: REAL_ATLAS_DIAGNOSTIC_NOT_CALIBRATED; not a new rebuild numerical certificate|-|-|
|27|20260912T064920_755417_rebuild_trapfree_both_2nm [historical artifact not bundled]|FAIL full-transfer native gates|0.73611|+22.520%|
|28|20260912T065050_238465_rebuild_contact_both_2nm [historical artifact not bundled]|PASS full-transfer native gates|0.72882|+21.499%|
|29|20260912T065744_067791_rebuild_contact_electron_2nm [historical artifact not bundled]|PASS full-transfer native gates|0.72882|+21.499%|
|30|20260912T070050_911750_baseline_electron_width [historical artifact not bundled]|PASS full-transfer native gates|0.72882|+21.499%|
|31|20260912T070159_840544_baseline_electron_xmesh [historical artifact not bundled]|PASS full-transfer native gates|0.73008|+21.542%|
|32|20260912T070330_900047_baseline_electron_ymesh [historical artifact not bundled]|PASS full-transfer native gates|0.72866|+21.413%|
|33|20260912T070545_728070_stage_scale_shift_2nm [historical artifact not bundled]|PASS full-transfer native gates|0.31848|-55.202%|
|34|20260912T070700_067594_class_interface_2nm [historical artifact not bundled]|UNVALIDATED exit: no native completion or full-transfer certificate; separate repeat exists|-|-|
|35|20260912T070939_155897_class_interface_repeat_2nm [historical artifact not bundled]|PASS full-transfer native gates|1.66590|-20.478%|
|36|20260912T071113_885520_class_bulk_tail_2nm [historical artifact not bundled]|PASS full-transfer native gates|0.33117|-24.956%|
|37|20260912T071321_152032_class_tokyo_2nm [historical artifact not bundled]|PASS full-transfer native gates|0.69267|-38.305%|
|38|20260912T071501_133624_bulk_dos192_2nm [historical artifact not bundled]|PASS full-transfer native gates|0.33045|-21.040%|
|39|20260912T071827_041454_bulk_energy384_dos [historical artifact not bundled]|PASS full-transfer native gates|0.33054|-20.028%|
|40|20260912T072315_482332_bulk_dos768_2nm [historical artifact not bundled]|PASS full-transfer native gates|0.33058|-19.774%|
|41|20260912T073059_633775_fit_bulk01_2nm [historical artifact not bundled]|PASS full-transfer native gates|0.12220|-1.868%|
|42|20260912T073717_435478_fit_bulk_width03_2nm [historical artifact not bundled]|PASS full-transfer native gates|0.07621|-2.372%|
|43|[20260912T074348_745974_quantum_charge_bound_2nm](<audit/results/local_session_20260910/runs/20260912T074348_745974_quantum_charge_bound_2nm/device.in>)|Separate quantum-charge diagnostic; not an Id-Vg fit; see QUANTUM_CHARGE_VERIFICATION.md|-|-|
|44|[20260912T074527_865393_fit_bulk_width04_2nm](<audit/results/local_session_20260910/runs/20260912T074527_865393_fit_bulk_width04_2nm/device.in>)|PASS full-transfer native gates|0.03339|+0.690%|
|45|[20260912T075145_706323_fit04_verify_width](<audit/results/local_session_20260910/runs/20260912T075145_706323_fit04_verify_width/device.in>)|PASS full-transfer native gates|0.03339|+0.690%|
|46|[20260912T075729_133091_fit04_verify_xmesh](<audit/results/local_session_20260910/runs/20260912T075729_133091_fit04_verify_xmesh/device.in>)|PASS full-transfer native gates|0.03345|+0.715%|
|47|[20260912T080711_514586_fit04_verify_ymesh](<audit/results/local_session_20260910/runs/20260912T080711_514586_fit04_verify_ymesh/device.in>)|PASS full-transfer native gates|0.03326|+0.566%|
|48|[20260912T081824_443496_fit04_verify_dos](<audit/results/local_session_20260910/runs/20260912T081824_443496_fit04_verify_dos/device.in>)|PASS full-transfer native gates|0.03350|+0.779%|
|49|20260912T082755_663447_fit04_contact1_sensitivity [historical artifact not bundled]|PASS full-transfer native gates|0.03339|+0.690%|
|50|20260912T083510_080453_extension01_13p2nm [historical artifact not bundled]|PASS full-transfer native gates|0.20347|+8.553%|
|51|20260912T084456_680995_extension01_6p3nm [historical artifact not bundled]|PASS full-transfer native gates|0.28941|+39.688%|
|52|20260912T085230_151594_extension01_31p8nm [historical artifact not bundled]|INCOMPLETE: task timeout; partial output preserved|-|-|
|53|[20260912T090754_224585_extension02_charge_13p2nm](<audit/results/local_session_20260910/runs/20260912T090754_224585_extension02_charge_13p2nm/device.in>)|PASS full-transfer native gates|0.05383|+2.152%|
|54|[20260912T091742_999942_extension02_charge_6p3nm](<audit/results/local_session_20260910/runs/20260912T091742_999942_extension02_charge_6p3nm/device.in>)|PASS full-transfer native gates|0.06399|+10.454%|
|55|20260912T092601_444418_extension02_donor_31p8nm [historical artifact not bundled]|PASS full-transfer native gates|0.26478|+12.246%|
|56|20260912T094451_112677_extension02_verify_13nm_dos [historical artifact not bundled]|PASS full-transfer native gates|0.05385|+2.202%|
|57|20260912T095808_596080_extension02_verify_6nm_dos [historical artifact not bundled]|PASS full-transfer native gates|0.06454|+10.653%|
|58|20260912T100732_374668_extension03_prpmob_31p8nm [historical artifact not bundled]|PASS full-transfer native gates|0.41801|+71.609%|
|59|20260912T102401_692471_extension03_tailshape_6p3nm [historical artifact not bundled]|PASS full-transfer native gates|0.08513|+9.157%|
|60|[20260912T103227_998562_contact_emission01_2nm](<audit/results/local_session_20260910/runs/20260912T103227_998562_contact_emission01_2nm/device.in>)|PASS full-transfer native gates|0.03313|+0.307%|
|61|[20260912T120614_604542_resume_6nm_y01_ymesh](<audit/results/local_session_20260910/runs/20260912T120614_604542_resume_6nm_y01_ymesh/device.in>)|PASS full-transfer native gates|0.06311|+10.168%|
|62|[20260912T121627_947928_priority3_fit6_mu12](<audit/results/local_session_20260910/runs/20260912T121627_947928_priority3_fit6_mu12/device.in>)|Not independently rechecked as a standard full-transfer rebuild|-|-|
|63|[20260912T122359_458630_priority3_fit13_nd89](<audit/results/local_session_20260910/runs/20260912T122359_458630_priority3_fit13_nd89/device.in>)|PASS full-transfer native gates|0.04903|+2.452%|
|64|[20260912T124052_500555_priority3_fit6_mu12_retry](<audit/results/local_session_20260910/runs/20260912T124052_500555_priority3_fit6_mu12_retry/device.in>)|Not independently rechecked as a standard full-transfer rebuild|-|-|
|65|[20260912T124657_803129_priority3_fit6_mu12_retry2](<audit/results/local_session_20260910/runs/20260912T124657_803129_priority3_fit6_mu12_retry2/device.in>)|PASS full-transfer native gates|0.04921|+1.967%|
|66|[20260912T125515_583761_priority3_verify6_x](<audit/results/local_session_20260910/runs/20260912T125515_583761_priority3_verify6_x/device.in>)|PASS full-transfer native gates|0.04918|+1.931%|
|67|[20260912T130613_869036_priority3_verify6_y](<audit/results/local_session_20260910/runs/20260912T130613_869036_priority3_verify6_y/device.in>)|PASS full-transfer native gates|0.04891|+1.702%|
|68|[20260912T131716_348906_priority3_verify6_dos](<audit/results/local_session_20260910/runs/20260912T131716_348906_priority3_verify6_dos/device.in>)|PASS full-transfer native gates|0.04971|+2.150%|
|69|[20260912T132642_597382_priority3_verify13_x](<audit/results/local_session_20260910/runs/20260912T132642_597382_priority3_verify13_x/device.in>)|PASS full-transfer native gates|0.04897|+2.430%|
|70|[20260912T134058_082088_priority3_verify13_y](<audit/results/local_session_20260910/runs/20260912T134058_082088_priority3_verify13_y/device.in>)|PASS full-transfer native gates|0.04914|+2.464%|

Selection and validation scope: this history records individual invocations and available native checks. It does not determine the latest selected candidate or grant numerical or measurement-fit acceptance. Consult docs/rebuild_20260912/PRIORITY_THREE_RUN_SUMMARY.md for the current phase and the exact candidate-specific certificates for completed controls. A different physical candidate does not inherit an earlier certificate. Missing metrics or an unfinished run are not a successful fit; low-current and predictive-physics limits remain separate from active-region agreement.

Machine-readable detail: [run_history_20260912T135521_917970/runs.csv](<audit/results/rebuild_20260912/run_history_20260912T135521_917970/runs.csv>) and [run_history_20260912T135521_917970/runs.json](<audit/results/rebuild_20260912/run_history_20260912T135521_917970/runs.json>).

This presentation copy links to included audit artifacts where available. Older unbundled entries are explicitly labeled; their original absolute paths remain in the unchanged audit/RUN_BY_RUN_SUMMARY.md and companion history JSON/CSV. For the current ten starts, use [RUNS_THIS_EXTENSION.md](RUNS_THIS_EXTENSION.md).
