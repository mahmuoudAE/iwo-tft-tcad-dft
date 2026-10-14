"""Build research_monograph/evidence/FACT_REGISTRY.tsv.

Each fact is pulled from a re-derivation JSON (qe_workflow/analysis_2026-10-13_full) or from the measured CSV, and,
where the JSON carries a raw-output pointer "path:line", the number is checked against that line of the raw
Quantum ESPRESSO output (independent of the JSON writer). Facts that exist only in the claims ledger are entered
with verification 'ledger-only'. This script never reads amorphous (aIO_*/aIWO_*) outputs or sealed runs.

Run from the repository root:  python3 -I research_monograph/tools/build_fact_registry.py
"""
import csv
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
QE = ROOT / "qe_workflow"
AF = QE / "analysis_2026-10-13_full"
BM = AF / "bands_masses" / "out"
OUT = ROOT / "research_monograph" / "evidence" / "FACT_REGISTRY.tsv"

FORBIDDEN = re.compile(r"(aIO_|aIWO_|run_007[5-7]|results/sealed|DIAGb)")


def jget(path, keys):
    d = json.loads(path.read_text())
    for k in keys:
        d = d[k]
    return d


def check_src(value, src):
    """Return 'raw-verified', 'raw-mismatch', 'no-pointer' or 'raw-absent' for a numeric value and 'path:line'."""
    if not src or ":" not in src:
        return "no-pointer"
    path, _, line = src.rpartition(":")
    if FORBIDDEN.search(path):
        raise RuntimeError("blind guard: refused to open " + path)
    p = QE / path
    if not p.exists() or not line.isdigit():
        return "raw-absent"
    lines = p.read_text(errors="replace").splitlines()
    n = int(line)
    # scan from the pointer to the end of its block (next k-point header or 60 lines), plus one line before
    block = [lines[n - 2]] if n >= 2 else []
    for j in range(n - 1, min(len(lines), n + 60)):
        if j > n + 1 and re.match(r"\s*k =", lines[j]):
            break
        block.append(lines[j])
    nums = []
    for ln in block:
        vals = [float(x) for x in re.findall(r"-?\d+\.\d+(?:[eE][-+]?\d+)?", ln)]
        nums += vals
        if "highest occupied, lowest unoccupied" in ln and len(vals) == 2:
            nums.append(vals[1] - vals[0])
    digits = len(repr(value).split(".")[-1]) if "." in repr(value) else 1
    tol = max(0.6 * 10 ** (-digits), abs(value) * 1e-6)
    return "raw-verified" if any(abs(x - value) <= tol for x in nums) else "raw-mismatch"


facts = []


def add(fid, quantity, value, units, label, claim, source, src_line, method, caveat, sections, verification=None,
        supersedes=""):
    if verification is None:
        verification = check_src(value, src_line) if isinstance(value, (int, float)) else "no-pointer"
    facts.append(dict(fact_id=fid, quantity=quantity, value=value, units=units, label=label, ledger_claim=claim,
                      source=source, raw_pointer=src_line or "", extraction=method, verification=verification,
                      caveat=caveat, monograph_sections=sections, supersedes=supersedes))


# ---------------------------------------------------------------- bulk In2O3 (PBE, PAW, 71 Ry)
f02 = AF / "out/f02_bulk_structure_bands.json"
a = jget(f02, ["vcrelax", "a_conv_A"])
add("FACT-001", "bixbyite In2O3 lattice constant, PBE vc-relax", a["value"], "angstrom", "COMPUTED", "C039",
    "out/f02_bulk_structure_bands.json:vcrelax.a_conv_A", a["src"], "f02 parser (2|a1_x| of primitive cell)",
    "PBE overestimates a by 1.87 % vs Marezio 1966 (10.117 A); all slabs and W cells use the PBE lattice",
    "dft-bulk", verification="raw-derived-verified (2 x 5.153045099 A from CELL_PARAMETERS after line 4565)")
