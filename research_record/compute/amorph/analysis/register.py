"""Registered thresholds and constants (single source for the whole package).

Every number below is copied from codex/work_chat/HYPOTHESIS_REGISTER.md (frozen 2026-10-10T18:33Z, amendments
A16, A24, A26, A27). The citation is given next to each value. Values marked IMPLEMENTATION are NOT registered:
they are choices this code had to make where the register is silent. They are listed in IMPLEMENTATION_CHOICES and
printed in every report, so a reader always sees them.
"""

# ---------------------------------------------------------------- units (QE 7.5 values, Modules/constants.f90)
HA_EV = 27.211386245988          # eV per Hartree
RY_EV = HA_EV / 2.0              # eV per Rydberg
BOHR_A = 0.529177210903          # Angstrom per bohr

# ---------------------------------------------------------------- section 1: projections (A16)
COMPLETENESS_FLAG = 0.90         # "A state with completeness < 0.90 is flagged."

# ---------------------------------------------------------------- section 1: localisation (A16)
PR_EXTENDED = 0.20               # "Extended: PR_n >= 0.20."
PR_LOCALISED = 0.05              # "Localised: PR_n <= 0.05."

# ---------------------------------------------------------------- section 1: host edge, operational rule (A16)
INTERIOR_FACTOR = 0.8            # "interior weight of at least 0.8 x the interior atom fraction"
HOST_EDGE_WINDOW_EV = 1.0        # "unresolved when no state qualifies within 1.0 eV above the lowest state above N_v"

# ---------------------------------------------------------------- section 1: regions; A24 interface cells
REGION_CUT_A = 3.0               # surface: within 3.0 A of the outermost non-H atom of each face; interface: 3.0 A of z_if
OUTER_FACE_A = 3.0               # A24: outer face = z < z(lowest substrate cation) + 3 A (mace_amorph.OUTER_FACE_A)
Z_IF_PERCENTILES = (95, 5)       # A24: z_if from substrate-cation p95 and p5 of film cations not on the outer face
FILM_CATIONS = ('In', 'W')       # mace_amorph.FILM
SUBSTRATE_CATIONS = ('Al', 'Hf') # mace_amorph.SUBCAT

# ---------------------------------------------------------------- section 1: projected-electron accounting (A16)
ACCOUNTING_TOL_E = 0.02          # "their sum must equal N_ex within 0.02 e"

# ---------------------------------------------------------------- section 1: valid interior alignment
PLATEAU_STD_EV = 0.05            # "plateau over the interior region, with a standard deviation of 0.05 eV or less"

# ---------------------------------------------------------------- H-G (registered predictions and forecasts)
W5D_STATE = 0.30                 # "lowest state with >= 30 % W-5d weight" (H-G, H-N Delta_W, f_locW)
HG_W_ABOVE_EDGE_EV = 0.3         # "> 0.3 eV above the host edge"
HG_W_ABOVE_LUMO_EV = 0.5         # forecast (Claude): ">= 0.5 eV above the LUMO"
HG_FEXT = 0.80                   # "1 e/W cells: >= 80 % of the nominal excess electrons ... extended host states"
HG_HOST_EDGE_W5D_MAX = 0.10      # Claude adds: "the host-edge state has <= 10 % W-5d weight"
HG_EG_COMP_EV = 0.15             # Claude adds: "|E_g(comp) - E_g(a-In2O3)| <= max(0.15 eV, sample spread)"
HG_FW5D_FORECAST = 0.15          # forecast: "<= 15 % of the excess electrons on W-5d"
HG_EF_FORECAST_EV = (0.4, 1.0)   # forecast: "E_F 0.4 to 1.0 eV above the host edge in the 1 e/W cells"

# ---------------------------------------------------------------- H-H, H-I, H-K
HH_SHIFT_EV = 0.15               # H-H: "Interior-aligned host-edge shift <= 0.15 eV at 2.0 nm"
GAPSTATE_WINDOW_EV = 0.3         # H-H, H-I: "within 0.3 eV below the host edge"
REGION_STATE_WEIGHT = 0.30       # H-H ">= 30 % surface weight"; H-I "interface weight >= 30 %"
HI_EDGE_EV = 0.2                 # H-I: "|host-edge difference| <= 0.2 eV at 2.0 nm"
HI_SPREAD_EV = 0.2               # H-I: "a vacuum s1/s2 spread above 0.2 eV" -> unresolved
HK_EG_DIFF_EV = (0.6, 1.3)       # H-K: "E_g(0.7 nm) - E_g(2.0 nm) = 0.6 to 1.3 eV"
HK_SPREAD_EV = (0.03, 0.20)      # H-K: "with sample spread 0.03 to 0.20 eV"
HK_EDGE_RISE_EV = (0.2, 1.0)     # H-K: "The aligned host edge rises by 0.2 to 1.0 eV from 2.0 to 1.0 nm"

