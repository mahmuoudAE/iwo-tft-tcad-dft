# Patch plan for chapters/13_dft_rev.tex (from report_latex_full/chapters/13_dft.tex @ 3fe6627)

Source: audit agent report (2026-10-14), each item spot-checked by the main session against the file. Line numbers are
those of the baseline file. Items marked VERIFIED were re-read; REJECTED items were found incorrect on checking.

## Corrections (change text)

| # | Lines | Change | Basis | Check |
|---|---|---|---|---|
| P1 | 549, 580-583, 1325-1328, 1700, 1704, 1711, 1751 | Unify the sign convention: dEv = signed shift of the VBM (negative = down), dEg = dEc - dEv, as in RESULTS_LOG errata item 1. Rewrite eq. at 549 as dEv(1)-dEv(2) = -(IP(1)-IP(2)) = +0.0019 eV; line 1328 "difference" with this convention. | errata item 1; FACT-013/015 | VERIFIED. In the chapter's own lowering convention (dEg = dEc + dEv) lines 549/1325/1328 were self-consistent; the audit's "sign error" there is REJECTED as stated, but the table (1711, 1751) uses the signed convention, so the chapter mixes two conventions. |
| P2 | 1711, 1751 | 1 nm dEv -0.056 -> -0.052 eV (-0.0521); add "dEc - dEv = 0.8998 eV = dEg(1 nm)". | errata item 1; FACT-015 | VERIFIED |
| P3 | 1225, 1265 | 5.5e21 -> 2.7e21 cm^-3 (3 e per 80-atom cell, a^3 = 1094.6 A^3); add slab range 1.4e21-3e21 (C022). | arithmetic; C022 | VERIFIED (5.5e21 = 3 e / 547 A^3 primitive volume) |
| P4 | 698-701 | "describes the fully ionized, degenerate limit" -> "describes a degenerate filling (3 donated e/cell); whether W stays ionised at device densities is INFERRED, not computed". | C022 caveat; LOG 2026-10-14 TCAD bullet | VERIFIED |
| P5 | 1267-1272 | "PBE thus predicts" -> "it is inferred (not computed: no lower-density cell, no hybrid functional for the W cells) that". | C022 | VERIFIED wording |
| P6 | 1213-1216, 403-405, 1753, 1787 | "identify W6+" -> "consistent with W6+ by the ionic-radius argument; Loewdin W-5d counts (0.09-0.43 e) are not the W charge". | FACT-041, FACT-045 | to apply |
| P7 | 187-188, 542-543, 648-649, 968 | Scope the "equivalent surfaces, no dipole" statement to the 1 and 2 nm slabs; add that the 0.695 nm slab built by the same recipe is polar (ramp -13.6 meV/A). | C021 | to apply |
| P8 | 1722-1730, 1784-1785 | Scope "band edges bulk-like" to 2 nm; at 0.461/0.695 nm the VB top is on OH oxygens (98 %/75 %). | LOG 2026-10-14 (0.51/0.75 nm) | to apply |
| P9 | 510-516, 941-945 | Name the fit basis: 4-point parabola (deck basis) 0.1588; band-edge 10-point Kane 0.1541 m0, alpha 0.58 (0.55-0.63). | C039 | to apply |
| P10 | 1017-1030, 1307-1310, 1748-1750, 1782-1783 | Label slab masses as 4-point basis; give band-edge 0.279 / 0.203 m0. | C039 | to apply |
| P11 | 1314-1317, 1763-1764 | Point forward to the current laws (fit3 dEg 0.8147 t^-1.3155, dm 0.1145 t^-1.2755, dEc fit2 p 1.478) in the masses chapter. | C039; FACT-020..025 | to apply |

## Status updates (stale "pending")

556 (two-step alignment done), 725/757/763 (2 nm IWO relax + final SCF done, cluster 12835211), 1266-1267 (2 nm
projections done: level +1.34 eV above host CB, +0.103 eV from E_F at Gamma), 1330-1334 (both checks closed),
1218/1246/1257/1106/1754/1789 ("preliminary" -> "computed at one filling"), 1752 (0.51/0.75 nm finished, H-H 0.461/0.695
nm), 1755/1792 (W masses: bulk 0.162 computed; slabs estimated), 1775-1776 (vacancy test H-L done; charge states not),
1517-1521 (resources "to date" = up to 2026-10-04), 1472-1509 (stuck rule revised; failures table incomplete).

## Missing results (go to new chapters, with a forward pointer from 13_dft_rev)

M1-M3, M5, M7 (masses, laws, HSE estimates, TCAD bridge) -> ch:mono-masses. M4 (0.51/0.75 nm) -> new section in
13_dft_rev. M6 (W caveats), M9 (H-L) -> ch:mono-w-vac. M8 (holes) -> ch:mono-masses. M10 (MACE) -> ch:mono-amorph.

## Labels

13_dft.tex defines 100 labels (incl. ch:dft, sec:dft-limits, sec:dft-pending, tab:dft-status); all must be kept in
13_dft_rev. External dependencies: sec:par-dec, sec:par-mstar, eq:dec-law, sec:der-confinement (ch. 4), ch:device,
ch:v2 (14_model_v2_rev keeps it).