add("FACT-002", "bulk PBE fundamental gap (indirect by 4.4 meV)", jget(f02, ["bands_path", "Eg_fundamental_eV"]),
    "eV", "COMPUTED", "C039", "out/f02_bulk_structure_bands.json:bands_path", None,
    "CBM(Gamma) - VBM(0.2 G-H) from bands_path.out lines 850, 931",
    "PBE gap problem: experimental fundamental gap ~2.7-2.9 eV (literature); PBE at PBE lattice",
    "dft-bulk; dft-theory-gap", verification="derived-from-raw-verified")
cbm = jget(f02, ["bands_path", "CBM_eV"]); vbm = jget(f02, ["bands_path", "VBM_eV"])
for fid, q, d in (("FACT-002a", "bulk CBM eigenvalue at Gamma (bands_path)", cbm),
                  ("FACT-002b", "bulk VBM eigenvalue (bands_path, k=[0.1,0.1,-0.1] crystal)", vbm)):
    add(fid, q, d["value"], "eV", "COMPUTED", "C039", "out/f02_bulk_structure_bands.json:bands_path", d["src"],
        "raw eigenvalue", "absolute eigenvalues have no meaning without a reference", "dft-bulk")
add("FACT-003", "bulk direct gap at Gamma", jget(f02, ["bands_path", "Eg_direct_Gamma_eV"]), "eV", "COMPUTED",
    "C039", "out/f02_bulk_structure_bands.json:bands_path", None, "CB(Gamma)-VB(Gamma)", "", "dft-bulk",
    verification="derived-from-raw-verified")

b01 = BM / "b01_masses.json"
add("FACT-004", "bulk electron band-edge mass (10-point Kane fit, isotropic within 0.2 %)", 0.1541, "m0",
    "COMPUTED", "C039", "bands_masses/BANDS_MASSES.md sec. 2; RESULTS_LOG 2026-10-14", None,
    "Kane fit E(1+alpha E) = hbar^2 k^2/2m over 10 points along [100],[110],[111]",
    "basis-dependent: 4-point deck basis 0.1588 m0; anchored parabolas 0.156 (25 meV) to 0.189 m0 (450 meV)",
    "dft-bulk; theory-kane", verification="log-and-json")
add("FACT-005", "bulk Kane non-parabolicity alpha", 0.58, "1/eV", "COMPUTED", "C039",
    "RESULTS_LOG 2026-10-14", None, "Kane fit", "range 0.55-0.63 over directions/windows", "dft-bulk; theory-kane",
    verification="log-only")
add("FACT-006", "bulk mass on the 4-point deck basis", jget(AF / "out/f05_slab_series.json", ["bulk_mass_m0"]),
    "m0", "COMPUTED", "C039", "out/f05_slab_series.json:bulk_mass_m0", None, "4 points incl. Gamma, free intercept",
    "deck basis used by the frozen C10 decks", "dft-bulk; multiscale", verification="json-only")

# ---------------------------------------------------------------- slab series (PBE, (001), OH-terminated)
f05 = AF / "out/f05_slab_series.json"
for key, fid, nom in (("2.0", "FACT-010", "2 nm"), ("1.0", "FACT-011", "1 nm")):
    s = jget(f05, ["slabs", key])
    add(fid, f"{nom} slab: H-H thickness", s["thickness_HH_nm"]["value"], "nm", "COMPUTED", "C020",
        f"out/f05_slab_series.json:slabs.{key}", s["thickness_HH_nm"]["src"], "scf.in geometry",
        "thickness definition matters (H-H vs O-O vs In-In)", "dft-slabs",
        verification="raw-derived-verified (H z-extent x c from scf.in; tools session check 2026-10-14)")
    add(fid + "a", f"{nom} slab: Kohn-Sham gap", s["gap_eV"], "eV", "COMPUTED", "C020",
        f"out/f05_slab_series.json:slabs.{key}", None, "CBM-VBM from scf.out HOMO/LUMO",
        "PBE; crystalline (001); one OH termination", "dft-slabs", verification="derived-from-raw-verified")
    for q in ("VBM_eV", "CBM_eV"):
        add(fid + ("b" if q == "VBM_eV" else "c"), f"{nom} slab: {q[:3]} eigenvalue", s[q]["value"], "eV",
            "COMPUTED", "C020", f"out/f05_slab_series.json:slabs.{key}", s[q]["src"], "raw", "", "dft-slabs")
    add(fid + "d", f"{nom} slab: dEg vs bulk 0.8887 eV", s["dEg_eV"], "eV", "COMPUTED", "C020",
        f"out/f05_slab_series.json:slabs.{key}", None, "slab gap - bulk gap", "HSE ratio r = 1.06-1.11 (FACT-030)",
        "dft-slabs; dft-confinement", verification="derived-from-raw-verified")
    add(fid + "e", f"{nom} slab: electron affinity (host CB)", s["EA_eV"], "eV", "COMPUTED", "C020",
        f"out/f05_slab_series.json:slabs.{key}", None, "E_vac (planar average) - CBM", "symmetric slab, no ramp",
        "dft-slabs; dft-alignment", verification="json-only")
    add(fid + "f", f"{nom} slab: ionisation potential", s["IP_eV"], "eV", "COMPUTED", "C020",
        f"out/f05_slab_series.json:slabs.{key}", None, "E_vac - VBM", "", "dft-slabs; dft-alignment",
        verification="json-only")
