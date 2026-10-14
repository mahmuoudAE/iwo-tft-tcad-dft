"""ElectronicData: one container for eigenvalues, weights, occupations and projections, whatever the source.

Sources (proj_kind):
  'exact'  data-file-schema.xml + atomic_proj.xml + state map (the registered A14 export; nspin 1 and 2)
  'table'  D-24 AFS tables occ_kw_final.dat + proj_atoms_final.dat (atom weights rounded to 1e-6) + scf.in geometry;
           nspin = 2 tables are malformed by the D-24 exporter and are reconstructed for DIAGNOSTICS ONLY (a section-1
           unresolved condition): spin results need the XML pair
  'text'   pw.x output + projwfc.x printout + pw.x input. The printout omits components below 0.001, so atom weights
           and PR_n are APPROXIMATE: every PR-based result from this source is marked unresolved. Used for the
           crystalline reproduction only.
Array layout: [spin, k, band] (band index 0-based in arrays, reported 1-based); atom weights [spin, k, band, atom].
"""
import os

import numpy as np

from . import qeio
from .geometry import Structure
from .register import RY_EV


class ElectronicData:
    def __init__(self, *, nspin, e_ev, wk_raw, nelec, ef_ev, smearing, degauss_ev, occupations_kind, f_qe=None,
                 atom_w=None, w5d=None, compl=None, proj_kind='exact', species=None, etot_ry=None, sources=None,
                 warnings=None, settings=None, diagnostic_only=None):
        self.nspin = int(nspin)
        self.e = np.asarray(e_ev, dtype=float)
        if self.e.ndim != 3 or self.e.shape[0] != self.nspin:
            raise ValueError('eigenvalues must be [spin, k, band]')
        self.nks, self.nbnd = self.e.shape[1], self.e.shape[2]
        wk_raw = np.asarray(wk_raw, dtype=float).reshape(self.nspin, self.nks)
        if (wk_raw <= 0).any():
            raise ValueError('non-positive k-weight')
        # register section 1 (A16): normalised k-weight including the spin factor (2 for nspin 1, 1 per channel for 2)
        self.w = wk_raw / wk_raw.sum(axis=1, keepdims=True) * (2.0 / self.nspin)
        self.wk_raw = wk_raw
        self.nelec = float(nelec)
        ef = np.atleast_1d(np.asarray(ef_ev if ef_ev is not None else [np.nan], dtype=float))
        self.ef = np.repeat(ef, self.nspin) if ef.size == 1 else ef
        self.smearing = smearing
        self.degauss_ev = float(degauss_ev or 0.0)
        self.occupations_kind = occupations_kind
        self.f_qe = None if f_qe is None else np.asarray(f_qe, dtype=float)
        self.atom_w = None if atom_w is None else np.asarray(atom_w, dtype=float)
        self.w5d = None if w5d is None else np.asarray(w5d, dtype=float)
        self.compl = None if compl is None else np.asarray(compl, dtype=float)
        self.proj_kind = proj_kind
        self.species = list(species) if species is not None else None
        self.etot_ry = etot_ry
        self.sources = sources or {}
        self.settings = settings or {}
        self.diagnostic_only = diagnostic_only    # None, or the reason why this data may not feed a primary score
        self.warnings = list(warnings or [])
        if self.atom_w is not None:
            if self.atom_w.shape[:3] != self.e.shape:
                raise ValueError(f'atom weights {self.atom_w.shape[:3]} do not match eigenvalues {self.e.shape}')
            if self.species is not None and self.atom_w.shape[3] != len(self.species):
                raise ValueError('atom weights and species disagree in the number of atoms')

    @property
    def nat(self):
        return None if self.atom_w is None else self.atom_w.shape[3]


def _src(paths):
    return {os.path.basename(p): {'path': os.path.abspath(p), 'sha256': qeio.sha256(p)} for p in paths if p}


K_COORD_TOL = 1e-5        # k coordinates (2 pi / alat, cartesian) printed with >= 8 digits by QE
K_WEIGHT_TOL = 1e-6       # normalised k-weight agreement


