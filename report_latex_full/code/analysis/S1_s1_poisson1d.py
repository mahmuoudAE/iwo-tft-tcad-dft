"""S1 electrostatics: (A) post-processing of ATLAS depth profiles (trapped-charge budget at the cut x=12 um),
(B) 1-D Poisson + gradual-channel (Pao-Sah) surrogate of the V1 model, used ONLY for decomposition / what-if
(lever arm of a back-surface charge, neutral-layer onset, no-confinement symmetric test). It is validated against
the ATLAS runs it mimics before any use; it is NOT an ATLAS result and never replaces one.
Physics identical to the V1 deck where possible: Fermi-Dirac electrons (Nc F1/2), acceptor tail NTA exp((E-Ec)/WTA)
(integral Nt), deep acceptor Gaussian NGA exp(-((E-(Ec-EGA))/WGA)^2), interface acceptor Gaussian in the first 0.25 nm,
fully ionised Nd, front fixed sheet Qf, optional back sheet Qb at the IWO/air surface, zero field in air,
series oxide Cox = 8.955e-7 F/cm2, gate WF, constant mobility mu0, Vd = 0.7 V, L = 20 um.
Omitted vs ATLAS: 2-D top-contact access (Pd over the film), lateral fields, contact regions.
"""
import os, sys, json, glob, re
import numpy as np
from scipy.linalg import solve_banded

PKG = r"C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_PHYSICS_CONSTRAINED_MODEL_V1"
OUT = os.path.join(PKG, 'analysis_2026-09-25', 'scratch', 'S1')
RUNS = os.path.join(PKG, 'results', 'runs')
sys.path.insert(0, os.path.join(PKG, 'scripts'))
from extract_metrics import metrics

q = 1.602176634e-19; eps0 = 8.8541878128e-14; kT = 8.617333262e-5 * 300.0
COX = 8.955369814335959e-7; CQ = COX / q; L_CM = 20e-4; VD = 0.7

# ---------------- tables ----------------
_eta = np.linspace(-12, 70, 16401)
_e = np.linspace(0, 110, 22001)
_F = np.empty_like(_eta)
for i0 in range(0, len(_eta), 400):
    et = _eta[i0:i0+400, None]
    _F[i0:i0+400] = 2/np.sqrt(np.pi) * np.trapezoid(np.sqrt(_e)[None, :] / (1 + np.exp(np.clip(_e[None, :] - et, -700, 700))), _e, axis=1)
_dF = np.gradient(_F, _eta)

def F12(x):
    return np.where(x < -12, np.exp(x), np.interp(x, _eta, _F))

def dF12(x):
    return np.where(x < -12, np.exp(x), np.interp(x, _eta, _dF))

_U = np.linspace(-4.0, 1.8, 5801)
_tab = {}
def occ_table(kind, a, b, Eg=3.2):
    key = (kind, round(a, 6), round(b, 6))
    if key in _tab:
        return _tab[key]
    E = np.linspace(-Eg, 0.0, 12801)
    g = (np.exp(E / a) / a) if kind == 'tail' else np.exp(-((E + a) / b) ** 2)
    val = np.empty_like(_U)
    for i0 in range(0, len(_U), 200):
        u = _U[i0:i0+200, None]
        f = 1 / (1 + np.exp(np.clip((E[None, :] - u) / kT, -700, 700)))
        val[i0:i0+200] = np.trapezoid(g[None, :] * f, E, axis=1)
    _tab[key] = (val, np.gradient(val, _U))
    return _tab[key]

def tab_eval(tb, u):
    return np.interp(u, _U, tb[0]), np.interp(u, _U, tb[1])

