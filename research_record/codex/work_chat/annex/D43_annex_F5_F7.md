# D-43 annex: F5, F6 and F7 (verbatim)

Source: compute/amorph/f9_checker/Release_decision.md (frozen, D-47; sha256 2a0b3c3d08bc4355ec72d2be8a340ba2adcbeb7b4809cc0325f877e35acfff2b), section A items F5-F7, unchanged. The F5 C4 failure route is already in force prospectively through A43 item 6 (annex codex/work_chat/annex/A43_C4_F5_rule.md, F5 block sha256 8aceddaa...). As-of note: the polishes named in F5 (12904172, 12904173) were resubmitted under A43 item 6 as 12920318 and 12920319 with byte-identical submit files; the "[fill from ...]" placeholder is answered by that A43 implementation record (annex/A43_implementation_record.md).

- **F5. C4 polish: failure route and qualification.** Polishes 12904172 (0.7 nm) and 12904173 (1.0 nm); settings as submitted 13:17Z [fill from checks/gpumax_work/submit_20261012T131733Z.log].
  - **Infrastructure stop** before the first energy: one repeat with identical input.
  - **FAILED [scf], or no verified 'bfgs converged' by 17 Oct 10:00 UTC:** one attempt only. There is no rescue: no other smearing, mixing or solver.
    - C4 is MISSING at that thickness, and the class is reported on the MV geometry only, labelled "C4 polish not converged".
    - A partial polish geometry is never certified 'polished' and gets no A39 read-out.
  - **Fresh final-geometry qualification (required, zero-step included; Codex 15:08Z).**
    - After 'bfgs converged', a fresh-start 'scf' with forces is run at the polish's final geometry with the polish relaxation settings (Gaussian 0.005 Ry, same cutoffs, k-points, nbnd, nspin, dipole keys, labels).
    - It is compared with the polish's last SCF within 1e-5 Ry in F and 1e-3 Ry/bohr in max |ΔF| (A35 tolerances).
    - It is due by 20 Oct 12:00 UTC. A non-converged qualification fails. An infrastructure stop before the first energy may be repeated with identical input. It needs its own submit with the user's go.
    - A failed or missing qualification means C4 is MISSING at that thickness.
  - **Restart gates of a polish (v3, new; flagged for Codex).** If a polish spans more than one segment with identical settings, the A35 restart gate (1e-5 Ry, 1e-3 Ry/bohr) applies at every boundary. A failed or unevaluable gate means C4 is MISSING at that thickness (the F9 inventory).
    - It is set before any polish output has been read by us. It adds no stop: chains continue as before.
  - **Zero-step convergence** (positions hash equal to the MV parent): the existing A26 FINAL is the polished reference only under A40 rule 4 (i)-(vi), which includes the qualification above. Otherwise a new polished FINAL runs.
  - **After convergence and qualification:** the polished FINAL (A26 settings) runs at the CPU-3 priority. The FINAL may run concurrently with the qualification, but certification waits for the qualification result.
- **F6. Bare route and H-H.**
  - aIWO_0p7_s1_bare stays on MV 0.01, the registered aIWO relaxation family.
  - **"MV against MV" describes the geometries.** H-H at 0.7 nm compares:
    - aIWO_0p7_s1 at its MV-converged geometry (A26 FINAL 12902517);
    - aIWO_0p7_s1_bare at its MV-converged geometry.

    Both FINALs are Gaussian 0.001 Ry (A26); the FINAL smearing stays Gaussian. The C4-polished OH geometry is never used for H-H.
  - **Bare FAILED [scf]: park** (Codex 15:08Z). segment_stop STOP armed, the retry not released, the DAG removed only on the user's go (D-35 precedent). H-H 0.7 nm is then UNRESOLVED. Any other route (for example MV plus aids) would need its own amendment; none is pre-declared. A Gaussian rescue is excluded, because it would break the MV-geometry pairing.
  - **Not converged at the cutoff:** H-H 0.7 nm UNRESOLVED. The A39 read-out at G* is an observation only. The 2.0 nm part of H-H stays UNRESOLVED (D-35).
- **F7. CPU priority order.** One list, sorted by JobPrio. Thin-cell jobs use 34-CPU slots and may run concurrently.
  - **CPU-1:** A15 audit FINALs (A31(a)) of the converged 2.0 nm roles (comp; aIWO_2p0_s1 or the s2 backup; aIO_2p0_s1 or the s2 backup). 0.001 Ry first, then 0.002 and 0.005 Ry. Section 3 priority 1.
  - **CPU-2:** other primary FINALs of converged cells: aIWO_2p0_s2 and aIO_2p0_s2 (when not used as backups), then aIWO_0p7_s1_bare (termination pair).
  - **CPU-3:** thin-cell H-N controls:
    - polish qualifications and polished FINALs (0.7, then 1.0 nm);
    - C3 companions (A40 order), including the MV-geometry companions of aIWO_0p7_s1 for the H-H reference (A40 rule 3);
    - C6 (0.7, then 1.0 nm);
    - C1 FINALs (0.7 nm).
  - **CPU-4:** A34(i) val CPU-fallback frames, before 17 Oct 10:00 only (A38).
  - **CPU-5:** A39 cutoff read-outs in the A39(c) order, only those admitted on 14 Oct (q + T + X ≤ 80 h). There is no read-out otherwise, and no automatic fallback.
  - **CPU-6:** non-duplicated 2.0 nm C3 companions where primary qualification needs them (A40 item 7). 2.0 nm C6 is cut.
