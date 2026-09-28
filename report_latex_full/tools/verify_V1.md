# Verifier V1 log

Scope: 02a_literature_target, 02b_literature_in2o3, 02c_literature_methods, 02d_provenance,
04_derivations_electrostatics, 05_derivations_transport.
Input: tools/citation_report.csv (rows for these files with status != OK: 95 rows, 78 distinct lines).

## Changes

| File | Line | Before | After | Reason |
|---|---|---|---|---|
| 02c_literature_methods.tex | 22 | `\citep[pp.~225102-12--225102-13]{Stokey2021}` | `\citep[pp.~225102-12--13]{Stokey2021}` | PAGE_MISSING formatting. Both pages exist: m* = 0.208 +- 0.006 is on -12 and -13, n = 2.81e17 is on -13 (Fig. caption). Now uses the same range form as 02d. |
| 02c_literature_methods.tex | 63 | `in later tests the trap density is fixed at $4\times10^{20}\cmcu$ \citep[p.~7]{Pandey2025}` | `the trap density in the source/drain regions is set to $4\times10^{20}\cmcu$, and it stays fixed there in the later channel-trap tests \citep[p.~7]{Pandey2025}` | Wrong claim. Pandey p.5 and p.7 give 4e20 as the S/D trap density, not the channel trap density. On p.7 the channel density is the swept variable. |
| 02d_provenance.tex | 99 | `\citet[p.~21539]{Lin2022}` (contacts context) | `\citet[p.~21538]{Lin2022}` | Wrong page. Lin2022 has no contact statement on p.21539. The low contact resistance from the CNL alignment of metal/In2O3 is on p.21538. |
| 02c_literature_methods.tex | 188 | (edited, then reverted) | `0.18\pm0.02\,m_e` kept | I first removed the +-0.02 by mistake. It is on Stokey p.225102-2 ("(0:18 + 0:02) me"), so the original text was restored. |

## Citation rows checked and kept (fact is on the cited page, or the flag is a false positive)
- 02a 137 Januar pp.7--8: Dsr 2.87 A is on p.8, Fig. 5f; the Ando term is on p.7. The range is correct.
- 02a 151 Januar p.3: p.3 has the 150 C RTA and the crystallinity-driven carrier increase at higher annealing. The numbers 15/2 nm and 290/20 um belong to `\citep{DeviceSchematic}` (false positive).
- 02a 131/133/135/139/140/145/147/148/182/183/208/210 (NO_NUMBERS): the stack, TiN 50 nm and ~2% W are on p.2; Pd 70 nm, RTA, 5.1-27.4 cm2/Vs and PBE-GGA are on p.3; theta_t Nt (Eq. 3) is on p.4; the fourfold Nt rise and Ando are on p.7; PBS is on p.9. All confirmed.
- 02b 19/22/24/44/236/240 Si2021: TNL 0.4 eV (pp.503-504), EC upshift ~0.6 eV at 1.5 nm with EV unchanged (p.504), 8.9 via Hamberg (p.501) and ~1e20 (p.500). All confirmed. The dEg values 0.33/0.94 eV are differences of the Lin p.21542 gaps (1.27-0.94, 1.88-0.94).
- 02b 63/65/67/85/235/237/239 Lin2022: CNL 0.4 eV (p.21539), slab masses 0.17/0.19/0.23/0.30 (p.21540), gaps 0.94/1.27/1.88 (p.21542), n2D 7.6e13 (p.21537), SS 63.5 and Dit 6e11 (p.21539). All confirmed.
- 02b 52/94/237/238 and 02c 20/188, 04 125/132/474 Stokey2021: eps_DC 10.55 +- 0.07 via LST (p.-12), m* 0.208 (p.-12/-13), 0.18 (+-0.02) (p.-2), Hamberg 8.9-9.5 (p.-3). All confirmed.
- 02b 93/144/147/235/238/239/240, 02c 187/190, 04 737/863 Wang2022: CNL above 0.4 eV (p.2), 6.3e11 (p.4 and p.5), eps 8.9 and ND 1e20 (p.4), Robertson and Clark (p.5). All confirmed.
- 02b 106/108/109/125/240 Si2022: 0.4 eV (p.167), 8.9 and 9.0e19 (p.168), O2 anneal at 250 C (p.169). All confirmed; the flags were cross-citation page numbers.
- 02b 241, 02d 81/132 Kim2024 p.173507-6: Nbt 2.37/3.12/14.6e18 for 10/20/30 nm. Confirmed.
- 02b 175, 02d 50/56/73/88/93, 02c 185/192/237, 05 729 Januar2026: all confirmed. The PBS Nt values 5.3e19 (2 nm IWO) and 3.39e18 (10 nm IWO) are on p.9.
- 02c 59/60/84 Pandey2025: the approximated Gaussian (p.2), Green's identity (p.3), eps_HfO2 = 15 (p.2) and ni = 5e19 (p.5). All confirmed.
- 02c 94/96/97/98, 02d 76 WangX2025: the Gaussian donor and the Gauss-Fermi erf/tanh (p.2391), Gauss's law (p.2393) and Monte Carlo on Tox/Tch/Nsd (p.2396). All confirmed.
- 02c 122/124/127/128 Anusha2024 (pp.2/4/5/14) and 02c 152/154 Giannozzi2009 (pp.1/2): confirmed.
- 02c 190 Si2021 p.504 (ref. 24): p.504 cites refs 24 and 26 for the TNL position. Confirmed.
- 02d 62/63/65/77/127/128, 04 170/207/254/296: confirmed.
- The remaining NUMBERS_NOT_IN_PAPER flags are model values (fits, run IDs, 19.57 from the SI), not claims attributed to the paper.

## Simulated-number spot checks (runs.csv / numbers.md): all match
- 04: run0026-0012 dVthcc -0.001 V; run0020/0021 +-0.100 V; run0016-0012 -0.315 V; run0017-0013 -0.023 V; run0050/0051 -0.044/-0.029 V; SS_cc -17.7/-13.2; run0023 +0.082 V, +49.0 mV/dec, -25.1 % Ion; run0024 +0.020 V, +4.6; run0025 +0.025 V, +0.1, -1.8 %; run0033 +0.051 V; run0001->0003 -0.309 V, +0.4, +27.1 %; run0022 -0.009 V, +0.7, +0.7 %; run0032 +0.030 V; run0030 +0.278 V, SS -64; run0048/0049 +0.100 V; SSmin run0012 73; m*(t) 0.257/0.218/0.211; Nt, Nd and dEc tabulated laws.
- 05: mu 17.69/11.41/60.39 and x1.015074/x1.020113 -> 11.582/61.6046; muFE 11.27/8.42/48.95; Ion -1.48 %/-1.97 %; run0003->0008 -0.009 V, -3.8 mV/dec, +7.9 %; run0037 SS_cc 410.9 vs 295.4; exponent 1.71; surface-plus-bulk 7.8e18 at 6.3 nm; x1.59/x2.51.
- 02d: Cox 8.955e-7 F/cm2, EOT 3.86 nm, Cox/q 5.59e12; roughness factors 0.734/0.911/0.957/0.982; NTA 5.0/2.1/1.2/0.63e20; dEg 0.353/0.072/0.026/0.008; sensitivity run IDs and their overrides.

## Unresolved
- 04 944: A5 (run0035) dVthcc -0.079 V, and 04 828 / 04 1091 deltas measured against the measured Vth. The measured Vth is not in runs.csv, so these were not checked.