p12 = jget(f05, ["partition_1_to_2"])
add("FACT-012", "EA(2 nm) - EA(1 nm) = dEc(1) - dEc(2)", p12["EA2_minus_EA1"], "eV", "COMPUTED", "C020",
    "out/f05_slab_series.json:partition_1_to_2", None, "EA difference (same termination)", "", "dft-alignment",
    verification="json-only")
add("FACT-013", "dEv(1 nm) - dEv(2 nm) = IP(2) - IP(1)", -p12["IP1_minus_IP2"], "eV", "COMPUTED", "C020",
    "RESULTS_LOG 2026-10-14 errata item 1", None, "sign corrected 2026-10-14", "", "dft-alignment",
    verification="json-only", supersedes="RESULTS_LOG line 440 old sign (-0.002 eV)")
add("FACT-014", "dEc / dEv partition at 2 nm (two-step alignment)", "+0.281 / -0.054", "eV", "COMPUTED", "C020",
    "RESULTS_LOG 2026-10-05 (local) dEc/dEv entry; b03 anchor_2nm_two_step", None, "two-step planar average",
    "CB share 0.84", "dft-alignment", verification="log-and-json")
add("FACT-015", "dEc / dEv at 1 nm (2 nm value + EA/IP differences)", "+0.848 / -0.052", "eV", "COMPUTED",
    "C020", "RESULTS_LOG 2026-10-14 errata item 1", None, "dEc - dEv = 0.8998 = dEg(1 nm)", "CB share 0.94",
    "dft-alignment", verification="log-only", supersedes="1 nm dEv -0.056 eV (report_latex_full 13_dft.tex:1711,1751)")
for key, fid in (("0.51", "FACT-016"), ("0.75", "FACT-017")):
    s = jget(f05, ["slabs", key])
    add(fid, f"{key} nm nominal slab: Kohn-Sham gap", s["gap_eV"], "eV", "COMPUTED", "C021",
        f"out/f05_slab_series.json:slabs.{key}", None, "HOMO/LUMO of scf.out",
        "0.51 nm = In8(OH)24, outside every law" if key == "0.51" else
        "polar, no dipole correction; vacuum ramp -13.6 meV/A", "dft-slabs", verification="derived-from-raw-verified")
add("FACT-018", "0.695 nm slab dEc sensitivity to vacuum reference (half ramp, ASSUMED)",
    jget(AF / "out/f06_confinement_laws.json", ["dEc_0p75_dipole_sensitivity", "half_ramp_eV"]), "eV", "ASSUMED",
    "C021", "out/f06_confinement_laws.json", None, "half of the vacuum ramp across the gap",
    "not an error bound; dipole-corrected SCF not run", "dft-slabs; dft-polar", verification="json-only")

