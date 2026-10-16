"""Build evidence/FIGURE_INDEX.tsv: every existing figure the monograph may reuse, with its generator, data source
and caption basis. Figures are reused, not regenerated, unless a correction requires it (column 'reuse')."""
import csv, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[2]
rows = []
# 1) baseline report figures with MANIFEST descriptions
man = (ROOT/"report_latex_full/figures/MANIFEST.md").read_text().split("\n## ")
desc = {}
for block in man[1:]:
    head, _, body = block.partition("\n")
    desc[head.strip()] = re.sub(r"\s+", " ", body)[:300]
for p in sorted((ROOT/"report_latex_full/figures").glob("*.pdf")):
    stem = p.stem
    rows.append([f"FIG-R-{stem}", str(p.relative_to(ROOT)), "report_latex_full/figures/src (Stage 0 make_figures.py)",
                 desc.get(stem, ""), "dft" if stem.startswith("dft_") else "tcad/device",
                 "check-DFT-currency" if stem.startswith("dft_") else "reuse", "safe"])
# 2) crystalline DFT re-derivation figures
gen = {f.stem: f.name for f in (ROOT/"qe_workflow/analysis_2026-10-13_full").glob("f*.py")}
for p in sorted((ROOT/"qe_workflow/analysis_2026-10-13_full/figures").glob("*.pdf")):
    key = p.stem.replace("fig", "f")[:3]
    script = next((v for k, v in gen.items() if k.startswith(key)), "")
    rows.append([f"FIG-Q-{p.stem}", str(p.relative_to(ROOT)), f"qe_workflow/analysis_2026-10-13_full/{script}",
                 f"data: out/{script.replace('.py','.json')}", "dft", "reuse (current, 2026-10-13)", "safe"])
for p in sorted((ROOT/"qe_workflow/analysis_2026-10-13_full/bands_masses/figures").glob("*.pdf")):
    rows.append([f"FIG-B-{p.stem}", str(p.relative_to(ROOT)), "bands_masses/b02_band_figures.py etc.",
                 "data: bands_masses/out/b0*.json; BANDS_MASSES.md", "dft", "reuse (current, 2026-10-14)", "safe"])
# 3) extraction / V2 / traps figures (pdf only)
for d in ("analysis_2026-10-06_extraction/figures", "analysis_2026-10-06_V2", "analysis_2026-10-06_traps"):
    for p in sorted((ROOT/d).rglob("*.pdf")):
        rows.append([f"FIG-X-{p.stem}", str(p.relative_to(ROOT)), d.split("/")[0], "", "device/extraction",
                     "reuse" if "/final/" in str(p) or "/paper/" in str(p) else "candidate", "safe"])
out = ROOT/"research_monograph/evidence/FIGURE_INDEX.tsv"
with open(out, "w", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["fig_id", "path", "generator", "data_or_caption_basis", "domain", "reuse", "blind_status"])
    w.writerows(rows)
print(out.relative_to(ROOT), len(rows), "figures")
