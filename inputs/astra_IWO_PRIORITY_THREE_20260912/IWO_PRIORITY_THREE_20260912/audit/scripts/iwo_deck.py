"""Render a self-contained ATLAS deck in explicit, ordered construction stages.

Rendering is deterministic and never executes the simulator. Each section owns
one responsibility. Output files remain relative to the isolated run directory.
"""
from __future__ import annotations

import math

import numpy as np

from iwo_model import (
    Geometry, Q, cox, equivalent_acceptor_gaussian, mobility_at, read_data, validate,
)


def section(number: int, title: str, lines: list[str]) -> list[str]:
    return ['', '# ' + '=' * 72, f'# {number:02d}. {title}', '# ' + '=' * 72, *lines]


def header(cfg: dict, key: str, smoke: bool) -> list[str]:
    g, c = cfg['geometry'], cfg['curves'][key]
    return [
        '# IWO TFT - generated electrical device deck',
        '# STATUS: UNCALIBRATED; latest code revision has not been rerun in ATLAS.',
        '# Direct device construction; no ATHENA process calibration is implied.',
        '# Geometry is from the uploaded screenshot; electronic values are seeds.',
        f'# Thickness: {c["thickness_nm"]} nm. Mode: {"TRAP-FREE SMOKE" if smoke else "FULL DOS SEED"}.',
        f'# Current output: terminal A for width={g["simulation_width_um"]} um; divide by this width once for A/um.',
        f'# Physical device: W={g["physical_width_um"]:g} um, L={g["channel_length_um"]:g} um.',
        f'# Thickness {c["thickness_nm"]} nm; effective Cox={cox(cfg):.9g} F/cm^2.',
        '# Ideal metal boundaries replace TiN50nm and Pd70nm metal volumes in DC.',
        '# The n+Si is screened by the continuous ideal TiN gate and is omitted.',
        '# Regions1/2 are IDENTICAL IWO; region2 regularizes sheet interface states.',
        '# Classical DD only. No confinement/BQP, dielectric tunnelling, stress kinetics.',
        f'# Mobility mode: {cfg["mobility"]["mode"]}.',
        '# Bias-indexed mobility updates remain unverified in the installed solver.',
        '# Edit config and regenerate; retain the input snapshot for every actual run.',
    ]


def mesh_lines(cfg: dict, geom: Geometry) -> list[str]:
    n = cfg['numerics']
    left, right = geom.source_end, geom.drain_start
    xs = [
        (0, .3), (left - .2, .05), (left, .01), (left + .2, .05),
        (left + 1, .2), ((left + right) / 2, .7), (right - 1, .2),
        (right - .2, .05), (right, .01), (right + .2, .05), (geom.right_edge, .3),
    ]
    ys = [
        (-geom.channel_thickness, min(.00025, geom.channel_thickness / 8)),
        (-geom.interface_depth, .0000625), (-geom.interface_depth / 2, .0000625),
        (0., .0000625), (geom.alumina_thickness, .00025), (geom.gate_y, .001),
    ]
    lines = [
        '# Coordinates and mesh spacings are in um. IWO/Al2O3 interface: y=0.',
        f'mesh width={cfg["geometry"]["simulation_width_um"]}',
    ]
    lines.extend(f'x.mesh loc={x:.10g} spac={spacing*n["x_mesh_scale"]:.10g}' for x, spacing in xs)
    lines.extend(f'y.mesh loc={y:.10g} spac={spacing*n["y_mesh_scale"]:.10g}' for y, spacing in ys)
    return lines


