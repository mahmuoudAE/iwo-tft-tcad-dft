# S2 part 1: mobility decomposition, curve-shape features, degeneracy Jacobian, paper-vs-workbook extraction test,
# thickness-law form tests. Reads only local data/run files; writes s2_part1_out.txt next to this script.
import numpy as np, csv, json, pathlib
from scipy.optimize import curve_fit, least_squares
ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = open(pathlib.Path(__file__).with_name('s2_part1_out.txt'), 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); OUT.write(s + '\n')
COX = 8.955369814335959e-07; L = 20e-4; W = 1e-4; VD = 0.7

def load_exp(t):
    vg, idv = [], []
    for r in csv.DictReader(open(ROOT/'data'/'experimental_clean.csv')):
        if abs(float(r['thickness_nm'])-t) < 1e-6: vg.append(float(r['vg_V'])); idv.append(float(r['id_A_per_um']))
    o = np.argsort(vg); return np.array(vg)[o], np.array(idv)[o]
def load_sim(run):
    d = next((ROOT/'results'/'runs').glob(run+'_*'))
    vg, a = [], []
    for r in csv.DictReader(open(d/'comparison.csv')):
        vg.append(float(r['vg_V'])); a.append(max(float(r['atlas_A_per_um']), 1e-30))
    return np.array(vg), np.array(a)
def feats(vg, idv):
    gm = np.gradient(idv, vg); i = int(np.argmax(gm)); g = gm[i]
    vlin = vg[i] - idv[i]/g
    lg = np.log10(np.maximum(idv, 1e-30)); j = np.where(lg >= -9)[0][0]
    vcc = vg[j-1] + (-9 - lg[j-1])*(vg[j]-vg[j-1])/(lg[j]-lg[j-1])
    ion = idv[-1]; mu = g*L/(W*COX*VD)
    # saturation-formula and effective-mobility variants (same curve, same Cox/W/L)
    sq = np.gradient(np.sqrt(np.maximum(idv, 0)), vg); mu_sat = np.max(2*L/(W*COX)*sq**2)
    ov = vg - vlin; m = ov > 0.3; mu_eff = np.max(idv[m]*L/(W*COX*ov[m]*VD)) if m.any() else np.nan
    return dict(Vcc=vcc, Vlin=vlin, gap=vlin-vcc, gm=g, vg_gm=vg[i], mu=mu, Ion=ion, ion_over_gm=ion/g,
                roll=gm[-1]/g, mu_sat=mu_sat, mu_eff=mu_eff)

P('=== A. Measured curve features (Cox 8.955e-7, L 20 um, Vd 0.7 V) ===')
E = {}
for t in (2.0, 6.3, 13.2, 31.8):
    vg, idv = load_exp(t)
    if t == 31.8:
        gm = np.gradient(idv, vg); g = gm.max(); P(f't=31.8 gm_max={g:.3e} A/V/um at Vg={vg[np.argmax(gm)]:.2f} -> apparent mu_FE={g*L/(W*COX*VD):.1f} cm2/Vs (always-on film, context only)'); continue
    f = feats(vg, idv); E[t] = f
    P(f"t={t:5.1f} Vcc={f['Vcc']:.3f} Vlin={f['Vlin']:.3f} gap={f['gap']:.3f} V  gm_max={f['gm']:.3e} at Vg={f['vg_gm']:.2f}  mu_FE={f['mu']:.2f}  Ion/gm={f['ion_over_gm']:.3f} V  gm(3V)/gm_max={f['roll']:.3f}  mu_sat-formula={f['mu_sat']:.2f}  mu_eff(Id/ov)max={f['mu_eff']:.2f}")
P('Paper peak mu_FE 5.1 (2 nm) / 27.4 (13.2 nm); ratio paper/workbook =', round(5.1/E[2.0]['mu'],3), round(27.4/E[13.2]['mu'],3))
for k in ('mu_sat', 'mu_eff'):
    P(f'  variant {k}: 2 nm {E[2.0][k]:.2f}, 13.2 nm {E[13.2][k]:.2f}; 13.2/2 ratio {E[13.2][k]/E[2.0][k]:.2f} (paper 13.2/2 = {27.4/5.1:.2f}; workbook linear = {E[13.2]["mu"]/E[2.0]["mu"]:.2f})')
# thickness-dependent series capacitance hypothesis (MISM model of SI Fig S1): C(t) = 1/(1/Cox + t/(eps0*9.3))
for t in (2.0, 13.2):
    C = 1/(1/COX + t*1e-7/(8.854e-14*9.3)); P(f'  series-C(t) hypothesis t={t}: C={C:.3e}, mu would be {E[t]["mu"]*COX/C:.1f} (moves the wrong way)')

