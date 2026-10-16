"""Tests for s6s7_plans.py (register A58). Reads the pinned inputs only (matrix, S4c record / plan, templates, configs); builds
decks in memory (no ATLAS, no run directory, no sealed file opened, nothing written).

    $env:IWO_MODEL_FILE = "config/iwo_material_model_v3.yaml"; python -I -B analysis_2026-10-10_campaign/test_s6s7_plans.py
"""
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import s6s7_plans as P   # noqa: E402

RES = []


def expect(name, got, want):
    ok = got == want; RES.append(ok); print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  got {got!r} want {want!r}'))


def refuses(name, fn):
    try: fn(); ok = False
    except SystemExit: ok = True
    RES.append(ok); print(('PASS ' if ok else 'FAIL ') + name)


def main():
    # unit: override editing
    ov = ['a.b=1', 'c.d[2.0]=3']
    expect('replace exactly one', P.replace(ov, 'a.b', '2'), ['a.b=2', 'c.d[2.0]=3'])
    refuses('replace a missing key refused', lambda: P.replace(ov, 'x', '1'))
    refuses('replace a doubled key refused', lambda: P.replace(ov + ['a.b=5'], 'a.b', '2'))
    refuses('append an existing key refused', lambda: P.append(ov, 'a.b', '2'))
    expect('append a new key at the end', P.append(ov, 'e', '0')[-1], 'e=0')
    expect('drop exactly one', P.drop(ov, 'a.b'), ['c.d[2.0]=3'])
    expect('fkey', [P.fkey(2), P.fkey(6.3), P.fkey(13.2), P.fkey(31.8)], ['2.0', '6.3', '13.2', '31.8'])
    expect('mass law reproduces the matrix V2 mass at 2.0 nm', round(P.mstar(0.11116, 1.26387, 2.0, 0.208), 5), 0.25429)
    expect('mu law: m_ref / m* factor and 1 + ell / t', round(P.mu_law(100.0, 10.0, 10.0, 0.25, 0.2), 6), 40.0)
    d = P.seal({'x': 1}); expect('seal round trip', P.seal_ok(d), True); d['x'] = 2; expect('seal detects a change', P.seal_ok(d), False)

    # registered set and order
    ids = P.order()
    expect('22 S6 + 2 S7 entries, each once', (len(ids), len(set(ids))), (24, 24))
    expect('kept out S6-16..19, S6-27 absent', sorted(set(ids) & set(P.KEPT_OUT)), [])
    expect('S6 core (12) before every S6 extra, S7 last', (ids[:12] == [i for i in ids if i in P.CORE], ids[-2:]), (True, ['S7-01', 'S7-02']))
    expect('extras in the PA-19 v3 allocation order K14 .. K5', ids[12:22],
           ['S6-07', 'S6-09', 'S6-08', 'S6-10', 'S6-12', 'S6-22', 'S6-20', 'S6-21', 'S6-14', 'S6-11'])
    expect('batches of at most 3', max(len(b) for _, b in P.BATCHES), 3)

    if os.environ.get('IWO_MODEL_FILE') != P.MODEL_ENV:
        print('FAIL IWO_MODEL_FILE must be set for the integration part'); RES.append(False)
    else:
        rec = P.build_record(); base = rec['frozen_model']['base_overrides']; E = rec['entries']
        expect('record sealed; S4c seal bound', (P.seal_ok(rec), rec['s4c_record_seal']), (True, P.S4C_SEAL))
        expect('deterministic (two builds equal)', P.build_record()['sha256'], rec['sha256'])
        mx = {r['id']: r for r in json.loads((P.HERE / 'campaign_matrix.json').read_text())['runs']}
        expect('labels, films and timeouts == matrix', all(E[i]['label'] == mx[i]['campaign_entry']['label'] and E[i]['thickness'] == mx[i]['film_nm']
                                                          and E[i]['timeout'] == mx[i]['timeout_s'] for i in ids), True)
        def delta(i):
            b = base[P.fkey(E[i]['thickness'])] if E[i]['thickness'] != 31.8 else base['13.2']
            return sorted(P.key_of(o) for o in set(E[i]['overrides']) ^ set(b))
        expect('S6-01 changes only the dEc point', delta('S6-01'), ['thickness_laws.dEc_eV.points[2.0]'])
        expect('S6-05 changes only the two law amplitudes', delta('S6-05'), ['thickness_laws.dEc_eV.a', 'thickness_laws.dEc_eV.a',
                                                                              'thickness_laws.dEg_QC_eV.a', 'thickness_laws.dEg_QC_eV.a'])
        expect('S6-07 changes m_bulk, mu_band[2.0] and NC[2.0] only', sorted(set(delta('S6-07'))),
               ['bulk_reference.mstar_bulk_m0.value', 'solver.physics_options.nc300_override_cm3[2.0]', 'thickness_laws.mu0_cm2Vs.mu_band_fitted[2.0]'])
        expect('S6-08 (6.3 nm) has no NC override', any('nc300_override' in o for o in E['S6-08']['overrides']), False)
        r7 = rec['derived']['S6-07']
        expect('S6-07 NC300 scales with m*', round(r7['nc300_q2d_cm3'] / 1.373e19, 6), round(r7['mstar_new_m0'] / r7['mstar_old_m0'], 6))
        expect('S6-07..09 mu_band ratio == (0.159 / m*\') / (0.208 / m*)', all(abs(rec['derived'][i]['mu_band_new_cm2Vs'] / rec['derived'][i]['mu_band_old_cm2Vs']
                                                                                - (0.159 / rec['derived'][i]['mstar_new_m0']) / (0.208 / rec['derived'][i]['mstar_old_m0'])) < 1e-12
                                                                            for i in ('S6-07', 'S6-08', 'S6-09')), True)
        expect('S6-13 / S6-15 N_D x10 only', (delta('S6-13'), delta('S6-15')), (['thickness_laws.Nd_eff_cm3.Nd0'] * 2, ['thickness_laws.Nd_eff_cm3.Nd0'] * 2))
        expect('S6-22 zeroes the two trap terms only', delta('S6-22'), ['traps.bulk_deep_acceptor_gaussian.NGA_cm3_eV', 'traps.interface_acceptor_sheet.peak_cm2_eV'])
        expect('S6-23 adds the 6.3 nm NC override 3.769e+18', [o for o in E['S6-23']['overrides'] if 'nc300_override_cm3[6.3]' in o],
               ['solver.physics_options.nc300_override_cm3[6.3]=3.769e+18'])
        expect('S6-24..26 strip mode with L_p 20 um', all(E[i].get('mode') == 'strip' and 'solver.physics_options.strip.L_p_um=20' in E[i]['overrides']
                                                          for i in ('S6-24', 'S6-25', 'S6-26')), True)
        expect('only strips carry a mode', sorted(i for i in ids if 'mode' in E[i]), ['S6-24', 'S6-25', 'S6-26'])
        s7 = E['S7-01']['overrides']
        expect('S7: no film-keyed mu_band / NC of the calibration films', [o for o in s7 if 'mu_band_fitted' in o or 'nc300_override' in o],
               [])
        expect('S7: shared law at the S4c mu_inf / ell, then R_sd 0 (last three)', s7[-3:],
               ['thickness_laws.mu0_cm2Vs.shared_law.mu_inf_cm2Vs=248.36', 'thickness_laws.mu0_cm2Vs.shared_law.ell_nm=50', 'contacts.series_resistance_ohm_um[31.8]=0'])
        expect('S7: R_sd 31.8 set to 0', 'contacts.series_resistance_ohm_um[31.8]=0' in s7 and 'contacts.series_resistance_ohm_um[31.8]=0' in E['S7-02']['overrides'], True)
        expect('S7-02 N_D 2.5e18', 'thickness_laws.Nd_eff_cm3.Nd0=2.5e+18' in E['S7-02']['overrides'], True)
        expect('dry build: every entry has a deck and a material sha256', all(len(rec['dry_build'][i]['deck_sha256']) == 64 for i in ids), True)
        expect('dry build: decks pairwise distinct', len({rec['dry_build'][i]['deck_sha256'] for i in ids}), 24)
        ps = P.plans(rec)
        expect('plans: one per batch, runnable, record seal bound', all(p['runnable'] is True and p['variable_reference']['sha256'] == rec['sha256']
                                                                         and [e['id'] for e in p['runs']] == dict(P.BATCHES)[s] for s, p in ps.items()), True)
        expect('plans: no gates, not state-only', any('gates' in p or 'state_only' in p for p in ps.values()), False)
        expect('S7 31.8 nm deck has no contact resistance statement', 'con.resist' in __import__('run_campaign').current_deck_text(E['S7-01'], s7).lower()
               if str(P.PKG / 'scripts') in sys.path else None, False)
    n = sum(RES); print(f'{n}/{len(RES)} passed'); return 0 if n == len(RES) else 1


if __name__ == '__main__':
    os.chdir(P.PKG); sys.exit(main())
