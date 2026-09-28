#!/usr/bin/env python3
"""Stage 0a: build REPORT/digest/ so that writers never re-read raw sources.

  papers/<key>.md        paper text split by PRINTED page (CONVENTIONS page map)
  used_items.csv         literature items used by the model, with page confirmed by string search
  report_citations.md    every literature citation found in the 2026-09-25 analysis reports (source line)
  atlas_manual_pages.md  manual pages for every statement/parameter the decks use (PDF page + printed page)
  runs.csv               all V1 runs with robust metrics recomputed from comparison.csv
  numbers.md             key-number lines from SYNTHESIS, S1-S6, PREDICTIONS_REGISTER with file:line
The digest contains copyrighted text excerpts for internal use only; it is NOT copied into the ZIP.
"""
from __future__ import annotations
import csv, json, re
from pathlib import Path
import numpy as np

REPORT = Path(__file__).resolve().parents[1]
PKG = REPORT.parent
DIG = REPORT / 'digest'
TXT = PKG / 'inputs' / 'papers_text'
ANA = PKG / 'analysis_2026-09-25'

PAGEMAP = {  # key: (file, function pdf_page -> printed page string)
    'Januar2026': ('Januar2026_SmallStruct_IWO.txt', lambda n: str(n)),
    'Si2021': ('Si2021_NanoLett_In2O3_0p7nm.txt', lambda n: str(499 + n)),
    'Lin2022': ('Lin2022_ACSNano_thick_In2O3.txt', lambda n: str(21535 + n)),
    'Si2022': ('NatElec2022_s41928-022-00718-w.txt', lambda n: str(163 + n)),
    'Wang2022': ('Wang2022_FrontMater_traps_HfO2In2O3.txt', lambda n: str(n)),
    'Kim2024': ('Kim2024_APL_IWO_thickness_stability.txt', lambda n: f'173507-{n - 1}' if n > 1 else 'cover'),
    'Stokey2021': ('Stokey2021_JAP_In2O3_dielectric_mass.txt', lambda n: f'225102-{n - 1}' if n > 1 else 'cover'),
    'Pandey2025': ('Pandey2025_TED_SCE_TFT.txt', lambda n: str(n)),
    'WangX2025': ('Wang2025_TED_IGZO_compact.txt', lambda n: str(2389 + n)),
    'Anusha2024': ('Anusha2024_MeasSens_IGZO_review.txt', lambda n: str(n)),
    'Giannozzi2009': ('Giannozzi2009_QE.txt', lambda n: str(n)),
}
ALIASES = {'Januar': 'Januar2026', 'Si2021': 'Si2021', 'Lin2022': 'Lin2022', 'Lin': 'Lin2022', 'NatElec2022': 'Si2022', 'Si2022': 'Si2022',
           'Wang2022': 'Wang2022', 'Kim2024': 'Kim2024', 'Kim': 'Kim2024', 'Stokey2021': 'Stokey2021', 'Stokey': 'Stokey2021',
           'Pandey2025': 'Pandey2025', 'Wang2025': 'WangX2025', 'WangX2025': 'WangX2025', 'Anusha2024': 'Anusha2024', 'Giannozzi2009': 'Giannozzi2009'}

def split_pages(key):
    fn, f = PAGEMAP[key]
    t = (TXT / fn).read_text(encoding='utf-8', errors='replace')
    parts = re.split(r'===== PAGE (\d+) =====', t)
    return [(int(parts[i]), f(int(parts[i])), parts[i + 1].strip()) for i in range(1, len(parts), 2)]

PAGES = {k: split_pages(k) for k in PAGEMAP}

def norm(s): return re.sub(r'\s+', ' ', s.replace('\u2212', '-').replace('\u2009', ' ').replace('\u00a0', ' ')).lower()