P('\n=== B. ATLAS runs: same features, decomposition mu_FE = mu_band x R(t) x P ===')
runs = {'run_0012': (2.0, 18.13), 'run_0023': (2.0, 18.13), 'run_0016': (2.0, 18.13), 'run_0014': (6.3, 12.4), 'run_0015': (6.3, 11.69), 'run_0013': (13.2, 61.9), 'run_0017': (13.2, 61.9)}
S = {}
for r, (t, mb) in runs.items():
    vg, a = load_sim(r); f = feats(vg, a); S[r] = f
    R = (1-0.287/t)**2; mun = mb*R; Pp = f['mu']/mun
    P(f"{r} t={t} Vcc={f['Vcc']:.3f} Vlin={f['Vlin']:.3f} gap={f['gap']:.3f} gm={f['gm']:.3e} mu_FE={f['mu']:.2f} Ion={f['Ion']:.3e} Ion/gm={f['ion_over_gm']:.3f} roll={f['roll']:.3f} | mu_band={mb} R={R:.3f} mun={mun:.2f} P=mu_FE/mun={Pp:.3f}")
P('Log-decomposition of measured mu_FE ratios (band, roughness, partition, model residual):')
cal = {2.0: ('run_0012', 18.13), 6.3: ('run_0015', 11.69), 13.2: ('run_0013', 61.9)}
def comp(t):
    r, mb = cal[t]; R = (1-0.287/t)**2; Pp = S[r]['mu']/(mb*R); res = E[t]['mu']/S[r]['mu']; return np.log([mb, R, Pp, res])
for a, b in ((6.3, 13.2), (2.0, 13.2), (2.0, 6.3)):
    d = comp(b) - comp(a); tot = np.log(E[b]['mu']/E[a]['mu'])
    P(f'  {a}->{b}: total ln={tot:.3f} (x{np.exp(tot):.2f}); band {d[0]:.3f} ({100*d[0]/tot:.0f}%), roughness {d[1]:.3f} ({100*d[1]/tot:.0f}%), partition {d[2]:.3f} ({100*d[2]/tot:.0f}%), residual {d[3]:.3f} ({100*d[3]/tot:.0f}%)')

P('\n=== C. Degeneracy Jacobian at 2 nm (run_0012 base; Nt x1.5 = run_0023; mu exact-linear; Qf rigid) ===')
b0, b1 = S['run_0012'], S['run_0023']; dl = np.log(1.5)
J = {'Vcc': (b1['Vcc']-b0['Vcc'])/dl, 'gap': (b1['gap']-b0['gap'])/dl, 'lngm': np.log(b1['gm']/b0['gm'])/dl, 'lnIon': np.log(b1['Ion']/b0['Ion'])/dl}
P('  per unit ln(Nt):', {k: round(v, 4) for k, v in J.items()})
P('  -> Ion is threshold-dominated: dlnIon/dlnNt =', round(J['lnIon'], 3), 'vs dln gm/dlnNt =', round(J['lngm'], 3))
P('  Nt needed to change mu_FE by x4.6 via partition alone (linearised): ln Nt change =', round(np.log(4.6)/abs(J['lngm']), 1), '-> factor', f"{np.exp(np.log(4.6)/abs(J['lngm'])):.1e}")
# 6.3 nm re-partition estimate using the 2-nm Jacobian (proxy): unknowns dlnNt, dlnmu, dQf(V)
t0 = S['run_0015']; ex = E[6.3]
res = np.array([ex['Vcc']-t0['Vcc'], ex['gap']-t0['gap'], np.log(ex['gm']/t0['gm'])])
A = np.array([[J['Vcc'], 0, 1], [J['gap'], 0, 0], [J['lngm'], 1, 0]])
x = np.linalg.solve(A, res)
P(f'  6.3 nm residual (exp - run_0015): dVcc={res[0]:+.3f} V, dgap={res[1]:+.3f} V, dln gm={res[2]:+.3f}')
P(f'  solution: Nt x{np.exp(x[0]):.2f} (Nt6.3 -> {8.459e18*np.exp(x[0]):.2e} cm-3), mu_band x{np.exp(x[1]):.2f} (-> {11.69*np.exp(x[1]):.1f}), rigid dV={x[2]:+.3f} V (Qf change {-x[2]/0.179e-12:+.2e} cm-2 -> Qf ~ {8.7e10 - x[2]/0.179e-12:.2e})')
# sensitivity: gap Jacobian scaled by sheet-trap ratio 6.3/2 (5.3e12/4.0e12) as an alternative proxy
for sc in (1.0, 5.3/4.0, 2.0):
    A2 = A.copy(); A2[1, 0] = J['gap']*sc; A2[0, 0] = J['Vcc']*sc; A2[2, 0] = J['lngm']*sc
    x2 = np.linalg.solve(A2, res)
    P(f'    Jacobian scale {sc:.2f}: Nt x{np.exp(x2[0]):.2f}, mu_band {11.69*np.exp(x2[1]):.1f}, Qf ~ {8.7e10 - x2[2]/0.179e-12:.2e}')