def pair_k_points(s, p):
    """rc6: pair the atomic_proj k blocks with the data-file-schema k-points by COORDINATES. Same order: accepted;
    otherwise a unique coordinate match in every spin channel reorders the projection blocks (a verified remapping);
    anything else (missing, ambiguous or duplicated coordinates) is refused. Returns (p, remapping or None)."""
    xs, xp = np.asarray(s.get('xk')), np.asarray(p.get('xk'))
    if xs.ndim != 2 or xp.ndim != 3 or xp.shape[1:] != xs.shape:
        raise ValueError('k coordinates missing or of another shape: k pairing not verified')
    perm_all = []
    for ch in range(xp.shape[0]):
        if np.max(np.abs(xp[ch] - xs)) <= K_COORD_TOL:
            perm_all.append(list(range(xs.shape[0])))
            continue
        perm = []
        for k in range(xs.shape[0]):
            hit = np.where(np.max(np.abs(xp[ch] - xs[k]), axis=1) <= K_COORD_TOL)[0]
            if hit.size != 1:
                raise ValueError(f'k-point {k + 1} of data-file-schema matched by {hit.size} atomic_proj blocks '
                                 f'(spin {ch + 1}): k pairing not verified')
            perm.append(int(hit[0]))
        if sorted(perm) != list(range(xs.shape[0])):
            raise ValueError('atomic_proj k blocks do not map one-to-one onto data-file-schema k-points')
        perm_all.append(perm)
    if all(pm == list(range(xs.shape[0])) for pm in perm_all):
        return p, None
    q = dict(p)
    for key in ('atom_w', 'w5d', 'compl', 'e_ev', 'wk', 'xk'):
        arr = np.asarray(p[key])
        q[key] = np.stack([arr[ch][perm_all[ch]] for ch in range(arr.shape[0])])
    return q, perm_all


# ---------------------------------------------------------------- builders
def from_xml(schema_path, proj_path, map_path):
    """The registered A14 export: data-file-schema.xml + atomic_proj.xml + state map."""
    s = qeio.read_schema(schema_path)
    smap = qeio.read_state_map(map_path)
    atom_of, is_w5d = qeio.map_matrices(smap, s['species'])
    p = qeio.read_atomic_proj(proj_path, atom_of, is_w5d, len(s['species']))
    warn = []
    if (p['nspin'], p['nks'], p['nbnd']) != (s['nspin'], s['nks'], s['nbnd']):
        raise ValueError(f'atomic_proj (nspin, nks, nbnd) {(p["nspin"], p["nks"], p["nbnd"])} != '
                         f'data-file-schema {(s["nspin"], s["nks"], s["nbnd"])}')
    p, remap = pair_k_points(s, p)
    if remap:
        warn.append(f'atomic_proj k blocks reordered by verified coordinates: {remap}')
    de = float(np.max(np.abs(p['e_ev'] - s['e_ev'])))
    if de > 1e-4:
        raise ValueError(f'atomic_proj and data-file-schema eigenvalues differ by {de:.2e} eV (spin/k order?)')
    # k-weights: proportional within each channel, or refused (rc6: no warning-only pairing)
    r = p['wk'] / p['wk'].sum(axis=1, keepdims=True) - s['wk_raw'] / s['wk_raw'].sum(axis=1, keepdims=True)
    if np.max(np.abs(r)) > K_WEIGHT_TOL:
        raise ValueError(f'atomic_proj k-weights are not proportional to data-file-schema ({np.max(np.abs(r)):.1e}): '
                         'k pairing not verified')
    st = Structure(s['species'], s['positions_A'], s['cell_A'], s['labels'])
    data = ElectronicData(nspin=s['nspin'], e_ev=s['e_ev'], wk_raw=s['wk_raw'], nelec=s['nelec'], ef_ev=s['ef_ev'],
                          smearing=s['smearing'], degauss_ev=s['degauss_ev'], occupations_kind=s['occupations_kind'],
                          f_qe=s['f_qe'], atom_w=p['atom_w'], w5d=p['w5d'], compl=p['compl'], proj_kind='exact',
                          species=s['species'], etot_ry=s['etot_ry'], sources=_src([schema_path, proj_path, map_path]),
                          warnings=warn, settings=s['settings'])
    data.sources['_max_abs_e_proj_vs_schema_eV'] = de
    data.sources['_atomic_proj_header'] = p['header']
    return data, st


