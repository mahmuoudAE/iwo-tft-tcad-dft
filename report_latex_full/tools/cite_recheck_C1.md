# Citation re-check C1 (2026-09-25)

Scope: chapters/02a_literature_target.tex, 02b_literature_in2o3.tex, 02c_literature_methods.tex, 02d_provenance.tex.
Method: every \citep/\citet/\citealp listed with a grep (195 citation instances: 02a 24, 02b 63, 02c 68, 02d 40).
Every page-cited fact was searched on the cited printed page of digest/papers/<key>.md; ATLAS manual pages were checked
in tools/atlas_manual_fulltext.json by statement header ("22.xx <STATEMENT>") and parameter lines.
Line numbers are those before editing.

## Summary

| Verdict | Count |
|---|---|
| confirmed | 178 |
| page corrected | 12 |
| reworded (citation kept, text corrected) | 5 |
| removed | 0 |
| total citation instances checked | 195 |

Other fixes that are not citation commands: 02a in-text page reference for SI Fig. S12 (p.8 -> p.9, caption p.11);
02b Kim2024 20 nm optimum (claim was "not re-located", now located and cited); 02c PDF/printed page offset
sentence for the ATLAS manual.

## Changes

| File:line | Before | After | Reason |
|---|---|---|---|
| 02a:149-151 | annealing "improves trap metrics at 150 C and higher temperatures increase mobility and carrier concentration through crystallinity" (p.3) | trap metrics improve after 150 C anneal; higher temperatures can raise mobility further but make the device harder to turn off through a crystallinity-driven carrier increase (p.3) | reworded: p.3 attributes only the carrier increase to crystallinity |
| 02a:180-182 | free-carrier fraction + theta_t, T_t, \citep[p.~4] | free-carrier fraction \citep[p.~7, Eq.~5]; theta_t, T_t \citep[p.~4, Eq.~3] | page corrected 4 -> 7 for the carrier-partition mobility (Eq. 5 is on p.7); theta_t and T_t are in Eq. 3 on p.4. "occupancy factor" wording softened (theta_t is not named on p.4) |
| 02a:219 | SI Fig. S12 "referred to on p.~8" | "referred to on p.~9 and captioned on p.~11" | S12 is mentioned on p.9 and captioned on p.11; nothing on p.8 (same fix as V2 made elsewhere) |
| 02b:205-208 | 20 nm optimum "not re-located on a printed page" | located: \citep[pp.~173507-1, 173507-6]{Kim2024}; paper gives highest mobility + low trap density at 20 nm but no crystallinity attribution, so not used as evidence | claim located; still not used as evidence |
| 02b:238 | 9.30/9.03 "(SI Fig. S1b of JanuarSI2026, not bundled)" | adds "values via the Astra audit, caption printed in \citealp[p.~11]{Januar2026}" | non-bundled source must name its record |
| 02c:63-64 | S/D trap density 4e20 fixed in later tests \citep[p.~7]{Pandey2025} | \citep[pp.~5, 7]{Pandey2025} | page corrected: "set to 4e20" is on p.5 (TCAD setup), "fixed at 4e20" in the channel-trap tests on p.7 |
| 02c:95-96 | "they derive an analytical approximation with an error-function form" (pp.2391--2392) | they take over a published erf approximation (their ref. 14) and replace erf by tanh for Verilog-A (pp.2391--2392) | reworded: the erf form is from ref. 14 (Paasch and Scheinert); WangX2025 use tanh (Eq. 3, p.2392) |
| 02c:194 | Lee2018 "key present in the bibliography; content not reached" / citing record "--" | "gate-current effects in oxide TFTs (title only)"; "no bundled record cites it; listed via the Astra package bibliography" | reworded: no bundled paper cites Lee2018 (searched all digest papers); bib note says read by Astra |
| 02c:205-206 | "the PDF page is 4--6 higher" | equal at p.179, +4 at p.513, +6 throughout the statement chapter | checked in atlas_manual_fulltext.json (p.179 -> PDF 179, p.513 -> PDF 517, pp.1117-1647 -> +6) |
| 02c:217 MESH, X.MESH, Y.MESH | pp.~1373--1377 | pp.~1117--1118, 1373--1377 | page corrected: X.MESH/Y.MESH are statement 22.2 on pp.1117-1118; MESH (22.35) is pp.1373-1377 |
| 02c:218 REGION | pp.~1553--1560 | pp.~1548--1560 | page corrected: REGION (22.53) syntax and parameter table start on p.1548; 1553-1560 is only the description |
| 02c:220 DOPING UNIFORM | pp.~1188--1194, 1203--1204 | pp.~1183--1193 | page corrected: syntax p.1183, UNIFORM/N.TYPE/CONCENTRATION in the table pp.1185-1186 and described pp.1189-1193; pp.1203-1204 are Athena parallelogram doping, not used |
| 02c:221 MATERIAL | pp.~1336, 1355--1366 | pp.~1307--1355 | page corrected: syntax p.1307, table pp.1316-1333, descriptions AFFINITY 1337, EG300 1338, PERMITTIVITY/NV300 1340, MUN 1343, TAUN0 1349, EGALPHA 1352, TMUN 1355; 1356-1366 hold none of the listed parameters |
| 02c:224 MODELS | pp.~1433, 1469--1477 | pp.~1426, 1433, 1444--1448, 1453, 1462, 1477--1478 | page corrected: syntax 1426; FERMIDIRAC 1433/1462; SRH 1447/1453; PRINT 1444/1477; TEMPERATURE 1448/1478; 1469-1476 are Schrodinger/k.p/geminate flags |
| 02c:225 DEFECTS | pp.~1168--1174 | pp.~1167--1174 | page corrected: DEFECTS (22.10) syntax and CONTINUOUS/EGA/EGD rows are on p.1167 |
| 02c:226 INTERFACE (QF) | pp.~1258--1264 | pp.~1252--1264 | page corrected: syntax p.1252, QF in table p.1254, described p.1260 |
| 02c:227 METHOD | pp.~1383--1389, 1395 | pp.~1378--1390, 1395 | page corrected: table pp.1378-1383 (CARRIERS, CLIMIT, CR.TOLER 1379; ITLIMIT, IR.TOL, MAXTRAPS 1381; NEWTON 1382); TRAP described p.1390 |
| 02c:228 SOLVE | pp.~1593--1611 | pp.~1587--1611 | page corrected: SOLVE syntax p.1587, INIT/NAME in table pp.1589-1590 |
| 02c:229 LOG, SAVE, PROBE, OUTPUT, EXTRACT | pp.~1299--1305 | pp.~1216, 1299--1305, 1504--1515, 1524--1540, 1566--1579 (+ note that EXTRACT is documented in the DeckBuild manual) | page corrected: 1299-1305 is LOG only; OUTPUT 22.44, PROBE 22.48, SAVE 22.55, EXTRACT 22.18 (p.1216 says it is a DeckBuild command) |
| 02d:124-126 | gate stack incl. HfO2 15 nm, Al2O3 2 nm, eps 19.57, 9.30 \citep[pp.~2--3, 11]{Januar2026} | TiN 50 nm and Pd \citealp[pp.~2--3]; HfO2 15 nm, Al2O3 2 nm from the schematic; 19.57 and 9.30 from SI Fig. S1b (caption \citealp[p.~11]) via the Astra audit | reworded: the 15/2 nm thicknesses are not in the paper (searched all pages) |

