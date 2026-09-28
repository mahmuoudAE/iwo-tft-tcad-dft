# Citation re-check C2 (2026-09-25)

Scope: chapters/00_abstract, 01, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12 and appendices/A_runs, B_code, C_decks,
D_register, E_reproducibility.
Method: every \citep / \citet / \citealp was listed with a regex over each file (139 instances before editing:
118 \citep/\citet + 21 \citealp; files 00, 07, 09, C, D have none). For each page-cited fact the cited printed page of
digest/papers/<key>.md was searched for the value or statement. ATLAS manual citations were checked in
tools/atlas_manual_fulltext.json (printed page = leading number of each page text; PDF page = printed + 6) by the
parameter or statement name. Line numbers below are those BEFORE editing.

## Summary

| Verdict | Count |
|---|---|
| confirmed | 106 |
| page corrected / page made exact | 19 |
| page added (bundled paper cited without page) | 9 |
| reworded (text changed to what the paper says, with page) | 5 |
| removed | 0 |
| total instances checked | 139 |

New citations added while fixing (not in the 139): 01:8 \citep[p.~2]{Januar2026} (2--13 nm series); 03:19
\citep[pp.~2--3]{Januar2026} (Sec. 2.1); 03:40 \citealp[p.~2]{Januar2026} (main-text permittivity "approximately 9");
04:862 \citep[p.~2]{Januar2026} (n > 1e19 in pristine In2O3, W raises vacancy formation energy); 05:124 second
citation p.~8 (Dsr value). One in-text manual page (not a cite command) corrected: 05:476 EGALPHA p.1336 -> p.1352.

Internal sources (DeviceSchematic 04:62, 03:19; ExperimentalWorkbook 03:20; DeckBuildManual 06:148) are project
records, not literature; counted as confirmed citations of records. Not-bundled literature in scope: JanuarSI2026
(04:64, 04:123), Fan2021 (04:165, 04:205, 04:695): each sentence already states "not bundled" and names the record
(Astra audit / digest/used_items.csv / configuration). No Hamberg1986, Yoo2024, Lee2018, King2008, Robertson2011,
Hinuma2019, Ando1982 keys occur in these files.

## Changes