def region_lines(geom: Geometry) -> list[str]:
    xmax = geom.right_edge
    return [
        '# 1: bulk IWO; 2: interface-regularization IWO; 3: Al2O3; 4: HfO2.',
        f'region num=1 user.material=IWO x.min=0 x.max={xmax:.9g} y.min={-geom.channel_thickness:.10g} y.max={-geom.interface_depth:.10g}',
        f'region num=2 user.material=IWO x.min=0 x.max={xmax:.9g} y.min={-geom.interface_depth:.10g} y.max=0',
        '# OXIDE supplies insulating Poisson regions. Permittivities are set below.',
        '# SiO2 tunnelling parameters are not used to represent Al2O3 or HfO2.',
        f'region num=3 material=oxide x.min=0 x.max={xmax:.9g} y.min=0 y.max={geom.alumina_thickness:.10g}',
        f'region num=4 material=oxide x.min=0 x.max={xmax:.9g} y.min={geom.alumina_thickness:.10g} y.max={geom.gate_y:.10g}',
    ]


def electrode_lines(geom: Geometry) -> list[str]:
    top = -geom.channel_thickness
    return [
        '# Source and drain contact the top IWO surface; gate is below HfO2.',
        '# Source is the reference terminal; the drain ramp is positive.',
        f'electrode name=source x.min=0 x.max={geom.source_end:.9g} y.min={top:.10g} y.max={top:.10g}',
        f'electrode name=drain x.min={geom.drain_start:.9g} x.max={geom.right_edge:.9g} y.min={top:.10g} y.max={top:.10g}',
        f'electrode name=gate x.min=0 x.max={geom.right_edge:.9g} y.min={geom.gate_y:.10g} y.max={geom.gate_y:.10g}',
    ]


def doping_lines(cfg: dict, key: str) -> list[str]:
    density = cfg['curves'][key]['nd_cm3']
    return [
        '# Effective background ionized donor concentration, NOT W atomic %.',
        '# Keep structure/doping statements before material and model statements.',
        f'doping uniform n.type conc={density:.9g} region=1',
        f'doping uniform n.type conc={density:.9g} region=2',
    ]


def material_lines(cfg: dict, key: str) -> list[str]:
    s, c = cfg['shared'], cfg['curves'][key]
    return [
        '# USER.DEFAULT supplies a template. The overrides remain unvalidated seeds.',
        '# Inherited properties still require an audit before predictive use.',
        'material material=IWO user.group=semiconductor user.default=silicon \\',
        f' eg300={s["eg_eV"]:.9g} affinity={s["affinity_eV"]:.9g} permittivity={s["eps_iwo"]:.9g} \\',
        f' nc300={s["nc300_cm3"]:.9g} nv300={s["nv300_cm3"]:.9g} \\',
        f' mun={c["mu_band_cm2Vs"]:.9g} mup={s["hole_mu_cm2Vs"]:.9g} \\',
        f' taun0={s["taun_s"]:.9g} taup0={s["taup_s"]:.9g}',
        f'material region=3 permittivity={s["eps_al2o3"]:.9g}',
        f'material region=4 permittivity={s["eps_hfo2"]:.9g}',
    ]


def contact_lines(cfg: dict) -> list[str]:
    s = cfg['shared']
    lines = [f'contact name=gate workfunction={s["gate_workfunction_eV"]:.9g}']
    if cfg['contacts']['mode'] == 'schottky':
        workfunction = s['affinity_eV'] + cfg['contacts']['effective_electron_barrier_eV']
        lines.extend([
            '# Effective contact barrier hypothesis, not tabulated bulk Pd workfunction.',
            f'contact name=source workfunction={workfunction:.9g}',
            f'contact name=drain workfunction={workfunction:.9g}',
        ])
    else:
        lines.append('# No S/D workfunction => ideal Ohmic contacts. Unverified seed hypothesis.')
    return lines


