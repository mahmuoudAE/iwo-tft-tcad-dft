# H-L crystalline cells: geometry binding (A20 logging prerequisite)

**Read 2026-10-13T02:04-02:11Z, lxplus via the existing SSH ControlMaster, read-only.** Trees: `~/iwo_amorph/vac/<cell>/` and `~/iwo_amorph/checks/gpumax_work/a20_g002/<cell>/` only. Tar members were read in memory (python `tarfile`), nothing was extracted or written on lxplus. No condor command, no git, no Codex call, no amorphous file opened. **No energies were parsed or printed** (only CELL_PARAMETERS, ATOMIC_POSITIONS, the pw.x header site positions, atom counts and the `bfgs converged` line).

**Canonical geometry hash** = sha256 of the text `CELL_PARAMETERS <unit>` + 3 rows + `ATOMIC_POSITIONS <unit>` + nat rows `label x y z`, whitespace-normalised, species labels as written, every number parsed to float and re-printed `%.10f` (-0 -> 0); `if_pos` flags dropped (none present in any file). **Units as written: positions `crystal` in every file, cell `angstrom`** (cubic, a = 10.3060902 A in every file). Max |Δcoord| is in crystal units (x a = A: 1e-8 crystal = 1.0e-7 A).

**(a) relaxed geometry** = the `ATOMIC_POSITIONS (crystal)` block between `Begin final coordinates` and `End final coordinates` in `vac/<cell>/relax.out` (one `bfgs converged` line per file). These are fixed-cell `relax` runs, so the final block carries no cell; the cell of (a) is the relax.in CELL_PARAMETERS, and the cell printed in the relax.out header (celldm(1) x crystal axes) agrees with it to 5.6e-8 A (print precision). For the 0-step hosts the final block is the input geometry (equal to the header site positions to <= 5e-8). For the four vacancy cells the final block is identical (Δ = 0) to the last BFGS geometry printed before it.

## 1. Binding table

| Cell | nat | Species | relax.out | hash (a) | (b) vac scf.in (k4 FINAL) max abs Δ / hash | (d) a20 scf.in max abs Δ / hash | (c) final tar scf.in / (d) a20 tar scf.in max abs Δ | Geometry pw.x ran (header, 7 dp): FINAL scf.out / final tar scf.out / A20(ii) tar scf.out | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| In32O48 | 80 | In32 O48 | bfgs converged (QE line: 0 BFGS steps) | `4a38745af874a820` | 0 / hash = | 0 / hash = | 0 / 0 | 1.9e-08 / 1.9e-08 / 1.9e-08 | BOUND |
| In31WO48 | 80 | In31 W1 O48 | bfgs converged (QE line: 0 BFGS steps) | `190b69fd7895d167` | 0 / hash = | 0 / hash = | 0 / 0 | 5.0e-08 / 5.0e-08 / 5.0e-08 | BOUND |
| In32O47 | 79 | In32 O47 | bfgs converged (QE line: 13 BFGS steps) | `22d5673303e3e6ca` | 0 / hash = | 0 / hash = | 0 / 0 | 5.0e-08 / 5.0e-08 / 5.0e-08 | BOUND |
| In31WO47_far | 79 | In31 W1 O47 | bfgs converged (QE line: 16 BFGS steps) | `d1904a6a7e039809` | 0 / hash = | 0 / hash = | 0 / 0 | 5.0e-08 / 5.0e-08 / 5.0e-08 | BOUND |
| In31WO47_near | 79 | In31 W1 O47 | bfgs converged (QE line: 18 BFGS steps) | `db53075a4ec265a6` | 0 / hash = | 0 / hash = | 0 / 0 | 4.9e-08 / 4.9e-08 / 4.9e-08 | BOUND |
| In31WO47_near72 | 79 | In31 W1 O47 | bfgs converged (QE line: 29 BFGS steps) | `00588209500d4887` | 0 / hash = | 0 / hash = | 0 / 0 | 5.0e-08 / 5.0e-08 / 5.0e-08 | BOUND |

All derived inputs: same nat (80 hosts, 79 vacancy cells), same species sequence (order identical), cell Δ = 0, one ATOMIC_POSITIONS card, no extra rows. The pw.x-printed geometries differ from (a) only by the 7-decimal header rounding (<= 5.0e-8 crystal). **(e)** `relax_s0_results.tar.gz::relax.out` and `final_results.tar.gz::relax.out` are byte-identical (sha256) to `vac/<cell>/relax.out` for all six; `relax_s0_results.tar.gz::relax.in`, `final_results.tar.gz::relax.in` and `vac/<cell>/relax.in` are byte-identical and equal (a) (Δ = 0).

**Caveat on (e):** `steps_relax.sh` (md5 4d6d99a9..., identical in all six cells) overwrites relax.in with the converged geometry (`qeio.py newgeom relax.in relax.out`) before `driver.sh` packs the tarball, so the archived relax.in files are the *converged* geometry, not the relaxation start. They agree with (a) by construction and are not independent evidence. Starting geometries are bound in section 2 instead. scf.in was produced by `qeio.py newgeom final.tmpl relax.out` (steps_final.sh, md5 19224739...); the A20(ii) scf.in was derived from vac scf.in.

**Input settings differences (non-geometry lines, inputs only):**

- final.tmpl -> vac scf.in: `max_seconds` only (1.0d8 -> runtime value; `driver.sh run_pw` rewrites it in the job sandbox).
- vac scf.in -> a20 scf.in: `degauss 0.005 -> 0.002` and `K_POINTS 4 4 4 0 0 0 -> 3 3 3 0 0 0` only, all six cells.
- a20 scf.in -> a20 tarball scf.in: `max_seconds` only (runtime rewrite). This is why the two files have different md5/sha256 while the geometry hash is equal.

## 2. Starting geometries and vacancy sites

The relaxation start (geometry 0) is bound three ways: the pw.x header site positions in relax.out (crystal, 7 dp), the built `<cell>.xyz` (Cartesian A, 8 dp, converted with the xyz Lattice = the same cubic cell, Δcell = 0), and, for the vacancy cells, the relaxed parent (a) with one O removed. The parents relaxed in 0 BFGS steps, so parent (a) = parent input.

