"""Run isolated numerical controls sequentially through the existing budget guard."""
import argparse
import copy
import json

from rebuild_model import ROOT, load
from rebuild_trial import evaluate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', required=True)
    p.add_argument('--key', default='2p0')
    p.add_argument('--label', required=True)
    p.add_argument('--kinds', nargs='+', default=['width', 'xmesh', 'ymesh'])
    p.add_argument('--timeout', type=int, default=900,
                   help='Recorded per-run seconds; still capped by the approved session deadline')
    a = p.parse_args()
    if a.timeout <= 0:
        p.error('--timeout must be positive')
    base = load(a.config)
    records = []
    output = ROOT/'results/rebuild_20260912'/f'{a.label}_numerics.json'
    if output.exists():
        raise ValueError('Use a new label; existing experiment index is preserved')
    for kind in a.kinds:
        cfg = copy.deepcopy(base)
        n, d = cfg['numerics'], cfg['defects']
        if kind == 'width':
            cfg['geometry']['simulation_width_um'] *= 2
        elif kind == 'xmesh':
            n['x_spacing_um'] /= 2
            n['contact_edge_spacing_um'] /= 2
        elif kind == 'ymesh':
            for name in ('channel_intervals', 'alumina_intervals', 'hafnia_intervals'):
                n[name] *= 2
        elif kind == 'dos':
            if not d['bulk'] and not d['interface']:
                raise ValueError('No enabled DOS to refine')
            for family in ('bulk', 'interface'):
                if d[family]:
                    for carrier in ('a', 'd'):
                        d[f'{family}_levels_{carrier}'] *= 2
        else:
            raise ValueError(kind)
        config_path = ROOT/'config'/f'{a.label}_{kind}.json'
        if config_path.exists():
            raise ValueError('Candidate config already exists')
        config_path.write_text(json.dumps(cfg, indent=2))
        try:
            folder, valid = evaluate(cfg, a.key, f'{a.label}_{kind}', timeout=a.timeout)
            records.append(dict(kind=kind, folder=str(folder), config=str(config_path), validation=valid))
        except Exception as exc:
            records.append(dict(kind=kind, config=str(config_path), failure=str(exc)))
            output.write_text(json.dumps(records, indent=2))
            raise
        output.write_text(json.dumps(records, indent=2))
        print(f'Completed {kind}: {folder}', flush=True)


if __name__ == '__main__':
    main()