def defect_lines(cfg: dict, key: str, region: int, interface: bool) -> list[str]:
    """Render the DOS card from the separately calculated Gaussian parameters."""
    c, s = cfg['curves'][key], cfg['shared']
    center, width, amplitude = equivalent_acceptor_gaussian(cfg, key, interface)
    capture = s['capture_cm2']
    return [
        f'# Region {region}: DOS amplitudes cm^-3 eV^-1; energy widths eV.',
        '# One moment-matched Gaussian is used if bulk and interface Gaussians overlap.',
        f'defects region={region} continuous numa={s["dos_levels_a"]} numd={s["dos_levels_d"]} \\',
        f' nta={c["nta_cm3_eV"]:.9g} wta={c["wta_eV"]:.9g} ntd={s["donor_tail_amplitude_cm3_eV"]:.9g} wtd=0.1 \\',
        f' nga={amplitude:.9g} ega={center:.9g} wga={width:.9g} \\',
        f' ngd={s["donor_gaussian_amplitude_cm3_eV"]:.9g} egd=2.8 wgd=0.1 \\',
        f' sigtae={capture:.9g} sigtah={capture:.9g} sigtde={capture:.9g} sigtdh={capture:.9g} \\',
        f' siggae={capture:.9g} siggah={capture:.9g} siggde={capture:.9g} siggdh={capture:.9g} \\',
        f' afile=acceptor_r{region}.dat dfile=donor_r{region}.dat',
    ]


def model_lines(cfg: dict, key: str, smoke: bool) -> list[str]:
    lines = [f'models fermi srh temp={cfg["shared"]["temperature_K"]:.9g} print']
    if smoke:
        lines.append('# SMOKE TEST: DOS disabled; this result is NOT a fit.')
    else:
        lines.extend(defect_lines(cfg, key, region=1, interface=False))
        lines.extend(defect_lines(cfg, key, region=2, interface=True))
    return lines


def solver_lines(cfg: dict, geom: Geometry, qf: float) -> list[str]:
    n = cfg['numerics']
    options = ''.join(
        f' {keyword}={n[field]:.9g}'
        for field, keyword in (
            ('continuity_absolute_tolerance', 'cr.toler'),
            ('current_absolute_tolerance', 'ir.tol'),
            ('continuity_relative_tolerance', 'cx.toler'),
        ) if field in n
    )
    if n.get('convergence_norm') == 'xand':
        options += ' xandrnorm weak=1'
    return [
        '# Fixed sheet charge: qf = -Cox * delta_Vfb / electron_charge [cm^-2].',
        f'interface qf={qf:.9g} x.min=0 x.max={geom.right_edge:.9g} y.min=-0.0000001 y.max=0.0000001',
        f'method newton trap maxtrap={n["maxtrap"]} itlimit={n["itlimit"]} climit={n["climit"]:.9g}' + options,
        'output con.band val.band e.mobility',
    ]


def gate_step(cfg: dict, key: str, voltage: float, smoke: bool) -> list[str]:
    lines = []
    if not smoke:
        lines.append(
            f'mobility mun={mobility_at(voltage,cfg,key):.10g} '
            f'mup={cfg["shared"]["hole_mu_cm2Vs"]:.9g}'
        )
    lines.append(f'solve vgate={voltage:.10g}')
    return lines


def initialization_lines(cfg: dict, key: str, first_gate: float, smoke: bool) -> list[str]:
    lines = ['solve init', 'save outf=equilibrium.str',
             '# Ramp gate, then drain, before opening the transfer log.']
    if first_gate != 0:
        steps = int(math.ceil(abs(first_gate) / cfg['numerics']['continuation_gate_step_V']))
        for voltage in np.linspace(0, first_gate, steps + 1)[1:]:
            lines.extend(gate_step(cfg, key, voltage, smoke))
    drain = cfg['shared']['vd_V']
    for voltage in np.linspace(0, drain, int(math.ceil(drain / .1)) + 1)[1:]:
        lines.append(f'solve vdrain={voltage:.10g}')
    return lines