def from_tables(directory, job='final', scf_in=None, scf_out=None):
    """The D-24 AFS tables, with the geometry from scf.in (and the total energy from scf.out when present)."""
    t = qeio.read_tables(directory, job)
    scf_in = scf_in or qeio.first_existing(directory, ['scf.in'])
    if not scf_in:
        raise FileNotFoundError(f'{directory}: scf.in (geometry) missing')
    g = qeio.read_pw_in(scf_in)
    if g['species'] != t['species']:
        raise ValueError('scf.in species order differs from proj_atoms_final.dat')
    scf_out = scf_out or qeio.first_existing(directory, ['scf.out'])
    etot, conv = None, None
    if scf_out:
        try:
            o = qeio.read_pw_out(scf_out)
            etot, conv = o['etot_ry'], o['converged']
        except Exception:                      # noqa: BLE001  (total energy is optional here)
            etot = None
    settings = qeio.pw_in_settings(scf_in)
    settings['scf_converged'] = conv
    # the width and family actually used are those of the occ_kw header (the occupations are recomputed with them);
    # scf.in may restate them but must not contradict them (rc3)
    t_kind = 'smearing' if t['smearing'] and t['smearing'] != 'none' else 'fixed'
    t_w = round(t['degauss_ev'] / RY_EV, 10) if t_kind == 'smearing' else None
    if settings.get('degauss_Ry') is not None and t_w is not None and abs(settings['degauss_Ry'] - t_w) > 1e-9:
        raise ValueError(f'table width {t_w} Ry (occ_kw header) disagrees with scf.in degauss {settings["degauss_Ry"]} Ry')
    if settings.get('smearing') and t_kind == 'smearing':
        from .smearing import ngauss_of
        if ngauss_of(settings['smearing']) != ngauss_of(t['smearing']):
            raise ValueError(f'table smearing {t["smearing"]} disagrees with scf.in smearing {settings["smearing"]}')
    settings['degauss_Ry'] = t_w
    settings['smearing'] = t['smearing'] if t_kind == 'smearing' else None
    settings['occupations'] = t_kind
    st = Structure(g['species'], g['positions_A'], g['cell_A'], g['labels'])
    warn = ['lsda tables reconstructed from the D-24 layout (spin-down rows: occ ibnd > nbnd, proj ik > nks)']\
        if t['lsda_reconstructed'] else []
    kind = 'smearing' if t['smearing'] and t['smearing'] != 'none' else 'fixed'
    data = ElectronicData(nspin=t['nspin'], e_ev=t['e_ev'], wk_raw=t['wk_norm'], nelec=t['nelec'], ef_ev=t['ef_ev'],
                          smearing=t['smearing'] if kind == 'smearing' else None, degauss_ev=t['degauss_ev'],
                          occupations_kind=kind, f_qe=t['f_qe'], atom_w=t['atom_w'], w5d=t['w5d'], compl=t['compl'],
                          proj_kind='table', species=t['species'], etot_ry=etot,
                          sources=_src(t['paths'] + [scf_in] + ([scf_out] if scf_out else [])), warnings=warn,
                          settings=settings,
                          diagnostic_only=('D-24 lsda tables (spin-down rows reconstructed): diagnostic only; the XML '
                                           'pair is required for nspin = 2') if t['lsda_reconstructed'] else None)
    return data, st


def from_text(scf_in, scf_out, projwfc_out):
    """Crystalline reference runs: pw.x input/output and the projwfc.x printout (APPROXIMATE projections)."""
    g = qeio.read_pw_in(scf_in)
    o = qeio.read_pw_out(scf_out)
    smap = qeio.read_state_map(projwfc_out)
    atom_of, is_w5d = qeio.map_matrices(smap, g['species'])
    p = qeio.read_projwfc_text(projwfc_out, atom_of, is_w5d, len(g['species']))
    if o['nspin'] != 1:
        raise ValueError('text source: nspin = 1 only')
    if (p['nks'], p['nbnd']) != (o['nks'], o['nbnd']):
        raise ValueError(f'projwfc text {(p["nks"], p["nbnd"])} != pw.x output {(o["nks"], o["nbnd"])}')
    de = float(np.max(np.abs(p['e_ev'] - o['e_ev'])))
    if de > 2e-4:
        raise ValueError(f'projwfc and pw.x eigenvalues differ by {de:.2e} eV')
    st = Structure(g['species'], g['positions_A'], g['cell_A'], g['labels'])
    kind = 'smearing' if o['smearing'] else 'fixed'
    data = ElectronicData(nspin=1, e_ev=o['e_ev'], wk_raw=o['wk_raw'], nelec=o['nelec'], ef_ev=o['ef_ev'],
                          smearing=o['smearing'], degauss_ev=o['degauss_ev'], occupations_kind=kind, f_qe=o['f_qe'],
                          atom_w=p['atom_w'], w5d=p['w5d'], compl=p['compl'], proj_kind='text', species=g['species'],
                          etot_ry=o['etot_ry'], sources=_src([scf_in, scf_out, projwfc_out]),
                          settings=dict(qeio.pw_in_settings(scf_in), scf_converged=o['converged']),
                          warnings=['text projections: components < 0.001 are not printed; atom weights and PR_n are '
                                    'approximate'])
    data.sources['_homo_lumo_ev'] = o['homo_lumo_ev']
    return data, st