# ---------------------------------------------------------------- H-N (A27)
HN_DONOR_FEXT = 0.80             # DONOR: f_ext >= 0.80
HN_DONOR_DW_EV = 0.3             # DONOR: Delta_W > 0.3 eV
HN_DONOR_FLOCW = 0.10            # DONOR: f_locW < 0.10
HN_ECB_FEXT = 0.50               # ECB: f_ext < 0.50
HN_ECB_FLOCW = 0.50              # ECB: f_locW >= 0.50
HN_COVERAGE_EV = 1.0             # "the FINAL nbnd must reach at least 1.0 eV above the host edge at every k-point"
HN_ATTR_WEIGHT = 0.30            # attribution (i) ">= 30 % of their weight on W plus its first-shell O", (ii) ">= 30 %"
HN_ATTR_WINDOW_EV = 0.10         # attribution (ii) "within +-0.10 eV"
HN_THICK = '2.0'                 # thick endpoint
HN_THIN = '0.7'                  # thin decisive endpoint
HN_NO_CROSSOVER_SET = ('bulk', '2.0', '1.0', '0.8', '0.7')   # NO CROSSOVER coverage
C3_EDGE_EV = 0.05                # C3: "edges move <= 0.05 eV"
C3_FRACTION = 0.05               # C3: "fractions move <= 5 percentage points"
C2_FEXT = 0.15                   # C2: "|Delta f_ext| <= 0.15"
C2_DW_EV = 0.15                  # C2: "|Delta Delta_W| <= 0.15 eV"
C1_MIN_AGREE = 2                 # C1: "agree between the independent-quench aIWO_t and at least 2 of the 3 paired cells"
C1_N_PAIRED = 3
# control table of A27 (required controls per endpoint); 'crossover' = required for a crossover claim
HN_CONTROLS_REQUIRED = {
    '2.0': ('C3', 'C4', 'C6'),
    '0.7': ('C3', 'C4', 'C6', 'C1'),
    '0.7_crossover': ('C2', 'C5'),
    '1.0': ('C4',),
}

# ---------------------------------------------------------------- frozen choices (rc2 Codex review; rc3 Codex review)
# Interior alignment (section 1 gives the 0.05 eV plateau rule, not the averaging window). ASSUMED, frozen:
ALIGN_PRIMARY_WINDOW_A = 5.153               # ASSUMED primary box width of the macroscopic average (a/2 of bixbyite)
ALIGN_SENSITIVITY_WINDOWS_A = (4.1224, 6.1836)   # fixed sensitivity widths (0.8 and 1.2 x primary); never widened
ALIGN_MIN_COMMON_SPAN_A = 2.0                # ASSUMED (rc3, Codex): common interval with every kernel inside the
                                             # interior must span >= 2 A, i.e. interior support >= 8.1836 A
ALIGN_MEAN_VARIATION_EV = 0.05               # max - min of the interior means over the three widths
ALIGN_PLOT_NUM = 11                          # pp.x plot_num 11 = ionic (bare) + Hartree potential; anything else, or
                                             # an unverifiable plot_num, makes the alignment UNRESOLVED

# C3 width roles (A27 C3 + A26): the reference is the Gaussian 0.001 Ry FINAL; the other run is Gaussian at the
# audit-selected width, or at 0.002 and 0.005 Ry while the A15 audit is pending.
C3_REFERENCE_WIDTH_RY = 0.001
C3_PENDING_WIDTHS_RY = (0.002, 0.005)
WIDTH_TOL_RY = 1e-9
GAUSSIAN = ('gaussian', 'gauss')

