# S2 part 4: where the saturation-formula mobility (2L/(W Cox)) (d sqrt(Id)/dVg)^2 peaks on the measured Vd = 0.7 V curves,
# and the linear-formula mobility at the same Vg (paper vs workbook mobility definitions, Task 5).
import numpy as np, csv, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
COX = 8.955369814335959e-07; L = 20e-4; W = 1e-4; VD = 0.7
rows = list(csv.DictReader(open(ROOT/'data'/'experimental_clean.csv')))
out = open(pathlib.Path(__file__).with_name('s2_part4_out.txt'), 'w')
for t in (2.0, 6.3, 13.2):
    d = sorted((float(r['vg_V']), float(r['id_A_per_um'])) for r in rows if abs(float(r['thickness_nm']) - t) < 1e-6)
    vg = np.array([a for a, b in d]); i = np.array([b for a, b in d])
    sq = np.gradient(np.sqrt(np.maximum(i, 0)), vg); mus = 2*L/(W*COX)*sq**2; k = int(np.argmax(mus))
    mul = np.gradient(i, vg)*L/(W*COX*VD)
    s = (f't={t}: mu_sat-formula peak {mus[k]:.2f} cm2/Vs at Vg={vg[k]:.2f} V (mu_lin there {mul[k]:.2f}); mu_sat at 3 V {mus[-1]:.2f}; '
         f'mu_lin at Vg=1,1.5,2,2.5,3 V: {[round(float(mul[np.argmin(abs(vg-v))]), 2) for v in (1.0, 1.5, 2.0, 2.5, 3.0)]}')
    print(s); out.write(s + '\n')
out.close()
