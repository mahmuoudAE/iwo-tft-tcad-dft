"""Revised copies of baseline chapters whose wording exceeds the current ledger labels or whose status is stale.

chapters/<name>_rev.tex = report_latex_full/chapters/<name>.tex (baseline 3fe6627) + exact-match patches (each must
occur once). Basis: framing-chapter audit of 2026-10-14 (each item spot-checked against the file), claims ledger
C004-C006, C014, C028, C030-C033, decision log D-07, D-17. Run: python3 -I research_monograph/tools/patch_reused.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = ROOT / "report_latex_full/chapters"
OUT = ROOT / "research_monograph/chapters"


def note(text):
    return "\n\\begin{statusbox}{Revision note (monograph, October 2026)}\n" + text + "\n\\end{statusbox}\n"


SPEC = {
    "03_device_data": [
        ("\\label{ch:device}\n", "\\label{ch:device}\n" + note(
            "Baseline chapter with three wording changes: the stack order (\\AlO{} against the channel) is stated as an\n"
            "assumption, and the saturation-formula correspondence with the published mobilities is stated as a numerical\n"
            "match (\\claim{C030}) that makes the formula the leading candidate for the paper's definition (\\claim{C031});\n"
            "same-device provenance and the current unit are not established (\\claim{C033}). Ownership and permission:\n"
            "\\cref{ch:mono-audit}.")),
        ("the \\AlO{} layer is in contact with the channel.",
         "the \\AlO{} layer is taken to be in contact with the channel (the stack order is not stated by the fabrication\ngroup and remains an open question; \\cref{ch:mono-provenance})."),
        ("which reproduces the numbers of the paper. The workbook\ncurves are therefore the thickness series of the paper, and the mobility of the paper is a saturation-formula peak\ntaken near threshold rather than a linear-regime field-effect mobility (\\evCORR;",
         "which matches the numbers of the paper with no adjustable factor \\claim{C030}. This\nmakes a saturation-formula peak taken near threshold, rather than a linear-regime field-effect mobility, the leading\ncandidate for the paper's definition \\claim{C031}, and it is consistent with the workbook curves being the paper's\nthickness series; neither the recipe nor the same-device provenance has been confirmed by the fabrication group\n\\claim{C033} (\\evCORR;"),
        ("The consistency of the saturation-formula mobility with the paper\n        (\\cref{sec:inp-metrics-measured}) supports this reading.",
         "The saturation-formula correspondence with the paper\n        (\\cref{sec:inp-metrics-measured}) constrains only the product $\\Cox\\cdot W/L\\cdot$(current normalisation);\n        it does not fix the unit convention \\claim{C031} \\claim{C033}."),
        ("The mobilities of the paper are saturation-formula values (5.09 and 27.40 are\nreproduced).",
         "The mobilities of the paper are reproduced numerically by the saturation formula (5.09 and 27.40;\nthe leading candidate for the paper's definition, unconfirmed \\claim{C031})."),
    ],
    "09_mechanisms": [
        ("outside the regime of that formula; the same procedure predicts $3.86\\cmVs$ at \\SI{6.3}{nm} (SYNTHESIS D12; S2 and S5 verdicts, demonstrated, provenance evidence).",
         "outside the validity range of that formula for the threshold definitions tested \\claim{C031}; the same procedure gives $3.86\\cmVs$ at \\SI{6.3}{nm} (SYNTHESIS D12; numerical correspondence \\claim{C030}; that the paper used this formula is the leading candidate, not established, \\claim{C031})."),
        ("Paper $\\mu$ = saturation formula & demonstrated (provenance) & \\evDATA &",
         "Paper $\\mu$ = saturation formula & numerical match derived; definition inferred \\claim{C031} & \\evCORR &"),
    ],
    "11_validation": [
        ("\\label{ch:validation}\n", "\\label{ch:validation}\n" + note(
            "This chapter records the validation status and the plan as of 25 September to 7 October 2026. Launch\n"
            "counts, budgets and the tier plan are historical: the budget was later raised (\\dlog{D-03}, \\dlog{D-13}), QE\n"
            "was installed and run (\\cref{ch:dft,ch:mono-masses,ch:mono-w-vac,ch:mono-amorph}), the registered V2 test\n"
            "failed (\\cref{ch:v2}), and the shared-model campaign is in \\cref{ch:mono-c10}. The current status of every\n"
            "claim is in \\cref{ch:mono-conclusions}.")),
        ("Paper $\\mu$ = saturation formula & \\evDATA{} (provenance) &",
         "Paper $\\mu$ = saturation formula (leading candidate) & \\evCORR{} (numerical match \\claim{C030}; definition inferred \\claim{C031}) &"),
        ("every genuinely out-of-sample test run so far (\\run{0014}, B0 \\run{0037}, C1 \\run{0052}) failed or partly failed.",
         "every genuinely out-of-sample test run so far (\\run{0014}, B0 \\run{0037}, C1 \\run{0052}, and later the registered V2 test \\run{0060}, \\cref{ch:v2}) failed or partly failed."),
        ("\\emph{``Predictions were registered internally with SHA-256 hashes; no third-party timestamp exists.''}",
         "\\emph{``Predictions were registered internally with SHA-256 hashes; no third-party timestamp exists.''} (Since then the V2 registration is in a public commit, 7b75ee6, and the frozen register carries a pushed git tag, \\dlog{D-17}; no DOI-based timestamp exists.)"),
        ("4.1 [LAB] 3--5 devices per thickness,",
         "4.1 [LAB] 3--5 devices per thickness (the later research-question file asks for at least 10, \\claim{C028}),"),
        ("& no QE installation; even a correct $\\dEc$ is not identifiable",
         "& carried out after this chapter was written (\\cref{ch:dft,ch:mono-w-vac,ch:mono-amorph}); even a correct $\\dEc$ is not identifiable"),
        ("\\item No model claim is validated; every out-of-sample test so far (\\run{0014}, \\run{0037}, \\run{0052}) failed or partly failed.",
         "\\item No model claim is validated; every out-of-sample test so far (\\run{0014}, \\run{0037}, \\run{0052}, \\run{0060}) failed or partly failed."),
    ],
    "14_model_v2": [
        ("\\label{ch:v2}\n", "\\label{ch:v2}\n" + note(
            "Baseline chapter of 6--7 October 2026 with four changes: the floor power law and the exclusion of gate\n"
            "leakage are labelled as fitted and inferred (\\claim{C004}, \\claim{C005}); the cause given for the missed 2~nm\n"
            "RMSE criterion is labelled as an untested estimate; and the empty T4 section now states that T4 was deferred\n"
            "(\\dlog{D-07}). The V2 laws are two-point laws at the Lin-label thicknesses 0.95/1.98~nm; the later laws use\n"
            "the relaxed H--H thickness (\\cref{ch:mono-masses}).")),
        ("\\item[V4] What would 1, 0.75 and 0.5~nm films do?",
         "\\item[V4] What would 1, 0.75 and 0.5~nm films do? (Deferred, \\dlog{D-07}; \\cref{sec:v2-thin}.)"),
        ("From 2 to 13.2~nm the floors grow as $t^{3.85}$.",
         "A single power law through the three floors gives $t^{3.85}$ (three points, one device each; the local exponents\nare 3.1 and 5.1, so a smooth law is not established \\claim{C004})."),
        ("\\paragraph{What is excluded.}",
         "\\paragraph{What is excluded (by inference: no gate current was recorded, \\claim{C005}).}"),
        ("the 0.75 and 0.51~nm films enter as tabulated DFT points (\\cref{sec:v2-thin}).",
         "the 0.75 and 0.51~nm films were planned to enter as tabulated DFT points (\\cref{sec:v2-thin}); the computed\nfilms turned out to be polar (0.695~nm) and In$_8$(OH)$_{24}$ (0.461~nm) (\\cref{sec:mono-dft-thin})."),
        ("The cause is an approximation in the transformation, not\na defect of the V2 decks.",
         "The most likely cause, estimated but not tested by a run, is this approximation in the\ntransformation rather than a defect of the V2 decks; the registered result stays a failure."),
        ("\\textit{[filled in after the 0.75 and 0.51~nm DFT films and the scenario runs]}",
         "T4 was not carried out. The user deferred registered sub-1~nm predictions (\\dlog{D-07}), and the shared-model\ncampaign C10 (\\cref{ch:mono-c10}) replaced the scenario runs. The computed sub-nanometre films are reported in\n\\cref{sec:mono-dft-thin}; the 0.461~nm film is In$_8$(OH)$_{24}$ and the 0.695~nm film is polar, so neither enters a\nthickness law without further work."),
    ],
}


def main():
    for name, patches in SPEC.items():
        text = (BASE / f"{name}.tex").read_text()
        for i, (old, new) in enumerate(patches, 1):
            n = text.count(old)
            if n != 1:
                sys.exit(f"{name} patch {i}: expected 1 occurrence, found {n}: {old[:90]!r}")
            text = text.replace(old, new)
        (OUT / f"{name}_rev.tex").write_text(text)
        print(f"{name}: {len(patches)} patches -> chapters/{name}_rev.tex")


if __name__ == "__main__":
    main()
