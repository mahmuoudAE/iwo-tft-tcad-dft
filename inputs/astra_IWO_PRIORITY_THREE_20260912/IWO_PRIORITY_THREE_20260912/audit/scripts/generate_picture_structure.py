"""Generate literal ATLAS decks for the pictured stack, without launching ATLAS.

These decks save geometry only: no SOLVE, transfer curve, or calibration.
The electrical generator and its recorded runs are intentionally separate.
"""
from __future__ import annotations

import json
from pathlib import Path

from iwo_model import ROOT, load_config


def render(cfg: dict, key: str) -> tuple[str, dict]:
    g, s, c = cfg['geometry'], cfg['shared'], cfg['curves'][key]
    channel = c['thickness_nm'] / 1000
    alumina = g['al2o3_nm'] / 1000
    hafnia_bottom = alumina + g['hfo2_nm'] / 1000
    gate_bottom = hafnia_bottom + g['gate_metal_nm'] / 1000
    contact_top = -channel - g['source_drain_metal_nm'] / 1000
    substrate_bottom = gate_bottom + .2  # Display truncation, not wafer thickness.
    overlap = g['contact_length_um']
    drain_start = overlap + g['channel_length_um']
    xmax = drain_start + overlap
    xmesh = [(0, .3), (overlap-.2, .05), (overlap, .02),
             (overlap+.2, .05), ((overlap+drain_start)/2, .7),
             (drain_start-.2, .05), (drain_start, .02),
             (drain_start+.2, .05), (xmax, .3)]
    ymesh = [(contact_top, .01), (-channel-.02, .005),
             (-channel-.005, .001), (-channel, min(channel/8, .00025)),
             (-channel*.75, min(channel/8, .00025)),
             (-channel*.5, min(channel/8, .00025)),
             (-channel*.25, min(channel/8, .00025)), (0, .00025),
             (alumina/2, .00025), (alumina, .00025),
             ((alumina+hafnia_bottom)/2, .001), (hafnia_bottom, .001),
             ((hafnia_bottom+gate_bottom)/2, .005), (gate_bottom, .005),
             (gate_bottom+.02, .005), (substrate_bottom, .025)]
    lines = [
        'go atlas',
        f'title IWO {c["thickness_nm"]:g} nm - pictured physical stack - geometry only',
        '# All coordinates in um. This deck constructs and saves a structure only.',
        '# No solve, no transfer prediction, and no claim of calibration.',
        '# Bottom to top: n+Si / TiN50nm / HfO2 15nm / Al2O3 2nm / IWO / Pd70nm.',
        '# TiN is represented by an ideal conductor; ATLAS Tin means elemental tin.',
        '# Pd uses the built-in Palladium display material; this sets no contact barrier.',
        f'# Physical W={g["physical_width_um"]:g} um; simulated slice W={g["simulation_width_um"]:g} um; L={g["channel_length_um"]:g} um.',
        f'# Assumed S/D overlap={overlap:g} um each. Substrate shown as a 200 nm slice.',
        '# The figure does not specify overlap, wafer thickness or substrate doping.',
        '# n+Si doping=1e19 cm^-3 is a display assumption. IWO values are unfitted seeds.',
        '', '# 1. Mesh: include every material and metal boundary explicitly.',
        f'mesh width={g["simulation_width_um"]:g}',
    ]
    lines += [f'x.mesh loc={x:.10g} spac={spacing:.10g}' for x, spacing in xmesh]
    lines += [f'y.mesh loc={y:.10g} spac={spacing:.10g}' for y, spacing in ymesh]
    lines += [
        '', '# 2. Complete stack. Regions cover the mesh without vertical gaps.',
        f'region num=1 material=Air x.min=0 x.max={xmax:g} y.min={contact_top:.10g} y.max={-channel:.10g}',
        f'region num=2 user.material=IWO x.min=0 x.max={xmax:g} y.min={-channel:.10g} y.max=0',
        f'region num=3 material=Al2O3 x.min=0 x.max={xmax:g} y.min=0 y.max={alumina:.10g}',
        f'region num=4 material=HfO2 x.min=0 x.max={xmax:g} y.min={alumina:.10g} y.max={hafnia_bottom:.10g}',
        '# Region 5 is the TiN gate volume, modeled electrically as an ideal conductor.',
        f'region num=5 material=Conductor x.min=0 x.max={xmax:g} y.min={hafnia_bottom:.10g} y.max={gate_bottom:.10g}',
        f'region num=6 material=Silicon x.min=0 x.max={xmax:g} y.min={gate_bottom:.10g} y.max={substrate_bottom:.10g}',
        '', '# 3. Electrodes. The Pd blocks replace Air within their rectangles.',
        f'electrode num=1 name=gate material=Conductor x.min=0 x.max={xmax:g} y.min={hafnia_bottom:.10g} y.max={gate_bottom:.10g}',
        f'electrode num=2 name=source material=Palladium x.min=0 x.max={overlap:g} y.min={contact_top:.10g} y.max={-channel:.10g}',
        f'electrode num=3 name=drain material=Palladium x.min={drain_start:g} x.max={xmax:g} y.min={contact_top:.10g} y.max={-channel:.10g}',
        '', '# 4. Doping and user material declaration. These values are not fitted.',
        f'doping uniform n.type conc={c["nd_cm3"]:.9g} region=2',
        'doping uniform n.type conc=1e19 region=6',
        'material material=IWO user.group=semiconductor user.default=silicon \\',
        f' eg300={s["eg_eV"]:.9g} affinity={s["affinity_eV"]:.9g} permittivity={s["eps_iwo"]:.9g} \\',
        f' nc300={s["nc300_cm3"]:.9g} nv300={s["nv300_cm3"]:.9g} \\',
        f' mun={c["mu_band_cm2Vs"]:.9g} mup={s["hole_mu_cm2Vs"]:.9g} \\',
        f' taun0={s["taun_s"]:.9g} taup0={s["taup_s"]:.9g}',
        f'material material=Al2O3 permittivity={s["eps_al2o3"]:.9g}',
        f'material material=HfO2 permittivity={s["eps_hfo2"]:.9g}',
        'material material=Air permittivity=1.0',
        '', '# 5. Save and inspect the geometry. No device equation is solved.',
        f'save outf=iwo_{key}nm_picture_structure.str',
        f'tonyplot iwo_{key}nm_picture_structure.str',
        'quit', '',
    ]
    metadata = {
        'status': 'GEOMETRY_DECK_NOT_RUN_IN_ATLAS', 'key': key,
        'channel_nm': c['thickness_nm'], 'channel_length_um': g['channel_length_um'],
        'physical_width_um': g['physical_width_um'], 'simulation_width_um': g['simulation_width_um'],
        'al2o3_nm': g['al2o3_nm'], 'hfo2_nm': g['hfo2_nm'],
        'gate_nm': g['gate_metal_nm'], 'source_drain_nm': g['source_drain_metal_nm'],
        'contact_overlap_um_assumed': overlap, 'substrate_slice_nm_assumed': 200,
        'substrate_doping_cm3_assumed': 1e19,
        'TiN_representation': 'Ideal Conductor; Tin must not be used for titanium nitride.',
        'x_bounds_um': [0, xmax],
        'y_boundaries_um': [contact_top, -channel, 0, alumina, hafnia_bottom, gate_bottom, substrate_bottom],
    }
    return '\n'.join(lines), metadata


def main() -> None:
    cfg = load_config(ROOT / 'config/local_baseline.json')
    for key in cfg['curves']:
        text, metadata = render(cfg, key)
        destination = ROOT / 'decks_picture' / f'iwo_{key}nm'
        destination.mkdir(parents=True, exist_ok=True)
        path = destination / f'iwo_{key}nm_picture_structure.in'
        path.write_text(text, encoding='ascii')
        (destination / 'structure_metadata.json').write_text(json.dumps(metadata, indent=2))
        print(path)


if __name__ == '__main__':
    main()