## Citations confirmed (fact found on the cited page)

### Januar2026
- 02a 67, 137, 02d 88: Dsr 2.87 A, p.8 Fig. 5f; Ando term p.7. confirmed.
- 02a 131 pp.2--3: TiN/HfO2/Al2O3 stack (p.2), Pd (p.3). confirmed.
- 02a 133, 192 (pp.3, 7): 5.1-27.4 cm2/Vs (p.3 and p.7). confirmed.
- 02a 135, 241(02b), 212(02b), 02d 73, 130: Nt roughly x4 from 13.2 to 2 nm, p.7 (Fig. 5a). confirmed.
- 02a 139: PBE-GGA (p.3). confirmed.
- 02a 140, 183, 205, 208: Eq. 8 theta_t Nt occupancy; PBS Nt 5.3e19 (2 nm) and 3.39e18 (10 nm); Delta Tt; p.9. confirmed.
- 02a 145, 02d 50: 50 nm TiN by PVD, HfO2/Al2O3 ALD, p.2. confirmed.
- 02a 147: lack of long-range crystallinity, nanoscale grains, IWO grains smaller than In2O3 at comparable thickness, p.2. confirmed.
- 02a 148, 02d 54: 70 nm Pd S/D, RTA 150 C, p.3. confirmed.
- 02a table rows (not cite commands): TiN p.2, bilayer p.2, ~2% W p.2, Pd p.3, S1b caption p.11, Fig.5f p.8, Fig.5a p.7, theta_t pp.4 and 9, mu_max pp.3 and 7, roll-off form p.7 (Eq. 6), smoother IWO/HfO2 interface pp.2 and 8, crystallinity pp.2-3. confirmed.
- 02a 210 pp.3, 5: band structure/PDOS (p.3 Fig. 1c; W raises m*, p.3), interface cross-sections (Fig. 3f-h caption, p.5). confirmed.
- 02a 214, 02d 56: n > 1e19 oxygen-vacancy donors and ~2% W, p.2. confirmed.
- 02a 238 (in-text pages 2, 5, 8 for the IWO/HfO2 interface). confirmed.
- 02b 175: smoother channel-dielectric interface for IWO, p.8. confirmed.
- 02c 185, 02d 51: SI captions printed on p.11. confirmed.
- 02c 192, 237, 02d 93: Ando ref. [39] cited on p.7, listed on p.11; roll-off form Eq. 6 on p.7. confirmed.
- 02c 193: Yoo2024 = ref. 14, listed on p.10. confirmed.

