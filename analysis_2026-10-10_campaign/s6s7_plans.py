"""S6 / S7 execution entries (register A59, 2026-10-16; no Codex review, D-63). NO launch; nothing sealed is opened.

Resolves the matrix S6 / S7 template entries (campaign_matrix.json, stages S6_sensitivity_frozen and S7_31p8_stress) at the
FROZEN MODEL = the S4c-confirmed point (register A52: S4A-04 at the profiled Q_f, mu_inf, ell; S4c PASS, s4c_confirm_A52.json):
the per-film S4c launch overrides of config/campaign_C10_S4c.json are the base; each entry changes only the registered keys
(rules below). Writes the sealed record profile/s6s7_record_A59.json (entries, derived values, dry-built deck / material text
sha256) and the route plans config/campaign_C10_S6_b1..b8.json and config/campaign_C10_S7.json (registered batch order).

    python -I -B analysis_2026-10-10_campaign/s6s7_plans.py build    # writes record + plans (refuses to change an existing file)
    python -I -B analysis_2026-10-10_campaign/s6s7_plans.py check    # recomputes in memory; exit 0 iff every file is equal

Run with IWO_MODEL_FILE=config/iwo_material_model_v3.yaml from the package root (the dry build imports scripts/run_campaign.py).

Resolution rules (A59 (b)); film keys '2.0', '6.3', '13.2'; every value from the matrix entry params unless stated:
  S6-01..03  confinement low: append thickness_laws.dEc_eV.points[t] = params dEc_eV (box MODEL); dEg unchanged (matrix).
  S6-04..06  confinement high (HSE x1.107): replace thickness_laws.dEc_eV.a and dEg_QC_eV.a by the template values; the law at t
             must equal params dEc_eV / dEg_eV to 1e-4 eV.
  S6-07..09  bulk mass 0.159 (PBE): append bulk_reference.mstar_bulk_m0.value=0.159; m*'(t) = 0.159 + b t^-q (b, q of the frozen
             model) must equal params mstar_m0 to 1e-4; mu_band_fitted[t] replaced by mu_inf (0.159 / m*'(t)) / (1 + ell / t) with the
             S4c native mu_inf, ell (the frozen law with m_ref = m_bulk; the frozen value must be reproduced at m_ref 0.208 to 1e-5
             relative); at 2.0 nm nc300_override_cm3[2.0] replaced by 1.373e19 x m*'(2.0) / m*(2.0) (N2D/t is linear in m*); at 6.3 /
             13.2 nm NC300 follows m*' through the 3-D formula of the builder.
  S6-10..15  N_D: replace thickness_laws.Nd_eff_cm3.Nd0 by params Nd_cm3.
  S6-20..22  append traps.bulk_deep_acceptor_gaussian.NGA_cm3_eV=0 and traps.interface_acceptor_sheet.peak_cm2_eV=0.
  S6-23      append solver.physics_options.nc300_override_cm3[6.3] = params Nc300_cm3 (box MODEL x1.467).
  S6-24..26  frozen ungated strip: mode strip, append solver.physics_options.strip.L_p_um=20 (as S2-14..17 / STRIP-6p3).
  S7-01/02   31.8 nm: the film-independent frozen overrides (S4C-13p2 without its mu_band_fitted[13.2]), the shared law at the
             S4c native mu_inf, ell (thickness_laws.mu0_cm2Vs.shared_law.mu_inf_cm2Vs / ell_nm; m_ref 0.208 unchanged), then
             contacts.series_resistance_ohm_um[31.8]=0 and Nd0 = params Nd_cm3 (template order).
  Kept out (register section 3, PA-19 v3 K0): S6-16..19, S6-27.
"""
import hashlib
import json
import math
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