s075 = jget(f05, ["slabs", "0.75"])
add("FACT-019", "0.695 nm slab: dipole implied by the vacuum ramp (periodic sawtooth model)",
    "slope -13.597 meV/A; c 32.483 A; step 0.442 V; 0.262 e*A per 107.34 A^2 cell (1.26 D)", "-", "DERIVED",
    "C021", "out/f05_slab_series.json:slabs.0.75 + slabL2_relax_v2/scf.in CELL_PARAMETERS", None,
    "dphi = |dV/dz| * c; dipole/area = eps0 * dphi (monograph analysis 2026-10-14)",
    "assumes a uniform compensating field over the whole cell; potential drop across the film ~0.095 eV is the scale of "
    "the untested gap sensitivity (INFERRED)", "dft-theory-slabs; dft-polar", verification="independent-recompute")

# ---------------------------------------------------------------- laws
b03 = BM / "b03_gaps_laws.json"
L = jget(b03, ["laws"])
add("FACT-020", "dEg(t) fit3 prefactor a (t in nm, H-H)", L["dEg_eV"]["fit3"]["a"], "eV", "FITTED", "C039",
    "bands_masses/out/b03_gaps_laws.json:laws.dEg_eV.fit3", None, "least squares in log space, 3 points",
    "dof 1; sigma_p 0.0073 = residual scatter only", "dft-confinement; multiscale", verification="json-only")
add("FACT-021", "dEg(t) fit3 exponent p", L["dEg_eV"]["fit3"]["p"], "-", "FITTED", "C039",
    "b03:laws.dEg_eV.fit3", None, "as FACT-020", "LOO p 1.290-1.323", "dft-confinement", verification="json-only")
add("FACT-022", "dEc(t) fit2 (1 and 2 nm, primary without polar 0.695 nm) exponent p",
    L["dEc_eV"]["fit2_1and2nm"]["p"], "-", "FITTED", "C039", "b03:laws.dEc_eV.fit2_1and2nm", None, "2-point",
    "fit3 incl. 0.695 nm gives p 1.318 (LOO 0.764-1.478)", "dft-confinement; multiscale", verification="json-only")
add("FACT-023", "dEc(t) fit2 prefactor a", L["dEc_eV"]["fit2_1and2nm"]["a"], "eV", "FITTED", "C039",
    "b03:laws.dEc_eV.fit2_1and2nm", None, "2-point", "", "dft-confinement", verification="json-only")
add("FACT-024", "dm(t) law (band-edge basis)", "0.1145 t^-1.2755", "m0", "FITTED", "C039",
    "RESULTS_LOG 2026-10-14", None, "fit3", "one residual dof", "dft-confinement", verification="log-only")
add("FACT-025", "dEc(6.3 nm) range over fit options", "0.050-0.075", "eV", "FITTED", "C039; C021",
    "RESULTS_LOG 2026-10-14; f06 dEc_0p75_dipole_sensitivity", None, "law evaluation",
    "partly outside configured S6 band 0.046-0.062 eV", "multiscale", verification="log-and-json")

# ---------------------------------------------------------------- slab masses
slabs = jget(b01, ["slabs"])
for key, fid in (("0.51", "FACT-026a"), ("0.75", "FACT-026b"), ("1.0", "FACT-026c"), ("2.0", "FACT-026d")):
    if key in slabs:
        es = slabs[key]["electron_summary"]
        add(fid, f"{key} nm nominal slab in-plane electron band-edge mass [100]/[110]",
            f"{es['m_edge_[100]']:.4f} / {es['m_edge_[110]']:.4f}", "m0", "COMPUTED", "C039",
            f"b01_masses.json:slabs.{key}.electron_summary", None, "10-point Kane fit per direction",
            "2-D DOS mass in RESULTS_LOG: 0.443/0.337/0.279/0.203 m0", "dft-slabs; dft-confinement",
            verification="json-only")

# ---------------------------------------------------------------- HSE
f07 = AF / "out/f07_hse_ratio.json"
add("FACT-030", "HSE06/PBE confinement ratio r (q1 / q3 worst)",
    f"{jget(f07, ['r_q1'])} / {jget(f07, ['r_q3_worst'])}", "-", "COMPUTED", "C020",
    "out/f07_hse_ratio.json", None, "dEg(HSE)/dEg(PBE) at 1 nm, SG15 NC 80 Ry",
    "applied as ASSUMED r rule to other thicknesses", "dft-hse", verification="json-only")