# ---------------- parameters ----------------
def params_from_run(rid):
    d = glob.glob(os.path.join(RUNS, rid + '_*'))[0]
    m = json.load(open(os.path.join(d, 'metadata.json')))['material']
    dev = open(os.path.join(d, 'device.in')).read()
    qb = re.findall(r'interface qf=([-+\d.eE]+) x\.min=2 x\.max=22', dev)
    return dict(t=m['t_nm'], chi=m['chi_eV'], wf=m['gate_wf'], eps=m['eps_iwo'] * eps0, Nc=m['Nc_cm3'], Nt=m['NTA_cm3_eV'] * m['WTA_eV'],
                WTA=m['WTA_eV'], Nd=m['Nd_cm3'], NGA=m['NGA'], EGA=m['EGA'], WGA=m['WGA'], NIT=m['it_peak'] / 2.5e-8, EIT=m['it_e'],
                WIT=m['it_w'], Qf=m['Qf_cm2'], Qb=float(qb[0]) if qb else 0.0, mu=m['mu0'], Eg=m['Eg_eV'], dEc=m['dEc_eV'], mstar=m['mstar_m0'])

def law_params(t, Qf=1.73e12, mu_band=None, qc=True):
    """V1 thickness laws (config/iwo_material_model.yaml) for thicknesses without an ATLAS run (e.g. 31.8 nm)."""
    dEc = 0.9205 * t ** -1.3815 if qc else 0.0
    ms = 0.208 + (0.1311 * t ** -1.412 if qc else 0.0)
    Nc = 2.549759003818449e18 * (ms / 0.217746617029316) ** 1.5   # scaled from the 6.3 nm metadata value
    rough = (1 - 0.287 / t) ** 2
    return dict(t=t, chi=4.3 - dEc, wf=4.7, eps=9.3 * eps0, Nc=Nc, Nt=2e19 * (2 / t) ** 0.75, WTA=0.04, Nd=2.5e17 * (1 + (t / 20) ** 4),
                NGA=5e16, EGA=0.6, WGA=0.15, NIT=3e11 / 2.5e-8, EIT=0.3, WIT=0.12, Qf=Qf, Qb=0.0, mu=mu_band * rough, Eg=3.05 + dEc, dEc=dEc, mstar=ms)

def no_qc(p):
    p = dict(p); p['Nc'] = p['Nc'] * (0.208 / p['mstar']) ** 1.5; p['chi'] = 4.3; p['Eg'] = 3.05; p['dEc'] = 0.0; p['mstar'] = 0.208
    return p

# ---------------- 1-D solver ----------------
class Film:
    def __init__(self, p):
        self.p = p
        self.N = max(121, int(p['t'] / 0.04) + 1)
        self.x = np.linspace(0, p['t'] * 1e-7, self.N)
        self.h = self.x[1] - self.x[0]
        self.w = np.full(self.N, self.h); self.w[0] = self.w[-1] = self.h / 2
        self.mit = (self.x < 0.25e-7 + 1e-12).astype(float)
        self.tt = occ_table('tail', p['WTA'], 0.0)
        self.tg = occ_table('gauss', p['EGA'], p['WGA'])
        self.ti = occ_table('gauss', p['EIT'], p['WIT'])

    def charges(self, u):
        p = self.p
        n = p['Nc'] * F12(u / kT); dn = p['Nc'] * dF12(u / kT) / kT
        t0, dt0 = tab_eval(self.tt, u); g0, dg0 = tab_eval(self.tg, u); i0, di0 = tab_eval(self.ti, u)
        nt, ng, ni = p['Nt'] * t0, p['NGA'] * g0, p['NIT'] * i0 * self.mit
        rho = p['Nd'] - n - nt - ng - ni
        drho = -(dn + p['Nt'] * dt0 + p['NGA'] * dg0 + p['NIT'] * di0 * self.mit)
        return rho, drho, n, nt, ng, ni

    def solve(self, Vg, Vc, V):
        p = self.p; a = p['eps'] / q / self.h; Vgate = Vg - p['wf']
        for it in range(300):
            u = V + p['chi'] - Vc
            rho, drho = self.charges(u)[:2]
            r = np.empty(self.N)
            r[1:-1] = a * (V[2:] - 2 * V[1:-1] + V[:-2]) + rho[1:-1] * self.h
            r[0] = a * (V[1] - V[0]) + CQ * (Vgate - V[0]) + p['Qf'] + rho[0] * self.h / 2
            r[-1] = p['Qb'] - a * (V[-1] - V[-2]) + rho[-1] * self.h / 2
            ab = np.zeros((3, self.N)); ab[0, 1:] = a; ab[2, :-1] = a
            ab[1, 1:-1] = -2 * a + drho[1:-1] * self.h
            ab[1, 0] = -a - CQ + drho[0] * self.h / 2; ab[1, -1] = -a + drho[-1] * self.h / 2
            dV = solve_banded((1, 1), ab, -r)
            mx = np.max(np.abs(dV))
            if mx > 0.1:
                dV *= 0.1 / mx
            V = V + dV
            if mx < 1e-9:
                break
        return V

    def state(self, V, Vc):
        u = V + self.p['chi'] - Vc
        rho, drho, n, nt, ng, ni = self.charges(u)
        W = self.w
        return dict(u_front=u[0], u_back=u[-1], ns=np.sum(n * W), nt=np.sum(nt * W), ng=np.sum(ng * W), ni=np.sum(ni * W),
                    bend=u[0] - u[-1])

    def idvg(self, vgs, vcs=np.linspace(0, VD, 36)):
        V = np.full(self.N, vgs[0] - self.p['wf'])
        ids, st0 = [], []
        for Vg in vgs:
            V = self.solve(Vg, 0.0, V); V0 = V.copy()
            ns = [self.state(V, 0.0)['ns']]; st0.append(self.state(V, 0.0))
            Vv = V.copy()
            for Vc in vcs[1:]:
                Vv = self.solve(Vg, Vc, Vv); ns.append(self.state(Vv, Vc)['ns'])
            ids.append(q * self.p['mu'] / L_CM * np.trapezoid(ns, vcs) * 1e-4)   # A/um
            V = V0
        return np.array(ids), st0