| File:line | Before | After | Reason |
|---|---|---|---|
| 01:8 | \citet{Januar2026}: ... IWO channel of nominal thickness 2, 6.3, 13.2 or 31.8 nm, Pd ..., air-exposed back channel | \citet[pp.~2--3]{Januar2026} for TiN / HfO2-Al2O3 / Pd; "the paper's IWO series spans 2--13 nm" \citep[p.~2]; 2/6.3/13.2/31.8 nm and the air-exposed back channel attributed to schematic + workbook | reworded: 6.3 and 31.8 nm occur nowhere in the paper (p.2: "channels spanning 2-13 nm"); stack items are on p.2 (TiN, ALD) and p.3 (70 nm Pd) |
| 03:167 | \citet{Januar2026} (2--13 nm series) | \citet[p.~2]{Januar2026} | page added; p.2 states 2-13 nm |
| 03:259 | SI of \citet{Januar2026} (Fig. S12, ...) | \citet[SI Fig.~S12, caption on p.~11]{Januar2026} | page added; S12 caption (65/85 C, 2 nm IWO) is on p.11 |
| 04:94, 04:136 | PERMITTIVITY \citep[p.~1336]{AtlasManual} | p.~1340 | page corrected: p.1336 is only the MATERIAL description; PERMITTIVITY is defined on p.1340 |
| 04:178 | EG300 p.~1336 | p.~1338 | page corrected (EG300 definition p.1338) |
| 04:218 | AFFINITY p.~1336 | p.~1337 | page corrected (AFFINITY definition p.1337) |
| 04:267 | AFFINITY + EG300 p.~1336 | pp.~1337--1338 | page corrected |
| 04:491, 04:539 | NC300 p.~1336 | p.~1340 | page corrected (NC300 entry on p.1340, printed there with the typo "NV300 ... conduction band density") |
| 04:571 | NV300 p.~1336 | p.~1340 | page corrected |
| 04:1021 | TAUN0 p.~1336 | p.~1349 | page corrected (TAUN0 definition p.1349) |
| 04:126 | 8.9 "for evaporated In2O3 films (Hamberg, as cited in \citealp[p.~501]{Si2021})" | 8.9 for In2O3 as quoted by \citet[p.~501]{Si2021}; its source (Hamberg and Granqvist) concerns evaporated Sn-doped In2O3, reference list p.506 | reworded: p.501 gives 8.9 for In2O3; the "evaporated" qualifier belongs to the cited ITO paper (ref. 25, p.506) |
| 04:344 | Si2021 slabs "Al2O3-terminated" \citealp[p.~504] | "In2O3 on one Al2O3 layer with an H-terminated top surface" \citealp[pp.~504--505] | reworded: p.504 (and methods p.505: vacuum/In2O3/Al2O3) says the In2O3 surface is H-terminated on one Al2O3 layer |
| 04:473 | \citep[abstract]{Stokey2021} | \citep[p.~225102-1, abstract]{Stokey2021} | page made exact (0.208 me, n = 2.81e17 in the abstract on p.225102-1) |
| 04:617 | \citep[Sec.~2.8, Fig.~5a]{Januar2026} | \citep[Sec.~2.8, Fig.~5a, p.~7]{Januar2026} | page added: "Nt increases by roughly a factor of four" from 13.2 to 2 nm is on p.7 |
| 04:737 | 6.3e11 subthreshold method \citep[p.~4]{Wang2022} | pp.~4--5 | page made exact: value on p.4, "subthreshold method" wording on p.5 |
| 04:881 | DOPING UNIFORM \citealp[p.~1188] | p.~1189 | page corrected: p.1188 is the DOPING description; UNIFORM is described on p.1189 |
| 04:937 | NGD, EGD \citealp[p.~1171] | pp.~1170--1171 | page corrected: EGD is described on p.1170, NGD on p.1171 |
| 05:92, 05:140 | MUN / MATERIAL \citep[p.~1336] | p.~1343 | page corrected (MUN definition p.1343) |
| 05:124 | value and form of Dsr \citep{Januar2026} | form = thickness factor of Eq. 6 \citep[p.~7]; Dsr about 2.87 A for IWO \citep[p.~8] | reworded with pages |
| 05:158 | \citep[Eq.~5]{Januar2026} | \citep[p.~7, Eq.~5]{Januar2026} | page added |
| 05:293 | "... paper's mobilities are therefore saturation-formula peaks ..., not linear-regime muFE \citep{Januar2026}" | citation moved to the paper's 5.1/27.4 values \citep[p.~7]; the saturation-formula reading marked as an inference of this analysis (paper calls it field-effect mobility, Fig. 1b caption p.3, gives no formula) | reworded: the paper does not state its extraction formula |
| 05:328 | \citet{Si2022} (Rc < 0.1 ohm mm, TLM) | \citet[p.~167]{Si2022} | page added |
| 05:479, 05:552 | MODELS TEMPERATURE \citep[p.~1474] | p.~1478 | page corrected: p.1474 mentions TEMPERATURE only in the BIPOLAR note; the parameter is described on p.1478 (default in table p.1448) |
| 05:729 | \citet{Januar2026} (ratio about 4) | \citet[p.~7]{Januar2026} | page added |
| 06:49 | x.mesh loc/spac in micrometres \citep[p.~633] | pp.~633, 1117 | page made exact: p.633 (VCSEL chapter) states the units; the X.MESH statement itself is p.1117 |
| 06:96 | afile/dfile \citep[p.~1169] | pp.~1169--1170 | page corrected: AFILE p.1169, DFILE p.1170 |
| B:109 | \citep{Giannozzi2009} | \citep[p.~1]{Giannozzi2009} | page added (title/abstract page of the QE paper) |
| B:194-195 | \citet{Januar2026}, \citet{Kim2024} | \citet[pp.~7, 9]{Januar2026}, \citet[pp.~173507-3, 173507-6]{Kim2024} | pages added: script uses the x4 ratio (p.7) and PBS Nt (p.9); Kim Table I SS-Nt (p.173507-3) and CNF Nbt (p.173507-6) |

## Confirmed (106)