hb = jget(b03, ["hse"])
add("FACT-031", "bulk HSE06 gap (NC, q1, PBE geometry)", hb["HSE_bulk_q1"]["gap_eV"]["value"], "eV", "COMPUTED",
    "C020", "b03:hse.HSE_bulk_q1", hb["HSE_bulk_q1"]["gap_eV"]["src"], "raw",
    "q-mesh sensitivity -41.8 meV (q3); PBE lattice; below experiment", "dft-hse")
add("FACT-032", "bulk NC-PBE gap (80 Ry)", hb["NC_PBE_bulk"]["gap_eV"]["value"], "eV", "COMPUTED", "C020",
    "b03:hse.NC_PBE_bulk", hb["NC_PBE_bulk"]["gap_eV"]["src"], "raw", "NC vs PAW +32 meV", "dft-hse")

# ---------------------------------------------------------------- W in crystalline cells
f09 = AF / "out/f09_iwo_bulk.json"
add("FACT-040", "W site preference E(8b) - E(24d), 4x4x4", 0.2577, "eV", "COMPUTED", "C022",
    "RESULTS_LOG 2026-09-29; f09", None, "total-energy difference", "3x3x3 gives 0.2580 eV", "dft-w",
    verification="log-and-json")
add("FACT-041", "W-O mean bond length, 24d / 8b", f"{jget(f09, ['24d', 'W_O_mean_A']):.3f} / "
    f"{jget(f09, ['8b', 'W_O_mean_A']):.3f}", "angstrom", "COMPUTED", "C022", "out/f09_iwo_bulk.json", None,
    "relaxed geometry", "consistent with W6+ (Shannon 1.98 A) rather than W4+ (2.04 A): ionic-radius argument only",
    "dft-w", verification="json-only")
add("FACT-042", "W-5d-rich level above host CB bottom at Gamma (1 nm / 2 nm / bulk 24d / bulk 8b)",
    "1.22 / 1.34 / 1.76 / 1.80", "eV", "COMPUTED", "C022", "RESULTS_LOG 2026-10-14 C022 caveat; f09, f10",
    None, "projwfc band character + eigenvalues", "at DFT filling only (3 e/cell, 1.4e21-3e21 cm^-3)", "dft-w",
    verification="log-and-json", supersedes="2026-09-30 'W level 0.19 eV below CB' (band-count error)")
add("FACT-043", "E_F - host CB bottom in W cells", "1.2-1.8", "eV", "COMPUTED", "C022",
    "RESULTS_LOG 2026-10-05 CORRECTION; 2026-10-14", None, "", "degenerate; MV smearing 0.01 Ry", "dft-w",
    verification="log-and-json")
ef24 = jget(f09, ["24d", "filling", "E_F_eV"])
add("FACT-044", "bulk W24d Fermi energy (k4 SCF)", ef24["value"], "eV", "COMPUTED", "C022",
    "out/f09_iwo_bulk.json:24d.filling", ef24["src"], "raw", "", "dft-w")
add("FACT-045", "bulk W24d W-5d Loewdin-projected electrons above VB top",
    jget(f09, ["24d", "filling", "W5d_projected_electrons"]), "e", "COMPUTED", "C022",
    "out/f09_iwo_bulk.json:24d.filling", None, "projwfc x MV occupations",
    "not the W charge; range 0.09-0.43 e over the four cells", "dft-w", verification="json-only")
add("FACT-046", "spin-polarised moments (3x3x3), 24d / 8b", "0.62 / 0.74", "muB", "COMPUTED", "C022",
    "RESULTS_LOG 2026-09-29", None, "", "preliminary; likely spurious Stoner moment from coarse sampling",
    "dft-w", verification="log-and-json")