VGS = np.round(np.arange(-1.5, 3.0001, 0.05), 4)

def run1d(p, vgs=VGS):
    f = Film(p)
    ids, st = f.idvg(vgs)
    m = metrics(vgs, ids, is_sim=True, t_nm=p['t'])
    vcc = m['Vth_cc_1e-9_V']
    # Gauss decomposition at the source-end (Vc = 0) threshold state (interpolated in Vg)
    dec = None
    if vcc is not None:
        k = int(np.searchsorted(vgs, vcc)); k = min(max(k, 1), len(vgs) - 1)
        wgt = (vcc - vgs[k-1]) / (vgs[k] - vgs[k-1])
        s = {key: st[k-1][key] * (1 - wgt) + st[k][key] * wgt for key in st[k]}
        tcm = p['t'] * 1e-7
        dec = {'wf_minus_chi_bulk': p['wf'] - 4.3, 'dEc': p['dEc'], 'u_front(EFn-Ec)': s['u_front'], 'Qf': -p['Qf'] / CQ, 'Qb': -p['Qb'] / CQ,
               'Nd': -p['Nd'] * tcm / CQ, 'tail_trapped': s['nt'] / CQ, 'deep_gauss': s['ng'] / CQ, 'interface_traps': s['ni'] / CQ,
               'free_electrons': s['ns'] / CQ, 'band_bending_front_minus_back_eV': s['bend'], 'nt_cm2': s['nt'], 'ns_cm2': s['ns']}
        dec['sum_check'] = sum(v for kk, v in dec.items() if kk in ('wf_minus_chi_bulk', 'dEc', 'Qf', 'Qb', 'Nd', 'tail_trapped', 'deep_gauss', 'interface_traps', 'free_electrons')) + s['u_front'] - vcc
    return {'metrics': {k: m[k] for k in ['Vth_cc_1e-9_V', 'Vth_lin_V', 'SS_cc_1e-10_1e-8_mV_dec', 'gm_max_A_V_um', 'Ion_A_per_um']}, 'decomp': dec,
            'Id_first': float(ids[0])}

def fmt(m):
    return (f"Vcc {m['Vth_cc_1e-9_V']:.3f} Vlin {m['Vth_lin_V']:.3f} gap {m['Vth_lin_V']-m['Vth_cc_1e-9_V']:.3f} SScc {m['SS_cc_1e-10_1e-8_mV_dec']:.1f} "
            f"gm {m['gm_max_A_V_um']:.3e} Ion {m['Ion_A_per_um']:.3e}")

