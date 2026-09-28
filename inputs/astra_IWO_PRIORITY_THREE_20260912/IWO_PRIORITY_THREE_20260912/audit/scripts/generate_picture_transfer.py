"""Add a trap-free transfer test to the pictured stack; never launch ATLAS."""
from __future__ import annotations

import json

import numpy as np

from generate_picture_structure import render as render_structure
from iwo_model import ROOT, load_config, read_data, validate


def render(cfg: dict, key: str) -> tuple[str, dict]:
    validate(cfg, key)
    if cfg['mobility']['mode'] != 'constant':
        raise ValueError('The pictured-stack transfer baseline requires constant mobility')
    if cfg['contacts']['mode'] != 'ohmic':
        raise ValueError('This baseline implements the explicitly assumed Ohmic S/D contacts only')
    geometry, metadata = render_structure(cfg, key)
    # Retain the entire geometry; replace only the old save/plot/quit ending.
    text = geometry.split('# 5. Save and inspect the geometry.')[0]
    text = text.replace('pictured physical stack - geometry only', 'pictured stack - uncalibrated transfer baseline')
    text = text.replace('# All coordinates in um. This deck constructs and saves a structure only.',
                        '# All coordinates in um. Transfer test: constant mobility, no DOS traps.')
    text = text.replace('# No solve, no transfer prediction, and no claim of calibration.',
                        '# NOT EXECUTED OR CALIBRATED. Convergence and current accounting require verification.')
    bottom = metadata['y_boundaries_um'][-1]
    right = metadata['x_bounds_um'][-1]
    substrate = (
        '# Additional backside terminal on the explicit Si substrate.\n'
        f'electrode num=4 name=substrate x.min=0 x.max={right:g} y.min={bottom:.10g} y.max={bottom:.10g}\n\n'
    )
    text = text.replace('# 4. Doping and user material declaration.', substrate + '# 4. Doping and user material declaration.')
    n, s = cfg['numerics'], cfg['shared']
    targets, _ = read_data(cfg, key)
    label = f'iwo_{key}nm_transfer'
    options = ''.join(
        f' {keyword}={n[field]:.9g}' for field, keyword in (
            ('continuity_absolute_tolerance', 'cr.toler'),
            ('current_absolute_tolerance', 'ir.tol'),
            ('continuity_relative_tolerance', 'cx.toler'),
        ) if field in n
    )
    lines = [
        '# 5. Electrical boundary conditions and transport assumptions.',
        '# Pd/IWO is assumed Ohmic here; no measured barrier is claimed.',
        '# Gate workfunction is an unfitted seed and also affects the TiN/Si interface.',
        f'contact name=gate workfunction={s["gate_workfunction_eV"]:.9g}',
        '# Assume the wafer backside is connected to the gate bias.',
        '# COMMON ties voltages; omit SHORT so substrate current remains separately observable.',
        'contact name=substrate common=gate',
        '# No interface/bulk DOS, tunnelling or quantum model in this debug baseline.',
        f'models srh fermi temp={s["temperature_K"]:.9g} print',
        f'method newton trap maxtrap={n["maxtrap"]} itlimit={n["itlimit"]} climit={n["climit"]:.9g}' + options,
        'output con.band val.band e.mobility',
        '', '# 6. Equilibrium, then gate and drain continuation.',
        'solve init',
        f'save outf={label}_equilibrium.str',
        'solve vsource=0',
    ]
    steps = int(np.ceil(abs(targets[0]) / n['continuation_gate_step_V']))
    lines += [f'solve vgate={v:.10g}' for v in np.linspace(0, targets[0], steps + 1)[1:]]
    drain_steps = int(np.ceil(s['vd_V'] / .1))
    lines += [f'solve vdrain={v:.10g}' for v in np.linspace(0, s['vd_V'], drain_steps + 1)[1:]]
    lines += [f'save outf={label}_off.str', '',
              '# 7. Transfer curve. All 121 workbook gate targets are explicit.',
              f'log outf={label}.log']
    lines += [f'solve vgate={v:.10g}' for v in targets]
    lines += ['log off', f'save outf={label}_on.str', '',
              '# 8. Export signed terminal currents and actual terminal biases.',
              '# Current conservation must include source, drain, gate AND substrate.',
              '# Divide raw A by simulated width once for A/um; width=1 here.',
              f'extract init infile="{label}.log"']
    exports = {}
    for terminal in ('drain', 'source', 'gate', 'substrate'):
        filename = f'{label}_{terminal}_signed.dat'
        lines.append(f'extract name="{terminal}_signed" curve(v."gate",i."{terminal}") outfile="{filename}"')
        exports[f'{terminal}_signed'] = filename
    for terminal in ('drain', 'source', 'substrate'):
        filename = f'{label}_{terminal}_bias.dat'
        lines.append(f'extract name="{terminal}_bias" curve(v."gate",v."{terminal}") outfile="{filename}"')
        exports[f'{terminal}_bias'] = filename
    absolute = f'{label}_drain_magnitude.dat'
    lines += [
        '# Magnitude-only plotting copy; signed data above remains authoritative.',
        '# No current offset/floor is added. A log axis cannot display zero current.',
        f'extract name="drain_magnitude" curve(v."gate",abs(i."drain")) outfile="{absolute}"',
        '', '# 9. Display EVERY saved structure and log, plus the drain-magnitude curve.',
        f'tonyplot {label}_equilibrium.str',
        f'tonyplot {label}_off.str',
        f'tonyplot {label}_on.str',
        f'tonyplot {label}.log',
        f'tonyplot {absolute}',
        'quit', '',
    ]
    metadata.update(
        status='TRANSFER_DECK_GENERATED_NOT_RUN_NOT_CALIBRATED',
        electrical_model='Trap-free constant-mobility debug baseline',
        substrate_connection='Backside tied to gate voltage; distinct current export; assumed wiring',
        sd_contacts='Ohmic assumption; not established by Palladium display material',
        gate_workfunction_eV=s['gate_workfunction_eV'],
        gate_targets_V=targets.tolist(), vd_V=s['vd_V'], current_exports=exports,
        drain_magnitude_export=absolute,
        current_conservation='Id + Is + Ig + Isub; preserve separate terminal signs',
        legacy_three_terminal_validator_applicable=False,
    )
    return text + '\n'.join(lines), metadata


def main() -> None:
    cfg = load_config(ROOT / 'config/local_baseline.json')
    for key in cfg['curves']:
        text, metadata = render(cfg, key)
        destination = ROOT / 'decks_picture_transfer' / f'iwo_{key}nm'
        destination.mkdir(parents=True, exist_ok=True)
        path = destination / f'iwo_{key}nm_transfer.in'
        path.write_text(text, encoding='ascii')
        (destination / 'transfer_metadata.json').write_text(json.dumps(metadata, indent=2))
        print(path)


if __name__ == '__main__':
    main()
