"""S1 task 3: what kind of gate-voltage-dependent charge reproduces the 6.3 nm on-state SHAPE (Vth_lin, gm_max) while
keeping Vth_cc, SS_cc and Ion? 1-D surrogate (validated vs ATLAS, see s1_poisson1d.out.txt). Hypothesis-generating only:
an extra acceptor Gaussian band (sheet density S, centre E0 below Ec, width W) is added to the run_0015 configuration;
Qf (exact rigid shift) and mu (exact scale) are then re-adjusted so that Vth_cc = 0.644 V and Ion(3 V) = 4.034e-7 A/um.
These are CALIBRATED numbers (2 free parameters matched + 1 band tried), not predictions."""
import numpy as np, json, os
import s1_poisson1d as s

class FilmBand(s.Film):
    def __init__(self, p, band):
        super().__init__(p)
        self.band = band
        self.tb = s.occ_table('gauss', band['E0'], band['W']) if band else None
        if band:
            self.Nb = band['S'] / (p['t'] * 1e-7 * band['W'] * np.sqrt(np.pi))
    def charges(self, u):
        rho, drho, n, nt, ng, ni = super().charges(u)
        if self.band:
            b, db = s.tab_eval(self.tb, u)
            rho = rho - self.Nb * b; drho = drho - self.Nb * db; nt = nt + self.Nb * b
        return rho, drho, n, nt, ng, ni

def adjust(vg, idv, vcc_t=0.644, ion_t=4.034e-7):
    shift, k = 0.0, 1.0
    lg = np.log10(np.clip(idv, 1e-40, None))
    for _ in range(30):
        cur = k * 10 ** np.interp(vg - shift, vg, lg)
        m = s.metrics(vg, cur, is_sim=True, t_nm=6.3)
        shift += vcc_t - m['Vth_cc_1e-9_V']
        cur = k * 10 ** np.interp(vg - shift, vg, lg)
        k *= ion_t / cur[-1]
    cur = k * 10 ** np.interp(vg - shift, vg, lg)
    return shift, k, s.metrics(vg, cur, is_sim=True, t_nm=6.3)

vg = np.round(np.arange(-1.5, 3.0001, 0.05), 4)
p0 = s.params_from_run('run_0015')
res = {}
print('measured 6.3: Vcc 0.644 Vlin 1.820 gap 1.176 SScc 295.4 gm 3.431e-07 Ion 4.034e-07')
cases = [None] + [dict(S=S, E0=E0, W=W) for S in (1.5e12, 3e12) for E0 in (0.0, 0.05, 0.10, 0.15) for W in (0.05,)]
for band in cases:
    f = FilmBand(p0, band)
    ids, _ = f.idvg(vg)
    sh, k, m = adjust(vg, ids)
    dQf = -sh * s.CQ   # a positive Vg shift = less positive Qf
    tag = 'no band (run_0015 config)' if band is None else f"band S={band['S']:.1e} E0=Ec-{band['E0']:.2f} W={band['W']:.2f}"
    res[tag] = dict(shift_V=sh, dQf_cm2=dQf, Qf_new=p0['Qf'] + dQf, mu_scale=k, mu_band_new=11.69 * k, **{kk: m[kk] for kk in ['Vth_cc_1e-9_V', 'Vth_lin_V', 'SS_cc_1e-10_1e-8_mV_dec', 'gm_max_A_V_um', 'Ion_A_per_um']})
    print(f"{tag}: Qf -> {p0['Qf'] + dQf:.3g} (shift {sh:+.3f} V), mu_band -> {11.69*k:.2f} | Vcc {m['Vth_cc_1e-9_V']:.3f} Vlin {m['Vth_lin_V']:.3f} gap {m['Vth_lin_V']-m['Vth_cc_1e-9_V']:.3f} SScc {m['SS_cc_1e-10_1e-8_mV_dec']:.1f} gm {m['gm_max_A_V_um']:.3e} Ion {m['Ion_A_per_um']:.3e}")
json.dump(res, open(os.path.join(s.OUT, 's1_shape_test.json'), 'w'), indent=1, default=float)

# no-QC single-(Nd, Qf) least-squares consistency check (linearised from s1_poisson1d B4/B5 sensitivities)
r = np.array([0.665 - 0.662, 0.588 - 0.644, 0.330 - 0.083])       # B4 misses (1-D no-QC, Qf 4.76e10)
a = np.array([0.0036, 0.0125, 0.0283 * 1.32])                     # dVth per +1e17 cm^-3 uniform Nd (B5 slopes; 2 nm from q t/Cox + q t^2/2eps)
A = np.c_[-a, np.ones(3)]
sol, *_ = np.linalg.lstsq(A, -r, rcond=None)
print('\nno-QC: best single extra uniform Nd (1e17 cm^-3) and rigid Vg offset:', sol, ' residual misses (V):', r + A @ sol)