def find_pages(key, needle):
    n = norm(str(needle))
    if not n or len(n) < 2: return []
    hits = [pp for pdf, pp, txt in PAGES.get(key, []) if n in norm(txt)]
    try:   # scientific notation as extracted from PDFs: "5.3 x 1019" / "6 x1011" (superscripts flattened)
        x = float(needle)
        if x >= 1e3 or (0 < x < 1e-3):
            m, e = f'{x:.3e}'.split('e'); m = ('%g' % float(m)); e = str(int(e))
            rx = re.compile(re.escape(m) + r'\s*[×x]\s*10\s*[−\-]?\s*' + e.lstrip('-'))
            hits += [pp for pdf, pp, txt in PAGES.get(key, []) if rx.search(txt.replace(' ', ' '))]
    except ValueError: pass
    return sorted(set(hits))

def papers():
    (DIG / 'papers').mkdir(parents=True, exist_ok=True)
    for k, pages in PAGES.items():
        out = [f'# {k} (source file {PAGEMAP[k][0]}); headings give PRINTED page = cite as p.~<printed>\n']
        for pdf, pp, txt in pages: out.append(f'\n## printed page {pp}  (PDF page {pdf})\n\n{txt}\n')
        (DIG / 'papers' / f'{k}.md').write_text(''.join(out), encoding='utf-8')

