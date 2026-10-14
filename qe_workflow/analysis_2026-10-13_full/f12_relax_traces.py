"""Fig. 12: relaxation histories of the crystalline slabs and W cells (energy and total force per SCF of the BFGS run).

Reads the '!' total energies and 'Total force' lines of each relax / vc-relax output up to the 'bfgs converged' line
(the SCF that follows it in a vc-relax is the final SCF with the new G vectors and is excluded). E is relative to the
converged energy. For the vc-relax runs (cell_dofree 2Dxy, target pressure 0) the BFGS objective is the enthalpy, which
equals E at P = 0 up to the residual in-plane stress term; '!' E is shown.
"""
import numpy as np

import qeio as q
from figstyle import plt, save, panel, CYCLE

RUNS = [('0.51 nm', 'slabL1_relax_v2/vcrelax.out'), ('0.75 nm', 'slabL2_relax_v2/vcrelax.out'), ('1 nm', 'slab1_relax_gpu/vcrelax.out'),
        ('2 nm', 'slab2_relax_c2/vcrelax.out'), ('1 nm W', 'iwo_slab1_W24d_x1/relax.out'), ('2 nm W', 'iwo_slab2_W24d_checkpoint/relax.out'),
        ('bulk W 24d', 'iwo_W24d/relax.out'), ('bulk W 8b', 'iwo_W8b/relax.out')]


def trace(p):
    _, ib = q.last(p, r'bfgs converged in')
    # only the last pw.x run in the file (some relax.out files hold an earlier, restarted run before it)
    starts = [i for _, i in q.grep(p, r'Program PWSCF')]
    s0 = max([i for i in starts if i < ib], default=0)
    E = [(float(m.group(1)), i) for m, i in q.grep(p, r'^!\s+total energy\s+=\s+(-?[\d.]+) Ry') if s0 < i < ib]
    F = [(float(m.group(1)), i) for m, i in q.grep(p, r'Total force =\s+([\d.]+)') if s0 < i < ib]
    return np.array([e for e, _ in E]), np.array([f for f, _ in F]), s0


def main():
    res = {}
    fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.6))
    for j, (lab, f) in enumerate(RUNS):
        p = q.RES / f
        E, F, s0 = trace(p)
        res[lab] = {'file': q.rel(p), 'from_line': s0, 'n_scf': len(E), 'E_first_minus_last_mRy': round((E[0] - E[-1]) * 1000, 3),
                    'last_total_force_Ry_bohr': float(F[-1]) if len(F) else None,
                    'last_step_dE_mRy': round((E[-1] - E[-2]) * 1000, 4) if len(E) > 1 else None}
        ls = '-' if j < 4 else '--'
        ax[0].semilogy(np.arange(len(E)), np.maximum((E - E[-1]) * 1000, 1e-4), ls, color=CYCLE[j % len(CYCLE)], lw=0.9, label=lab)
        ax[1].semilogy(np.arange(len(F)), F, ls, color=CYCLE[j % len(CYCLE)], lw=0.9, label=lab)
    ax[0].set_xlabel('SCF number in the BFGS run'); ax[0].set_ylabel(r'$E - E_{\rm conv}$ (mRy)')
    ax[1].set_xlabel('SCF number in the BFGS run'); ax[1].set_ylabel('total force (Ry/bohr)')
    h, l = ax[1].get_legend_handles_labels()
    panel(ax[0], 'a', x=-0.2); panel(ax[1], 'b', x=-0.2)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.legend(h, l, loc='lower center', ncol=4, fontsize=6.5, bbox_to_anchor=(0.5, 0.0))
    save(fig, 'fig12_relax_traces')
    q.dump('f12_relax_traces', res)
    for k, v in res.items():
        print(k, v)


if __name__ == '__main__':
    main()
