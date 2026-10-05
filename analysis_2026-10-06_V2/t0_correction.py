"""Corrected exact-transformation predictions AT THE PARAMETERS OF THE V2 RUNS (registered V2 yaml: Qf 1.38345e12,
mu_band 17.6897 / 63.2597, T3 mu_P 38.3893), after the end-of-sweep clipping fix in t0_prechecks.transform.
Written before the T3 (6.3 nm) ATLAS result existed. Output: t0_correction.json."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t0_prechecks as t0  # noqa: E402

REG = json.loads((HERE / 't0_results_registered.json').read_text())['dft_swap']
dvq = REG['shared_Qf_shift_V']                              # 0.062 V, i.e. Qf 1.38345e12 as in the V2 yaml
shift = {t: (t0.dEc_v2(t) - t0.dEc_v1(t)) + t0.dv_mass(t) for t in t0.FILMS}
mu_run = {2.0: REG['films']['2.0']['mu_band_V2'], 13.2: REG['films']['13.2']['mu_band_V2'], 6.3: REG['films']['6.3']['mu_P']}
out = {'note': __doc__, 'dvq_V': dvq, 'mu_as_run': mu_run, 'films': {}}
for t in (2.0, 13.2):
    vg, im = t0.measured(t)
    out['films'][t] = {'corrected_prediction_at_run_parameters': t0.score(t, t0.transform(t, shift[t] + dvq, mu_run[t], vg)),
                       'registered_prediction': REG['films'][str(t)]['V2']}
t = 6.3
vg, im = t0.measured(t)
dv = -(t0.QF_V1 - t0.QF_RUN[t]) / t0.CQ + shift[t] + dvq
cur = t0.transform(t, dv, mu_run[t], vg)
mu_e = mu_run[t] * im[-1] / cur[-1]
out['films'][t] = {'P_corrected': t0.score(t, cur), 'E_corrected': t0.score(t, cur * mu_e / mu_run[t]), 'mu_E_corrected': mu_e,
                   'P_registered': REG['films']['6.3']['V2_P_mu_powerlaw'], 'E_registered': REG['films']['6.3']['V2_E_mu_Ion_normalized']}
(HERE / 't0_correction.json').write_text(json.dumps(out, indent=1, default=float))
for t, r in out['films'].items():
    for k, v in r.items():
        if isinstance(v, dict):
            print(f"{t} nm {k:40} rmse {v['rmse_active_dec']:.4f} Vth_cc {v['Vth_cc']:.4f} Vth_lin {v['Vth_lin']:.4f} SS_cc {v['SS_cc']:.1f} Ion {v['Ion']:.4e}")
        else:
            print(f'{t} nm {k} {v}')
