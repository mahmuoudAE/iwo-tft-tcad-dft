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
 ("M001", "The registered H-N outcome is UNRESOLVED in every branch; neither CROSSOVER nor NO CROSSOVER can be claimed from the current campaign", "DERIVED (from frozen rules)", "", "HYPOTHESIS_REGISTER A27, A37; D-42", "Follows from the rules alone, independent of any sealed value", "amorph-hn; conclusions"),
 ("M002", "Effective-mass theory with the computed electron and hole DOS masses predicts a CB share of the confinement opening close to 1, larger than the computed 0.84 (2 nm) and 0.94 (1 nm)", "DERIVED (monograph analysis)", "FACT-004; FACT-014; FACT-015; FACT-061", "theory chapter derivation", "Interpretation of the difference (surface dipoles, OH-derived VB) is INFERRED", "theory-confinement; dft-alignment"),
 ("M003", "The PBE confinement exponent p ~ 1.3 lies between the infinite-well value 2 and smaller values expected from finite barriers and non-parabolicity", "DERIVED (monograph analysis)", "FACT-020; FACT-021; FACT-005", "theory chapter", "Qualitative ordering only; no fitted barrier", "theory-confinement"),
]
for m in MONO:
    rows.append([m[0], m[1], m[2], m[3], m[4], m[5], m[6], "monograph (proposed)"])
out = ROOT/"research_monograph/evidence/CLAIM_SOURCE_MAP.tsv"
with open(out, "w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["claim_id","claim","label","facts","evidence","caveat_excerpt","monograph_sections","origin"])
    w.writerows(rows)
print(out.relative_to(ROOT), len(rows), "rows")