add("FACT-047", "bulk host-CB band-edge mass with 3.1 % W", 0.162, "m0", "COMPUTED", "C039",
    "b01_masses.json:W_bulk.8b.electron_summary.m_dos; RESULTS_LOG 2026-10-14", None, "Kane fit", "+5 % vs pure",
    "dft-w", verification="log-and-json")
w1 = jget(AF / "out/f10_iwo_slabs.json", ["1 nm", "W_effect"])
add("FACT-048", "1 nm slab: W effect on gap / EA / IP", f"{w1['dGap_eV']} / {w1['dEA_eV']} / {w1['dIP_eV']}", "eV",
    "COMPUTED", "C022", "out/f10_iwo_slabs.json:1 nm.W_effect", None, "IWO minus pure twin",
    "gap here = VB top to host CB bottom", "dft-w", verification="json-only")

# ---------------------------------------------------------------- H-L oxygen vacancies (crystalline)
f11 = AF / "out/f11_hl_vacancy.json"
D = jget(f11, ["differences_eV"])
add("FACT-050", "H-L dE_local(O30) k3 / k4", f"{D['dE_local_O30']['k3_g005']} / {D['dE_local_O30']['k4_g005']}",
    "eV", "COMPUTED", "C038", "out/f11_hl_vacancy.json", None, "E(near)-E(far) definition per register H-L",
    "k3->k4 -25.7 meV > 10 meV: UNRESOLVED significance", "dft-vacancy", verification="json-only")
add("FACT-051", "H-L dE_dop k3 / k4", f"{D['dE_dop']['k3_g005']} / {D['dE_dop']['k4_g005']}", "eV", "COMPUTED",
    "C038", "out/f11_hl_vacancy.json", None, "register H-L", "PASS under registered settings (> +0.05 eV)",
    "dft-vacancy", verification="json-only")
add("FACT-052", "H-L raw cross-check: energies re-parsed from raw_cern/hl vs r23.out",
    jget(AF / "out/f13_hl_raw.json", ["energy_max_abs_diff_vs_r23_Ry"]), "Ry", "COMPUTED", "C038",
    "out/f13_hl_raw.json", None, "independent parse", "", "dft-vacancy", verification="json-only")

# ---------------------------------------------------------------- holes
b05 = BM / "b05_holes.json"
nv = jget(b05, ["bulk_Nv"])
add("FACT-060", "valence effective DOS N_V(300 K) range", f"{nv['Nv_range_cm3'][0]:.3g}-{nv['Nv_range_cm3'][1]:.3g}",
    "cm^-3", "COMPUTED", "C040", "b05_holes.json:bulk_Nv", None, "Boltzmann integral of grid DOS",
    "k-mesh convergence not established; holes self-trap per hybrid-functional literature", "dft-holes",
    verification="json-only")
add("FACT-061", "hole DOS mass range", f"{nv['m_h_dos_range'][0]}-{nv['m_h_dos_range'][1]}", "m0", "COMPUTED",
    "C040", "b05_holes.json:bulk_Nv", None, "(N_V/2.5094e19)^(2/3)", "deck NV300 = 1e19 implies 0.54 m0 (ASSUMED)",
    "dft-holes; multiscale", verification="json-only")
add("FACT-062", "bulk VBM camel back: E(VBM) - E(Gamma) and k", "4.4 meV at 0.122 1/A along <100>", "-",
    "COMPUTED", "C040", "b01_masses.json:bulk", None, "bands_path", "below kT", "dft-holes; dft-bulk",
    verification="json-only")

# ---------------------------------------------------------------- amorphous force-only checks (permitted)
add("FACT-070", "MACE-MPA-0 force check overall verdict", "OVERALL FAIL (W first shell)", "-", "COMPUTED", "C037",
    "RESULTS_LOG 2026-10-12 12:35Z", None, "frozen comparator compare_val.py v1.0.0",
    "aIWO_bulk_s1 RMSE_W1 0.434/0.449 eV/A; aIWO_0p7_s1 final fails all three limits", "amorph-ml",
    verification="ledger-only")
