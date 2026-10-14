"""Fig. 3: two-step band alignment of the relaxed slabs to bulk In2O3 (split of dEg into dEc and dEv).

The bulk constants E_v - <V> and E_c - <V> were logged as 3.9098 / 4.7985 eV (RESULTS_LOG 2026-10-05) from the cell
mean of the pp.x plot_num 11 potential (bulk_v11.cube), which was deleted on 2026-10-06; the bulk save (tmp/vcr.save)
is also empty now, and the disk has < 1 GB free, so pp.x cannot be re-run here.

Independent re-derivation used instead: the cell mean of V_bare + V_H equals QE's G = 0 term of the local
pseudopotential (V_H has no G = 0 component), <V> = (4 pi / Omega) sum_t N_t vloc0_t with
vloc0_t = int_0^{10 bohr} r (r V_loc,t(r) + 2 Z_t) dr (PW/src vloc_of_g, QE simpson rule) read from the UPF files.
The method is VALIDATED on every slab here: the z-mean of each slab planar average (pp.x plot_num 11 -> average.x)
must equal the same expression for the slab cell.

Slab side: macroscopic average of the slab planar average at the slab centre (midpoint of the In planes), windows a/2
(bixbyite [001] period), a/2 * a/4 (double) and a/4 (the rejected first choice); plateau spread over +- a/8.
dEc = CBM_slab - (Vbar_centre + (E_c - <V>)_bulk), dEv likewise; dEc - dEv = dEg by construction.
"""
import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

A = 10.30609                         # relaxed bulk a (f02), sets the averaging windows
UPF = {'In': 'In.pbe-dn-kjpaw_psl.1.0.0.UPF', 'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF', 'H': 'H.pbe-kjpaw_psl.1.0.0.UPF',
       'W': 'W.pbe-spn-kjpaw_psl.1.0.0.UPF'}
SLABS = [('slab1_v15', 'scf.in'), ('slab1_v25', 'scf.in'), ('slab1_v35', 'scf.in'), ('slabL1_relax_v2', 'scf.in'),
         ('slabL2_relax_v2', 'scf.in'), ('slab1r_final_cpu', 'scf.in'), ('slab2_relax_c2', 'scf.in'), ('slab2r_pdos_cpu', 'scf.in'),
         ('iwo_slab1_final_cpu', 'scf.in'), ('iwo_slab2_final_cpu', 'scf.in')]


def alpha_table():
    out = {}
    for el, f in UPF.items():
        a, z, msh = q.upf_alpha(q.PSEUDO / f)
        import hashlib
        out[el] = {'vloc0_Ry_bohr3': a, 'Z': z, 'msh': msh, 'file': q.rel(q.PSEUDO / f),
                   'sha256': hashlib.sha256((q.PSEUDO / f).read_bytes()).hexdigest(),
                   'convention': 'int_0^r(msh) r (r V_loc + 2 Z) dr, msh = first r > 10 bohr made odd, QE simpson'}
    return out


def vmean_expected(alpha, sym, vol_A3):
    om = vol_A3 / q.BOHR ** 3
    return 4 * np.pi / om * sum(alpha[s]['vloc0_Ry_bohr3'] for s in sym) * q.RY      # eV


def two_step(job, dv_b, dc_b):
    d = q.RES / job
    z, vp, vm, f = q.avg_dat(d)
    h, l, sg = q.homo_lumo(d / 'scf.out')
    cell, sym, frac, cart, s_in = q.read_struct_in(d / 'scf.in')
    zin = cart[[s == 'In' for s in sym], 2] / q.BOHR
    zc = 0.5 * (zin.min() + zin.max())
    out = {'VBM_eV': q.V(h, sg), 'CBM_eV': q.V(l, sg), 'centre_z_A': round(zc * q.BOHR, 3), 'avg_src': f}
    win = np.abs(z - zc) <= A / 8 / q.BOHR
    for name, vmac in (('a/2', q.macro(z, vp, A / 2 / q.BOHR)),
                       ('a/2*a/4', q.macro(z, q.macro(z, vp, A / 4 / q.BOHR), A / 2 / q.BOHR)),
                       ('a/4', q.macro(z, vp, A / 4 / q.BOHR))):
        vc = float(np.interp(zc, z, vmac)) * q.RY
        out[name] = {'Vbar_centre_eV': round(vc, 4), 'dEc_eV': round(l - (vc + dc_b), 4), 'dEv_eV': round(h - (vc + dv_b), 4),
                     'plateau_spread_meV': round(float(vmac[win].max() - vmac[win].min()) * q.RY * 1000, 1)}
    return out


