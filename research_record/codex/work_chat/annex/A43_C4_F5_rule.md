# A43 annex: the C4-polish F5 rule text, bound prospectively (D-43 is still a draft)

Copied verbatim from the reviewed release-decision draft (drafts13oct/Release_decision.md, section A, item F5). sha256 of the quoted block below (from "- **F5." through the line before "- **F6.", LF line endings): 8aceddaaacf919c5d5e9c882efef05361610f122c1b99f964aea4a0260d155ac

```markdown
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
```