def sweep_lines(cfg: dict, key: str, vg: np.ndarray, smoke: bool) -> list[str]:
    lines = [
        '# Every requested target is explicit. Continuation points are also logged.',
        '# The runner requires target coverage; missing endpoints must not be extrapolated.',
        'log outf=transfer.log',
    ]
    previous = float(vg[0])
    for index, voltage in enumerate(vg):
        steps = max(1, int(math.ceil(
            abs(voltage - previous) / cfg['numerics']['continuation_gate_step_V']
        )))
        values = np.linspace(previous, voltage, steps + 1)[1:] if index else np.array([voltage])
        for value in values:
            lines.extend(gate_step(cfg, key, value, smoke))
        previous = float(voltage)
    return [*lines, 'log off', 'save outf=final.str']


def export_lines() -> list[str]:
    return [
        '# Preserve signed terminal currents and achieved drain/source voltages.',
        '# These files belong to this run; never reuse exports from an earlier run.',
        'extract init infile="transfer.log"',
        'extract name="IdVg" curve(v."gate",i."drain") outfile="idvg.dat"',
        'extract name="IgVg" curve(v."gate",i."gate") outfile="igvg.dat"',
        'extract name="IsVg" curve(v."gate",i."source") outfile="isvg.dat"',
        'extract name="VdVg" curve(v."gate",v."drain") outfile="vdvg.dat"',
        'extract name="VsVg" curve(v."gate",v."source") outfile="vsvg.dat"',
        'quit',
    ]


def generate(cfg: dict, key: str, vg_values=None, smoke: bool = False) -> tuple[str, dict]:
    """Compose ordered sections; return deck text and metadata without file I/O writes."""
    validate(cfg, key)
    geom = Geometry.from_config(cfg, key)
    vg = read_data(cfg, key)[0] if vg_values is None else np.asarray(vg_values, dtype=float)
    if smoke:
        vg = np.array([-3., 0., 3.])
    if vg.ndim != 1 or len(vg) == 0 or not np.all(np.isfinite(vg)) or not np.all(np.diff(vg) > 0):
        raise ValueError('Gate grid must be finite, one-dimensional and increase strictly')
    qf = -cox(cfg) * cfg['curves'][key]['delta_vfb_V'] / Q
    stages = [
        ('SIMULATOR', ['go atlas']),
        ('MESH AND COORDINATES', mesh_lines(cfg, geom)),
        ('REGIONS AND DIELECTRIC STACK', region_lines(geom)),
        ('ELECTRODES', electrode_lines(geom)),
        ('BACKGROUND DONORS', doping_lines(cfg, key)),
        ('MATERIAL PARAMETERS', material_lines(cfg, key)),
        ('CONTACT BOUNDARY CONDITIONS', contact_lines(cfg)),
        ('TRANSPORT AND TRAP DISTRIBUTIONS', model_lines(cfg, key, smoke)),
        ('INTERFACE CHARGE AND NUMERICAL METHOD', solver_lines(cfg, geom, qf)),
        ('EQUILIBRIUM AND BIAS INITIALIZATION', initialization_lines(cfg, key, float(vg[0]), smoke)),
        ('TRANSFER SWEEP', sweep_lines(cfg, key, vg, smoke)),
        ('SIGNED CURRENT AND BIAS EXPORTS', export_lines()),
    ]
    lines = header(cfg, key, smoke)
    for number, (title, commands) in enumerate(stages, start=1):
        lines.extend(section(number, title, commands))
    meta = {
        'status': 'DECK_GENERATED_NOT_SIMULATED',
        'key': key,
        'thickness_nm': cfg['curves'][key]['thickness_nm'],
        'Cox_F_cm2': cox(cfg),
        'qf_cm2': qf,
        'vg_min_V': float(vg[0]),
        'vg_max_V': float(vg[-1]),
        'requested_points': len(vg),
        'smoke': smoke,
        'signed_current_normalization': f'ATLAS signed A / {cfg["geometry"]["simulation_width_um"]} um = target A/um',
        'native_gate_leakage_model': False,
    }
    return '\n'.join([*lines, '']), meta
