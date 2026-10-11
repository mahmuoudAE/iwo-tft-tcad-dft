"""V3 model file check (NO simulator call). For every planned_fixed entry of campaign_matrix.json (written for
IWO_MODEL_FILE=config/iwo_material_model_v2.yaml), build the deck with V2 + overrides and with V3 + the same overrides and
require identical solver statements (non-comment lines). Only header comments (labels / sources) may differ.
Also checks the S0 stop-rule header values of S0-01 (chi 4.0184 eV, NC300 1.373e19, MUN 12.977, Qf 1.383e12) and that a
V3 deck WITHOUT overrides reproduces the matrix start values at 2.0 / 6.3 / 13.2 nm.
  python analysis_2026-10-10_campaign/check_v3_equivalence.py"""
import re
import sys

import campaign_tools as ct


def main():
    mx = ct.matrix(); bad = 0; n = 0; comment_only = 0
    for r in mx['runs']:
        if r['status'] != 'planned_fixed': continue
        e = r['campaign_entry']; n += 1
        t2, _ = ct.entry_deck(e, ct.V2); t3, _ = ct.entry_deck(e, ct.V3)
        if ct.statements(t2) != ct.statements(t3):
            bad += 1; print(f'{e["id"]}: SOLVER STATEMENTS DIFFER')
            import difflib
            print('\n'.join(list(difflib.unified_diff(ct.statements(t2), ct.statements(t3), lineterm='', n=0))[:12]))
        elif t2 != t3: comment_only += 1
    print(f'planned_fixed entries {n}: identical solver statements V2 vs V3 {n - bad}; differing {bad}; header-comment-only differences {comment_only}')
    # S0 stop rule: S0-01 deck header values
    s01 = next(r for r in mx['runs'] if r['id'] == 'S0-01')['campaign_entry']
    txt, meta = ct.entry_deck(s01, ct.V3); mat = meta['material']
    want = {'chi_eV': 4.0184, 'Nc_cm3': 1.373e19, 'mu0': 12.977, 'Qf_cm2': 1.383e12}
    got = {'chi_eV': mat['chi_eV'], 'Nc_cm3': mat['Nc_cm3'], 'mu0': mat['mu0'], 'Qf_cm2': mat['Qf_cm2']}
    ok = all(abs(got[k] / want[k] - 1) < 5e-4 for k in want)
    print('S0-01 header values', {k: f'{v:.6g}' for k, v in got.items()}, 'vs', want, '->', 'OK' if ok else 'MISMATCH')
    for line in ('affinity=', 'nc300=', ' mun=', 'interface qf='):
        print('   deck:', next(l.strip() for l in txt.splitlines() if line in l and not l.startswith('#')))
    # V3 with no override = the matrix start values (DFT fit3 laws, Ns/t, constant Nd, shared law) at the three films
    for key, t in (('2p0', 2.0), ('6p3', 6.3), ('13p2', 13.2)):
        _, meta = ct.entry_deck({'id': f'V3-{key}', 'thickness': t, 'overrides': []}, ct.V3); mat = meta['material']; d = mx['derived_per_film'][key]
        pairs = {'affinity_eV': mat['chi_eV'], 'mstar_m0': mat['mstar_m0'], 'Nt_cm3': mat['Nt_cm3'], 'Nd_cm3': mat['Nd_cm3'], 'MUN_cm2Vs': mat['mu0'], 'Nc300_3d_cm3': mat['Nc_cm3'], 'Qf_cm2': mat['Qf_cm2']}
        dev = {k: abs(v / d[k] - 1) for k, v in pairs.items()}
        print(f'V3 no-override {t:>4} nm: max relative deviation from matrix derived_per_film {max(dev.values()):.1e} ({max(dev, key=dev.get)})')
        bad += max(dev.values()) > 5e-4
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
