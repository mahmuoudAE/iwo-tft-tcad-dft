# DFT protocol, stage 4: W-doped bulk and In2O3 slabs on CERN HTCondor

Written 2026-09-27, before any calculation of this stage had run. The criteria below are fixed in advance. Settings are inherited from the bulk protocol (`../bulk_In2O3_protocol/PROTOCOL.md`): PBE, pslibrary 1.0.0 PAW, 71 Ry / 568 Ry. All four data sets suggest lower cutoffs (In 41/212, O 47/323, W 50/475, H 46/221 Ry, from the UPF headers).

## 1. Structures
All structures come from `../structures_v2/build_structures.py`, run on the PBE-relaxed host of stage 2. The script was first tested on the experimental structure, and every structure passes these checks:
- composition and electron count;
- the spglib space group and number of symmetry operations;
- bond lengths and minimum non-bonded distances.

**IWO bulk.** 80-atom conventional cell, one In replaced by W, giving In31WO48 (W/(W+In) = 3.1 %).
- **Sites computed:** both cation sites of bixbyite, so the site preference is a result, not an assumption:
  - 8b: site symmetry -3; the doped cell keeps 6 operations;
  - 24d: site symmetry 2; the doped cell keeps 2 operations (P2).
- **Carriers:** relative to In3+, W6+ gives 3 electrons to the conduction band, about 2.8e21 cm^-3 in this cell. This is far above the carrier density of the TFT channel. The cell therefore describes the fully ionized, degenerate limit, and band-edge quantities are read from the dispersion near Gamma.

**Slabs.** These follow the recipe of Lin et al., ACS Nano 16, 21536 (2022), p. 21542:
- take the 80-atom conventional cell (or its 1x1x2 supercell);
- remove the In layer at the cell boundary;
- passivate the top and bottom O layers with one H per O;
- add 25 A of vacuum.

Applied to our cell, the recipe gives:
- **slab 1:** In24O48H24, 96 atoms, 0.98 nm H to H;
- **slab 2:** In56O96H24, 176 atoms, 1.99 nm H to H.

Lin et al. quote 0.95 nm and 1.98 nm.

Properties of these slabs:
- **Surface oxygen:** each of the 24 surface O atoms loses exactly two In neighbours.
- **Electron count:** it closes, 3 n(In) + n(H) = 2 n(O), so the slabs are expected to be insulating.
- **Symmetry:** space group Pcca, 8 operations. The two surfaces are related by symmetry, so the slab has no dipole.
- **Hydrogen:** H starts 0.97 A from O, pointing along the mean direction of the two removed In-O bonds.

## 2. Calculations (job list in `jobs/make_jobs.py`)

| job | what | k-points | resources |
|---|---|---|---|
| iwo_W8b, iwo_W24d | relax (forces < 1e-3 Ry/bohr, energy < 1e-4 Ry), then SCF 4x4x4 + PDOS + bands near Gamma, then spin-polarized SCF 3x3x3 | relax 3x3x3 | 32 cores, testmatch |
| slab1_v15, slab1_v25, slab1_v35 | SCF + planar-averaged potential + in-plane bands near Gamma, unrelaxed geometry: vacuum test | 3x3x1 | 16 cores, tomorrow |
| slab2_v25 | same, unrelaxed slab 2 | 3x3x1 | 16 cores, tomorrow |
| slab1_relax, slab2_relax | atoms and in-plane cell relaxed (cell_dofree = '2Dxy'), then SCF + potential + bands | 3x3x1 | 32 cores, testmatch / nextweek |

**Numerical choices:**
- **Smearing:** doped cells use Marzari-Vanderbilt cold smearing, 0.01 Ry (N. Marzari et al., Phys. Rev. Lett. 82, 3296 (1999)).
- **Slab occupations:** slabs use fixed occupations, as the bulk did.
- **Slab mixing:** slabs use Thomas-Fermi-screened mixing (local-TF; D. Raczkowski, A. Canning, L.-W. Wang, Phys. Rev. B 64, 121101 (2001)).
- **Vacuum level:** taken from the planar average of the electrostatic potential (bare + Hartree, pp.x plot_num 11) in the vacuum region. Macroscopic averages follow A. Baldereschi, S. Baroni, R. Resta, Phys. Rev. Lett. 61, 734 (1988).
- **Bulk band path:** Gamma-H-N-Gamma-P-H|P-N (W. Setyawan, S. Curtarolo, Comput. Mater. Sci. 49, 299 (2010)).

**Deviations from Lin et al., recorded in advance:**
- PAW at 71 Ry instead of norm-conserving at 140 Ry.
- Relaxation to 1e-3 Ry/bohr instead of 1e-4 Ry/bohr, because of the compute budget.

## 3. Acceptance criteria and read-out (fixed in advance)

