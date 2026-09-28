"""Bounded real ATLAS evaluation and independent diagnostics for the rebuild."""
import argparse
import contextlib
import hashlib
import json
from pathlib import Path

import numpy as np

from rebuild_model import ROOT, load, render
from local_probe import run
from paper_trial import inspect
from atlas_workflow import read_xy, check_coverage
from rebuild_check import load_run as independently_load_run


def evaluate(cfg, key, label, timeout=900):
    deck, meta = render(cfg, key)
    folder = run(['C:/sedatools/exe/deckbuild.exe', '-run', '{deck}', '-outfile', '{stdout}'],
                 deck, label, timeout, config=cfg, verbose=False)
    (folder/'rebuild_metadata.json').write_text(json.dumps(meta, indent=2))
    with (folder/'postprocess_stdout.txt').open('w', encoding='utf-8') as stream:
        with contextlib.redirect_stdout(stream):
            valid = inspect_rebuild(folder, cfg, key)
    return folder, valid


def inspect_rebuild(folder, cfg, key):
    """Inspect immutable real output; can correct an older postprocessor without rerunning."""
    try:
        execution = load(folder/'execution.json')
        if execution['actual_started_simulator_stages'] != ['atlas']:
            raise ValueError('Expected one genuine ATLAS stage')
        valid = inspect(folder, cfg, key, allow_recovered_steps=True)
        observed = np.genfromtxt(ROOT/cfg['curves'][key]['data'], delimiter=',', names=True)
        vg, measured = observed['vg_V'], observed['id_A_per_um']
        off = np.median(measured[(vg >= -2) & (vg <= -.5)])
        active = measured > 5*off if key != '31p8' else np.ones(len(vg), bool)
        probe = {}
        for filename in ('mobility_vg.dat', 'electrons_vg.dat'):
            x, y = read_xy(folder/filename)
            check_coverage(x, vg)
            y = y[np.argmin(abs(x[:, None]-vg[None, :]), axis=0)]
            probe[filename] = {'positive_points': int((y > 0).sum()),
                               'positive_at_all_active_points': bool((y[active] > 0).all()),
                               'minimum': float(y.min()), 'maximum': float(y.max()),
                               'sha256': hashlib.sha256((folder/filename).read_bytes()).hexdigest()}
        valid['native_probes'] = probe
        valid['native_probes_pass'] = all(v['positive_at_all_active_points'] for v in probe.values())
        native = independently_load_run(folder)
        valid['independent_native_checks'] = native['summary']
        valid['native_evidence_pass'] = native['summary']['run_acceptable']
        valid['calibration_eligible'] = False  # Requires independent width/mesh/DOS evidence.
        if (folder/'trial_failure.json').exists():
            valid['prior_postprocessor_failure'] = load(folder/'trial_failure.json')
            valid['prior_failure_retained_for_audit'] = True
        (folder/'rebuild_validation.json').write_text(json.dumps(valid, indent=2))
        return valid
    except Exception as exc:
        (folder/'trial_failure.json').write_text(json.dumps({'error': str(exc)}, indent=2))
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, default=ROOT/'config/rebuild_seed.json')
    p.add_argument('--key', default='2p0', choices=['2p0', '6p3', '13p2', '31p8'])
    p.add_argument('--label', required=True)
    p.add_argument('--timeout', type=int, default=900)
    a = p.parse_args()
    folder, valid = evaluate(load(a.config), a.key, a.label, a.timeout)
    metrics = load(folder/'diagnostic_metrics.json')
    print(json.dumps({'run': str(folder), 'native_evidence_pass': valid.get('native_evidence_pass'),
                      'active_log_RMSE': metrics['regions']['active']['rmse_log10_decades'],
                      'on_error_percent': metrics['on_error_percent'],
                      'validation_file': str(folder/'rebuild_validation.json')}, indent=2))


if __name__ == '__main__':
    main()