P('\n=== D. Thickness-law form tests (3 thin films) ===')
t3 = np.array([2.0, 6.3, 13.2])
series = {'mu_FE': [E[t]['mu'] for t in t3], 'Ion': [E[t]['Ion'] for t in t3], 'gm_max': [E[t]['gm'] for t in t3],
          'mu_band_fit': [18.13, 11.69, 61.9], 'Vth_cc': [E[t]['Vcc'] for t in t3], 'Vth_lin': [E[t]['Vlin'] for t in t3]}
def fitpow(t, y):
    b, la = np.polyfit(np.log(t), np.log(y), 1); return lambda tt: np.exp(la)*tt**b, f'a t^{b:.2f}'
def fitinv(t, y):
    B, A = np.polyfit(1/t, y, 1); return lambda tt: A + B/tt, f'{A:.3g}+{B:.3g}/t'
def fitexp(t, y):
    b, la = np.polyfit(t, np.log(y), 1); return lambda tt: np.exp(la + b*tt), f'a exp({b:.3f} t)'
def fitlin(t, y):
    b, a = np.polyfit(t, y, 1); return lambda tt: a + b*tt, f'{a:.3g}+{b:.3g} t'
def fitstep(t, y):
    lo = np.mean(y[:2]); return lambda tt: np.where(tt < 9.75, lo, y[2]), f'step {lo:.3g}|{y[2]:.3g} (tc in 6.3-13.2)'
for name, y in series.items():
    y = np.array(y); pos = np.all(y > 0)
    P(f'{name}: {np.round(y, 4).tolist()}')
    for lab, fn in (('power', fitpow), ('A+B/t', fitinv), ('exp', fitexp), ('linear', fitlin), ('step', fitstep)):
        if lab in ('power', 'exp') and not pos: continue
        f, desc = fn(t3, y); yp = f(t3)
        rel = (yp - y)/np.abs(y); rms = np.sqrt(np.mean(rel**2))
        # leave-one-out: fit on 2 and 13.2, predict 6.3
        idx = [0, 2]; f2, _ = fn(t3[idx], y[idx]) if lab != 'step' else (lambda tt: np.where(tt < 9.75, y[0], y[2]), '')
        p63 = float(f2(np.array([6.3]))[0])
        P(f'   {lab:7s} {desc:32s} rms rel resid {rms:6.3f}  max {np.max(np.abs(rel)):6.3f} | LOO(2,13.2)->6.3: {p63:.4g} vs {y[1]:.4g} ({p63/y[1]:.2f}x)')
# 31.8 nm held-out check on Ion (context only)
vg, i318 = load_exp(31.8)
b = np.log(E[13.2]['Ion']/E[6.3]['Ion'])/np.log(13.2/6.3)
P(f'Ion power law through 6.3/13.2 (exponent {b:.2f}) predicts Ion(31.8) = {E[13.2]["Ion"]*(31.8/13.2)**b:.2e} vs measured {i318[-1]:.2e} A/um; pure series-R ceiling 0.7 V/9e4 ohm.um = {0.7/9e4:.1e}')
b2 = np.log(E[13.2]['Ion']/E[2.0]['Ion'])/np.log(13.2/2)
P(f'Ion power law through 2/13.2 (exponent {b2:.2f}) predicts Ion(31.8) = {E[13.2]["Ion"]*(31.8/13.2)**b2:.2e}')

P('\n=== E. Model laws: Nt surface+bulk decomposition, dEc vs EMA upper bound, m* ===')
B = (2e19 - 4.857e18)/(1/2 - 1/13.2); A = 2e19 - B/2
P(f'Nt = A + B/t through the V1 anchors: A={A:.2e} cm-3, B={B*1e-7:.2e} cm-2 (sheet); at 6.3: {A+B/6.3:.2e} vs power law 8.46e18')
P('Januar2026 internal Nt values: 5.3e19 (2 nm) / 3.39e18 (10 nm) -> exponent', round(np.log(5.3e19/3.39e18)/np.log(5), 2), '; Sec.2.8 "x4 from 13.2 to 2" -> exponent', round(np.log(4)/np.log(6.6), 2))
for t in (1.98, 2.0, 3.0, 6.3, 13.2):
    law = 0.9205*t**-1.3815; ms = 0.208 + 0.1311*t**-1.412
    ema_b = 0.376/(0.208*t*t); ema_t = 0.376/(ms*t*t)
    P(f't={t:5.2f} dEc law {law:.4f} eV | infinite-well EMA upper bound m*=0.208: {ema_b:.4f}, m*(t): {ema_t:.4f} | law/EMA = {law/ema_b:.2f}')
P('law exceeds the infinite-well parabolic bound (m*=0.208) for t >', round((0.376/(0.208*0.9205))**(1/0.6185), 2), 'nm')
OUT.close()