**1. k-points for the doped cell.** Compare k3 with k4 at the relaxed geometry. The energy must change by less than 1 mRy/atom (the same criterion as the host). The site-preference energy dE = E(8b) - E(24d) must change by less than 10 meV.
- If the criteria fail, the k4 values are used and the failure is reported.
- The smearing term (-TS) per atom is reported.

**2. Site preference.** dE is reported with its thermal meaning. The occupation ratio 24d:8b is 3 exp(dE/kT), where the factor 3 is the multiplicity ratio. If |dE| < kT at the anneal temperature, both sites are counted as populated.

**3. W oxidation state from structure.** Mean W-O bond lengths are compared with Shannon radii (R. D. Shannon, Acta Cryst. A 32, 751 (1976)): O2- (CN 4) 1.38 A, W6+ 0.60 A, W5+ 0.62 A, W4+ 0.66 A (CN 6), and In3+ 0.80 A. The expected bond lengths are therefore:

| cation | expected bond to O |
|---|---|
| W6+ | 1.98 A |
| W5+ | 2.00 A |
| W4+ | 2.04 A |
| In3+ | 2.18 A |

**4. Magnetism.** The cell is called non-magnetic if |total magnetization| < 0.05 muB/cell and the spin-polarized energy is not lower by more than 1 mRy.

**5. Resonant or localized W 5d.** From the PDOS, report the energy of the W 5d weight relative to the CBM and E_F. Also report the Burstein-Moss filling E_F - CBM, and the CB mass near Gamma (parabolic within 0.05 1/A), compared with the host.

**6. Vacuum convergence.** The electron affinity EA = E_vac - CBM and the ionization potential IP = E_vac - VBM must change by less than 10 meV from 15 to 25 A and from 25 to 35 A. If they do, 25 A (Lin et al.) is confirmed; otherwise the largest vacuum is used.

**7. Confinement.**
- dEg(t) = Eg(slab) - Eg(bulk), with the bulk gap from stage 3 at the same lattice constant. The band-edge partition comes from the changes of EA and IP between the slabs.
- m*(t) comes from in-plane parabolic fits within 0.05 1/A along [100] and [110].
- These are compared with Lin et al. (p. 21540 and p. 21542): dEg of +0.94 eV (0.95 nm) and +0.33 eV (1.98 nm), and m* of 0.30 m0 (0.95 nm) and 0.23 m0 (1.98 nm).
- The recipe counts as reproduced if dEg agrees within 0.1 eV. A larger difference is reported and not hidden.

**8. Status labels.** The TCAD proxies (DFT_PURE_IN2O3_PROXY) are replaced only by results that pass items 1 and 6. Replacing a proxy makes the input "computed", not "validated": validation needs measured IWO data.

**IWO slabs** are designed after the site preference is known, and their design will be recorded here before they run.

## 3a. Execution log

**Host (2026-09-27).** Stage 2 gave a = 10.3061 A. The structures were rebuilt from it in `../structures_v2/relaxed_pbe/`:
- slab 1 is 0.988 nm H to H; slab 2 is 2.018 nm;
- all checks passed.

**First submission: cluster 12756318, 00:56Z.**
- The four 32-CPU jobs stopped after 18 s. Their slots expose hardware threads, and PRRTE refused 32 ranks. The fix was mpirun `--map-by :OVERSUBSCRIBE`, verified locally.
- slab2_v25 (16 CPUs, 4 pools) was held: it used 95.8 GB against a 48 GB limit, about 24 GB per pool.
- No physics output came from the failed attempts. They are archived in `results/failed_20260927a/`.

**Resubmission: cluster 12756469, 01:08Z.**
- The five affected jobs were resubmitted.
- Slab 2 now uses 32 CPUs, at most 2 pools and 80 GB.
- The three vacuum-test jobs (16 CPUs) of cluster 12756318 kept running.

**Bands diagonalization (01:25Z).**
- The local non-SCF bands run of bulk In2O3 aborted with Davidson (MPI abort after 9 of 16 k-points, with repeated "eigenvalues not converged"). It was restarted with CG diagonalization.
- The bands inputs of the not-yet-started CERN jobs (slab1_relax, slab2_relax) were patched to CG before they started. make_jobs.py now uses CG for all bands runs.
- The jobs already running (iwo_*, slab1_v*, slab2_v25) keep Davidson in their final bands step. If that step fails, their SCF, PDOS and potential results are unaffected, and the masses come from the relax jobs.

**slab2_relax moved to 64 CPUs (01:38Z).** It was resubmitted with 64 CPUs, 128 GB and 2 pools as cluster 12756505. It started within 5 min, and the 32-CPU copy (12756469.4, running about 10 min) was removed. The settings are otherwise identical.

