"""Z9 wrapper (offline, 0 launches). Imports the registered leakage_bounds.py unmodified (its constants,
floors and FN form), checks that the wrapper reproduces its FN lines, then extends the gate-injection bound
to a two-layer stack with a numerical WKB exponent at the gate Fermi level.
J = A(phi_inj, m_inj) * E_inj^2 * exp(-S_WKB) + Richardson thermionic term over the highest barrier.
For a single triangular barrier S_WKB = B/E exactly, so J reduces to the leakage_bounds.py FN line.
Usage: python z9_leakage_wrapper.py <path to analysis_2026-10-10_campaign>
"""
import contextlib, io, math, re, sys
sys.path.insert(0, sys.argv[1])
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import leakage_bounds as LB          # unmodified registered script
q, h, hb, m0, kT = LB.q, LB.h, LB.hb, LB.m0, LB.kT
floors = LB.floors; W_cm = LB.W_cm
GATE_CM = 24e-4                          # leakage_bounds.py l.24: 24 um gate (L 20 + 2x2 overlap, ASSUMED)

def fn_A(phi, mr):                       # leakage_bounds.py l.20 (A/V^2, SI)
    return q ** 3 / (8 * math.pi * h * phi * q) / mr

def fn_B(phi, mr):                       # leakage_bounds.py l.21 (V/m)
    return 8 * math.pi * math.sqrt(2 * mr * m0) * (phi * q) ** 1.5 / (3 * q * h)

# --- regression against the imported script's printed FN lines
E_hf_LB = LB.E_hf
reg = []
for line in buf.getvalue().splitlines():
    m = re.match(r'phi=([\d.]+) eV m\*=([\d.]+):.*I\(24 um gate x 1 um\)=([\d.e+-]+)', line)
    if m:
        phi, mr, I_lb = float(m[1]), float(m[2]), float(m[3])
        E = E_hf_LB * 100
        I = fn_A(phi, mr) * E ** 2 * math.exp(-fn_B(phi, mr) / E) / 1e4 * GATE_CM * W_cm
        reg.append((phi, mr, I_lb, I))

def stack_current(layers, phi_inj, V_ox, franz=False, n=20000):
    """layers: list of (d_nm, eps, chi_eV, m_r, Eg) from the gate side. phi_inj = W_gate - chi(layer 1).
    Returns I (A/um), S_WKB, E_inj (V/cm), U_max (eV)."""
    d = [L[0] * 1e-7 for L in layers]              # cm
    inv = sum(di / L[1] for di, L in zip(d, layers))
    D = V_ox / inv                                  # eps*E (V/cm * eps), continuous
    E = [D / L[1] for L in layers]                  # V/cm
    U0 = phi_inj; S = 0.0; Umax = phi_inj
    for i, (di, L) in enumerate(zip(d, layers)):
        if i > 0:
            U0 += layers[i - 1][2] - L[2]           # CB step = chi_prev - chi_this
        Umax = max(Umax, U0)
        dx = di / n
        for k in range(n):
            U = U0 - E[i] * (k + 0.5) * dx          # eV
            if U > 0:
                kap2 = 2 * L[3] * m0 * U * q / hb ** 2
                if franz: kap2 *= max(1 - U / L[4], 0.0)
                S += 2 * math.sqrt(kap2) * dx * 1e-2   # dx in m
        U0 -= E[i] * di
    Einj = E[0] * 100                               # V/m
    J_t = fn_A(phi_inj, layers[0][3]) * Einj ** 2 * math.exp(-S) / 1e4      # A/cm^2
    J_th = 120.0 * 300 ** 2 * math.exp(-Umax / kT)                          # A/cm^2 (A* = 120, m0)
    return (J_t + J_th) * GATE_CM * W_cm, J_t * GATE_CM * W_cm, S, E[0], Umax

W = 4.7                                           # gate work function, ASSUMED (design 4.2)
HF = dict(nom=(2.5, 0.20, 5.8), worst=(3.2, 0.10, 5.8), mon=(2.0, 0.11, 5.8))
AL = dict(nom=(1.25, 0.35, 8.8), worst=(1.6, 0.30, 8.8), ald_exp=(1.85, 0.35, 6.4), ald_cons=(2.45, 0.35, 6.4),
          ald_exp_m22=(1.85, 0.22, 6.4), ald_cons_m22=(2.45, 0.22, 6.4))
cases = [  # name, HfO2 key, Al2O3 key, phi override (registered sets fix phi independently of W - chi)
    ('a1 registered nominal', 'nom', 'nom', 2.2),
    ('a2 registered worst', 'worst', 'worst', 1.5),
    ('b1 nominal HfO2 + ALD Al2O3 chi 1.85', 'nom', 'ald_exp', 2.2),
    ('b2 nominal HfO2 + ALD Al2O3 chi 2.45', 'nom', 'ald_cons', 2.2),
    ('b3 b1 with m_Al 0.22', 'nom', 'ald_exp_m22', 2.2),
    ('b4 b2 with m_Al 0.22', 'nom', 'ald_cons_m22', 2.2),
    ('c1 Monaghan HfO2 + registered Al2O3', 'mon', 'nom', None),
    ('c2 Monaghan HfO2 + ALD chi 1.85', 'mon', 'ald_exp', None),
    ('c3 Monaghan HfO2 + ALD chi 2.45', 'mon', 'ald_cons', None),
]
if __name__ == '__main__':
    print('# regression vs leakage_bounds.py FN lines (phi, m, I_script, I_wrapper)')
    for r in reg: print('REG %.1f %.2f %.1e %.2e' % r)
    print('# case | order | V_ox | franz | phi_inj | E_inj V/cm | S_WKB | U_max | I_G A/um | margins 2.0/6.3/13.2 dec')
    for name, hk, ak, phi in cases:
        chH, mH, gH = HF[hk]; chA, mA, gA = AL[ak]
        hf = (15.0, 19.57, chH, mH, gH); al = (2.0, 9.0, chA, mA, gA)
        for order, layers in (('TiN/HfO2/Al2O3/IWO', [hf, al]), ('TiN/Al2O3/HfO2/IWO', [al, hf])):
            p = phi if (phi is not None and order.startswith('TiN/HfO2')) else W - layers[0][2]
            if phi is not None and order.startswith('TiN/Al2O3'):
                p = W - layers[0][2]
            for V in (3.0, 3.43):
                for fr in (False, True):
                    I, It, S, E1, Um = stack_current(layers, p, V, fr)
                    mg = [math.log10(floors[t] / I) for t in (2.0, 6.3, 13.2)]
                    print(f'{name} | {order} | {V} | {int(fr)} | {p:.2f} | {E1:.3e} | {S:.2f} | {Um:.3f} | {I:.2e} | '
                          + ' / '.join(f'{x:.1f}' for x in mg))
    # single-barrier sanity: triangular limit reproduces FN exactly
    I, It, S, E1, Um = stack_current([(15.0, 19.57, 2.5, 0.2, 5.8)], 2.2, 2.325 + 3.0)
    print('# sanity single HfO2 15 nm, V 5.325: S_WKB %.4f vs B/E %.4f' % (S, fn_B(2.2, 0.2) / (E1 * 100)))