def main():
    res = {}
    alpha = alpha_table()
    res['vloc0'] = alpha
    # ---- validation on the slabs
    val = []
    for job, fin in SLABS:
        d = q.RES / job
        z, vp, vm, f = q.avg_dat(d)
        cell, sym, frac, cart, s_in = q.read_struct_in(d / fin)
        vol = abs(np.linalg.det(cell))
        exp = vmean_expected(alpha, sym, vol)
        got = float(vp.mean() * q.RY)
        val.append({'job': job, 'mean_planar_avg_eV': round(got, 5), 'expected_vloc0_eV': round(exp, 5), 'diff_meV': round((got - exp) * 1000, 3),
                    'src': f, 'n_atoms': len(sym)})
    res['validation'] = val
    # ---- bulk
    vr = q.BULK / 'vcrelax_ecut71_k3.out'
    cell, sym, frac, s_fin = q.final_struct_out(vr)
    vol = abs(np.linalg.det(cell))
    vb = vmean_expected(alpha, sym, vol)
    import json
    f02 = json.loads((q.OUT / 'f02_bulk_structure_bands.json').read_text())
    ev_b, ec_b = f02['bands_path']['VBM_eV'], f02['bands_path']['CBM_eV']
    dv_b, dc_b = ev_b['value'] - vb, ec_b['value'] - vb
    res['bulk'] = {'Vmean_eV': q.V(round(vb, 5), s_fin + ' (cell) + UPF PP_LOCAL', note='G=0 term of vltot; V_H has no G=0 component'),
                   'logged_Vmean_eV': q.V(4.1687, 'cern_htcondor/results/RESULTS_LOG.md:349', 'LOGGED'),
                   'E_v_eV': ev_b, 'E_c_eV': ec_b,
                   'Ev_minus_V_eV': round(dv_b, 4), 'Ec_minus_V_eV': round(dc_b, 4),
                   'logged': {'Ev_minus_V': 3.9098, 'Ec_minus_V': 4.7985, 'src': 'cern_htcondor/results/RESULTS_LOG.md:349'}}
    # ---- slabs
    res['two_step'] = {j: two_step(j, dv_b, dc_b) for j in ('slab2_relax_c2', 'slab2r_pdos_cpu', 'slab1r_final_cpu', 'slabL2_relax_v2')}
    q.dump('f03_bulk_alignment', res)
    for v in val:
        print(v)
    print('bulk', res['bulk']['Vmean_eV'], dv_b, dc_b)
    for j, t in res['two_step'].items():
        print(j, {k: t[k] for k in ('a/2', 'a/2*a/4', 'a/4')})

    # ---- figure: (a) planar + macroscopic averages of the 2 nm slab with the aligned bulk edges, (b) validation
    d = q.RES / 'slab2_relax_c2'
    z, vp, vm, f = q.avg_dat(d)
    t = res['two_step']['slab2_relax_c2']
    zc = t['centre_z_A']
    vmac = q.macro(z, vp, A / 2 / q.BOHR) * q.RY
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.6), gridspec_kw={'width_ratios': [1.6, 1]})
    zz = z * q.BOHR - zc
    ax[0].plot(zz, vp * q.RY, color='0.6', lw=0.5, label='planar average')
    ax[0].plot(zz, vmac, color=CYCLE[0], lw=1.2, label='macroscopic (a/2)')
    vcen = t['a/2']['Vbar_centre_eV']
    ax[0].hlines([vcen + dc_b, vcen + dv_b], -A / 2, A / 2, colors=[CYCLE[1], CYCLE[2]], lw=1.0, linestyles='--')
    ax[0].hlines([t['CBM_eV']['value'], t['VBM_eV']['value']], -A / 2, A / 2, colors=[CYCLE[1], CYCLE[2]], lw=1.0)
    ax[0].set_xlim(-22.6, 22.6)
    ax[0].set_xlabel(r'$z - z_{\rm centre}$ (Å)'); ax[0].set_ylabel('Energy (eV)')
    ax[0].legend(loc='lower left', fontsize=7)
    panel(ax[0], 'a', x=-0.13)
    ax[1].plot(range(len(val)), [v['diff_meV'] for v in val], 'o', mfc='none', color='k')
    ax[1].axhline(0, color='0.6', lw=0.6)
    ax[1].set_xticks(range(len(val)))
    short = {'slab1_v15': '1 nm v15', 'slab1_v25': '1 nm v25', 'slab1_v35': '1 nm v35', 'slabL1_relax_v2': '0.46 nm', 'slabL2_relax_v2': '0.70 nm',
             'slab1r_final_cpu': '0.93 nm', 'slab2_relax_c2': '1.96 nm', 'slab2r_pdos_cpu': '1.96 nm CPU', 'iwo_slab1_final_cpu': '0.93 nm W',
             'iwo_slab2_final_cpu': '1.96 nm W'}
    ax[1].set_xticklabels([short[v['job']] for v in val], rotation=60, ha='right', fontsize=6.5)
    ax[1].minorticks_off(); ax[1].tick_params(axis='y', which='minor', left=True)
    ax[1].set_ylabel(r'$\langle V\rangle_{\rm avg.x} - \langle V\rangle_{\rm UPF}$ (meV)')
    panel(ax[1], 'b', x=-0.32)
    fig.tight_layout()
    save(fig, 'fig03_two_step_alignment')


if __name__ == '__main__':
    main()