PKG = Path(r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1")
HERE = PKG / 'analysis_2026-10-10_campaign'
CFG = PKG / 'config'
RECORD_REL = 'analysis_2026-10-10_campaign/profile/s6s7_record_A59.json'
MODEL_ENV = 'config/iwo_material_model_v3.yaml'
S4C_SEAL = 'd49ab722714eb294d46fc9458e2b781e353487e7853f9e6359873b4bfecac1fd'   # A52 variable reference (record seal)
PINS = {'analysis_2026-10-10_campaign/campaign_matrix.json': 'f06e8d7721f75aec3f78da06de1c1686c59307c33725bd8822c3ec3e0f0a443c',
        'analysis_2026-10-10_campaign/profile/s4c_record_A52.json': '821867bcd6751da22dfc1be3501f119338ed50ed85119b745c8709370284255a',
        'analysis_2026-10-10_campaign/profile/s4c_confirm_A52.json': '91d0f3cb18307d313b994220de57a4bd46d07410c29912807f1354aa09140b3f',
        'analysis_2026-10-10_campaign/profile_shared.py': '958c3605a316393184f022a80c421505e8b9f99a1d214423ec79b83286209d17',
        'config/campaign_C10_S4c.json': '0809527954bc97be56667c8a151837ae4f61c474a9307599962f55eb049dc0e4',
        'config/campaign_C10_S6_sensitivity.template.json': '02f2096ad1106479916cf502681b40340a5341da1303a80dfe33091c6542abcb',
        'config/campaign_C10_S7_31p8.template.json': 'e1e33f221ab7db7757ab73319acaa757d78bd34997bdcabfaf580e3937af6ef1',
        'config/iwo_material_model_v3.yaml': '51b184e8728c4e4ce5ed4110c56d4b1083b5d12f1d4d6b45aef52816ba63961c',
        'config/solver.yaml': 'd5a9101219d1238923da096766443fd021751fad1a9f55770b3851301481d583',
        'scripts/build_iwo_decks.py': '734125a8915e2a7790b2794db0c7bf429c477a83238b638a200af2b5fbeeca3c',
        'scripts/run_atlas.py': 'b7927ac5b9747d5531ac827d220da6004e4a144d672ae16ab9bca2a28f46e6ae',
        'scripts/run_campaign.py': 'fb6e802f8c1cb71b56e153ed99504cc8e7e83d4c8eb7af8f13dc421d0fd125ac'}
S4C_ID = {2.0: 'S4C-2p0', 6.3: 'S4C-6p3', 13.2: 'S4C-13p2'}
BATCHES = [('campaign_C10_S6_b1', ['S6-01', 'S6-02', 'S6-03']),          # S6 core (never cut): confinement low
           ('campaign_C10_S6_b2', ['S6-04', 'S6-05', 'S6-06']),          # confinement high
           ('campaign_C10_S6_b3', ['S6-13', 'S6-15', 'S6-23']),          # N_D x10 pair, NC 6.3 nm box
           ('campaign_C10_S6_b4', ['S6-24', 'S6-25', 'S6-26']),          # frozen strips
           ('campaign_C10_S6_b5', ['S6-07', 'S6-09', 'S6-08']),          # S6 extras in PA-19 allocation order K14, K13, K12 ...
           ('campaign_C10_S6_b6', ['S6-10', 'S6-12', 'S6-22']),          # K11, K10, K9
           ('campaign_C10_S6_b7', ['S6-20', 'S6-21', 'S6-14']),          # K8, K7, K6
           ('campaign_C10_S6_b8', ['S6-11']),                            # K5
           ('campaign_C10_S7', ['S7-01', 'S7-02'])]                      # S7 (never cut), after S6 (register order)
KEPT_OUT = ['S6-16', 'S6-17', 'S6-18', 'S6-19', 'S6-27']
CORE = ['S6-01', 'S6-02', 'S6-03', 'S6-04', 'S6-05', 'S6-06', 'S6-13', 'S6-15', 'S6-23', 'S6-24', 'S6-25', 'S6-26']
M_BULK, M_BULK_S6, NC_Q2D_2P0 = 0.208, 0.159, 1.373e19
TEMPLATES = {'S6': 'config/campaign_C10_S6_sensitivity.template.json', 'S7': 'config/campaign_C10_S7_31p8.template.json'}
AMENDMENT = ('A59 (2026-10-16; S6 / S7 execution entries resolved at the S4c frozen model, PA-19 v3 section 4 allocation at the S5 -> S6 '
             'point, J gate; no Codex review, D-63): invoke only after A59 and its decision row are logged and the sealed record is committed, '
             'with the go for THIS launch (the hook asks the user), immediately after prelaunch_gate_c10_j.py has exited 0 naming this plan')
ENFORCED = 'main session (manual); run_campaign.py enforces the launch budget and C10 cap and refuses runnable=false plans; no gates'
LAST_RULE = ('run_campaign.py records a failed launch and CONTINUES (this plan declares no gates); it stops automatically only at the launch '
             'budget / C10 cap. S6 / S7 have no stop rule (CAMPAIGN_DESIGN l.334-336): every result is reported; a failed launch is kept, '
             'never retried automatically (a repair only from the reserved six by a logged decision). Until the A59 read-out, the console '
             'and RUN_INDEX are read for state fields only (id, run_id, status, error; exit_code, converged, elapsed_s).')


def fsha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tsha(s): return hashlib.sha256(s.encode()).hexdigest()


def _canon(d): return json.dumps(d, sort_keys=True, default=float, separators=(',', ':'))


def seal(d):
    d = {k: v for k, v in d.items() if k != 'sha256'}; d['sha256'] = tsha(_canon(d)); return d


def seal_ok(d): return isinstance(d, dict) and d.get('sha256') == tsha(_canon({k: v for k, v in d.items() if k != 'sha256'}))


def fkey(t): return f'{float(t):.1f}'


def pin_problems():
    return [f'{f} sha256 differs (pinned {h[:8]})' for f, h in PINS.items() if not (PKG / f).is_file() or fsha(PKG / f) != h]


# ------------------------------------------------------------------ override editing (exact, refusing)
def key_of(o): return o.split('=', 1)[0]


def replace(ov, key, value):
    idx = [i for i, o in enumerate(ov) if key_of(o) == key]
    if len(idx) != 1: raise SystemExit(f'replace {key}: {len(idx)} matching overrides (exactly one required)')
    out = list(ov); out[idx[0]] = f'{key}={value}'; return out


def append(ov, key, value):
    if any(key_of(o) == key for o in ov): raise SystemExit(f'append {key}: already set')
    return list(ov) + [f'{key}={value}']


def drop(ov, key):
    idx = [i for i, o in enumerate(ov) if key_of(o) == key]
    if len(idx) != 1: raise SystemExit(f'drop {key}: {len(idx)} matching overrides (exactly one required)')
    return [o for i, o in enumerate(ov) if i != idx[0]]


def get(ov, key):
    v = [o.split('=', 1)[1] for o in ov if key_of(o) == key]
    if len(v) != 1: raise SystemExit(f'get {key}: {len(v)} matching overrides')
    return float(v[0])


def mstar(b, q, t, m_bulk): return m_bulk + b * t ** (-q)


def mu_law(mu_inf, ell, t, ms, m_ref): return mu_inf * (m_ref / ms) / (1.0 + ell / t)


def g6(x): return f'{x:.6g}'


def g4(x): return f'{x:.4g}'


# ------------------------------------------------------------------ inputs
def inputs():
    bad = pin_problems()
    if bad: raise SystemExit('pins: ' + '; '.join(bad))
    rec = json.loads((HERE / 'profile' / 's4c_record_A52.json').read_text())
    if rec.get('sha256') != S4C_SEAL or not seal_ok(rec): raise SystemExit('S4c record seal differs from the A52 variable reference')
    conf = json.loads((HERE / 'profile' / 's4c_confirm_A52.json').read_text())
    if not str(conf.get('verdict', '')).startswith('PASS'): raise SystemExit('S4c verdict is not PASS')
    s4c = {e['id']: e for e in json.loads((CFG / 'campaign_C10_S4c.json').read_text())['runs']}
    base = {t: list(s4c[i]['overrides']) for t, i in S4C_ID.items()}
    nlv = rec['native_launch_values']
    for t in S4C_ID:   # the S4c plan carries exactly the record's written variables
        for o in nlv['per_film'][fkey(t)]['overrides']:
            if o not in base[t]: raise SystemExit(f'S4c plan {S4C_ID[t]} lacks the record override {o}')
    mx = {r['id']: r for r in json.loads((HERE / 'campaign_matrix.json').read_text())['runs']}
    tpl = {}
    for f in TEMPLATES.values():
        for e in json.loads((PKG / f).read_text())['runs']: tpl[e['id']] = e
    return rec, base, mx, tpl


# ------------------------------------------------------------------ resolution
def resolve(i, rec, base, mx, tpl):
    """(entry, derived) for one registered id"""
    m = mx[i]; t = float(m['film_nm']); p = m['params']; e = tpl[i]; derived = {}
    nlv = rec['native_launch_values']; mu_inf, ell = float(nlv['mu_inf_cm2Vs']), float(nlv['ell_nm'])
    if e['label'] != m['campaign_entry']['label'] or float(e['thickness']) != t or int(e['timeout']) != int(m['timeout_s']):
        raise SystemExit(f'{i}: template and matrix differ (label / thickness / timeout)')
    n = int(i.split('-')[1]); mode = None
    if i.startswith('S7'):
        ov = drop(base[13.2], 'thickness_laws.mu0_cm2Vs.mu_band_fitted[13.2]')
        ov = append(ov, 'thickness_laws.mu0_cm2Vs.shared_law.mu_inf_cm2Vs', g6(mu_inf))
        ov = append(ov, 'thickness_laws.mu0_cm2Vs.shared_law.ell_nm', g6(ell))
        ov = append(ov, 'contacts.series_resistance_ohm_um[31.8]', '0')
        ov = replace(ov, 'thickness_laws.Nd_eff_cm3.Nd0', f'{float(p["Nd_cm3"]):g}')
        b, q = get(ov, 'thickness_laws.mstar_m0.b'), get(ov, 'thickness_laws.mstar_m0.q'); ms = mstar(b, q, t, M_BULK)
        derived = {'mstar_m0': ms, 'mu_band_cm2Vs_shared_law': mu_law(float(g6(mu_inf)), float(g6(ell)), t, ms, M_BULK)}
        rule = 'S7: frozen model (film-independent S4c overrides), shared law at the S4c mu_inf / ell, R_sd 0, N_D as the matrix entry'
    else:
        ov = list(base[t]); tail = e['overrides'][0].split('{frozen model} + ', 1)[1] if len(e['overrides']) == 1 else None
        if tail is None: raise SystemExit(f'{i}: template override is not "{{frozen model}} + ..."')
        if 1 <= n <= 3:
            ov = append(ov, f'thickness_laws.dEc_eV.points[{fkey(t)}]', f'{float(p["dEc_eV"]):g}')
            rule = 'S6 confinement low: dEc point (box MODEL) appended'
        elif 4 <= n <= 6:
            for item in tail.split('; '):
                k, v = item.split('=', 1); ov = replace(ov, k, v)
            dec = get(ov, 'thickness_laws.dEc_eV.a') * t ** (-get(ov, 'thickness_laws.dEc_eV.p'))
            deg = get(ov, 'thickness_laws.dEg_QC_eV.a') * t ** (-get(ov, 'thickness_laws.dEg_QC_eV.p'))
            if abs(dec - p['dEc_eV']) > 1e-4 or abs(deg - p['dEg_eV']) > 1e-4: raise SystemExit(f'{i}: HSE law {dec:.5f}/{deg:.5f} != matrix {p}')
            derived = {'dEc_eV': dec, 'dEg_eV': deg}; rule = 'S6 confinement high: dEc / dEg law amplitudes x1.107 (template values)'
        elif 7 <= n <= 9:
            b, q = get(ov, 'thickness_laws.mstar_m0.b'), get(ov, 'thickness_laws.mstar_m0.q')
            m_old, m_new = mstar(b, q, t, M_BULK), mstar(b, q, t, M_BULK_S6)
            if abs(m_new - p['mstar_m0']) > 1e-4: raise SystemExit(f'{i}: m* {m_new:.5f} != matrix {p["mstar_m0"]}')
            k_mu = f'thickness_laws.mu0_cm2Vs.mu_band_fitted[{fkey(t)}]'; mu_frozen = get(ov, k_mu)
            mu_old = mu_law(mu_inf, ell, t, m_old, M_BULK)
            if abs(mu_old / mu_frozen - 1.0) > 1e-5: raise SystemExit(f'{i}: frozen mu_band {mu_frozen} not reproduced ({mu_old})')
            mu_new = mu_law(mu_inf, ell, t, m_new, M_BULK_S6); ov = replace(ov, k_mu, g6(mu_new))
            derived = {'mstar_old_m0': m_old, 'mstar_new_m0': m_new, 'mu_band_old_cm2Vs': mu_old, 'mu_band_new_cm2Vs': mu_new}
            if t == 2.0:
                k_nc = 'solver.physics_options.nc300_override_cm3[2.0]'
                if get(ov, k_nc) != NC_Q2D_2P0: raise SystemExit(f'{i}: frozen NC override is not {NC_Q2D_2P0:g}')
                nc = NC_Q2D_2P0 * m_new / m_old; ov = replace(ov, k_nc, g4(nc)); derived['nc300_q2d_cm3'] = nc
            ov = append(ov, 'bulk_reference.mstar_bulk_m0.value', f'{M_BULK_S6:g}')
            rule = 'S6 bulk mass 0.159: m_bulk replaced; mu_band (law with m_ref = m_bulk) and the 2.0 nm quasi-2D NC300 recomputed'
        elif 10 <= n <= 15:
            ov = replace(ov, 'thickness_laws.Nd_eff_cm3.Nd0', f'{float(p["Nd_cm3"]):g}'); rule = 'S6 N_D: Nd0 replaced'
        elif 20 <= n <= 22:
            ov = append(ov, 'traps.bulk_deep_acceptor_gaussian.NGA_cm3_eV', '0'); ov = append(ov, 'traps.interface_acceptor_sheet.peak_cm2_eV', '0')
            rule = 'S6 trap set removed: deep Gaussian and interface acceptor sheet zero'
        elif n == 23:
            ov = append(ov, f'solver.physics_options.nc300_override_cm3[{fkey(t)}]', g4(float(p['Nc300_cm3']))); rule = 'S6 NC 6.3 nm box MODEL x1.467'
        elif 24 <= n <= 26:
            ov = append(ov, 'solver.physics_options.strip.L_p_um', '20'); mode = 'strip'; rule = 'S6 frozen ungated strip deck (L_p 20 um)'
        else:
            raise SystemExit(f'{i}: not a registered A59 entry')
    ent = {'depends_on': ['S4c'], 'id': i, 'label': e['label'], 'matrix_status': m.get('status'), 'overrides': ov,
           'params_rule': f'resolved from the sealed record {RECORD_REL} (register A59): {rule}',
           'purpose': f'{e["purpose"]} Register A59: frozen model = S4c-confirmed S4A-04 (Q_f 1.61169e12 cm^-2, mu_inf {g6(mu_inf)} cm2/Vs, ell {g6(ell)} nm).',
           'thickness': t, 'timeout': int(e['timeout'])}
    if mode: ent['mode'] = mode
    return ent, derived


def order(): return [i for _, ids in BATCHES for i in ids]


def build_record():
    rec, base, mx, tpl = inputs()
    ids = order()
    if len(ids) != len(set(ids)) or set(ids) & set(KEPT_OUT): raise SystemExit('batch order: duplicate or kept-out id')
    want = sorted(i for i in mx if mx[i]['stage'] in ('S6_sensitivity_frozen', 'S7_31p8_stress') and i not in KEPT_OUT)
    if sorted(ids) != want: raise SystemExit(f'batch order != the registered S6 / S7 set: {sorted(set(want) ^ set(ids))}')
    entries, derived = {}, {}
    for i in ids: entries[i], derived[i] = resolve(i, rec, base, mx, tpl)
    sys.path.insert(0, str(PKG / 'scripts'))
    if os.environ.get('IWO_MODEL_FILE') != MODEL_ENV: raise SystemExit(f'IWO_MODEL_FILE must be {MODEL_ENV}')
    cwd = os.getcwd(); os.chdir(PKG)
    try:
        import run_campaign as rc
        dry = {}
        for i, e in entries.items():
            deck = rc.current_deck_text(e, e['overrides'])
            if deck is None: raise SystemExit(f'{i}: no dry build for this mode')
            dry[i] = {'deck_sha256': tsha(deck), 'model_sha256': tsha(rc.current_material_text(e['overrides']))}
    finally:
        os.chdir(cwd)
    nlv = rec['native_launch_values']
    out = {'record': 'S6 / S7 execution entries (register A59): resolved at the S4c frozen model; sealed; committed before the first S6 launch',
           'generator_sha256': fsha(Path(__file__)), 'pins': PINS, 's4c_record_seal': S4C_SEAL,
           'frozen_model': {'candidate': rec['candidate'], 'Qf_cm2': nlv['Qf_cm2'], 'mu_inf_cm2Vs': nlv['mu_inf_cm2Vs'], 'ell_nm': nlv['ell_nm'],
                            'base_overrides': {fkey(t): v for t, v in base.items()}, 'qualification': rec.get('qualification')},
           'batches': [[s, ids_] for s, ids_ in BATCHES], 'kept_out': KEPT_OUT, 'core': CORE,
           'entries': entries, 'derived': derived, 'dry_build': dry,
           'labels': ('decks COMPUTED by the pinned builder (dry build); perturbation values from the matrix entries (MODEL / COMPUTED / ASSUMED as labelled '
                      'there); mu_band and NC300 for S6-07..09 CALCULATED by the stated exact rules; frozen model FITTED (S4c, calibration-conditional; '
                      'ell at the 50 nm range bound); sensitivity runs, never calibration or validation')}
    return seal(out)


def plan_of(stem, ids, record):
    tpl = json.loads((PKG / TEMPLATES['S7' if stem.endswith('S7') else 'S6']).read_text())
    rules = [r for r in tpl['global_rules'] if not r.startswith('run_campaign.py records a failed launch')] + [LAST_RULE]
    return {'campaign': stem, 'runnable': True,
            'purpose': (f'2026-10-10 DFT-informed campaign, {", ".join(ids)}. Generated by analysis_2026-10-10_campaign/s6s7_plans.py; entries resolved '
                        f'from the sealed record {RECORD_REL} (register A59).'),
            'model_file_env': f'IWO_MODEL_FILE={MODEL_ENV}', 'global_rules': rules,
            'stop_rules': [f'Register A59: {stem} runs {", ".join(ids)} in this order and stops; no stop rule (CAMPAIGN_DESIGN l.334-336). '
                           'Next batch only after prelaunch_gate_c10_j.py exits 0 naming it; no launch whose start could fall after 2026-10-16T10:00Z (A59 (f)).'],
            'stop_rules_enforced_by': ENFORCED, 'register_amendment': AMENDMENT,
            'launch_command': (f'$env:IWO_MODEL_FILE = "{MODEL_ENV}"; <project venv python> scripts/run_campaign.py config/{stem}.json *> results/{stem}_console.log   '
                               '(PowerShell, package root, immediately after prelaunch_gate_c10_j.py exited 0 naming this plan; no --retry; console read for state lines only)'),
            'variable_reference': {'record': RECORD_REL, 'sha256': record['sha256']},
            'runs': [record['entries'][i] for i in ids]}


def plans(record): return {stem: plan_of(stem, ids, record) for stem, ids in BATCHES}


def _write(path, text):
    if path.exists() and path.read_text() != text: raise SystemExit(f'{path.name} exists and differs: not overwritten')
    if not path.exists(): path.write_text(text)


def main(argv):
    if not argv or argv[0] not in ('build', 'check'): print(__doc__); return 2
    rec = build_record(); ps = plans(rec)
    rtext = json.dumps(rec, indent=1, default=float) + '\n'
    texts = {CFG / f'{s}.json': json.dumps(p, indent=1, default=float) + '\n' for s, p in ps.items()}
    if argv[0] == 'build':
        _write(PKG / RECORD_REL, rtext)
        for pth, tx in texts.items(): _write(pth, tx)
        print(json.dumps({'record': RECORD_REL, 'sha256': rec['sha256'], 'plans': list(ps), 'entries': len(rec['entries'])}, indent=1)); return 0
    bad = [str(p.relative_to(PKG)) for p, tx in [(PKG / RECORD_REL, rtext)] + list(texts.items()) if not p.is_file() or p.read_text() != tx]
    print('CHECK OK' if not bad else 'CHECK DIFFERS: ' + ', '.join(bad)); return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
