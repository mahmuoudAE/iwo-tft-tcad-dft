# ML potential validation: criteria fixed before any result (2026-10-10)

**Potential:** MACE-MPA-0 "medium" foundation model.
- File: `/eos/user/m/melrashe/iwo_amorph/env/mace-mpa-0-medium.model` (79,462,305 bytes).
- Environment archive SHA-256: `2b79ed8647f166cec5ac3c994cdfa1901b9aac29856daa3822b7c3b58927e874`.

**What is compared.** DFT (PBE, PAW pslibrary, 60/480 Ry, mv 0.01 Ry, k 2×2×2 bulk / 2×2×1 slab, dipole correction for slabs) against MACE. MACE is evaluated as float64 on the identical snapshot. Script: `compute/amorph/dft/make_val.py`.

**Snapshots:**

| Structure | Snapshots |
|---|---|
| `aIWO_bulk_s1` | melt_3000K, quenched_300K, final |
| `aIO_bulk_s1` | quenched_300K, final |
| `aIWO_2p0_s1` | slab_annealed, final (surfaces with OH/H, W environment) |
| `aIWO_0p7_s1` | final (thinnest film) |

**Pass limits.** They apply to the quenched, annealed and final frames. Melt frames are reported, not scored.

| Quantity | Limit |
|---|---|
| Force RMSE (all atoms, all components) | ≤ 0.15 eV/Å |
| Force MAE | ≤ 0.10 eV/Å |
| W atoms and their first-shell O, force RMSE | ≤ 0.25 eV/Å |

These are reported separately because W is the least-sampled element.

**If a limit fails:**
- Production DFT relaxations continue (decision D-12).
- The ML structures are then described as "starting points relaxed by DFT", not as validated amorphous models.
- Any structural statistic taken from the ML stage alone (coordination, density) is not reported as a result.
- If the 2 nm slab fails badly (force RMSE > 0.3 eV/Å), its production run is stopped, and the slot is reused for a short DFT anneal of that slab.

**Known limits even on a pass:**
- Force agreement on 8 snapshots does not prove the ML-quenched ensemble is representative of sputtered films.
- One or two samples per structure give no disorder statistics. A difference smaller than the gap between the two 2 nm samples is not a result.