Januar2026: 01:8 p.2 (lack long-range crystallinity, nanoscale grains), p.8 (AFM RMS 2 nm > 10 nm), p.9 (PBS Nt
5.3e19->1.05e20 at 2 nm, 3.39e18->3.20e17 at 10 nm), SI S12 caption p.11 (65/85 C, 2 nm); 03:18 author mention;
03:26 p.2 (0.92 / 1.04 A per cycle, ALD 250 C); 03:39 SI via Astra record (not bundled, stated); 03:228 author
mention; 03:229 p.3 (5.1-27.4); 03:230 p.7 (27.4 -> 5.1, Nt about x4); 04:619 p.9 (5.3e19, 3.39e18); 05:729 p.9
(same values); 08:193 p.9 (PBS shifts 0-1.2 V, 0-0.72 V); 10:6 S12 p.9 and caption p.11; 11:73 p.8; 12:48 p.2;
A:113 SI via Astra record (not bundled, stated).
Stokey2021: 04:125 and 04:132 p.225102-12 (eps_DC 10.55 from LST); 04:474 p.225102-2 (0.18 me at the lowest density).
Si2021: 04:170 p.504 (Ev almost unchanged); 04:207 pp.503-504 (CNL/TNL about 0.4 eV above Ec); 04:254 p.504
(1.5 nm, Ec up by about 0.6 eV); 04:296 p.504; (04:344 Si2021 reworded above).
Lin2022: 04:167, 04:252, 04:296, 04:344 p.21542 (PBE gaps 0.94/1.27/1.88 eV; H passivation, 25 A vacuum);
04:475 p.21540 (0.17/0.19/0.23/0.30 m0); 04:737 and 04:1170 p.21539 (SS 63.5 mV/dec -> Dit 6e11).
Wang2022: 04:623 and 04:863 pp.4-5 (subgap DOS 3.3e20, ND 1e20 from C-V).
Kim2024: 04:857 p.173507-6 (Nbt 2.37/3.12/14.6e18 from the CNF model, 10/20/30 nm).
AtlasManual: 04:269, 04:492 p.1469 (SP.DIR masses, MODELS); 04:540 p.1433 (FERMIDIRAC); 04:651, 708, 763, 882
p.1171 (NTA, NGA, NGD); 04:652 p.1173 (WTA); 04:653 p.1169 (one exponential + one Gaussian per type); 04:654 p.1168
(NUMA/NUMD 12); 04:709 pp.1168-1169 (NGA 5e17, WGA 0.1); 04:821 p.1260 (QF, sign); 04:822 p.1264 (default
semiconductor-insulator), p.1263 (example); 04:976 p.1145 (no CONTACT -> charge-neutral Ohmic); 04:977 p.1148
(WORKFUN default 0); 04:1000 p.1169 (SIGTAE 1e-16, SIGTAH 1e-14); 04:1020 pp.1168-1169; 05:92 and 05:457 p.179
Eq. 3-215; 05:183 pp.1169, 1171, 1173; 05:231 p.179; 05:359 p.1145, p.1153 (CON.RESIST, RESISTANCE; example p.1155);
05:454 p.179 Table 3-43 (TMUN 1.5; also p.1413 table, p.1355 definition); 05:479 p.1355 (TMUN on MATERIAL);
05:648 p.1168; 05:683 pp.1168-1169 and p.1171 (NUMA/NUMD cannot be modified); 06:16 general; 06:47 p.1376 (WIDTH
scale factor) and p.1374 (default 1.0 um); 06:55 p.1559; 06:58 pp.1207-1209; 06:60 p.1208 (electrode material
applies no electrical property); 06:66 p.1189 (UNIFORM needs type + CONCENTRATION, box defaults to the whole region);
06:72 p.1366 (USER.DEFAULT); 06:75 p.1336 (MATERIAL description); 06:82 pp.108-109 (Fermi-Dirac statistics);
06:91, 92 p.1169 (four distributions; CONTINUOUS); 06:94 p.1171; 06:95 p.1173; 06:97 p.1168; 06:100 pp.1168-1169;
06:112 p.1260; 06:113 p.1264; 06:120 p.1384; 06:128 p.1299 (PROBE values stored in log); 06:133 p.1598 (SOLVE INIT
zero-carrier); 06:135 pp.1593, 1609; 06:141 pp.1299, 1301; 06:213, 224, 231 p.1386 (CARRIERS, IR.TOL, CR.TOLER);
06:221, 233 p.1383 (TRAP true, XANDRNORM false); 06:222 pp.1389, 1395 (MAXTRAPS 1-10); 06:223 p.1389 (ITLIMIT);
06:232 p.1387 (XANDRNORM); 06:257 p.179; 06:258 p.1672 (Table B-5 TMUN 1.5); E:18 general.
Other: 04:62, 03:19 DeviceSchematic; 03:20 ExperimentalWorkbook; 06:148 DeckBuildManual (internal records);
04:64, 04:123 JanuarSI2026 and 04:165, 04:205, 04:695 Fan2021 (not bundled; text names the record).

## Unresolved

- JanuarSI2026 values (eps HfO2 19.57, IWO 9.30 +- 0.04, In2O3 9.03; 04:64, 04:123, 03:39, A:113): the SI is not
  bundled; the main text (p.2) gives only "approximately 9". Not verifiable here; text states the record.
- Fan2021 values (IWO gap, 96/4 affinity estimate, NGA range 2.5-3.7e16; 04:165, 04:205, 04:695): not bundled;
  not verifiable; text states the record.
- DeckBuildManual (06:148): no local full text in tools/; not checked.
- Linter (tools/lint_latex.py) after editing: 0 errors, 0 warnings.
