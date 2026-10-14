"""Build evidence/CLAIM_SOURCE_MAP.tsv from research_record/03_CLAIMS_LEDGER.yaml (C001-C040) plus the
monograph-level synthesis claims listed in MONO below. The ledger label is copied, never upgraded."""
import csv, pathlib, yaml
ROOT = pathlib.Path(__file__).resolve().parents[2]
led = yaml.safe_load((ROOT/"research_record/03_CLAIMS_LEDGER.yaml").read_text())
SECT = {  # claim -> monograph chapter tags (filled as chapters are written)
 **{f"C{n:03d}": "device; extraction" for n in range(1, 14)},
 "C014": "tcad-history; six-nm", "C015": "tcad-traps", "C016": "tcad-electrostatics", "C017": "tcad-traps",
 "C018": "identifiability", "C019": "tcad-contacts", "C020": "dft-confinement; multiscale", "C021": "dft-slabs",
 "C022": "dft-w", "C023": "literature-w", "C024": "provenance", "C025": "provenance", "C026": "device",
 "C027": "alternatives", "C028": "six-nm; alternatives", "C029": "device", "C030": "provenance",
 "C031": "provenance", "C032": "provenance", "C033": "provenance", "C034": "amorph-numerics",
 "C035": "amorph-numerics", "C036": "amorph-numerics", "C037": "amorph-ml", "C038": "dft-vacancy",
 "C039": "dft-bulk; dft-slabs; multiscale", "C040": "dft-holes; multiscale"}
FACTS = {"C002": "FACT-101..103", "C003": "FACT-101..103", "C029": "FACT-104", "C030": "FACT-100; FACT-111..113",
 "C020": "FACT-010..015; FACT-030", "C021": "FACT-016..018", "C022": "FACT-040..048", "C037": "FACT-070",
 "C034": "FACT-071", "C035": "FACT-072", "C036": "FACT-073", "C038": "FACT-050..052",
 "C039": "FACT-001..006; FACT-020..026d; FACT-047", "C040": "FACT-060..062"}
rows = []
for c in led:
    ev = c.get("evidence", [])
    ev = "; ".join(str(e) for e in ev) if isinstance(ev, list) else str(ev)
    rows.append([c["id"], c["claim"].replace("\t", " "), c["status"], FACTS.get(c["id"], ""), ev[:400],
                 (c.get("caveats") or "")[:300].replace("\n", " "), SECT.get(c["id"], ""), "ledger"])
MONO = [  # monograph synthesis claims: label, evidence; status = proposed until chapter review
 ("M001", "The registered H-N outcome is UNRESOLVED in every branch; neither CROSSOVER nor NO CROSSOVER can be claimed from the current campaign", "DERIVED (from frozen rules)", "", "HYPOTHESIS_REGISTER A27, A37; D-42", "Follows from the rules alone, independent of any sealed value", "ch:mono-amorph (prop:mono-hn)"),
 ("M002", "Kane-consistent single-band EMA (hole confinement dEc(1+alpha dEc) m_b/m_h, m_h >= 3.2 m0) gives dEv -0.061 eV and CB share 0.93 at 0.930 nm, matching the computed -0.052 eV / 0.94; at 1.962 nm it gives -0.016 eV / 0.95 against computed -0.054 eV / 0.84. The 2 nm excess of ~38 meV exceeds the alignment-route spread (5 meV) and the plateau flatness (8 meV) and is unexplained", "DERIVED; 2 nm excess UNRESOLVED", "FACT-029; FACT-014; FACT-015", "tools/confinement_analysis.py", "a systematic common to both alignment routes (bulk reference, termination dipole, strain) is not excluded", "ch:mono-confinement-theory"),
 ("M003", "The dEc exponent between 1 and 2 nm (1.48) is below the bulk-Kane prediction for a box width proportional to t (1.62); the dEg exponent (1.32) is lower because dEv is nearly constant", "DERIVED", "FACT-028", "tools/confinement_analysis.py", "Kane fit only up to 0.45 eV", "ch:mono-confinement-theory"),
 ("M004", "The in-plane mass increase of the crystalline films is consistent with the bulk Kane non-parabolicity at the subband energy: m_b(1+2 alpha dEc) reproduces the computed mass within 1 % at 1.962 nm and overestimates it by 10 % at 0.930 nm, with no fit; the 0.461 and 0.695 nm films (within 2 %) do not test it (outside the fit window; +-9 % from the polar-field uncertainty)", "DERIVED", "FACT-027", "tools/confinement_analysis.py", "crystalline PBE; to ~10 % the mass and dEc laws are one input (Delta m itself within ~20 %)", "ch:mono-confinement-theory; ch:mono-masses"),
 ("M005", "The frozen absolute PR thresholds correspond to different localised support sizes across the registered cells (6.3-7.4 atoms in bulk/thin cells, 13.2-13.5 at 2.0 nm)", "DERIVED (property of the rule)", "FACT-081", "register section 1; cell compositions", "reading aid; rule unchanged", "ch:mono-defect-theory; ch:mono-amorph"),
 ("M006", "Quantum confinement can roughly double shallow-donor binding in films thinner than a_B (2.7 nm), up to 4x in the strict 2-D limit; dielectric enhancement is small for the HfO2-backed device stack (up to ~0.45 eV only for an Al2O3/air environment); a W-independent mechanism for thickness-dependent donor activation", "THEORY (not computed)", "FACT-080", "Bastard1981b; Diarra2007; Bjork2009", "order-of-magnitude only", "ch:mono-defect-theory; ch:mono-alternatives"),
 ("M007", "Transferred rigidly (1:1) to the threshold, the computed dEc law accounts for 44 % of the measured 2.0-13.2 nm threshold difference (-0.257 of -0.579 V) but implies -0.21 to -0.22 V between 2.0 and 6.3 nm against a measured -0.018 V, the direction and size of the three failed 6.3 nm predictions", "DERIVED (uses MEASURED device data)", "FACT-022; FACT-023; FACT-101; FACT-102; FACT-103", "evidence/derived/multiscale_budget.json; tools/fig_threshold_vs_dft.py; C014", "rigid transfer, not a model run; cause not identified (C018); device data need the fab's permission", "ch:mono-multiscale"),
 ("M008", "The saturation-mobility identity mu_sat = mu_FE V_D/(2 V_ov - V_D) under-predicts the observed mu_sat/mu_FE ratios of the measured curves by factors 1.5-1.8 at the mu_sat peaks (constant-mobility prediction); the saturation-formula peaks, which match the paper's numbers, are numerical correspondences, not channel mobilities", "DERIVED (uses MEASURED device data)", "FACT-111; FACT-112; FACT-113", "evidence/derived/musat_ratio.json; C030", "constant-mobility identity; V_ov from V_th,cc", "ch:mono-provenance"),
]
for m in MONO:
    rows.append([m[0], m[1], m[2], m[3], m[4], m[5], m[6], "monograph (proposed)"])
out = ROOT/"research_monograph/evidence/CLAIM_SOURCE_MAP.tsv"
with open(out, "w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["claim_id","claim","label","facts","evidence","caveat_excerpt","monograph_sections","origin"])
    w.writerows(rows)
print(out.relative_to(ROOT), len(rows), "rows")
