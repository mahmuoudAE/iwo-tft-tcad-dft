"""IWO configuration, measurement inputs and explicitly provisional model formulas.

This module does not render ATLAS commands or launch external processes.
Lengths in configuration carry units in their names; ATLAS lengths are um.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EPS0 = 8.8541878128e-14  # F/cm
Q = 1.602176634e-19  # C


@dataclass(frozen=True)
class Geometry:
    """Derived coordinates in um; y=0 is the IWO/Al2O3 interface."""

    channel_thickness: float
    interface_depth: float
    alumina_thickness: float
    gate_y: float
    source_end: float
    drain_start: float
    right_edge: float

    @classmethod
    def from_config(cls, cfg: dict, key: str) -> Geometry:
        g = cfg['geometry']
        source_end = g['contact_length_um']
        drain_start = source_end + g['channel_length_um']
        alumina = g['al2o3_nm'] / 1000.0
        return cls(
            channel_thickness=cfg['curves'][key]['thickness_nm'] / 1000.0,
            interface_depth=g['interface_regularization_nm'] / 1000.0,
            alumina_thickness=alumina,
            gate_y=alumina + g['hfo2_nm'] / 1000.0,
            source_end=source_end,
            drain_start=drain_start,
            right_edge=drain_start + source_end,
        )


def load_config(path: str | Path | None = None) -> dict:
    return json.loads(Path(path or ROOT / 'config/model_seed.json').read_text())


def key_from_thickness(thickness: float) -> str:
    return str(float(thickness)).replace('.', 'p')


def cox(cfg: dict) -> float:
    """Series dielectric capacitance per area, F/cm^2."""
    g, s = cfg['geometry'], cfg['shared']
    return EPS0 / (
        g['hfo2_nm'] * 1e-7 / s['eps_hfo2']
        + g['al2o3_nm'] * 1e-7 / s['eps_al2o3']
    )


def read_data(cfg: dict, key: str) -> tuple[np.ndarray, np.ndarray]:
    path = Path(cfg['curves'][key]['data'])
    if not path.is_absolute():
        path = ROOT / path
    data = np.genfromtxt(path, delimiter=',', names=True)
    vg = np.atleast_1d(data['vg_V'])
    current = np.atleast_1d(data['id_A_per_um'])
    # These specific source curves contain positive values. Reject unexpected
    # signs instead of silently taking absolute values or rewriting the input.
    if (
        len(vg) < 3
        or not np.all(np.isfinite(vg))
        or not np.all(np.isfinite(current))
        or not np.all(current > 0)
        or not np.all(np.diff(vg) > 0)
    ):
        raise ValueError(f'Invalid measurement curve {path}')
    return vg, current


def mobility_at(vg: float, cfg: dict, key: str) -> float:
    """Proposed effective DC law; native bias-update behavior is unverified."""
    c = cfg['curves'][key]
    mode = cfg['mobility']['mode']
    if mode == 'constant':
        return float(c['mu_band_cm2Vs'])
    if mode != 'bias_indexed_effective':
        raise ValueError('Unknown mobility mode')
    kappa = cfg['mobility']['softplus_kappa_Vinv']
    overdrive = float(np.logaddexp(0.0, kappa * (vg - c['roll_reference_V'])) / kappa)
    return float(c['mu_band_cm2Vs'] / (1.0 + c['theta_Vinv'] * overdrive))


def _positive_fields(values: dict, fields: tuple[str, ...]) -> None:
    for field in fields:
        value = values[field]
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f'{field} must be finite and positive')


def validate(cfg: dict, key: str) -> None:
    if key not in cfg['curves']:
        raise KeyError(f'No thickness {key}')
    g, s, c = cfg['geometry'], cfg['shared'], cfg['curves'][key]
    _positive_fields(g, (
        'channel_length_um', 'contact_length_um', 'hfo2_nm', 'al2o3_nm',
        'simulation_width_um', 'interface_regularization_nm',
    ))
    _positive_fields(c, ('thickness_nm', 'mu_band_cm2Vs', 'wta_eV'))
    if g['interface_regularization_nm'] >= c['thickness_nm']:
        raise ValueError('Interface regularization depth must be below channel thickness')
    _positive_fields(s, (
        'eps_iwo', 'eps_hfo2', 'eps_al2o3', 'eg_eV', 'nc300_cm3', 'nv300_cm3',
        'temperature_K', 'vd_V', 'deep_acceptor_width_eV', 'interface_acceptor_width_eV',
    ))
    _positive_fields(cfg['numerics'], (
        'x_mesh_scale', 'y_mesh_scale', 'continuation_gate_step_V', 'climit',
    ))
    for field in ('continuity_absolute_tolerance', 'current_absolute_tolerance',
                  'continuity_relative_tolerance'):
        if field in cfg['numerics']:
            _positive_fields(cfg['numerics'], (field,))
    for field in ('theta_Vinv', 'nd_cm3', 'nta_cm3_eV', 'nga_cm3_eV',
                  'interface_gaussian_peak_cm2_eV'):
        if not math.isfinite(c[field]) or c[field] < 0:
            raise ValueError(f'{field} must be finite and nonnegative')
    if not math.isfinite(c['delta_vfb_V']):
        raise ValueError('delta_vfb_V must be finite')
    if cfg['contacts']['mode'] not in ('ohmic', 'schottky'):
        raise ValueError('contacts.mode must be ohmic or schottky')
    if cfg['mobility']['mode'] not in ('constant', 'bias_indexed_effective'):
        raise ValueError('Unknown mobility mode')
    _positive_fields(cfg['mobility'], ('softplus_kappa_Vinv',))


def equivalent_acceptor_gaussian(cfg: dict, key: str, interface: bool) -> tuple[float, float, float]:
    """Return center, width and peak amplitude for the provisional DOS approximation.

    ATLAS Gaussian convention: exp(-((E-E0)/W)^2), variance W^2/2.
    Sheet amplitudes are divided by regularization depth in cm. The resulting
    bulk/interface Gaussian approximation preserves area and two moments;
    this is not proof that the approximation is physically adequate.
    """
    c, s, g = cfg['curves'][key], cfg['shared'], cfg['geometry']
    bulk_amplitude = c['nga_cm3_eV']
    bulk_width = s['deep_acceptor_width_eV']
    bulk_center = s['deep_acceptor_center_from_Ec_eV']
    interface_amplitude = (
        c['interface_gaussian_peak_cm2_eV'] / (g['interface_regularization_nm'] * 1e-7)
        if interface else 0.0
    )
    interface_width = s['interface_acceptor_width_eV']
    interface_center = s['interface_acceptor_center_from_Ec_eV']
    mass = bulk_amplitude * bulk_width + interface_amplitude * interface_width
    if mass > 0:
        center = (
            bulk_amplitude * bulk_width * bulk_center
            + interface_amplitude * interface_width * interface_center
        ) / mass
        variance = (
            bulk_amplitude * bulk_width * (bulk_width**2 / 2 + (bulk_center - center)**2)
            + interface_amplitude * interface_width
            * (interface_width**2 / 2 + (interface_center - center)**2)
        ) / mass
        width = math.sqrt(2 * variance)
        amplitude = mass / width
    else:
        center, width, amplitude = bulk_center, bulk_width, 0.0
    return center, width, amplitude