def used_items():
    rows = []
    ev = list(csv.DictReader((PKG / 'tables' / 'THICKNESS_LAW_EVIDENCE.csv').open(encoding='utf-8')))
    for r in ev:
        src = r['source']; key = next((v for a, v in ALIASES.items() if src.startswith(a)), None)
        val = r['value']; cand = [val, val.rstrip('0').rstrip('.') if '.' in val else val]
        try:
            x = float(val)
            if x >= 1e3: m, e = f'{x:.2e}'.split('e'); cand += [m.rstrip('0').rstrip('.') + 'e' + str(int(e)), m.rstrip('0').rstrip('.') + ' x 10', m.rstrip('0').rstrip('.') + '\u00d710']
        except ValueError: pass
        found = sorted({p for c in cand for p in (find_pages(key, c) if key else [])})
        rows.append({'key': key or src, 'quantity': r['quantity'], 'value': val, 'unit': r['unit'], 'thickness_nm': r['thickness_nm'], 'material': r['material'],
                     'label': r['label'], 'package_location': r['location'], 'pages_where_value_string_found': ';'.join(found) or 'NOT_FOUND_BY_STRING (check manually / not bundled)'})
    for r in csv.DictReader((PKG / 'tables' / 'PARAMETER_PROVENANCE.csv').open(encoding='utf-8')):
        rows.append({'key': r['source'], 'quantity': r['parameter'], 'value': '', 'unit': '', 'thickness_nm': '', 'material': '', 'label': r['label'],
                     'package_location': r['location'], 'pages_where_value_string_found': r.get('notes', '')})
    with (DIG / 'used_items.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    # citations inside the analysis reports and package docs
    pat = re.compile(r'(Januar\s?2026|Januar|Si\s?2021|Lin\s?2022|Si\s?2022|NatElec2022|Wang\s?2022|Kim\s?2024|Stokey\s?2021|Pandey\s?2025|Wang\s?2025|Anusha\s?2024|Giannozzi|Fan\s?2021|Feneberg|Hamberg)[^|\n]{0,80}?(p\.\s?\d[\d\-]*|pp\.\s?\d[\d\-]*|Sec\.\s?[\d.]+|Fig\.\s?S?\d+\w?|Eq\.\s?\(?\d+\w?\)?)', re.I)
    out = ['# Literature citations found in analysis reports and package docs (file:line: text)\n']
    for f in sorted(list(ANA.glob('*.md')) + list((PKG / 'docs').glob('*.md')) + [PKG / 'FINAL_STATUS.md']):
        if f.name.startswith('FULL_REPORT'): continue
        for i, line in enumerate(f.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
            if pat.search(line): out.append(f'- {f.relative_to(PKG)}:{i}: {line.strip()[:400]}')
    (DIG / 'report_citations.md').write_text('\n'.join(out) + '\n', encoding='utf-8')

STATEMENTS = {
    'MESH / X.MESH / Y.MESH': [r'MESH\s+statement', r'X\.MESH'], 'REGION': [r'REGION\s+statement'], 'ELECTRODE': [r'ELECTRODE\s+statement'],
    'DOPING UNIFORM': [r'DOPING\s+statement', r'UNIFORM'], 'MATERIAL (USER.GROUP, USER.DEFAULT, EG300, AFFINITY, PERMITTIVITY, NC300, NV300, MUN, MUP, TAUN0, EGALPHA, TMUN)': [r'MATERIAL\s+statement', r'TMUN', r'NC300', r'EGALPHA', r'USER\.DEFAULT'],
    'CONTACT (WORKFUNCTION, RESISTANCE)': [r'CONTACT\s+statement', r'WORKFUNCTION'], 'MODELS (FERMI, SRH, TEMPERATURE, PRINT)': [r'MODELS\s+statement', r'FERMIDIRAC|FERMI\b'],
    'DEFECTS (CONTINUOUS, NUMA, NUMD, NTA, WTA, NGA, EGA, WGA, NGD, EGD, SIGTAE, AFILE)': [r'DEFECTS\s+statement', r'NUMA', r'WTA'], 'INTERFACE (QF)': [r'INTERFACE\s+statement', r'\bQF\b'],
    'METHOD (NEWTON, TRAP, MAXTRAPS, ITLIMIT, CLIMIT, IR.TOL, CR.TOLER, XANDRNORM, CARRIERS)': [r'METHOD\s+statement', r'MAXTRAPS', r'XANDRNORM', r'CR\.TOL'],
    'SOLVE (INIT, VSTEP, VFINAL, NAME)': [r'SOLVE\s+statement', r'VFINAL'], 'LOG / SAVE / PROBE / OUTPUT / EXTRACT': [r'PROBE\s+statement', r'LOG\s+statement'],
    'Constant low-field mobility temperature dependence (TMUN)': [r'TMUN'], 'Continuous defect DOS model (tail + Gaussian)': [r'exponential tail', r'Gaussian distribution'],
    'Fermi-Dirac statistics': [r'Fermi-Dirac statistics'], 'Contact resistance (lumped, ohm.um in 2D)': [r'lumped resistance|RESISTANCE'],
}

def printed_page(txt):
    m0 = re.match(r'\s*(\d{1,4})\s+Atlas User', txt)
    if m0: return m0.group(1)
    m = re.search(r'(?m)^\s*(\d{1,2}-\d{1,4})\s*$', txt[-400:]) or re.search(r'(\d{1,2}-\d{1,4})\s*$', txt.strip()[-60:]) or re.search(r'(?m)^\s*(\d{1,2}-\d{1,4})\s', txt[:200])
    return m.group(1) if m else ''

def atlas_manual():
    pdf = Path(r'C:\sedatools\lib\atlas\5.28.1.R\docs\atlas_users1.pdf'); cache = REPORT / 'tools' / 'atlas_manual_fulltext.json'
    if cache.exists(): pages = json.loads(cache.read_text(encoding='utf-8'))
    else:
        from pypdf import PdfReader
        rd = PdfReader(str(pdf)); pages = []
        for i, p in enumerate(rd.pages, 1):
            try: pages.append(p.extract_text() or '')
            except Exception: pages.append('')
        cache.write_text(json.dumps(pages), encoding='utf-8')
    out = ['# ATLAS 5.28.1.R user manual: pages for the statements/parameters used by the decks\n',
           'PDF page -> printed page (from the page footer/header when detectable). Cite \\citep[p.~<printed>]{AtlasManual}; verify the text.\n']
    for name, pats in STATEMENTS.items():
        out.append(f'\n## {name}\n')
        hits = []
        for i, t in enumerate(pages, 1):
            score = sum(len(re.findall(p, t)) for p in pats)
            head = re.match(r'([A-Z.]+)', name).group(1).split('.')[0]
            if re.search(rf'(?m)^{head}\s+Statements?\b', t[:300]): score += 50   # statement-reference chapter page
            if score: hits.append((score, i))
        for score, i in sorted(hits, reverse=True)[:6]:
            t = pages[i - 1]; pp = printed_page(t)
            m = re.search(pats[0], t) or re.search(pats[-1], t); a = max(0, (m.start() if m else 0) - 300)
            out.append(f'\n### PDF page {i} (printed {pp or "not detected"}), score {score}\n\n```\n{t[a:a + 1500]}\n```\n')
    (DIG / 'atlas_manual_pages.md').write_text(''.join(out), encoding='utf-8')
    return len(pages)

def fixed_ss(vg, i, lo, hi):
    ok = i > 0
    if ok.sum() < 3: return None
    li, v = np.log10(i[ok]), vg[ok]
    def vat(x):
        idx = np.where((li[:-1] < x) & (li[1:] >= x))[0]
        if not len(idx): return None
        k = idx[0]; return v[k] + (x - li[k]) * (v[k + 1] - v[k]) / (li[k + 1] - li[k])
    a, b = vat(np.log10(lo)), vat(np.log10(hi))
    return None if a is None or b is None else 1000 * (b - a) / np.log10(hi / lo)

def category(label):
    L = label.lower()
    for k, c in [('pred_idvd', 'prediction ID-VD'), ('pred_t', 'prediction temperature'), ('recal', 'DOS 384/192 recalibration'), ('check', 'numerical check'),
                 ('sens_wf', 'isolation (WF)'), ('sens_mstar', 'isolation (m*)'), ('sens_no_conf', 'counterfactual (no confinement)'), ('sens', 'one-at-a-time sensitivity'),
                 ('hyp', '6.3 nm hypothesis'), ('validation', 'validation (held-out 6.3 nm)'), ('prediction', 'validation (held-out 6.3 nm)'), ('tuned', 'device-specific tuning'),
                 ('backsheet', '31.8 nm hypothesis'), ('stage', 'calibration stage'), ('final', 'final calibrated (DOS 96/48)'), ('baseline', 'baseline laws')]:
        if k in L: return c
    return 'other'

def runs():
    idx = {}
    for r in csv.DictReader((PKG / 'results' / 'RUN_INDEX.csv').open(encoding='utf-8')): idx[r['run_id']] = r
    meas = {}
    for r in csv.DictReader((PKG / 'data' / 'experimental_clean.csv').open(encoding='utf-8')): meas.setdefault(float(r['thickness_nm']), []).append((float(r['vg_V']), float(r['id_A_per_um'])))
    rows = []
    for d in sorted((PKG / 'results' / 'runs').glob('run_*')):
        rid = d.name[:8]; ex = json.loads((d / 'execution.json').read_text()) if (d / 'execution.json').exists() else {}
        r = idx.get(rid, {}); sim = ex.get('device_metrics_sim', {}); fm = ex.get('fit_metrics', {})
        row = {'run_id': rid, 'dir': d.name, 'film_nm': ex.get('thickness_nm', r.get('thickness_nm')), 'label': ex.get('label', r.get('label')), 'category': category(ex.get('label', r.get('label', ''))),
               'status': ex.get('status', 'NO_EXECUTION_JSON'), 'overrides': ' ; '.join(ex.get('overrides', [])), 'elapsed_s': round(ex.get('elapsed_s', 0) or 0, 1),
               'Vth_cc_V': sim.get('Vth_cc_1e-9_V'), 'Vth_lin_V': sim.get('Vth_lin_V'), 'SS_min_mVdec': sim.get('SS_min_window_mV_dec'), 'SS_cc_mVdec': sim.get('SS_cc_1e-10_1e-8_mV_dec'),
               'gm_max_A_V_um': sim.get('gm_max_A_V_um'), 'mu_FE_cm2Vs': sim.get('mu_FE_cm2Vs'), 'Ion_A_um': sim.get('Ion_A_per_um'),
               'active_rmse_dec': fm.get('regions', {}).get('active', {}).get('rmse_log10'), 'Id3V_err_pct': fm.get('on_error_3V_percent'), 'max_kcl_A': ex.get('validation', {}).get('max_kcl_abs_A'),
               'SS_1e-11_1e-10': None, 'SS_1e-10_1e-9': None, 'note': ''}
        c = d / 'comparison.csv'
        if c.exists():
            a = np.array([[float(x['vg_V']), float(x['atlas_A_per_um'])] for x in csv.DictReader(c.open())])
            row['SS_1e-11_1e-10'] = fixed_ss(a[:, 0], a[:, 1], 1e-11, 1e-10); row['SS_1e-10_1e-9'] = fixed_ss(a[:, 0], a[:, 1], 1e-10, 1e-9)
        if rid == 'run_0027': row['note'] = 'MALFORMED: x.mesh ends at 24 um, drain collapsed; overlap result retracted (S5)'
        if rid in ('run_0010',): row['note'] = 'aborted in SOLVE INIT, no currents'
        if rid in ('run_0011',): row['note'] = 'stopped with the chain; no currents'
        if rid in ('run_0018',): row['note'] = 'timed out at 900 s; rerun as run_0028'
        if ex.get('mode') == 'output_prediction': row['note'] = 'ID-VD prediction; output_characteristics.csv'
        if 'temp=3' in row['overrides']: row['note'] = 'elevated T; ATLAS tmu=1.5 applied (P-phonon as simulated)'
        rows.append(row)
    for t, pts in meas.items():
        a = np.array(sorted(pts)); rows.append({'run_id': f'MEASURED_{t:g}nm', 'dir': 'data/experimental_clean.csv', 'film_nm': t, 'label': 'measured', 'category': 'data', 'status': 'DATA',
            'SS_1e-11_1e-10': fixed_ss(a[:, 0], a[:, 1], 1e-11, 1e-10), 'SS_1e-10_1e-9': fixed_ss(a[:, 0], a[:, 1], 1e-10, 1e-9)})
    keys = list(rows[0].keys())
    with (DIG / 'runs.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
        for r in rows: w.writerow({k: (f'{v:.6g}' if isinstance(v, float) else v) for k, v in r.items()})
    return len(rows)

def numbers():
    out = ['# Key-number lines (file:line) from the 2026-09-25 analysis. Quote numbers from here with their source.\n']
    for f in ['SYNTHESIS.md', 'S1_electrostatics_6p3nm.md', 'S2_transport_mobility_powerlaw.md', 'S3_quantum_confinement.md', 'S4_defects_traps.md',
              'S5_contacts_experimental_validation.md', 'S6_tcad_numerics_predictions.md', 'REVIEW.md', 'PREDICTIONS_REGISTER.md', 'EVIDENCE_BRIEF.md']:
        out.append(f'\n## {f}\n')
        for i, line in enumerate((ANA / f).read_text(encoding='utf-8', errors='replace').splitlines(), 1):
            if re.search(r'\d', line) and (line.startswith('|') or re.search(r'run_\d{4}|\be1\d|e1[0-9]|mV|meV| V\b|%|cm', line)) and len(line) < 700 and not line.startswith('| `'):
                out.append(f'- {f}:{i}: {line.strip()}')
    (DIG / 'numbers.md').write_text('\n'.join(out) + '\n', encoding='utf-8')

if __name__ == '__main__':
    DIG.mkdir(exist_ok=True)
    papers(); used_items(); n = runs(); numbers(); m = atlas_manual()
    print('digest built:', {p.name: p.stat().st_size for p in DIG.rglob('*') if p.is_file() and p.parent == DIG}, 'runs rows', n, 'manual pages', m)
