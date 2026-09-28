"""Insert the campaign-D results (run_0053 timeout, run_0054 tmun=0, run_0055 overlap) into the report text."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
def rep(f, old, new):
    p = R / f; t = p.read_text(encoding='ascii'); assert old in t, (f, old[:50]); p.write_text(t.replace(old, new, 1), encoding='ascii')
rep('chapters/07_calibration.tex', '\\multicolumn{6}{l}{\\textbf{retracted}: malformed deck (drain collapsed; see text)} & --\\\\',
    '\\multicolumn{6}{l}{\\textbf{retracted}: malformed deck (drain collapsed; see text)} & --\\\\\n2.0 & overlap 2 $\\rightarrow$ 4~\\textmu m (corrected mesh) & \\run{0038}$\\rightarrow$\\run{0055} & \\multicolumn{6}{l}{$\\Delta\\Vthcc = 0.000$~V, $\\Delta\\Ion = -0.006\\,\\%$, identical SS (DOS 384/192)} & --\\\\')
rep('chapters/07_calibration.tex', '\\item \\run{0027} (overlap) is retracted as malformed; contact geometry was not tested.',
    '\\item \\run{0027} (overlap) is retracted as malformed. The corrected repetition \\run{0055} (overlap 4~\\textmu m, mesh following the contacts; the first attempt \\run{0053} exceeded the 900~s time limit) changes $\\Ion$ by $-0.006\\,\\%$ and leaves $\\Vthcc$ and the subthreshold slope unchanged, so with ideal Ohmic contacts the assumed overlap does not influence the results.')
rep('chapters/05_derivations_transport.tex', 'Their activation energies differ by exactly 42.3 meV. All temperature results are registered predictions (\\evPRED).',
    'Their activation energies differ by exactly 42.3 meV. A direct check, \\run{0054} (2 nm, 358.15 K, $\\mathrm{tmun}=0$ declared explicitly), reproduces \\run{0045}$\\times1.30441$ to within 0.11\\,\\% at every gate voltage, which confirms the rescaling numerically. All temperature results are registered predictions (\\evPRED).')
print('ok')