| Cell | xyz nat / species | xyz vs relax.out geometry 0 (max abs Δ, crystal) | Parent | Removed parent atom (0-based) | Other atoms vs parent (a), order preserved | W-O of removed O in relaxed In31WO48 | Max displacement (a) vs start (crystal / A) |
|---|---|---|---|---|---|---|---|
| In32O48 | 80 / In32 O48 | 1.9e-08 | - | - | - | - | 1.9e-08 (0 steps) |
| In31WO48 | 80 / In31 W1 O48 | 5.0e-08 | - | - | - | - | 5.0e-08 (0 steps) |
| In32O47 | 79 / In32 O47 | 1.9e-08 | In32O48 | O17 | 4.9e-11, yes; header geometry 0: O17 removed, 1.9e-08 | n/a (no W) | 0.01198 / 0.123 |
| In31WO47_far | 79 / In31 W1 O47 | 5.0e-08 | In31WO48 | O32 | 4.8e-10, yes; header geometry 0: O32 removed, 5.0e-08 | 6.84785 A | 0.01607 / 0.166 |
| In31WO47_near | 79 / In31 W1 O47 | 4.8e-03 (restart start = attempt1 geometry 2, see section 3); vs attempt1 start 4.8e-10 | In31WO48 | O30 | 4.8e-10, yes; attempt1/relax.in: O30 removed, 0 | 1.89194 A | 0.01558 / 0.161 (vs restart start) |
| In31WO47_near72 | 79 / In31 W1 O47 | 5.0e-08 | In31WO48 | O72 | 4.8e-10, yes; header geometry 0: O72 removed, 5.0e-08 | 1.90237 A | 0.03556 / 0.367 |

W-O distances in the relaxed In31WO48 (a) (W = atom 4, 0-based; minimum image):

```
In31WO48 relaxed: W index 4
  W-O30  1.89194285 A
  W-O69  1.89194285 A
  W-O72  1.90236897 A
  W-O73  1.90236897 A
  W-O32  6.84784581 A
  W-O33  6.84784581 A
  W-O29  6.76579654 A
  W-O70  6.76579654 A
```

Site rule check: registered near = O30 (O30/O69 unsplit, Δ = 0 at 1e-8 A); O72/O73 pair +0.01042612 A (> 1e-3 A, no TIE); far = O32, which has an exact symmetry partner O33 (equal to 1e-8 A); the next pair O29/O70 is 0.08205 A closer. Removed atoms O30, O72, O32 match A19/A28 exactly.

## 3. In31WO47_near: A28 restart history