### Si2021
- 02b 17, 44, 240: bulk In2O3 electron density ~1e20, p.500. confirmed.
- 02b 19, 235: TNL/CNL ~0.4 eV above EC, pp.503 (Fig. 4 caption) and 504. confirmed.
- 02b 22, 236, 02d 62, 63, 128: EC up ~0.6 eV at 1.5 nm, EV almost unchanged, p.504 (Fig. 4b). confirmed.
- 02b 24, 41, 238, 02a 101, 02c 187: eps 8.9 with ref. 25 (Hamberg), p.501. confirmed.
- 02c 189: ref. 26 (King 2008) cited with ref. 24 for the TNL, p.504; listed p.506. confirmed.
- 02c 190: ref. 24 (Robertson and Clark), p.504. confirmed.
- 02c 191: ref. 27 (Hinuma) listed p.506. confirmed.

### Lin2022
- 02b 61, 85: n2D ~7.6e13 cm-2, p.21537. confirmed.
- 02b 63, 79, 235, 239, 02a 66, 02d 77, 131: SS 63.5 mV/dec, Dit 6e11 (unit printed cm-1 eV-1), CNL ~0.4 eV above EC, p.21539. confirmed.
- 02b 65, 237, 02c 47, 02d 65, 129: masses 0.17/0.19/0.23/0.30 m0, p.21540. confirmed.
- 02b 67, 236, 02d 62, 127: PBE gaps 0.94/1.27/1.88 eV, p.21542. confirmed.
- 02d 99: low contact resistance from CNL alignment at metal/In2O3, p.21538. confirmed.

### Si2022
- 02b 104: Ni gate/HfO2 (p.164), EDX of W/HfO2/Al2O3/In2O3/Ni stack (p.165). confirmed.
- 02b 106, 235, 02d 99: CNL ~0.4 eV above EC and contact resistance < 0.1 Ohm mm, p.167. confirmed.
- 02b 108, 125, 238, 240, 02c 187: 1/C^2 ND = 9.0e19 with eps ~8.9 (ref. 33 = Hamberg), p.168. confirmed.
- 02b 109: O2 anneal 250 C, p.169. confirmed.

### Wang2022
- 02b 143, 165: ND 1e20 and subgap DOS 3.3e20 by conductance, pp.1-2. confirmed.
- 02b 144, 235: CNL above 0.4 eV above EC, p.2. confirmed.
- 02b 93, 146, 239, 02d 77, 131: Dit 6.3e11 (p.4 transistor, p.5 subthreshold method). confirmed.
- 02b 147, 238, 02c 187: eps_S 8.9 from optical measurement (Hamberg), p.4. confirmed.
- 02b 149: tail + Gaussian trap distributions, peak bulk DOS ~6e21, p.6 (distribution types also defined p.4). confirmed.
- 02b 240: donor density 1e20, p.1. confirmed.
- 02c 190: Robertson and Clark 2011 cited on p.5. confirmed.

### Kim2024
- 02b 184: 99:1 wt In2O3:WO3 RF sputter, 90 nm SiO2, 300 C anneal, p.173507-2. confirmed.
- 02b 186: RMS 0.134/0.199/0.258 nm, p.173507-3. confirmed.
- 02b 188, 241, 02d 81, 132, 02a 70: Nbt 2.37/3.12/14.6e18, p.173507-6. confirmed.

### Stokey2021
- 02c 17, 39, 02b 95, 237, 02c 188: Feneberg m*(0) = (0.18 +- 0.02) me and nonparabolicity, p.225102-2. confirmed.
- 02c 18, 187: Hamberg and Granqvist eps_DC 8.9-9.5, p.225102-3. confirmed.
- 02c 20, 02b 52, 94, 237, 238, 02d 129: eps_inf 4.05 +- 0.05, eps_DC 10.55 +- 0.07 (LST, Table II caption), m* 0.208, p.225102-12. confirmed.
- 02c 22, 02d 65: m* (0.208 +- 0.006) me at n = 2.81e17, pp.225102-12 and -13. confirmed.
- 02c table and text (in-text p.225102-13): optical Hall mobility 112 cm2/Vs. confirmed.

