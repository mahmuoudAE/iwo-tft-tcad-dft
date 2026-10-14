"""Register section 1 (frozen 2026-10-10, A16, A24) for one cell.

Implemented exactly as written (quotes from HYPOTHESIS_REGISTER.md section 1):
  * Projections: "p_i is the Loewdin projection summed over all orbitals of atom i. It is then normalised so that
    sum_i p_i = 1. Completeness: the unnormalised sum (1 - spilling) is reported per state. A state with completeness
    < 0.90 is flagged. A test that rests on flagged states is unresolved."
  * Localisation: "PR_n = 1 / (N sum_i p_i^2)", N = all atoms of the cell (H and oxide atoms included); a film-only PR_n
    is reported, not used. "Extended: PR_n >= 0.20. Localised: PR_n <= 0.05."
  * Occupations and k-weights: "each state contributes f_nk w_k", w_k normalised with the spin factor, f_nk from the
    final SCF's own smearing function.
  * Host edge: "lowest eigenvalue over all k of any state that is above band index N_v; PR_n >= 0.20; interior-weighted,
    with an interior weight of at least 0.8 x the interior atom fraction"; unresolved "when no state qualifies within
    1.0 eV above the lowest state above N_v; or the interior region contains no atoms".
  * Host valence edge: "the highest eigenvalue over all k of any state with PR_n >= 0.20 and an interior weight of at
    least 0.8 x the interior atom fraction, at or below band N_v".
  * Accounting: "N_v = (N_el - N_ex)/2 ... Excess electrons: all occupation in bands above N_v, at any energy ...
    their sum must equal N_ex within 0.02 e. Otherwise the accounting is unresolved." Fractions use N_ex.
  * Alignment: "A planar-averaged potential plateau over the interior region, with a standard deviation of 0.05 eV or
    less. Without such a plateau ... the alignment is unresolved".
For nspin = 2 every (spin, k, band) is a state; w_k carries spin factor 1 per channel; N_v applies to each channel.
"""
import numpy as np

from . import register as R
from .geometry import detect_mode, regions, z_in_frame
from .smearing import occupations


def box_average(z, v, width):
    """Centred box average of width `width` (unit of z) of a periodic function sampled on the uniform average.x grid
    (period = number of points x step), exact width through the cumulative trapezoid integral."""
    z = np.asarray(z, dtype=float)
    v = np.asarray(v, dtype=float)
    dz = z[1] - z[0]
    L = len(z) * dz
    zz = np.concatenate([z - L, z, z + L, [z[0] + 2 * L]])
    vv = np.concatenate([v, v, v, [v[0]]])
    F = np.concatenate([[0.0], np.cumsum(0.5 * (vv[1:] + vv[:-1]) * np.diff(zz))])
    return (np.interp(z + width / 2, zz, F) - np.interp(z - width / 2, zz, F)) / width


def macro_average(z, v, window):
    """Periodic box average of v over `window` (same length unit as z); the form used by the crystalline two-step
    alignment (dft_to_tcad_extract.macro), kept identical so that the reproduction is exact."""
    dz = z[1] - z[0]
    n = max(1, int(round(window / dz)))
    ext = np.concatenate([v[-n:], v, v[:n]])
    return np.convolve(ext, np.ones(n) / n, mode='same')[n:-n]


