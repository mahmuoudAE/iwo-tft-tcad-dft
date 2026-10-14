# F13 export integrity record (2026-10-14; sizes from listings only, contents never opened)

| Cell | FINAL | EOS export dir bytes (7 files) | returned final_results.tar.gz bytes | in-job manifest (export_manifest_final.dat) entries / local mismatches |
|---|---|---|---|---|
| aIO_bulk_s1 | 12890432 | 99716723 | 1934483 | 5 / 0 |
| aIWO_bulk_s1 | 12891160 | 101666350 | 1983804 | 5 / 0 |
| aIO_1p0_s1 | 12891132 | 54217431 | 1097711 | 5 / 0 |
| aIWO_1p0_s1 | 12889857 | 56060996 | 1148129 | 5 / 0 |
| aIO_0p7_s1 | 12894279 | 58391183 | 1184598 | 5 / 0 |
| aIWO_0p7_s1 | 12902517 | 58351611 | 1179239 | 5 / 0 |
| aIO_0p8_s1 | 12904001 | 59848243 | 1222700 | 5 / 0 |

- Total: 498003201 bytes (0.498 GB) over 56 files; below the 1 GB pending rule. Local copy: C:\Users\moham\iwo_exports_final_20261014 (outside OneDrive), SHA256MANIFEST.txt sha256 43aaf7a68e286ba5822e6e9b0e56483310fb5f1dcf41bbef57e0d663f94e98df; 56/56 size+sha256 equal to the lxplus listing (golist/r43_f13_sha.out).
- AFS quota (fs listquota ~, 2026-10-14T09:58Z): user.melrashe quota 2097152 kB, used 503369 kB (24%), partition 26%.
- Each in-job manifest's 5 EOS entries (atomic_proj.xml.gz, data-file-schema.xml.gz, final_small.tar.gz, pdos_atoms.tar.gz, projwfc_final.out.gz; status XRD_ADLER32) equal the local bytes and sha256.
- Format note for F9: the in-job manifest is export_manifest_final.dat ('# D-24 export of <cell> (cluster <N>), <utc>; EOS directory ...', rows '<file> <bytes> <sha256> <status>'), not the 'exp/MANIFEST' form '# run <name> cluster <N> written_utc <t>' + '<basename> <bytes> <sha256>' that F9 v15 supports.
- Not done here: the A39(d) test transfer before P1 and daily fs listquota (A39 cutoff read-outs, not these FINALs).