### Pandey2025
- 02c 57: 1e19-1e20 cm-3, p.1. confirmed.
- 02c 59, 84: Green's function vs scale length, approximated Gaussian (Fig. 2), HfO2 permittivity 15, p.2. confirmed.
- 02c 60: Green's identity, p.3. confirmed.
- 02c 63: channel trap 1e20 at 0.4 eV above EC, Gaussian, ni = 5e19, Sentaurus calibrated, p.5. confirmed.

### WangX2025
- 02c 94: Gaussian shallow donors as positive charge in depletion, pp.2390-2391. confirmed.
- 02c 97: Gauss's law across the gate oxide (Eq. 10), p.2393. confirmed.
- 02c 98: Monte Carlo with Gaussian Tox, Tch, Nsd, p.2396. confirmed.
- 02d 76: Gaussian DOS definition Eq. 1, p.2391. confirmed.

### Anusha2024
- 02c 122 (Sentaurus/Silvaco structure editors, p.2), 124 (WIZO mobility decline, Fig. 2a, p.4), 127 (SS = qkT(Nss tch + Dit)/Ci log e, one term set to zero, p.5), 128 (~120 mV/dec, p.14). confirmed.

### Giannozzi2009
- 02c 152 (open-source suite, p.1), 154 (DFT, plane waves, NC/US/PAW pseudopotentials, GNU GPL, p.2). confirmed.

### AtlasManual (confirmed as cited)
- 02c 219 ELECTRODE pp.1207-1211. confirmed.
- 02c 222, 02d 95 TMUN: constant low-field mobility (TL/300)^-TMUN, p.179; TFT chapter table, p.513. confirmed.
- 02c 223 CONTACT pp.1145-1156: WORKFUN (1148, 1150), RESISTANCE (1153). confirmed.
- 02d 104 NUMA/NUMD pp.1168-1174 (table 1168, descriptions 1171-1172). confirmed.
- 02d 105 mesh spacing factor: SPACE.MULT on pp.1374-1375, inside 1373-1377. confirmed.
- 02d 107 VSTEP/VFINAL pp.1593-1611 (1593, 1596-1597). confirmed.
- 02d 108 Newton, electrons only pp.1383-1389 (NEWTON 1385, CARRIERS 1386 descriptions). confirmed.

### Non-page citations (narrative author references or non-literature keys), confirmed as correct usage
- \citet{Januar2026} 02a 129, 156; \citet{Si2021} 02b 15, 27; \citet{Lin2022} 59, 70; \citet{Si2022} 102, 112;
  \citet{Wang2022} 140, 152; \citet{Kim2024} 183, 192; \citet{Stokey2021} 02c 13, 25; \citet{Pandey2025} 55, 67;
  \citet{WangX2025} 92, 101; \citet{Anusha2024} 121, 131; \citet{Giannozzi2009} 151, 157: section openers and
  "Items used from" box titles; every fact in those sentences carries its own page citation.
- \citep{DeviceSchematic} (02a 152, 02d 48), \citep{ExperimentalWorkbook} (02d 49): local data, not papers.

### Non-bundled sources (left, citing record checked)
- JanuarSI2026 (02b 238 fixed; 02c 185; 02d 51, 68): via Astra audit, captions on Januar2026 p.11. confirmed.
- Hamberg1986 (02b 41 via Si2021 p.501; 02c 187 four citing records). confirmed.
- Fan2021 (02c 186; 02d 60, 61, 75, 76): "via Astra (defect_papers.md)". confirmed as labelled.
- King2008, Robertson2011, Hinuma2019, Ando1982, Yoo2024: citing record and page verified (see above). confirmed.
- Lee2018: reworded (see Changes).

## Unresolved
1. Values only in the non-bundled SI or Fan2021 (eps 19.57, 9.30 +- 0.04, 9.03; Eg 3.05 eV, chi 4.30 eV, deep-acceptor 2.5-3.7e16, Fan "p.9") cannot be checked locally; they are labelled "via Astra".
2. Lee2018: no bundled record cites it; its role in the report is not established (row kept as "attribution to be confirmed").
3. 02a roughness-unit note (figure axis in nm vs text in A) comes from the Astra audit; the figure axis is not readable from the text digest.
4. 02c table row CONTACT lists the parameter as WORKFUNCTION; the manual name is WORKFUN (pp.1148, 1150). Not a citation error; decks not checked (out of scope).