# C5 registered settings (A27 C5): SG15 NC 80 Ry, ecutfock 160 Ry; q = k-mesh, or Gamma with q = 1 only after the
# NC-PBE Gamma vs production-mesh qualification.
C5_NC_ECUTWFC_RY = 80.0
C5_ECUTFOCK_RY = 160.0
C5_HSE_INPUT_DFT = 'HSE'                     # QE input_dft of HSE06
C5_EXX_FRACTION = 0.25                       # QE HSE default exx_fraction (explicit override accepted only if equal)
C5_SCREENING_BOHR = 0.106                    # QE HSE default screening_parameter (bohr^-1), same rule
C5_HYB_TOL = 1e-6

# C6 (A27): one localised start (moment on W and its first-shell O labels only) and one delocalised start (a small
# uniform moment on every species). ASSUMED resolution of the lower-energy choice (as the A25 equivalence gate).
C6_ENERGY_RESOLUTION_RY = 1e-5
C6_DELOCALISED_MAX_MOMENT = 0.2              # IMPLEMENTATION: 'small uniform moment' = equal nonzero |m| <= 0.2

# H-N series (A27): canonical labels; thickness of a cell from its certified name (_<a>p<b>_) or the bulk tag.
SERIES_LABELS = ('bulk', '2.0', '1.5', '1.0', '0.8', '0.7')

# float guard for the strict and non-strict registered thresholds (rc3, Codex A26)
EPS = 1e-9

# ---------------------------------------------------------------- IMPLEMENTATION choices (not registered)
W_O_FIRST_SHELL_A = 2.45         # W-O coordination cutoff of mace_amorph.CUT[('W','O')]; first shell for attribution (i)
IN_O_CN_CUT_A = 2.75             # In-O coordination cutoff of mace_amorph.CUT[('In','O')] (C1 site rule CN >= 5)
C1_SITE_MIN_CN = 5
TRAP_MIN_OCC_E = 0.01            # an occupied / trapping state holds >= 0.01 e (spin-summed f_nk x 2/nspin per state)
ATTR_SUPPORT_FRACTION = 0.80     # attribution (ii): "same non-W atoms" = top-ranked non-W atoms holding 80 % of the
                                 # trapping state's non-W weight
NEAR_FRACTION = 0.05             # threshold-proximity report margin for fractions
NEAR_EV = 0.05                   # threshold-proximity report margin for energies
NEAR_PR = 0.02                   # threshold-proximity report margin for PR_n
NEAR_W5D = 0.03                  # threshold-proximity report margin for W-5d weights
BULK_VACUUM_A = 5.0              # largest empty z gap below this -> bulk cell (no vacuum)
NEX_DIGITS = 1e-6                # N_v must be an integer to this tolerance
FQE_TOL = 1e-3                   # recomputed vs QE occupations: larger deviation is reported as a warning
FIXED_FRACTIONAL_TOL = 1e-6      # fixed occupations: 1e-6 < f < 1 - 1e-6 is fractional (no global gap shown, A15)
GEOMETRY_HASH_DECIMALS = 4       # geometry hash: species, positions and cell rounded to 1e-4 A
FORMAL_CHARGE = {'In': 3, 'W': 6, 'Al': 3, 'Hf': 4, 'H': 1, 'O': -2}