add("FACT-071", "smearing MV vs Gaussian force change, relaxed aIWO_1p0_s1", "max 2.4e-4 (RMS 6.7e-5)",
    "Ry/bohr", "COMPUTED", "C034", "RESULTS_LOG 2026-10-11 10:41Z", None, "single-point screen",
    "below A15 threshold 1e-3 Ry/bohr; one cell", "amorph-numerics", verification="ledger-only")
add("FACT-072", "split species labels force equivalence (aIO_1p0_s1)", "|dE| 1e-8 Ry; max |dF| 3e-8 Ry/bohr", "-",
    "COMPUTED", "C035", "RESULTS_LOG 2026-10-11 13:36Z", None, "", "PASS vs 1e-5 tolerances", "amorph-numerics",
    verification="ledger-only")
add("FACT-073", "aIWO_0p8_s2 MV relaxation non-convergence and restart non-reproducibility",
    "max |dF| 4.99e-3 Ry/bohr (identical settings)", "-", "COMPUTED", "C036", "RESULTS_LOG 2026-10-12 07:22Z",
    None, "", "cause open", "amorph-numerics", verification="ledger-only")

# ---------------------------------------------------------------- device metrics (independent re-derivation)
dev_path = ROOT / "research_monograph/evidence/derived/device_facts.json"
if dev_path.exists():
    dev = json.loads(dev_path.read_text())
    F = dev["films"]
    add("FACT-100", "geometric C_ox (HfO2 15 nm eps 19.57 + Al2O3 2 nm eps 9.0)",
        round(dev["cox_recomputed_F_cm2"], 10), "F/cm^2", "DERIVED", "C030",
        "tools/verify_device_facts.py", None, "series capacitors", "eps(Al2O3) ASSUMED; stack order from schematic",
        "device; extraction", verification="independent-recompute")
    for t in ("2.0", "6.3", "13.2"):
        g = F[t]
        add(f"FACT-10{['2.0','6.3','13.2'].index(t)+1}", f"{t} nm: V_th,cc (1e-9 A/um) / floor / I_D(+3 V)",
            f"{g['vth_cc_V']:.4f} V / {g['floor_A_per_um']:.4g} A/um / {g['id_p3V_A_per_um']:.4g} A/um",
            "-", "DERIVED", "C002; C003", "data/experimental_clean.csv", None,
            "log-linear crossing; median I over V_G in [-2,-0.5]; nearest point",
            "one device per film; V_D = 0.7 V", "device; extraction", verification="independent-recompute")
        add(f"FACT-11{['2.0','6.3','13.2'].index(t)+1}", f"{t} nm: peak saturation-formula mobility",
            f"{g['mu_sat_peak_cm2_Vs']:.3f} at V_G = {g['mu_sat_peak_at_V']:.2f} V", "cm^2/Vs", "DERIVED", "C030",
            "data/experimental_clean.csv", None, "2L/(W C_ox)(d sqrt(I_D)/dV_G)^2, central differences",
            "formula outside its validity range at its peak (C031); numerical match to paper only",
            "extraction; provenance", verification="independent-recompute")
    g = F["31.8"]
    add("FACT-104", "31.8 nm: I_D(-3 V) and on/off over the sweep",
        f"{g['id_m3V_A_per_um']:.3g} A/um; {g['on_off_p3_over_m3']:.1f}", "-", "DERIVED", "C029",
        "data/experimental_clean.csv", None, "nearest points", "never falls below 1e-9 A/um: no V_th,cc",
        "device", verification="independent-recompute")

# ---------------------------------------------------------------- write
with open(OUT, "w", newline="") as f:
    cols = list(facts[0].keys())
    w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", lineterminator="\n")
    w.writeheader()
    for r in facts:
        w.writerow(r)
bad = [r for r in facts if r["verification"] in ("raw-mismatch", "raw-absent")]
print(f"{len(facts)} facts written to {OUT.relative_to(ROOT)}")
for r in facts:
    if r["verification"].startswith("raw"):
        print(r["fact_id"], r["verification"], r["value"], r["raw_pointer"])
print("PROBLEMS:", [(r['fact_id'], r['verification']) for r in bad])