| Check | Result |
|---|---|
| attempt1/relax.in = relax.in.pre_A28_20261011T130452Z = a28_staging/relax.in.template_current = a28_staging/s0/relax.in = attempt1 tar::relax.in | byte-identical (sha256 560d0e2a..., md5 1dbac6b9...) |
| attempt1/relax.out = a28_staging/s0/relax.out = attempt1 tar::relax.out | byte-identical (md5 409ed686..., as in apply_A28_near.sh and MANIFEST.md5) |
| attempt1/relax.out | nat 79, `bfgs converged` 0, `convergence NOT achieved` 1, 3 BFGS geometries printed (1-3), no final block -> failed at geometry 3 (A28 erratum) |
| attempt1 start (attempt1/relax.in) | = In31WO48 (a) minus O30 exactly (Δ 0, order preserved); = xyz to 4.8e-10; = pw.x header geometry 0 to 5.0e-08 |
| relax.in.A28 positions vs attempt1 geometries 1 / 2 / 3 | 2.4e-03 / **0** / 3.1e-03 -> relax.in.A28 = geometry 2 exactly |
| relax.in.A28 vs attempt1/relax.in, non-geometry lines and cell | no difference (A19 settings, cell Δ 0); local-TF fallback not used |
| current vac relax.in vs relax.in.pre_A28, non-geometry lines | `max_seconds` only (70181 vs 70185, runtime rewrites) |
| relax.in.A28 md5 vs MANIFEST.md5 (0dbaae02...) | match; template_current, s0/relax.in, s0/relax.out also match |
| restart 1 pw.x header geometry 0 vs relax.in.A28 | 5.0e-08 (7-dp print rounding) -> restart started from geometry 2 |
| restart 1 relax.out | `bfgs converged in 19 scf cycles and 18 bfgs steps`; final (a) vs restart start 0.01558 crystal (0.161 A) |
| relax.sub / final.sub vs a28_staging/*.A28q2 | byte-identical (md5 be6809f1... / 3ab7d9d5...) |

Geometry hashes of the A28 history: attempt1 start `80e8ccb43889b2e58cb9b9045d97e67bbcb5e5e9d010d8ae258ac7415d06db35`, relax.in.A28 (restart start) `6d2572e3976e8108f0a1b7efca48db9a99dfb8df15ad3bafc06be4f2b80489c2`.

## 4. Full canonical geometry hashes (a)

| Cell | sha256(canonical CELL+ATOMIC_POSITIONS, %.10f) | sha256(ATOMIC_POSITIONS only) |
|---|---|---|
| In32O48 | `4a38745af874a82080f88ee05aa38cfeecba68fb19c08255b99d5c94b6da61fa` | `56e526635fcfdc8a57e9be65d549a1db076a76146815a0d767bd6335bf9fba58` |
| In31WO48 | `190b69fd7895d1671319c8e3c64beed7bb2bbae6278ef5ad0885bcfdc5279976` | `0ac039b1cc7ffabbea20a942d8ba93917f975fd7afecd2b29d8b3c01dcb1df5e` |
| In32O47 | `22d5673303e3e6ca1dce468d73ca3d50639a3370a7b4f35ac7b272cb69121822` | `f4222313eba2668b179b088413d87366f48e2993ee8e7516fccc640cc09d52c3` |
| In31WO47_far | `d1904a6a7e039809562e48da60796adcb22c4e346499a543272aa65bbf6589bb` | `33e9ebbbc7e3f44dbdc1ec6625b38d610953f2165eff8ae410736375a1a95b05` |
| In31WO47_near | `db53075a4ec265a6105b1ec6b4a9939a3b5fae3e5b1104db3ae0051003eaf6a4` | `efd3440d2ee96d7bcbf28836945cc40761513f66f9ec5d570d57ba14ddd25e42` |
| In31WO47_near72 | `00588209500d48873a01ad6e7c851c652a9407da3a837861ee919c877f27d17f` | `842bfebb75faeea3865330b82b9ec9c569e2b51e3b3c3e602c7da5a70662c88b` |

These are the geometry identities to freeze for A20(i): each spin single point should carry the hash of its ATOMIC_POSITIONS+CELL, which must equal the row above.

## 5. Structure sanity of the relaxed geometries (distances only)

```
In32O48 nat 80 | shortest contact 2.1671 A | In-O 1st-shell min 2.1671 max(6th) 2.2561, CN(<2.6 A) range 6-6 over 32 In
In31WO48 nat 80 | shortest contact 1.8919 A | In-O 1st-shell min 2.1246 max(6th) 2.4784, CN(<2.6 A) range 6-6 over 31 In | W-O 1st-shell min 1.8919 max(6th) 2.1523, CN(<2.6 A) range 6-6 over 1 W
In32O47 nat 79 | shortest contact 2.1137 A | In-O 1st-shell min 2.1137 max(6th) 4.0159, CN(<2.6 A) range 5-6 over 32 In
In31WO47_far nat 79 | shortest contact 1.8836 A | In-O 1st-shell min 2.1270 max(6th) 4.0097, CN(<2.6 A) range 5-6 over 31 In | W-O 1st-shell min 1.8836 max(6th) 2.1641, CN(<2.6 A) range 6-6 over 1 W
In31WO47_near nat 79 | shortest contact 1.8792 A | In-O 1st-shell min 2.1173 max(6th) 3.9791, CN(<2.6 A) range 5-6 over 31 In | W-O 1st-shell min 1.8792 max(6th) 3.8457, CN(<2.6 A) range 5-5 over 1 W
In31WO47_near72 nat 79 | shortest contact 1.7905 A | In-O 1st-shell min 2.1062 max(6th) 3.7910, CN(<2.6 A) range 5-6 over 31 In | W-O 1st-shell min 1.7905 max(6th) 3.8070, CN(<2.6 A) range 5-5 over 1 W
```

In32O48: In-O first shell 2.1671-2.2561 A, every In 6-coordinated. The upper end is above the 2.12-2.21 A protocol window because the cell is the frozen PBE host value (a = 10.3061 A, about 1.9 % above experiment); the window is a check on experimental-lattice builds, not a defect here.

## 6. File hashes (md5, sha256)

Paths relative to `~/iwo_amorph/`; `X::m` = member m of tarball X (read in memory).

| Bytes | md5 | sha256 | File |
|---|---|---|---|
| 20694 | `37f849622e5f0759bd564d70f985c97c` | `4d4808ab2e82af0d406b0e489f92c1060999b3bab1d28213b41f3422b1739369` | vac/In32O48/relax_s0_results.tar.gz |
| 48488 | `1fb557a992fa8532679b100fc992323e` | `d1614c6c26b5b097b93aacd08189ce524268c1e16ccb878358a0a77e2fa59ac6` | vac/In32O48/final_results.tar.gz |
| 4212 | `43966ad339234bbf514f69b8cf2a5c6e` | `12e6399c2c92c38687c01115ee1fc87d9c637e0a2cacd92d40e64b69d5e7cfe0` | vac/In32O48/final.tmpl |
| 199127 | `331a91dac6ebab255989b74b9338729f` | `fa8c79bd5be11390a828349ef37fe7c9929ae1b4c94221322607c3fd53f790bd` | vac/In32O48/scf.out |
| 19318 | `3ff4a19863ef98f9e2eaf299cbeaa8ba` | `95e045dbabbd60766c218ba2890ca29cea8e90234fe2f7fbbe9e9dd4e5968a17` | checks/gpumax_work/a20_g002/In32O48/a20g002_In32O48_results.tar.gz |
| 6548 | `391273777efe035ca62ba5bb467b5d69` | `e89421cc96b92580618bddbdff71c6ab8a33f57dec4e6a63f5a6b97e30903d75` | vac/In32O48/relax.in |
| 143078 | `ec532bce6f2d381440460a16e57fd797` | `47de6ca01f1ba5c672fd143fbf7771b5235d57db3b48ab79ab30fdb7253458f1` | vac/In32O48/relax.out |
| 6452 | `f07243438cfa7870fad7ee8118c92e71` | `a9968110956481ed99c5713b19c42362fd58d7523c65860942d45bafdbfc5ed5` | vac/In32O48/scf.in |
| 4029 | `3bac31f6fe4b3985f222357eedb29574` | `8e531314ea99574e5022a34ed56b4a0a58ac6ff02611f0cb42447951c84718a5` | vac/In32O48/In32O48.xyz |
| 6452 | `f07243438cfa7870fad7ee8118c92e71` | `a9968110956481ed99c5713b19c42362fd58d7523c65860942d45bafdbfc5ed5` | vac/In32O48/final_results.tar.gz::scf.in |
| 6548 | `391273777efe035ca62ba5bb467b5d69` | `e89421cc96b92580618bddbdff71c6ab8a33f57dec4e6a63f5a6b97e30903d75` | vac/In32O48/final_results.tar.gz::relax.in |
| 143078 | `ec532bce6f2d381440460a16e57fd797` | `47de6ca01f1ba5c672fd143fbf7771b5235d57db3b48ab79ab30fdb7253458f1` | vac/In32O48/final_results.tar.gz::relax.out |
| 199127 | `331a91dac6ebab255989b74b9338729f` | `fa8c79bd5be11390a828349ef37fe7c9929ae1b4c94221322607c3fd53f790bd` | vac/In32O48/final_results.tar.gz::scf.out |
| 6548 | `391273777efe035ca62ba5bb467b5d69` | `e89421cc96b92580618bddbdff71c6ab8a33f57dec4e6a63f5a6b97e30903d75` | vac/In32O48/relax_s0_results.tar.gz::relax.in |
| 143078 | `ec532bce6f2d381440460a16e57fd797` | `47de6ca01f1ba5c672fd143fbf7771b5235d57db3b48ab79ab30fdb7253458f1` | vac/In32O48/relax_s0_results.tar.gz::relax.out |
| 6452 | `214f90c2b9275696a43d168ab47342df` | `11e2e9030d83df0c19546c4c5d3bffd7b4bd73656b60c55c7f85ec534d0e72d7` | checks/gpumax_work/a20_g002/In32O48/scf.in |
| 6452 | `b8e27abf998bba2306bb8ef7b7677be1` | `37852a828034c8c4de4c002a346f84dce125bef90d75408e1a5bdbf5dfaf7381` | checks/gpumax_work/a20_g002/In32O48/a20g002_In32O48_results.tar.gz::scf.in |
| 136917 | `6cdb228af508d8c46c3c43d461bc6cc4` | `714f2e19053da038d83588e5b72a96bff1e10e319635e7bd69b128d2f68b6459` | checks/gpumax_work/a20_g002/In32O48/a20g002_In32O48_results.tar.gz::scf.out |
| 36342 | `31ec63a964f3503f5dc0fa5c003a9071` | `1bb9519fe2e11a14eb97aa89523bfe8147161431eade7605fef903611d788934` | vac/In31WO48/relax_s0_results.tar.gz |
| 100295 | `d7db775140c0710029a96bdf6c6246a2` | `8e849e88f16a7aa505069cf443ba6ff26e194f6406c7153b779688ea54cca4d3` | vac/In31WO48/final_results.tar.gz |
| 4255 | `4d43688942a9f10ea79d76708ae797f3` | `3600b2e5639508c43e7d4c1000baf4f035961495a812525773229628c4b06927` | vac/In31WO48/final.tmpl |
| 340351 | `0b38b421e054a171e53fd9adb9f75c1b` | `de417f025469799f85ae24c1ddc168fbac205dae47fa84fcb0f3295c94418c74` | vac/In31WO48/scf.out |
| 34962 | `cd940fd3fbf9fa306030393bc66edee0` | `96d948a974fa671589ea60053012a074ed422d63362f998c07d0dc99386db45c` | checks/gpumax_work/a20_g002/In31WO48/a20g002_In31WO48_results.tar.gz |
| 6589 | `210520bc636705202626644d01c9954f` | `3b8b7db5fb65ef84676b66d9f1d448f5da14d1590689d3773716446f67364ebe` | vac/In31WO48/relax.in |
| 180089 | `fee15ef06369c21a7a77bf388eb1a451` | `106b4d81cdd81b5ab19583c02630210ccee83effb072e992b0751e59a5b77337` | vac/In31WO48/relax.out |
| 6493 | `c7861e1f35254d9e7fcbe8a9df8ed2d3` | `1bd9105027571e3db2c414d9810d016da9e2a7aa1438900c7c30261391b1a219` | vac/In31WO48/scf.in |
| 4030 | `c5d3bddbc433460cd5ce5c7f365c8efb` | `29c2b8bd5b00e96d0c5028cc059320c7c2609fdc97d31582f0f7306df1b3ebe3` | vac/In31WO48/In31WO48.xyz |
| 6493 | `c7861e1f35254d9e7fcbe8a9df8ed2d3` | `1bd9105027571e3db2c414d9810d016da9e2a7aa1438900c7c30261391b1a219` | vac/In31WO48/final_results.tar.gz::scf.in |
| 6589 | `210520bc636705202626644d01c9954f` | `3b8b7db5fb65ef84676b66d9f1d448f5da14d1590689d3773716446f67364ebe` | vac/In31WO48/final_results.tar.gz::relax.in |
| 180089 | `fee15ef06369c21a7a77bf388eb1a451` | `106b4d81cdd81b5ab19583c02630210ccee83effb072e992b0751e59a5b77337` | vac/In31WO48/final_results.tar.gz::relax.out |
| 340351 | `0b38b421e054a171e53fd9adb9f75c1b` | `de417f025469799f85ae24c1ddc168fbac205dae47fa84fcb0f3295c94418c74` | vac/In31WO48/final_results.tar.gz::scf.out |
| 6589 | `210520bc636705202626644d01c9954f` | `3b8b7db5fb65ef84676b66d9f1d448f5da14d1590689d3773716446f67364ebe` | vac/In31WO48/relax_s0_results.tar.gz::relax.in |
| 180089 | `fee15ef06369c21a7a77bf388eb1a451` | `106b4d81cdd81b5ab19583c02630210ccee83effb072e992b0751e59a5b77337` | vac/In31WO48/relax_s0_results.tar.gz::relax.out |
| 6493 | `1c046838b3fe0a923df38d9e74487e77` | `2e7d010f9e9b5c32d43a21a8019a72850ea671b453e6dbcd2a1411843a33ba1b` | checks/gpumax_work/a20_g002/In31WO48/scf.in |
| 6493 | `9a2ea6286629e62bfba009ae294354f0` | `07bbbe62b013ae108a64405e82369de136eeb2bc7a7df06e0dd1870a1857aafc` | checks/gpumax_work/a20_g002/In31WO48/a20g002_In31WO48_results.tar.gz::scf.in |
| 174706 | `a2d34709ee55645ed4e5f4ac1d8cbd49` | `8cfc1b4f97b05f2890eda6636e20d759a64ef8e7ac302ede132cc966a8e321c7` | checks/gpumax_work/a20_g002/In31WO48/a20g002_In31WO48_results.tar.gz::scf.out |
| 490285 | `a3baf281447c725752a8010fb0db8b66` | `5a65cafd14d19a632f9c929067226d98596693e4c543302eb58ac92bd0c54570` | vac/In32O47/relax_s0_results.tar.gz |
| 563957 | `08b9e0d477419520b9a5ab269ce2cbd1` | `39ad0b206ed2e818f1ed72af78e78d2b539859c189133b83a60132e74d5765e2` | vac/In32O47/final_results.tar.gz |
| 4168 | `b5f4270bea2ea6d3559fca2103947e8b` | `17164838072676c75b12e2b161f324302c7b6e3f41cddf547a2f80a3bedef7bd` | vac/In32O47/final.tmpl |
| 376567 | `ca6125f24b7f6a526f8f775a758469fd` | `32352fc6e0b0b2ee0242356c2a166a9a0ae6c951c534f3aae049f805faf17cd1` | vac/In32O47/scf.out |
| 41855 | `783820966eafd286b37c169b429c5da1` | `1d1e0cce2661596d5f2dfe9e370ef5aaa15f3f9232947318bb96706aeef5d3ec` | checks/gpumax_work/a20_g002/In32O47/a20g002_In32O47_results.tar.gz |
| 6476 | `bf687e0c1e70cb51dd2a88f30e3b9c38` | `25a3156ca1494caf3b133a7b95e7ce402582f91c87af18b5bb8cfbb0b2bcd556` | vac/In32O47/relax.in |
| 2457981 | `634f627f9da7a761be08a0d090194019` | `fa796a25465bf75b2f72ac750b8fb24fce6c24eca024ce9bd8904c11c9940b4d` | vac/In32O47/relax.out |
| 6380 | `e5d64dc63f2ca6438b965e6eaeb054fb` | `2bdc62ef2eef85a462acaff151cd8e43e5c7a1ce2c1e10823785f9e156a154e6` | vac/In32O47/scf.in |
| 3981 | `f9ab15301a47b0f4546b40a048b9137e` | `f018310131f92bb542efc0ff596b59ed092cefa2ad14293cd2a3dde3b0cc8cf9` | vac/In32O47/In32O47.xyz |
| 6380 | `e5d64dc63f2ca6438b965e6eaeb054fb` | `2bdc62ef2eef85a462acaff151cd8e43e5c7a1ce2c1e10823785f9e156a154e6` | vac/In32O47/final_results.tar.gz::scf.in |
| 6476 | `bf687e0c1e70cb51dd2a88f30e3b9c38` | `25a3156ca1494caf3b133a7b95e7ce402582f91c87af18b5bb8cfbb0b2bcd556` | vac/In32O47/final_results.tar.gz::relax.in |
| 2457981 | `634f627f9da7a761be08a0d090194019` | `fa796a25465bf75b2f72ac750b8fb24fce6c24eca024ce9bd8904c11c9940b4d` | vac/In32O47/final_results.tar.gz::relax.out |
| 376567 | `ca6125f24b7f6a526f8f775a758469fd` | `32352fc6e0b0b2ee0242356c2a166a9a0ae6c951c534f3aae049f805faf17cd1` | vac/In32O47/final_results.tar.gz::scf.out |
| 6476 | `bf687e0c1e70cb51dd2a88f30e3b9c38` | `25a3156ca1494caf3b133a7b95e7ce402582f91c87af18b5bb8cfbb0b2bcd556` | vac/In32O47/relax_s0_results.tar.gz::relax.in |
| 2457981 | `634f627f9da7a761be08a0d090194019` | `fa796a25465bf75b2f72ac750b8fb24fce6c24eca024ce9bd8904c11c9940b4d` | vac/In32O47/relax_s0_results.tar.gz::relax.out |
| 6380 | `e05b8f371fa1def88964ecdf92fa2729` | `5f8ebf81b00b52fef67963c3b732348ef6688719c9715081e4f3d562a5d09462` | checks/gpumax_work/a20_g002/In32O47/scf.in |
| 6380 | `8b6d74365508ad43f43cd5965679cfd2` | `3bb2d9185e029eb4ace2abe130da0e7b1a7fb40059fdd4d3ef15e1e96bab9d19` | checks/gpumax_work/a20_g002/In32O47/a20g002_In32O47_results.tar.gz::scf.in |
| 197000 | `18ba5ec249e92da06afd3acf34b04cdd` | `f1850ecb8db702182197b7cbbaaf9a0edb0621739c76d21e2e5e60a693fe0d3f` | checks/gpumax_work/a20_g002/In32O47/a20g002_In32O47_results.tar.gz::scf.out |
| 605984 | `be1e71a7220a3837ee2ae915a170238e` | `e7684051b49f859a700e48aa75eaadad3c6893f00d5f18d62878352f4b8ddb49` | vac/In31WO47_far/relax_s0_results.tar.gz |
| 681559 | `06ee1a8d5d178580690ee107abdda3f1` | `52dac6f1d4f271bda852f16d40e20a4fdfd42fd7fc14a5d9299f46c09567232f` | vac/In31WO47_far/final_results.tar.gz |
| 4211 | `ff81eda850f3adf55a9dbf924539c4cc` | `74bfa2dea7968ace72429b345d88b4e7a14e9c87e289ec599d43bf348f2cbbd3` | vac/In31WO47_far/final.tmpl |
| 387169 | `6db225cc1c1eb62bee469eccda90e72d` | `bbd35a7636c85f5238727fb8bf53bc30642834ee8daccd017588f385b9d6e7bb` | vac/In31WO47_far/scf.out |
| 42899 | `850478178609f301021d8107e94bafe5` | `30cbd53ba1cec5cc4db1c516f63cbd6ffd97c90e7c839d7cf6e18513d8bb0365` | checks/gpumax_work/a20_g002/In31WO47_far/a20g002_In31WO47_far_results.tar.gz |
| 6517 | `b40f8250d44f120c8344fcd2c6983509` | `d98ff7b6d8b0771c4779b52520eee40a4753b7495314e8d38f624061d0763bd6` | vac/In31WO47_far/relax.in |
| 3080702 | `a8f04a195f36ab10da844c594c5ca86c` | `aba2d33cddd26a4478b7749eb8c3b7be89c62f058d0f4f7caf8d216cd9fe0a13` | vac/In31WO47_far/relax.out |
| 6421 | `082a00f6a6bc0b2a34cb82982c3dd885` | `130ddcb1d0fc9476ea3e6fca7e2d9df00f32d2c0d33224bf677ee41ac4c1e6ea` | vac/In31WO47_far/scf.in |
| 3986 | `999e1717c9e5dab7b9915dc05c7f18d8` | `bfd53f4f939e9c35d2093211a73ce982ce1042e1ce2786e42e7ddb009e572f95` | vac/In31WO47_far/In31WO47_far.xyz |
| 6421 | `082a00f6a6bc0b2a34cb82982c3dd885` | `130ddcb1d0fc9476ea3e6fca7e2d9df00f32d2c0d33224bf677ee41ac4c1e6ea` | vac/In31WO47_far/final_results.tar.gz::scf.in |
| 6517 | `b40f8250d44f120c8344fcd2c6983509` | `d98ff7b6d8b0771c4779b52520eee40a4753b7495314e8d38f624061d0763bd6` | vac/In31WO47_far/final_results.tar.gz::relax.in |
| 3080702 | `a8f04a195f36ab10da844c594c5ca86c` | `aba2d33cddd26a4478b7749eb8c3b7be89c62f058d0f4f7caf8d216cd9fe0a13` | vac/In31WO47_far/final_results.tar.gz::relax.out |
| 387169 | `6db225cc1c1eb62bee469eccda90e72d` | `bbd35a7636c85f5238727fb8bf53bc30642834ee8daccd017588f385b9d6e7bb` | vac/In31WO47_far/final_results.tar.gz::scf.out |
| 6517 | `b40f8250d44f120c8344fcd2c6983509` | `d98ff7b6d8b0771c4779b52520eee40a4753b7495314e8d38f624061d0763bd6` | vac/In31WO47_far/relax_s0_results.tar.gz::relax.in |
| 3080702 | `a8f04a195f36ab10da844c594c5ca86c` | `aba2d33cddd26a4478b7749eb8c3b7be89c62f058d0f4f7caf8d216cd9fe0a13` | vac/In31WO47_far/relax_s0_results.tar.gz::relax.out |
| 6421 | `54fbb65615ce74c72c30575811c15c90` | `6f593dd5863e57a2c3804fe0243b00481f31b8af28517e7f214ca1a151075464` | checks/gpumax_work/a20_g002/In31WO47_far/scf.in |
| 6421 | `9c735fda8727481af364a6176ac7bff5` | `82a68d50df7915e9142a1738071f8440e0806fe4a40595a67a20dd18b48c9e3d` | checks/gpumax_work/a20_g002/In31WO47_far/a20g002_In31WO47_far_results.tar.gz::scf.in |
| 207974 | `1188be2cbfa4cd7a6764a4b6c2402dbb` | `b0f47b15e9960e73919512cafc47bfaa00fe57968db04fb59b78f7784ebd2535` | checks/gpumax_work/a20_g002/In31WO47_far/a20g002_In31WO47_far_results.tar.gz::scf.out |
| 680873 | `1a9d94032fba071927e3950bd326bdb9` | `0ad25b2a987497f0fd0f5420c1cfd433e11b6366ba8c4fb1140dddbf41b6816b` | vac/In31WO47_near/relax_s0_results.tar.gz |
| 754133 | `9fcfd02f971f117e8ff580ffc6cf940e` | `98ccd46148daf5f30cfc20b9cd5a5479f1a07cca4361b47cf69c8917c655518f` | vac/In31WO47_near/final_results.tar.gz |
| 4211 | `815328fb8e408c0914ba33cfa579d624` | `67d706cbb5dd57977bf1ce2bae9f69bed8a04dff0771996e22df3e8971d3491b` | vac/In31WO47_near/final.tmpl |
| 383972 | `cac699c8374119223222702392c2bbaa` | `557efeb9229788877cba8060c83a3253bbf90880657b083faed6214b05f836ea` | vac/In31WO47_near/scf.out |
| 42722 | `32cee44aec226b8f17873bbc0c4c9223` | `b27bfc3d18657d3a962d80738661b59ef4c7c65739f0236ed8d96499935338ee` | checks/gpumax_work/a20_g002/In31WO47_near/a20g002_In31WO47_near_results.tar.gz |
| 6517 | `1d31e99671ac9299ff6b81f46cf41e02` | `335e745559fef92db906da3bfa1dbb05746b0a2265cc7261c9da23cb83c27ff4` | vac/In31WO47_near/relax.in |
| 3511784 | `0eef1518151c028cd504fa23d258e489` | `3c7708855c8765c8e2420f7ee74a0b67836722a59c1b06032705c7c4aac9219d` | vac/In31WO47_near/relax.out |
| 6421 | `19e95727cf027c5836ea4b13d10452fa` | `fc417c04dad8a04bd4193df132f794f966fc746956e8c6492fd82e6c2cb6b28f` | vac/In31WO47_near/scf.in |
| 3987 | `2620a24ad69e7fbe647b473f2bed4300` | `57ed52c6f50e03cf8f1df846800cdab086b84559daf24e16d5a6006e63b88ea2` | vac/In31WO47_near/In31WO47_near.xyz |
| 6421 | `19e95727cf027c5836ea4b13d10452fa` | `fc417c04dad8a04bd4193df132f794f966fc746956e8c6492fd82e6c2cb6b28f` | vac/In31WO47_near/final_results.tar.gz::scf.in |
| 6517 | `1d31e99671ac9299ff6b81f46cf41e02` | `335e745559fef92db906da3bfa1dbb05746b0a2265cc7261c9da23cb83c27ff4` | vac/In31WO47_near/final_results.tar.gz::relax.in |
| 3511784 | `0eef1518151c028cd504fa23d258e489` | `3c7708855c8765c8e2420f7ee74a0b67836722a59c1b06032705c7c4aac9219d` | vac/In31WO47_near/final_results.tar.gz::relax.out |
| 383972 | `cac699c8374119223222702392c2bbaa` | `557efeb9229788877cba8060c83a3253bbf90880657b083faed6214b05f836ea` | vac/In31WO47_near/final_results.tar.gz::scf.out |
| 6517 | `1d31e99671ac9299ff6b81f46cf41e02` | `335e745559fef92db906da3bfa1dbb05746b0a2265cc7261c9da23cb83c27ff4` | vac/In31WO47_near/relax_s0_results.tar.gz::relax.in |
| 3511784 | `0eef1518151c028cd504fa23d258e489` | `3c7708855c8765c8e2420f7ee74a0b67836722a59c1b06032705c7c4aac9219d` | vac/In31WO47_near/relax_s0_results.tar.gz::relax.out |
| 6421 | `78851e7a34c0afd44895e3e9a3f2d813` | `24a4cf10a178cbf6183be680f4d97683db79355bf39df2e8962e6d608d79a487` | checks/gpumax_work/a20_g002/In31WO47_near/scf.in |
| 6421 | `9d2bddb16029c8646913755faeb8adf6` | `bcfb71412eafb6532f51d3434a4a2fb403a4c3c454a20f4f4c20e9a0b432b21a` | checks/gpumax_work/a20_g002/In31WO47_near/a20g002_In31WO47_near_results.tar.gz::scf.in |
| 206461 | `51b12fa4ad7ba3ebd482132327586ab1` | `67e0bb4ac35d1a7f6ec4426a2713f1dfc5261088b25d07a95645ff6ae59d5180` | checks/gpumax_work/a20_g002/In31WO47_near/a20g002_In31WO47_near_results.tar.gz::scf.out |
| 1064357 | `407d5fce9c95205040a557a9fdd1e5e3` | `5796d7388e09107d3038daa6573b1b75897d32204efb23cf485941d9c0d29eb4` | vac/In31WO47_near72/relax_s0_results.tar.gz |
| 1138646 | `792cf7888749c3368d32e4e2712288b6` | `9c24071fa8c62a2a8de303e00052d66f5676ac066927cd9110262218a39ff8b3` | vac/In31WO47_near72/final_results.tar.gz |
| 4211 | `0375b7fe0bab6129c0af1f88a96f75c7` | `8d3e2021588f6aea1a7f3efb80e8800be4e24e2f8c058b335c5615f1e8107891` | vac/In31WO47_near72/final.tmpl |
| 383578 | `3d0404dd20a2b8a87d47d0d60d15b2be` | `f812a04f9fb0ed8fc17e828355bf4a51d065d491745b0a1fc49364aaf12329c3` | vac/In31WO47_near72/scf.out |
| 42552 | `35d745d1927ef732dfe979ce938a2b6d` | `1c740c75cf424d0131ae53f27ba830a8af063db35c98414f03916f376f2e7e2b` | checks/gpumax_work/a20_g002/In31WO47_near72/a20g002_In31WO47_near72_results.tar.gz |
| 6517 | `b93c5a1f82c8ca08e5d941e172885911` | `52a3626d246811acf59e4a6691e0f81b8e86cce0d3c8aad1ceba6ee704ca0fbd` | vac/In31WO47_near72/relax.in |
| 5457084 | `e7cf6a3ddfb2fd6fc7102f8bc957ff36` | `e676d7e6c0c46d572bb5ed579f6dcb16c566d0278f794dc627d4521d5ee1fb2c` | vac/In31WO47_near72/relax.out |
| 6421 | `02ef748f1ca094bcfed9d7d0f5b16996` | `6d460182adfe14a0b73128b475ebc02523ba3110495c4ba6d98d19aac26e2096` | vac/In31WO47_near72/scf.in |
| 3989 | `4674520bc8dc76880fba4353f07f52a3` | `937448241a4bfdc11ad277636d9c81cb06b3c28ba9af7ecaadd1afad58df00ae` | vac/In31WO47_near72/In31WO47_near72.xyz |
| 6421 | `02ef748f1ca094bcfed9d7d0f5b16996` | `6d460182adfe14a0b73128b475ebc02523ba3110495c4ba6d98d19aac26e2096` | vac/In31WO47_near72/final_results.tar.gz::scf.in |
| 6517 | `b93c5a1f82c8ca08e5d941e172885911` | `52a3626d246811acf59e4a6691e0f81b8e86cce0d3c8aad1ceba6ee704ca0fbd` | vac/In31WO47_near72/final_results.tar.gz::relax.in |
| 5457084 | `e7cf6a3ddfb2fd6fc7102f8bc957ff36` | `e676d7e6c0c46d572bb5ed579f6dcb16c566d0278f794dc627d4521d5ee1fb2c` | vac/In31WO47_near72/final_results.tar.gz::relax.out |
| 383578 | `3d0404dd20a2b8a87d47d0d60d15b2be` | `f812a04f9fb0ed8fc17e828355bf4a51d065d491745b0a1fc49364aaf12329c3` | vac/In31WO47_near72/final_results.tar.gz::scf.out |
| 6517 | `b93c5a1f82c8ca08e5d941e172885911` | `52a3626d246811acf59e4a6691e0f81b8e86cce0d3c8aad1ceba6ee704ca0fbd` | vac/In31WO47_near72/relax_s0_results.tar.gz::relax.in |
| 5457084 | `e7cf6a3ddfb2fd6fc7102f8bc957ff36` | `e676d7e6c0c46d572bb5ed579f6dcb16c566d0278f794dc627d4521d5ee1fb2c` | vac/In31WO47_near72/relax_s0_results.tar.gz::relax.out |
| 6421 | `96e24b5f80c1af0f40029afe52505dcd` | `c114f167b7c6a46914c66024498df32bc836f8ce8f4fc62e281c726523200643` | checks/gpumax_work/a20_g002/In31WO47_near72/scf.in |
| 6421 | `2279400883dd802d05910b82c91c3ae0` | `48165f460cc580cf86d585ace09c6ff2305598d39f8e102a0eb203c79cd57913` | checks/gpumax_work/a20_g002/In31WO47_near72/a20g002_In31WO47_near72_results.tar.gz::scf.in |
| 203091 | `5fae04dff1445399005a3fccd396502a` | `090331b1dd753e10621a58b49b26f6daa845f668b20b717206879dc43a17e163` | checks/gpumax_work/a20_g002/In31WO47_near72/a20g002_In31WO47_near72_results.tar.gz::scf.out |
| 4307 | `1dbac6b93ae28ee094ecea35cd7c7256` | `560d0e2abd7e032ef3d108fbb177778e4afb539b29d28f7928d60385e899f3ec` | vac/In31WO47_near/attempt1/relax.in |
| 689565 | `409ed686c9d2af7c86a78d5290f79fb5` | `030434986517dad868c328b0a77d2a7f64d951f17f41a04556ba7cc6d7e37931` | vac/In31WO47_near/attempt1/relax.out |
| 4307 | `1dbac6b93ae28ee094ecea35cd7c7256` | `560d0e2abd7e032ef3d108fbb177778e4afb539b29d28f7928d60385e899f3ec` | vac/In31WO47_near/relax.in.pre_A28_20261011T130452Z |
| 6517 | `0dbaae0253e27a7fa93755019d120bdf` | `afbc59b4debc43b0d0dcb3763fc031293b7f5b71ecb717d193cc74e8ffae3634` | vac/In31WO47_near/a28_staging/relax.in.A28 |
| 4307 | `1dbac6b93ae28ee094ecea35cd7c7256` | `560d0e2abd7e032ef3d108fbb177778e4afb539b29d28f7928d60385e899f3ec` | vac/In31WO47_near/a28_staging/relax.in.template_current |
| 4307 | `1dbac6b93ae28ee094ecea35cd7c7256` | `560d0e2abd7e032ef3d108fbb177778e4afb539b29d28f7928d60385e899f3ec` | vac/In31WO47_near/a28_staging/s0/relax.in |
| 689565 | `409ed686c9d2af7c86a78d5290f79fb5` | `030434986517dad868c328b0a77d2a7f64d951f17f41a04556ba7cc6d7e37931` | vac/In31WO47_near/a28_staging/s0/relax.out |
| 4307 | `1dbac6b93ae28ee094ecea35cd7c7256` | `560d0e2abd7e032ef3d108fbb177778e4afb539b29d28f7928d60385e899f3ec` | vac/In31WO47_near/attempt1/relax_s0_results.tar.gz::relax.in |
| 689565 | `409ed686c9d2af7c86a78d5290f79fb5` | `030434986517dad868c328b0a77d2a7f64d951f17f41a04556ba7cc6d7e37931` | vac/In31WO47_near/attempt1/relax_s0_results.tar.gz::relax.out |
| 121877 | `ef8b9bcc8968eddff09d4c69f663877b` | `1d414b8b4a5d6b64380835c22a1e69916d60d2b251f5f29488a91193bb9242fd` | vac/In31WO47_near/attempt1/relax_s0_results.tar.gz |
| 604 | `2777ef57014ebc3ab03c10a2956bcd45` | `71d474465bf1a475c71b730589f0ea2015bc313f2606cfe56c849bd15b36d9e2` | vac/In31WO47_near/a28_staging/MANIFEST.md5 |
| 20459 | `4f5482734cb5df90b9d497cc3612ca5b` | `9ddd3e7ab2260826ed15f6dbaf5646e147e056f2408ae104ccda4c520abcd0e2` | vac/In31WO47_near/a28_staging/apply_A28_near.sh |
| 8258 | `e780b8cfe955c95ea9535620ad9520ed` | `e73c74f77d0fd13d7e3dcb0e96fc5ce61c2da70b2e68f912049a6543d219fa91` | vac/In31WO47_near/a28_staging/a28_verify.py |
| 1177 | `be6809f1e36c5612416d0620ad6d2d37` | `30921c9f2c50464723cee36462b6812cdc183cec7244c08fc5ffd360f02b0ad9` | vac/In31WO47_near/a28_staging/relax.sub.A28q2 |
| 1128 | `3ab7d9d506dbf748cc7719a3be3804a7` | `cb18d5c372424a6b098f9ef7a254020a09be17961084d8b54ce62b7afaeaaee8` | vac/In31WO47_near/a28_staging/final.sub.A28q2 |
| 1177 | `be6809f1e36c5612416d0620ad6d2d37` | `30921c9f2c50464723cee36462b6812cdc183cec7244c08fc5ffd360f02b0ad9` | vac/In31WO47_near/relax.sub |
| 1128 | `3ab7d9d506dbf748cc7719a3be3804a7` | `cb18d5c372424a6b098f9ef7a254020a09be17961084d8b54ce62b7afaeaaee8` | vac/In31WO47_near/final.sub |

## 7. Bookkeeping notes

- **BFGS step counts.** QE's own converged lines read In32O48 0, In31WO48 0, In32O47 13, far 16, near 18 (restart 1), near72 29 BFGS steps (14/17/19/30 SCF cycles for the vacancy cells), and the number of BFGS geometries printed before the final block is 13/16/18/29. digest_hl_a20ii.md quotes 12/15/17/28, which is the last `number of bfgs steps =` counter, one lower. Use the QE converged-line values in the log (or say which counter is quoted).
- **In32O47** removed O17 of In32O48; all 48 O of bixbyite In2O3 are one Wyckoff class (48e), so the choice carries no site label.
- **near72** is the sensitivity cell (O72 removed, W-O 1.90237 A); **near** (O30) is the registered cell; both bind.
- The register text gives a = 10.3061 A; every file carries 10.3060902 A (consistent rounding).

## 8. Scripts (in this folder)

- `g1_list.sh` (directory and tar listings), `g2_code.sh`, `g3_code.sh`, `g4_code.sh` (generator code: geomsel.py, steps_*.sh, *_node_vac.sh, driver.sh, qeio.py, A28 staging), `g5_bind.sh` (binding: parsing, canonical hashes, comparisons, md5/sha256 manifest), `g6_dist.sh` (distances). Outputs: `g1_list.out` ... `g6_dist.out`, `g5_bind.json`. `mk_md.py` builds this file from them.
- Run as `MSYS_NO_PATHCONV=1 wsl -d Ubuntu -- bash .../golist/run_r.sh <script>` (SSH master check first; `NO SSH MASTER` would have stopped the run).

**all_bound = true**: every cell's k4 FINAL inputs (vac scf.in, final_results.tar.gz::scf.in) and A20(ii) inputs (a20 scf.in, results tarball scf.in) equal its relaxed geometry exactly at print precision (Δ = 0, canonical hash equal), and the geometry each pw.x run printed matches to <= 5e-8 crystal.