IMPLEMENTATION_CHOICES = {
    'W5d_weight_convention': 'primary = raw W-5d Loewdin weight / completeness (A16 normalisation, D-24 header); the '
                             'class with the OPPOSITE convention is always computed and a difference is flagged '
                             'CONVENTION-SENSITIVE; comparisons and the series accept only normalised read-outs; the '
                             'legacy nc_readout adapter (raw W-5d) is non-primary for C5',
    'occupied': f'a state is occupied when it holds >= {TRAP_MIN_OCC_E} e (f_nk x 2/nspin); used by the H-H and H-G '
                'P3 searches (register: "occupied")',
    'HI_occupation': 'FROZEN (rc4): the H-I interface-state search counts localised interface states of ANY occupation '
                     '(register H-I wording names no occupation; a conservative superset: an empty interface state can '
                     'give FAILED, never a false SUPPORTED)',
    'gap_search_references': 'H-H and H-I need a resolved host edge AND a resolved host valence edge (the valence '
                             'reference gates the gap window); a missing or unresolved one makes the search UNRESOLVED',
    'UPF_identity': 'pseudopotentials compare by certified content hash (element -> sha256 from the run certificate, '
                    'verified against lineage_final.dat); file names are compared only for runs without certified '
                    'hashes, which are unqualified anyway; the lineage must cover every UPF the run uses',
    'fraction_tolerances': 'C3 / C5 / C6 / C2 fraction tolerances use conclusive interval differences of the '
                           'flagged-state bounds (f_ext, f_locW, f_W5d), like Delta_W',
    'C5_hybrid': f'HSE06 = input_dft {C5_HSE_INPUT_DFT!r} with effective exx_fraction {C5_EXX_FRACTION} and '
                 f'screening_parameter {C5_SCREENING_BOHR} bohr^-1 (QE defaults; explicit overrides only if equal); '
                 'other values INVALID, missing values UNRESOLVED',
    'C1_parent': 'the aIO parent must be certified with a converged relaxation (structural requirement; its smearing '
                 'qualification does not gate C1); otherwise C1 is UNRESOLVED',
    'gate_propagation': 'rc5: any certificate gate problem (NOT VALID) makes the run unqualified for every primary '
                        'score, and certified facts (kind, seed, construction, passivation, polish, relaxation, '
                        'manifest N_ex) are used only from a VALID gate',
    'missing_values': 'rc5: two missing values never compare equal (meshes must be known grids of positive integers, '
                      'widths, functionals, cutoffs, geometry hashes and UPF identities must be present); missing '
                      'sampling in C5 gives UNRESOLVED',
    'input_parsing': 'rc5: pw.x / pp.x namelists are read with comments stripped and quoted values masked; repeated '
                     'assignments are refused; cards ignore comment lines; conflicting lineage entries are not coverage',
    'rests_on_flagged': 'edges: strict; gap searches: any flagged state in the window; fractions: conservative bounds; '
                        'Delta_W: quantitative bounds from flagged states gaining (raw + missing weight) or losing '
                        '(raw only) W character; the class must be the same over every combination of the extremes; '
                        'comparisons need conclusive difference bounds',
    'alignment': f'ASSUMED primary window {ALIGN_PRIMARY_WINDOW_A} A, sensitivity {ALIGN_SENSITIVITY_WINDOWS_A} A, '
                 'box averages recomputed from the planar plot_num 11 average (ionic + Hartree; plot_num must be '
                 'verified); all three evaluated over the common interval where every kernel lies inside the '
                 f'atom-defined interior z-range; that interval must span >= {ALIGN_MIN_COMMON_SPAN_A} A (ASSUMED); valid '
                 f'only if the primary std <= 0.05 eV and the spread of the three means <= {ALIGN_MEAN_VARIATION_EV} '
                 'eV; the average.x grid must span the cell; aligned edges are released only for a resolved edge, a '
                 'passing accounting and a qualified run; the planar-average inputs are bound by the certificate',
    'regions': 'z-planar bands (|dz| <= 3.0 A) on the slab unwrapped across the periodic boundary; H always surface; '
               'interface cells: A24 outer face excluded from interface and interior; A24 outer-face states are '
               'removed from the H-I interface list',
    'edges_compared': 'C3 and C6: absolute host and valence edges are scored at 0.05 eV (common gauge verified: same '
                      'geometry, pseudopotentials, cutoffs, k-mesh, functional); C5: relative quantities only',
    'unknown_differences': 'a comparison item that applies but cannot be evaluated or bounded makes the comparison '
                           'UNRESOLVED, never PASS/ROBUST',
    'control_identity': 'a control report binds to a series cell only through its prescribed input role (C3 '
                        'reference, C6 nspin = 1 reference, C1 main, C5 PAW input, C2 full = a paired input of the '
                        'bound C1 report) with identical run files and certificate; correct kind, current code, valid '
                        'self-hash; inline objects are rejected; per-seed coverage at 2.0 nm; C3 at both 0.002 and '
                        '0.005 Ry for a 0.001 Ry reference cell',
    'attribution': f'trapping states: n > N_v, PR_n <= 0.05, f_nk w_k >= {TRAP_MIN_OCC_E} e (excluded localised '
                   'occupation reported; flagged occupied states above N_v make membership unbounded); (i) '
                   'occupation-weighted weight on W + O within 2.45 A, bounded by completeness; (ii) support = top '
                   'non-W atoms holding 80 % of the non-W weight, with sure / possible member sets when the missing '
                   'weight (1 - completeness) is placed adversarially, mapped with the immutable C1 atom map; complete '
                   'parent atomic weights, bounded by the parent completeness and the support bounds; a decision needs '
                   'all bounds on one side of 30 %; energies relative to each cell host edge are OPERATIONAL '
                   'comparisons; absence in the parent needs a qualified parent and complete, unflagged coverage',
    'constructions': 'C3: Gaussian 0.001 Ry reference vs Gaussian 0.002 / 0.005 Ry (or the audit width) at fixed '
                     'geometry, functional, cutoffs, k-mesh, lsda and pseudopotentials; C6: one localised start (moment '
                     'on W and on labels whose atoms are all W first-shell O) and one delocalised start (equal nonzero '
                     f'|m| <= {C6_DELOCALISED_MAX_MOMENT} on every species), XML pair, converged, energy resolution '
                     f'{C6_ENERGY_RESOLUTION_RY} Ry; C5: PAW-PBE (paw) -> NC-PBE -> HSE06 (norm-conserving, one '
                     f'element -> pseudopotential map, {C5_NC_ECUTWFC_RY} Ry, ecutfock {C5_ECUTFOCK_RY} Ry, q = k, or '
                     'Gamma with q = 1 qualified by NC-PBE at the production mesh), nspin 1, three distinct runs; C2: '
                     'certified C2-diluted construction of the full C1 paired cell (one lateral vector doubled, c '
                     'unchanged, composition 2 x full + In - W - O), identical functional, cutoffs, width, lsda and '
                     'pseudopotentials; C1: exactly three certified C1-paired constructions of the certified aIO parent '
                     '(immutable atom map, W on the recorded interior In site with In-O CN >= 5 at 2.75 A, distinct '
                     'sites), main = certified W-doped cell of the same thickness, other geometry and seed, same width '
                     'and functional; the seeded draw order is recorded by the construction, not recomputed',
    'species_labels': 'split species labels (A25/A30: In1/In2, O1/O2, ...) are read as their element everywhere '
                      '(structure, projections, tables, manifests, pseudopotential maps); labels are kept in the '
                      'structure record and never enter the geometry hash',
    'W_O_first_shell_A': W_O_FIRST_SHELL_A,
    'HG_P1_domain': 'H-G P1 historical score: all states (the registered wording); the n > N_v (A23 reader) and the '
                    'A27 domain (above the host valence edge) are reported separately and never replace it',
    'N_ex': 'from a composition-checked manifest in the run certificate (kind W-doped / compensated / undoped / '
            'reference; formal-charge count must equal the declared N_ex); without it N_ex is the formal-charge count '
            'and the run is unqualified; an unverified N_ex = 0 for a W-containing cell gives UNRESOLVED, not N/A',
    'certification': 'smearing qualification needs a numeric certified width equal to the width actually used and the '
                     'Gaussian family; relaxation status defaults to UNKNOWN; every consumed scientific input (run '
                     'files, planar-average files, pseudopotential provenance) is bound by sha256; unknown statuses '
                     'and malformed certificates make the gate NOT VALID; missing qualification makes every primary '
                     'score UNRESOLVED',
    'unconverged': 'a FINAL whose SCF convergence is not shown (scf_converged not True) is a section-1 unresolved '
                   'condition for every read-out',
    'fixed_occupations': 'A15: fixed occupations need a global gap: fractional occupations or an occupied level at or '
                         'above an empty one make every read-out UNRESOLVED',
    'series': 'canonical labels only; each cell certified W-doped with the label thickness in its name; bulk slot in '
              'bulk mode; one common (smearing, width) across the series; C4 = certified Gaussian polish at 2.0 '
              '(both seeds), 1.0 and 0.7 nm, required for CROSSOVER and NO CROSSOVER',
    'spin': 'C6 accepts only XML-pair nspin = 2 runs; D-24 lsda tables are reconstructed for diagnostics only',
    'threshold_guard': f'registered thresholds are applied with a float guard of {EPS} (strict: x > t + eps, '
                       'x < t - eps; non-strict: x >= t - eps, x <= t + eps)',
    'text_source': 'projwfc.x printout input (crystalline reproduction only) marks every PR-based result unresolved',
}


def gt(x, t):
    return x > t + EPS


def lt(x, t):
    return x < t - EPS


def ge(x, t):
    return x >= t - EPS


def le(x, t):
    return x <= t + EPS
