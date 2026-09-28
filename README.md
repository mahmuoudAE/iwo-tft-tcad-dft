# Ultrathin IWO (W:In₂O₃) TFTs: physics-constrained TCAD and first-principles inputs

**Author:** Mahmoud Elrasheedy · **PI:** Chao-Hsin Wu · **Mentor:** Mukul Kumar

This project studies how channel thickness (2 to 31.8 nm) changes the transfer characteristics of W-doped In₂O₃ thin-film transistors. It combines:
- a **Silvaco ATLAS** device model constrained by physics and literature, with every input traced to its source and page;
- **density-functional theory** (Quantum ESPRESSO, PBE) that replaces the borrowed pure-In₂O₃ proxies in the model with computed values: the confinement gap shift ΔEg(t), the in-plane mass m*(t), and W doping.

The DFT results are *computed*, not *validated*: validation needs measured IWO data.

## Results so far (DFT)
| Quantity | This work | Reference |
|---|---|---|
| Relaxed lattice constant (PBE) | 10.306 Å (+1.87 %) | exp. 10.117 Å; Lin 2022: 10.30 Å |
| Bulk gap (PBE) | 0.889 eV | Lin 2022: 0.94 eV |
| Conduction-band mass | 0.159 m₀ | Lin 2022: 0.17; exp. 0.18–0.21 |
| Vacuum convergence (1 nm slab) | ≤ 0.1 meV change from 15 to 35 Å | criterion 10 meV |
| W site preference | 24d favoured by 0.26 eV | computed here |
| W–O bond length | 1.97–1.98 Å (W⁶⁺) | Shannon (1976): 1.98 Å |

The relaxed 1 nm and 2 nm slab confinement results are running. Current status: `qe_workflow/cern_htcondor/results/RESULTS_LOG.md`.

## Layout
| Path | Content |
|---|---|
| `scripts/`, `config/` | ATLAS deck generator, runner (`run_atlas.py`), campaigns (`run_campaign.py`) |
| `results/` | ATLAS runs, `RUN_INDEX.csv`, campaign summaries |
| `report_latex_full/` | thesis-style report (LaTeX + `main.pdf`) |
| `analysis_2026-09-25/` | mechanism analysis |
| `qe_workflow/` | DFT workflow |

The DFT workflow in `qe_workflow/` has four parts:
- **Protocols:** `bulk_In2O3_protocol/PROTOCOL.md` and `cern_htcondor/PROTOCOL_CERN.md`. Criteria were fixed before the results.
- **Structures:** `structures_v2/build_structures.py`, verified with ASE and spglib; the slab recipe follows Lin et al., ACS Nano 16, 21536 (2022).
- **Workflow:** `dft_flow.sh`, a single documented entry point for CERN HTCondor (CPU and GPU) and local runs, with automatic resource allocation, a watchdog and a live dashboard.
- **Dashboard:** `dashboard_cern.py`, the live results page at http://localhost:8767.

## Run the DFT workflow
```bash
cd qe_workflow
./dft_flow.sh              # help: every command documented
./dft_flow.sh login        # prints the CERN login command (you authenticate yourself)
./dft_flow.sh generate NAME && ./dft_flow.sh plan NAME && ./dft_flow.sh submit NAME
./dft_flow.sh auto 10      # real-time status, fetch, analysis, watchdog
./dft_flow.sh dashboard    # live page
```
VS Code: open `qe_workflow/iwo_dft.code-workspace` and use **Terminal → Run Task → DFT: …**.

## Methods (short)
- **DFT method:** Quantum ESPRESSO 7.5 (CPU) and 7.3.1 (GPU, NVIDIA NGC); PBE; PAW pslibrary 1.0.0; 71/568 Ry.
- **Crystal structure:** bixbyite Ia-3 (Marezio 1966).
- **GPU validation:** H100 NVL against 16 CPU cores gave identical results (ΔE = 5×10⁻⁷ Ry) at 8.2× the speed.

## Not included
- Copyrighted papers.
- DFT wavefunction and charge-density scratch data, which can be regenerated.
- ATLAS `.str` files and archives.

No credentials are stored in this repository.