if __name__ == '__main__':
    R = {}
    # ---------- (B1) validation of the surrogate against ATLAS ----------
    print('=== (B1) 1-D surrogate vs ATLAS (same parameters) ===')
    val_runs = ['run_0012', 'run_0016', 'run_0014', 'run_0015', 'run_0030', 'run_0031', 'run_0032', 'run_0033', 'run_0034', 'run_0035', 'run_0013', 'run_0017']
    for rid in val_runs:
        p = params_from_run(rid)
        out = run1d(p)
        ex = json.load(open(glob.glob(os.path.join(RUNS, rid + '_*'))[0] + '/execution.json'))['device_metrics_sim']
        R[rid] = {'p': {k: v for k, v in p.items()}, '1d': out, 'atlas': {k: ex[k] for k in out['metrics']}}
        print(f"{rid} t={p['t']} Qf={p['Qf']:.3g} Qb={p['Qb']:.3g}\n   1-D  : {fmt(out['metrics'])}\n   ATLAS: {fmt(ex)}")
        d = out['decomp']
        print('   Gauss terms at 1-D threshold (V): ' + ', '.join(f"{k} {v:+.3f}" for k, v in d.items() if k not in ('nt_cm2', 'ns_cm2')) + f", nt {d['nt_cm2']:.3g} cm-2, ns {d['ns_cm2']:.3g} cm-2")
    json.dump(R, open(os.path.join(OUT, 's1_poisson1d_validation.json'), 'w'), indent=1, default=float)

    # ---------- (B2) one-at-a-time switches on the calibrated configurations ----------
    print('\n=== (B2) one-at-a-time term removal (1-D), dVth_cc = Vth(full) - Vth(term removed) ===')
    SW = {}
    for rid in ['run_0012', 'run_0015', 'run_0013']:
        p0 = params_from_run(rid); base = run1d(p0)['metrics']
        row = {'full': base['Vth_cc_1e-9_V']}
        for name, mod in [('Qf', {'Qf': 0.0}), ('Nd', {'Nd': 0.0}), ('tail', {'Nt': 0.0}), ('Dit', {'NIT': 0.0}),
                          ('mu->13.30', {'mu': 13.30})]:
            p = dict(p0); p.update(mod); v = run1d(p)['metrics']['Vth_cc_1e-9_V']
            row[name] = base['Vth_cc_1e-9_V'] - v
        v = run1d(no_qc(p0))['metrics']['Vth_cc_1e-9_V']; row['confinement(dEc+m*)'] = base['Vth_cc_1e-9_V'] - v
        p = dict(p0); p['Nc'] = p0['Nc'] * (0.208 / p0['mstar']) ** 1.5; v = run1d(p)['metrics']['Vth_cc_1e-9_V']; row['m*_only(Nc)'] = base['Vth_cc_1e-9_V'] - v
        SW[rid] = row
        print(rid, ' '.join(f"{k} {v:+.3f}" for k, v in row.items()))
    json.dump(SW, open(os.path.join(OUT, 's1_poisson1d_switches.json'), 'w'), indent=1)

    # ---------- (B3) lever arm of a back-surface sheet charge ----------
    print('\n=== (B3) back-surface charge Qb = -1e12 cm^-2: dVth_cc, dVth_lin (1-D); front-equivalent = 0.179 V ===')
    LA = {}
    for rid in ['run_0012', 'run_0015', 'run_0013']:
        p0 = params_from_run(rid); base = run1d(p0)['metrics']
        for tag, mod in [('fullDOS', {}), ('no_tail', {'Nt': 0.0})]:
            pb = dict(p0); pb.update(mod); b0 = run1d(pb)['metrics'] if mod else base
            pb2 = dict(pb); pb2['Qb'] = -1e12; b1 = run1d(pb2)['metrics']
            t = p0['t']; analytic_back = (1e12 / CQ) * (1 + COX * t * 1e-7 / (9.3 * eps0))
            LA[f"{rid}_{tag}"] = dict(dVcc=b1['Vth_cc_1e-9_V'] - b0['Vth_cc_1e-9_V'], dVlin=b1['Vth_lin_V'] - b0['Vth_lin_V'], dSScc=b1['SS_cc_1e-10_1e-8_mV_dec'] - b0['SS_cc_1e-10_1e-8_mV_dec'])
            print(f"{rid} t={t} {tag}: dVcc {LA[f'{rid}_{tag}']['dVcc']:+.3f} dVlin {LA[f'{rid}_{tag}']['dVlin']:+.3f} dSScc {LA[f'{rid}_{tag}']['dSScc']:+.1f} | analytic front 0.179, back-referenced {analytic_back:.3f}")
    json.dump(LA, open(os.path.join(OUT, 's1_poisson1d_leverarm.json'), 'w'), indent=1)

    # ---------- (B4) no-confinement symmetric test ----------
    print('\n=== (B4) no confinement, single Qf = 4.76e10 (A6 value), per-film mu0 ===')
    SY = {}
    for rid in ['run_0012', 'run_0014', 'run_0013']:
        p = no_qc(params_from_run(rid)); p['Qf'] = 4.76e10; out = run1d(p)['metrics']; SY[rid] = out
        print(rid, fmt(out))
    json.dump(SY, open(os.path.join(OUT, 's1_poisson1d_symmetry.json'), 'w'), indent=1, default=float)

    # ---------- (B5) neutral-layer onset: Vth_cc and Id(-3 V) vs uniform Nd at 6.3 / 13.2 / 31.8 nm ----------
    print('\n=== (B5) uniform Nd scan (confinement on, Qf 1.73e12), Vg from -3 V ===')
    vgs3 = np.round(np.arange(-3.0, 3.0001, 0.05), 4)
    NL = {}
    for t, mu_b in [(6.3, 12.4), (13.2, 61.9), (31.8, 84.0)]:
        for Nd in [2.5e17, 1e18, 2e18, 3e18, 5e18]:
            p = law_params(t, mu_band=mu_b); p['Nd'] = Nd
            o = run1d(p, vgs3)
            NL[f"{t}_{Nd:.1e}"] = dict(Vcc=o['metrics']['Vth_cc_1e-9_V'], Id_m3V=o['Id_first'], NdT=Nd * t * 1e-7)
            vcc = o['metrics']['Vth_cc_1e-9_V']
            print(f"t={t} Nd={Nd:.1e} (Nd*t={Nd*t*1e-7:.2e} cm-2): Vth_cc {('%.3f' % vcc) if vcc is not None else 'none(always on)'} Id(-3V) {o['Id_first']:.2e} A/um")
        p = law_params(t, mu_band=mu_b); o = run1d(p, vgs3)
        vcc = o['metrics']['Vth_cc_1e-9_V']
        print(f"t={t} V1-law Nd={p['Nd']:.2e}: Vth_cc {('%.3f' % vcc) if vcc is not None else 'none'} Id(-3V) {o['Id_first']:.2e}")
    json.dump(NL, open(os.path.join(OUT, 's1_poisson1d_neutral_layer.json'), 'w'), indent=1, default=float)

    # ---------- (B6) pre-check of campaign-B B0 (S2 re-partition) and a pure front-Qf fit, 6.3 nm ----------
    print('\n=== (B6) 6.3 nm on-state shape: B0 parameters (Nt 2.66e19, mu_band 19.6, Qf 9.8e11) in 1-D ===')
    p = params_from_run('run_0014'); p['Nt'] = 2.66e19; p['mu'] = 19.6 * 0.9109641975308642; p['Qf'] = 9.8e11
    o = run1d(p)['metrics']; print('B0-1D:', fmt(o))
    p = params_from_run('run_0015'); print('0015-1D:', fmt(run1d(p)['metrics']))
    print('measured 6.3: Vcc 0.644 Vlin 1.820 gap 1.176 SScc 295.4 gm 3.431e-07 Ion 4.034e-07')