**Thread oversubscription found and fixed (08:46Z).**

*Measurement at 08:44Z.* After about 7.5 h, the running jobs had completed only 4-27 SCF iterations, while slab1_v35 needed 84 s per iteration. Inside the jobs (condor_ssh_to_job):
- HTCondor sets OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = RequestCpus in the job environment;
- each pw.x process ran 65 threads (OpenBLAS), and node loads reached 206-1072;
- the driver had set only OMP_NUM_THREADS = 1.

*Why slab1_v35 was unaffected.* It finished at normal speed, presumably because its node was less loaded. Its numbers are unaffected, because thread counts change speed, not results.

*Fix.* The driver now exports OMP_NUM_THREADS, OPENBLAS_NUM_THREADS and MKL_NUM_THREADS = 1.

*Resubmission.* All seven running jobs were removed (clusters 12756318, 12756469, 12756505) and resubmitted unchanged otherwise, as cluster 12756948 (`jobs/gen_20260927d`).

*Local runs.* Local runs were checked and are not affected: 3 threads per process, which are MPI helper threads.

**09:02-10:00Z: 64-CPU upgrade attempt.** 64-CPU copies of the IWO cells and slab1_relax (cluster 12756979) did not start within about 1 h and were removed.
- A scheduler outage (bigbird26, SECMAN:2007) interrupted the automatic decision.
- The duplicates were resolved once the scheduler answered.

**14:36Z: relaxations resized.**
- *Cause of the queueing.* `condor_q -better-analyze` showed that jobs of 32 or more CPUs go to the 'bigmcore' host group. It has 10 slots, 0 of them free, and 3 were held by our own running jobs.
- *Change.* slab1_relax was moved to 16 CPUs (normal pool; same layout as slab1_v35, 84 s per SCF iteration). slab2_relax was moved to 32 CPUs, 2 pools.
- *Resubmission.* Both were resubmitted as cluster 12757723 (`jobs/gen_20260927f`); the idle originals were removed.
- *Note.* HTCondor at CERN shows RequestMemory as 1.5x the requested value.

**GPU validation (2026-09-28).**
- *Setup.* NVIDIA's NGC container `hpc/quantum_espresso:qe-7.3.1` (GPU build, 1.61 GB SIF on EOS; user-approved download) was benchmarked on 1x H100 NVL. The benchmark repeated the finished CPU job slab1_v15 (QE 7.5, 16 CPUs) with identical input.
- *Agreement.* E = -11888.29271202 Ry versus -11888.29271155 Ry (dE = 5e-7 Ry). Gap 0.9586 eV in both. 46 SCF iterations in both.
- *Speed.* 9 min 16 s versus 1 h 16 min, i.e. 8.2x.
- *Consequence.* The QE version difference (7.3.1 on GPU, 7.5 on CPU) has no effect at the protocol tolerances.
- *Decision.* The slab relaxations continue on GPUs:
  - slab1 restarts from the geometry of CPU BFGS step 13 (force 0.076 Ry/bohr; the BFGS history is not carried over);
  - slab2 starts fresh on 2 GPUs (its CPU run had not finished its first SCF).
  - Each CPU job is removed only once its GPU replacement runs.
- *Post-processing.* pp.x and projwfc.x remain on the CPU environment inside the same job.

## 4. Execution

**How the jobs run:**
- QE 7.5 comes from a conda-pack archive on EOS.
- `jobs/common/driver.sh` unpacks it on the worker node and runs the steps of each job.
- pw.x's max_seconds is set from the flavour limit, so every run stops cleanly before the wall-time limit.
- The outputs are always packed into `<job>_results.tar.gz`.
- `cern_submit.sh` uploads and submits.
- `cern_wait.sh` fetches finished results into `results/`.

**Test before submission:** the whole pipeline was tested locally, using the same driver and steps, on small W test systems before submission.

Local test result (2026-09-27, 2 MPI processes):
- Bulk-type job: relax -> geometry transfer -> SCF -> PDOS -> bands all completed.
- Slab-type job: vc-relax (in-plane cell 3.17 -> 2.97 A, vacuum axis fixed) -> cell and geometry transfer -> SCF -> planar average (3000 points) -> bands all completed.
- The results tarballs were complete in both cases.

Two findings from the toy runs changed the production settings:
- **Test settings.** The toy W metal did not converge at 2x2x2 k-points with 0.01 Ry smearing. The test was therefore run with denser k-points and 0.02 Ry.
- **Spin-polarized SCF.** The toy spin-polarized SCF (W metal with an imposed starting moment) did not converge in 300 iterations. For production:
  - electron_maxstep is capped at 100 for the doped cells and 150 for the slabs;
  - the spin run uses mixing_beta 0.2;
  - a non-converged spin run is reported as such and never read as a result.
