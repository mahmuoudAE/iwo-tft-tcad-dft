# toy cell In15WO24 (d24ok replay): bands 174-178 at every k from the AFS table: e - E_F, f_nk, completeness, PR_n, W-5d fraction
import numpy as np, sys
t = np.array([l.split() for l in open(sys.argv[1]) if not l.startswith('#')], float)
ef = float([l for l in open(sys.argv[1]) if 'fermi_energy_eV' in l][0].split('fermi_energy_eV')[1].split()[0])
for r in t[(t[:, 1] >= 174) & (t[:, 1] <= 178) & (t[:, 0] <= 2)]:
    print(f'k{int(r[0])} band {int(r[1])}: e-E_F {r[2]-ef:+.3f} eV  f {r[3]:.3f}  compl {r[5]:.3f}  PR {r[6]:.3f}  W-5d frac {r[-1]*1e-6/r[5]:.3f}')