# ---------------------------------------------------------------- export directory discovery
def attach_lineage(d, dirs, job='final'):
    """The run lineage (D-24 lineage_<job>.dat) is consumed provenance: it is bound by the certificate and supplies
    the pseudopotential sha256 that the certificate must reproduce."""
    lp = qeio.first_existing(dirs, [f'lineage_{job}.dat'])
    if lp:
        from .certify import parse_lineage
        d.sources[os.path.basename(lp)] = {'path': os.path.abspath(lp), 'sha256': qeio.sha256(lp)}
        d.settings['pseudo_sha256'] = parse_lineage(lp)



SCHEMA_NAMES = ['data-file-schema.xml', 'data-file-schema_final.xml', 'tmp/slab.save/data-file-schema.xml',
                'save/slab.save/data-file-schema.xml']
PROJ_NAMES = ['atomic_proj.xml', 'atomic_proj_final.xml', 'tmp/slab.save/atomic_proj.xml']
MAP_NAMES = ['projwfc_map_final.dat', 'projwfc_final.out', 'projwfc_final_summary.out']


def load_export(directory, source='auto', job='final'):
    """Choose the source in a FINAL export directory: the XML pair (registered) if complete, else the AFS tables.
    Returns (data, structure, source_used, notes)."""
    notes = []
    dirs = [directory] if isinstance(directory, (str, os.PathLike)) else list(directory)
    sch = prj = None
    if source in ('auto', 'xml'):
        # the schema and atomic_proj of one run come from ONE search root: the first root holding either of them
        # decides; its partner in another root is refused (two runs), its absence everywhere means 'pair incomplete'
        found = [(d, qeio.first_existing([d], SCHEMA_NAMES), qeio.first_existing([d], PROJ_NAMES)) for d in dirs]
        first = next((x for x in found if x[1] or x[2]), None)
        if first is not None and first[1] and first[2]:
            sch, prj = first[1], first[2]
        elif first is not None:
            other = any((x[2] if first[1] else x[1]) for x in found)
            if other:
                raise ValueError(f'run files split across directories: {first[0]} holds only '
                                 f'{"data-file-schema" if first[1] else "atomic_proj"}, the partner lies elsewhere')
    mp = qeio.first_existing(dirs, MAP_NAMES)
    if source in ('auto', 'xml') and sch and prj and mp:
        d, st = from_xml(sch, prj, mp)
        attach_lineage(d, dirs, job)
        return d, st, 'xml', notes
    if source == 'xml':
        raise FileNotFoundError(f'{directory}: XML pair incomplete (schema {bool(sch)}, atomic_proj {bool(prj)}, '
                                f'map {bool(mp)})')
    if source in ('auto', 'table'):
        if source == 'auto':
            notes.append('XML pair not complete in the export: AFS tables used (atom weights rounded to 1e-6)')
        occ_p = qeio.first_existing(dirs, [f'occ_kw_{job}.dat'])
        pa_p = qeio.first_existing(dirs, [f'proj_atoms_{job}.dat'])
        if occ_p and pa_p and os.path.dirname(occ_p) != os.path.dirname(pa_p):
            raise ValueError('run files split across directories: occ_kw and proj_atoms tables')
        d, st = from_tables(dirs, job)
        attach_lineage(d, dirs, job)
        return d, st, 'table', notes
    if source == 'text':
        dirs = [directory] if isinstance(directory, (str, os.PathLike)) else list(directory)
        scf_in = qeio.first_existing(dirs, ['scf.in'])
        scf_out = qeio.first_existing(dirs, ['scf.out'])
        cands = [f for d in dirs for f in sorted(os.listdir(d)) if f.startswith('projwfc_') and '.out' in f
                 and 'summary' not in f]
        pw = qeio.first_existing(dirs, [f'projwfc_{job}.out'] + cands)
        d, st = from_text(scf_in, scf_out, pw)
        return d, st, 'text', notes
    raise ValueError(f'unknown source {source!r}')