class Section1:
    """All section-1 quantities of one cell. States are flattened over (spin, k, band)."""

    def __init__(self, data, st, name=None, nex=None, mode='auto', avg=None, w5d_convention='normalised',
                 manifest=None):
        """manifest: the composition manifest of a VALIDATED certificate (or None); nex: explicit override for
        reference / legacy runs only (unverified)."""
        self.data, self.st, self.name = data, st, name
        self.warnings = list(data.warnings)
        self.reasons = []                      # section-1 unresolved conditions that affect every test of this cell
        if data.diagnostic_only:
            self.reasons.append(data.diagnostic_only)
        if data.settings.get('scf_converged') is not True:
            self.reasons.append(f'final SCF convergence not shown (scf_converged = {data.settings.get("scf_converged")}): '
                                'every read-out of this run is unresolved')
        self.manifest = manifest
        if data.atom_w is None:
            raise ValueError('projections are required')
        if data.nat != st.nat or (data.species is not None and list(data.species) != list(st.species)):
            raise ValueError('projection atoms and structure disagree')
        geo, w = detect_mode(st, name)
        self.warnings += w
        self.mode = geo if mode == 'auto' else mode
        self.masks, self.reg = regions(st, self.mode)
        self.N = st.nat
        self._nex(nex)
        self._occupations()
        self._flatten(w5d_convention)
        self._accounting()
        self._edges()
        self.alignment = self._alignment(avg)

    # ------------------------------------------------------------ projected-electron accounting
    def _accounting(self):
        above = self.n > self.N_v
        nab = float(self.fw[above].sum())
        dev = nab - self.N_ex
        ok = abs(dev) <= R.ACCOUNTING_TOL_E
        self.acc = {'electrons_above_Nv': nab, 'N_ex': self.N_ex, 'deviation': dev,
                    'check': 'PASS' if ok else 'FAIL', 'tolerance_e': R.ACCOUNTING_TOL_E,
                    'electrons_at_or_below_Nv': float(self.fw[~above].sum()), 'expected_at_or_below_Nv': 2.0 * self.N_v}
        if not ok:
            self.reasons.append(f'excess-electron accounting: {nab:.4f} e above N_v vs N_ex {self.N_ex} '
                                f'(|deviation| {abs(dev):.4f} > {R.ACCOUNTING_TOL_E})')

    # ------------------------------------------------------------ N_ex, N_v
    def _nex(self, nex):
        """N_ex from the composition-checked manifest (kind W-doped: n_W; compensated, undoped: 0), never from the
        cell name. Without a manifest: an explicit override, else the formal-charge count; both are unverified."""
        n_w = self.st.count('W')
        formal = self.st.formal_excess()
        verified = False
        if self.manifest is not None:
            used, src, verified = int(self.manifest['N_ex']), f'manifest ({self.manifest.get("kind")})', True
        elif nex is not None:
            used, src = int(nex), 'override (reference / legacy run; unverified)'
        elif formal is not None:
            used, src = int(formal), 'formal-charge count (no manifest; unverified)'
        else:
            used, src = n_w, 'n_W (no manifest, no formal count; unverified)'
        if formal is not None and formal != used:
            self.warnings.append(f'N_ex used ({used}, {src}) differs from the formal-charge count ({formal})')
        self.kind = (self.manifest or {}).get('kind')
        nel = self.data.nelec
        nv = (nel - used) / 2.0
        self.N_ex, self.N_el = used, nel
        self.nex_info = {'N_el': nel, 'N_ex': used, 'N_ex_source': src, 'N_ex_verified': verified,
                         'N_ex_formal_charge': formal, 'n_W': n_w, 'N_v': nv, 'kind': self.kind}
        if abs(nv - round(nv)) > R.NEX_DIGITS:
            self.reasons.append(f'N_v = (N_el - N_ex)/2 = {nv} is not an integer')
            self.N_v = int(np.floor(nv))
        else:
            self.N_v = int(round(nv))
        if self.N_v >= self.data.nbnd:
            self.reasons.append(f'N_v {self.N_v} >= nbnd {self.data.nbnd}: no band above N_v')

    # ------------------------------------------------------------ occupations
    def _occupations(self):
        d = self.data
        info = {'occupations_kind': d.occupations_kind, 'smearing': d.smearing, 'degauss_eV': d.degauss_ev,
                'E_F_eV': d.ef.tolist(), 'nspin': d.nspin}
        if d.occupations_kind == 'smearing':
            if np.isnan(d.ef).any():
                raise ValueError('smearing run without a Fermi energy')
            f = np.stack([occupations(d.e[s], d.ef[s], d.degauss_ev, d.smearing) for s in range(d.nspin)])
            info['f_source'] = f'recomputed with the run\'s own smearing function ({d.smearing})'
            if d.f_qe is not None:
                dev = float(np.max(np.abs(f - d.f_qe)))
                info['max_abs_f_recomputed_minus_qe'] = dev
                if dev > R.FQE_TOL:          # rc6: an unverified pairing is a section-1 condition, never a warning
                    self.reasons.append(f'recomputed occupations differ from the run\'s own (QE) occupations by up to '
                                        f'{dev:.2e} (> {R.FQE_TOL}): smearing / E_F / band pairing not verified')
        elif d.occupations_kind == 'fixed':
            if d.f_qe is None:
                raise ValueError('fixed occupations without QE occupations')
            f = d.f_qe
            info['f_source'] = 'QE fixed occupations (A15: used only after a global gap has been shown)'
            tol = R.FIXED_FRACTIONAL_TOL
            frac = (f > tol) & (f < 1.0 - tol)
            occ, emp = d.e[f >= 1.0 - tol], d.e[f <= tol]
            gap = float(emp.min() - occ.max()) if occ.size and emp.size else None
            info['global_gap_eV'] = gap
            info['fractional_occupations'] = int(frac.sum())
            if frac.any():
                self.reasons.append(f'A15: fixed occupations with {int(frac.sum())} fractional occupation(s): no global '
                                    'gap shown')
            elif gap is None or gap <= 0:
                self.reasons.append(f'A15: fixed occupations without a global gap (gap {gap} eV)')
        else:
            raise ValueError(f'occupations {d.occupations_kind!r} not supported')
        self.f = f
        tot = float((f * d.w[:, :, None]).sum())
        info['sum_f_w'] = tot
        info['electron_count_deviation'] = tot - self.N_el
        if abs(tot - self.N_el) > R.ACCOUNTING_TOL_E:
            self.reasons.append(f'occupations do not reproduce N_el ({tot:.4f} vs {self.N_el}): smearing/E_F inconsistent')
        self.occ_info = info

    # ------------------------------------------------------------ per-state arrays
    def _flatten(self, w5d_convention):
        d = self.data
        ns, nk, nb = d.e.shape
        S = np.indices((ns, nk, nb)).reshape(3, -1)
        self.s, self.k, self.n = S[0], S[1], S[2] + 1                 # band index 1-based
        self.e = d.e.reshape(-1)
        self.fw = (self.f * d.w[:, :, None]).reshape(-1)              # electrons in the state
        self.focc = self.f.reshape(-1)
        aw = d.atom_w.reshape(-1, self.N)
        tot = aw.sum(axis=1)
        self.compl = d.compl.reshape(-1) if d.compl is not None else tot
        with np.errstate(invalid='ignore', divide='ignore'):
            p = np.where(tot[:, None] > 0, aw / tot[:, None], 0.0)
            s2 = (p * p).sum(axis=1)
            self.PR = np.where(s2 > 0, 1.0 / (self.N * s2), 0.0)
            self.Neff = self.N * self.PR
            film = self.masks['film']
            pf = aw[:, film]
            tf = pf.sum(axis=1)
            pfn = np.where(tf[:, None] > 0, pf / tf[:, None], 0.0)
            sf2 = (pfn * pfn).sum(axis=1)
            self.PR_film = np.where(sf2 > 0, 1.0 / (max(1, film.sum()) * sf2), 0.0)
            raw = d.w5d.reshape(-1) if d.w5d is not None else np.zeros_like(self.e)
            self.W5d_raw = raw
            self.W5d_norm = np.where(self.compl > 0, raw / self.compl, 0.0)
        self.p = p
        self.W5d = self.W5d_norm if w5d_convention == 'normalised' else self.W5d_raw
        self.w5d_convention = w5d_convention
        self.flagged = R.lt(self.compl, R.COMPLETENESS_FLAG)
        self.regw = {k: p[:, m].sum(axis=1) for k, m in self.masks.items()}
        frac = self.reg['interior_fraction']
        self.interior_ok = R.ge(self.regw['interior'], R.INTERIOR_FACTOR * frac)
        self.approx = d.proj_kind == 'text'
        self.completeness_info = {'n_states': int(self.e.size), 'n_flagged': int(self.flagged.sum()),
                                  'min_completeness': float(self.compl.min()),
                                  'proj_kind': d.proj_kind}
        if self.approx:
            self.reasons.append('projections from the projwfc.x printout (components < 0.001 omitted): PR_n and '
                                'region weights approximate')

    # ------------------------------------------------------------ edges
    def state(self, i, top=5):
        """JSON record of state i."""
        i = int(i)
        order = np.argsort(-self.p[i])[:top]
        return {'spin': int(self.s[i]) + 1, 'k': int(self.k[i]) + 1, 'band': int(self.n[i]), 'E_eV': float(self.e[i]),
                'f': float(self.focc[i]), 'electrons': float(self.fw[i]), 'PR_n': float(self.PR[i]),
                'N_eff': float(self.Neff[i]), 'PR_film': float(self.PR_film[i]), 'W5d': float(self.W5d[i]),
                'W5d_raw': float(self.W5d_raw[i]), 'W5d_normalised': float(self.W5d_norm[i]),
                'completeness': float(self.compl[i]), 'flagged': bool(self.flagged[i]),
                'weights': {k: float(v[i]) for k, v in self.regw.items()},
                'top_atoms': [[int(a) + 1, self.st.species[a], float(self.p[i, a])] for a in order]}

    def _edges(self):
        above, below = self.n > self.N_v, self.n <= self.N_v
        no_int = self.reg['counts']['interior'] == 0
        self.lowest_above = int(np.argmin(np.where(above, self.e, np.inf))) if above.any() else None
        # host (conduction) edge
        he = {'E_eV': None, 'state': None, 'unresolved': []}
        cand = above & R.ge(self.PR, R.PR_EXTENDED) & self.interior_ok
        if no_int:
            he['unresolved'].append('interior region contains no atoms')
        if not above.any():
            he['unresolved'].append('no band above N_v')
        elif not cand.any():
            he['unresolved'].append('no state above N_v qualifies (PR_n >= 0.20 and interior weight)')
        else:
            i = int(np.argmin(np.where(cand, self.e, np.inf)))
            e_low = float(self.e[self.lowest_above])
            he.update({'E_eV': float(self.e[i]), 'state': self.state(i), 'index': i,
                       'lowest_state_above_Nv_eV': e_low, 'distance_from_lowest_above_Nv_eV': float(self.e[i] - e_low)})
            if R.gt(self.e[i] - e_low, R.HOST_EDGE_WINDOW_EV):
                he['unresolved'].append(f'no state qualifies within {R.HOST_EDGE_WINDOW_EV} eV above the lowest state '
                                        f'above N_v ({self.e[i] - e_low:.3f} eV)')
            comp = above & ~cand & self.flagged & (self.e < self.e[i])
            if self.flagged[i] or comp.any():
                he['unresolved'].append('rests on flagged states (completeness < 0.90): '
                                        + ('selected state flagged; ' if self.flagged[i] else '')
                                        + f'{int(comp.sum())} lower non-qualifying flagged state(s)')
        if self.approx:
            he['unresolved'].append('approximate (text) projections')
        he['candidates'] = int(cand.sum())
        self.host_edge = he
        # host valence edge
        hv = {'E_eV': None, 'state': None, 'unresolved': []}
        vc = below & R.ge(self.PR, R.PR_EXTENDED) & self.interior_ok
        if no_int:
            hv['unresolved'].append('interior region contains no atoms')
        if not vc.any():
            hv['unresolved'].append('no state at or below N_v qualifies (PR_n >= 0.20 and interior weight)')
        else:
            i = int(np.argmax(np.where(vc, self.e, -np.inf)))
            hv.update({'E_eV': float(self.e[i]), 'state': self.state(i), 'index': i})
            comp = below & ~vc & self.flagged & (self.e > self.e[i])
            if self.flagged[i] or comp.any():
                hv['unresolved'].append('rests on flagged states (completeness < 0.90): '
                                        + ('selected state flagged; ' if self.flagged[i] else '')
                                        + f'{int(comp.sum())} higher non-qualifying flagged state(s)')
        if self.approx:
            hv['unresolved'].append('approximate (text) projections')
        hv['candidates'] = int(vc.sum())
        self.host_valence_edge = hv

    def edge_ok(self, which='host_edge'):
        e = getattr(self, which)
        return e['E_eV'] is not None and not e['unresolved']

    @property
    def E_c(self):
        return self.host_edge['E_eV']

    @property
    def E_v(self):
        return self.host_valence_edge['E_eV']

    # ------------------------------------------------------------ interior alignment (rc3 frozen rule)
    def _alignment(self, avg):
        """Section 1: 'A planar-averaged potential plateau over the interior region, with a standard deviation of
        0.05 eV or less.' Frozen rc3 implementation (ASSUMED window; Codex rc2 review): centred box averages of the
        planar average (pp.x plot_num verified as 11) at 5.153 A (primary) and 4.1224 / 6.1836 A (sensitivity), all
        evaluated over the whole common interval in which every kernel lies wholly inside the atom-defined interior
        z-range; that interval must span >= ALIGN_MIN_COMMON_SPAN_A = 2.0 A (interior support >= 8.1836 A); valid only
        if the primary standard deviation <= 0.05 eV and the three interior means agree within 0.05 eV; the average.x
        grid must be a complete uniform grid over the cell. The window is never widened to obtain a pass. Aligned
        edges are released by aligned_edges() only (gated). A pass establishes a stable interior potential reference,
        not bulk-like behaviour."""
        out = {'valid': False, 'unresolved': [],
               'rule': f'rc3: ASSUMED 5.153 A primary, 4.1224 / 6.1836 A sensitivity, all kernels inside the interior, '
                       f'common interval >= {R.ALIGN_MIN_COMMON_SPAN_A} A, plot_num {R.ALIGN_PLOT_NUM} verified'}
        if self.mode == 'bulk':
            out['unresolved'].append('bulk cell: no alignment (not needed)')
            return out
        if avg is None:
            out['unresolved'].append('no planar-averaged potential in the export')
            return out
        if avg.get('plot_num') != R.ALIGN_PLOT_NUM:
            out['unresolved'].append(f'planar average plot_num {avg.get("plot_num")} (must be verified as '
                                     f'{R.ALIGN_PLOT_NUM}, ionic + Hartree; pp input missing or another quantity)')
            return out
        zb = np.asarray(avg['z_bohr'], dtype=float)
        if zb.size < 3:
            out['unresolved'].append('planar average has fewer than 3 grid points')
            return out
        dz = zb[1] - zb[0]
        c_bohr = float(self.st.cell[2, 2]) / R.BOHR_A
        out['grid'] = {'n': int(zb.size), 'dz_bohr': float(dz), 'span_bohr': float(zb.size * dz), 'c_bohr': c_bohr}
        if dz <= 0 or np.max(np.abs(np.diff(zb) - dz)) > 1e-6 * max(1.0, dz) or abs(zb.size * dz - c_bohr) > dz \
                or abs(zb[0]) > dz:
            out['unresolved'].append('the average.x grid is not a complete uniform grid over the cell (n dz != c): '
                                     'truncated or foreign file')
            return out
        zr = self.reg.get('interior_z_range_A')
        if not zr:
            out['unresolved'].append('interior region contains no atoms')
            return out
        widths = (R.ALIGN_PRIMARY_WINDOW_A,) + tuple(R.ALIGN_SENSITIVITY_WINDOWS_A)
        wmax = max(widths)
        lo, hi = zr[0] + wmax / 2, zr[1] - wmax / 2
        span = hi - lo
        out.update({'interior_z_range_A': zr, 'common_interval_A': [lo, hi], 'common_span_A': span,
                    'required_span_A': R.ALIGN_MIN_COMMON_SPAN_A, 'windows_A': list(widths)})
        if R.lt(span, R.ALIGN_MIN_COMMON_SPAN_A):
            out['unresolved'].append(f'common interval {span:.2f} A < {R.ALIGN_MIN_COMMON_SPAN_A} A (interior '
                                     f'{zr[1] - zr[0]:.2f} A minus the widest kernel {wmax} A)')
            return out
        z = z_in_frame(avg['z_bohr'], self.reg, R.BOHR_A)
        sel = (z >= lo) & (z <= hi)
        if sel.sum() < 2:
            out['unresolved'].append('fewer than 2 grid points in the common interval')
            return out
        res = {}
        for w in widths:
            v = box_average(avg['z_bohr'], avg['planar_ry'], w / R.BOHR_A)[sel] * R.RY_EV
            res[f'{w:g}'] = {'mean_eV': float(v.mean()), 'std_eV': float(v.std())}
        prim = res[f'{R.ALIGN_PRIMARY_WINDOW_A:g}']
        means = [x['mean_eV'] for x in res.values()]
        var = max(means) - min(means)
        out.update({'by_window': res, 'plateau_std_eV': prim['std_eV'], 'V_interior_eV': prim['mean_eV'],
                    'mean_variation_eV': var, 'n_points': int(sel.sum())})
        if R.gt(prim['std_eV'], R.PLATEAU_STD_EV):
            out['unresolved'].append(f'primary plateau standard deviation {prim["std_eV"]:.3f} eV > {R.PLATEAU_STD_EV} eV')
        if R.gt(var, R.ALIGN_MEAN_VARIATION_EV):
            out['unresolved'].append(f'interior mean varies by {var:.3f} eV across the three widths '
                                     f'(> {R.ALIGN_MEAN_VARIATION_EV} eV)')
        out['valid'] = not out['unresolved']
        return out

    def aligned_edges(self, qualification_reasons):
        """Aligned edges, released only for a valid plateau, a resolved edge, a passing accounting with no section-1
        unresolved condition, and a qualified run."""
        al = self.alignment
        gate = []
        if not al.get('valid'):
            gate.append('alignment not valid')
        if self.reasons:
            gate.append('section-1 unresolved conditions: ' + '; '.join(self.reasons))
        if self.acc['check'] != 'PASS':
            gate.append('excess accounting not passing')
        gate += [f'run qualification: {r}' for r in qualification_reasons]
        out = {'aligned_host_edge_eV': None, 'aligned_host_valence_edge_eV': None, 'gate': list(gate)}
        if gate:
            return out
        if self.edge_ok('host_edge'):
            out['aligned_host_edge_eV'] = self.E_c - al['V_interior_eV']
        else:
            out['gate'].append('host edge unresolved')
        if self.edge_ok('host_valence_edge'):
            out['aligned_host_valence_edge_eV'] = self.E_v - al['V_interior_eV']
        else:
            out['gate'].append('host valence edge unresolved (aligned valence edge withheld)')
        return out

    # ------------------------------------------------------------ summary
    def summary(self):
        lumo = self.state(self.lowest_above) if self.lowest_above is not None else None
        gap = None
        if self.E_c is not None and self.E_v is not None:
            gap = {'E_g_host_eV': self.E_c - self.E_v,
                   'unresolved': self.host_edge['unresolved'] + self.host_valence_edge['unresolved']
                   + [f'section 1: {x}' for x in self.reasons]}
        ef = self.data.ef.tolist()
        return {
            'cell': self.name, 'mode': self.mode, 'n_atoms': self.N, 'composition': self.st.composition(),
            'accounting_partition': self.nex_info, 'occupations': self.occ_info, 'excess_accounting': self.acc,
            'regions': {k: v for k, v in self.reg.items() if k != 'z_A'},
            'completeness': self.completeness_info,
            'host_edge': {k: v for k, v in self.host_edge.items() if k != 'index'},
            'host_valence_edge': {k: v for k, v in self.host_valence_edge.items() if k != 'index'},
            'host_gap': gap, 'lowest_state_above_Nv': lumo,
            'E_F_minus_host_edge_eV': None if self.E_c is None else [x - self.E_c for x in ef],
            'alignment': self.alignment, 'section1_unresolved': list(self.reasons), 'warnings': self.warnings,
        }
