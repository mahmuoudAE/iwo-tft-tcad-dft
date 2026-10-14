# Audit-created archive-identity (mapping) records: construction provenance (A44 addendum 1)

Dated note 2026-10-14T11:05Z; Codex 2026-10-14 (real-record audit): "The archive-identity construction is acceptable: cluster/segment mappings are independently corroborated by user logs and DAGMan events. Preserve these as audit-created mapping records, with their construction provenance."

- **Status.** These records were written by the audit on 2026-10-14 at about 10:49:50Z, not in-job and not contemporaneously with the runs. They are mapping records (iwo-f9-archive-identity/1): for each returned archive, run, size and sha256, cluster and segment k.
- **Construction.** Written by a44_add1_build_lineage.py (below):
  - Archive names, sizes and sha256 come from the verified local copies in C:\Users\moham\iwo_lineage_evidence_20261014.
    Those copies equal the lxplus values logged before processing (annex A44_add1_lineage_inventory.txt a1c5dcb1; SHA256MANIFEST b83240ce, 134/134).
  - The cluster-to-segment mapping is taken from each run's HTCondor user log (000/001/005 events per cluster) and from the driver stdout names logs/relax_s<k>.<cluster>.out (pilot: logs/pilot_relax_s<k>.<cluster>.out).
  - The checkpoint names relax_s<k>_<cluster>.tar.gz carry the same cluster.
- **Corroboration** (Codex): the user logs and DAGMan nodes.log/dagman.out events agree with every mapping.
- **Cross-checks by the frozen v18 writers:**
  - every archive member written in-job carries an mtime inside its cluster's last execution window (bound user log, logged lxplus offset evidence);
  - item-B segments name their job in relax_s<k>_lineage.log;
  - checkpoint relax.out equals the returned relax.out.
- **Use.** They bind archives to jobs for the F9 relaxation_lineage records only. They are not in-job evidence, and they never replace a missing in-job saved input or checkpoint (aIO_0p8_s1 pilot s0 stays underivable).

| Cell | File | sha256 | archives listed | user log |
|---|---|---|---|---|
| aIO_bulk_s1 | archive_identity_aIO_bulk_s1.txt | f523776caaf5b8911167311b9c64f39f55935df14b6121ce91f78de7cdd10e1d | 2 | logs/relax.log |
| aIWO_bulk_s1 | archive_identity_aIWO_bulk_s1.txt | 9d377ec987c6f95cb56b39585d0d25c544977f3870c84d51b023f5f7008a0b22 | 2 | logs/relax.log |
| aIO_1p0_s1 | archive_identity_aIO_1p0_s1.txt | 49ba24f635ed290478bb057d58920f4b9825dd6afa8170ee4c3935d6eff866ec | 4 | logs/relax.log |
| aIWO_1p0_s1 | archive_identity_aIWO_1p0_s1.txt | eae54b74579759662fedd1381d90c1ee4a1b3616f045f8c7b46109d66346fdce | 2 | logs/relax.log |
| aIO_0p8_s1 | archive_identity_aIO_0p8_s1.txt | 1b3ae8beb4b5d7be69d571a598bb09bfa81b5b96168bd4489201620fa06a84a2 | 2 | logs/pilot_relax.log |
| aIO_0p7_s1 | archive_identity_aIO_0p7_s1.txt | 3a3aff24df657f82bd0ba0410a0fe5b13d671b0ceacd233ccb62e41dfb587b06 | 3 | logs/relax.log |
| aIWO_0p7_s1 | archive_identity_aIWO_0p7_s1.txt | 7b47da07053e9a24569f9eadb75019716573759188127f1baa13bdf4da114972 | 5 | logs/relax.log |

Scripts (byte-exact copies):
- `a44_add1_build_lineage.py` sha256 328a8fd1fe5f40da15c3097a70aba475c34db5682e5497e936a03366eccc945f
- `a44_add1_runner.py` sha256 6738fab2dff454d43fb0318f34742db78c2e80840045f997769e5b86a96654f5
