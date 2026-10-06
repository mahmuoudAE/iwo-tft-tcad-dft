# Traps in the V1 TCAD device: location, definition, computation

Parameters are parsed from the `device.in` decks of the final runs 0038, 0039 and 0040 (`trap_figures.py` → `trap_parameters.json`). The curves are checked against the trap tables ATLAS wrote (`acceptor_r1.dat`, `acceptor_r2.dat`, symbols in `figures/trap_dos`).

| # | trap | where | energy distribution | values (2.0 / 6.3 / 13.2 nm) | source |
|---|---|---|---|---|---|
| 1 | Acceptor-like band tail | whole IWO film (regions 1 + 2) | g = N<sub>TA</sub> exp[-(E<sub>c</sub> - E)/W<sub>TA</sub>] | W<sub>TA</sub> = 40 meV; N<sub>t</sub> = N<sub>TA</sub>W<sub>TA</sub> = 2.0 / 0.85 / 0.49 × 10<sup>19</sup> cm<sup>-3</sup> | W<sub>TA</sub> and N<sub>t</sub>(2 nm) fitted on the 2 nm device; N<sub>t</sub>(t) = N<sub>t</sub>(2 nm)·(2/t)<sup>0.75</sup>, exponent from the target paper's trap-density ratio |
| 2 | Deep acceptor Gaussian | bulk IWO (region 1) | g = N<sub>GA</sub> exp{-[(E - (E<sub>c</sub> - 0.6 eV))/0.15 eV]<sup>2</sup>} | N<sub>GA</sub> = 5 × 10<sup>16</sup> cm<sup>-3</sup> eV<sup>-1</sup>; √π N<sub>GA</sub>W<sub>GA</sub> = 1.3 × 10<sup>16</sup> cm<sup>-3</sup> | assumed (order of the value reported for another IWO device); V<sub>th</sub> effect <= 3 mV |
| 3 | Interface acceptor states D<sub>it</sub> | 0.25 nm IWO layer at the Al<sub>2</sub>O<sub>3</sub> interface (region 2) | Gaussian at E<sub>c</sub> - 0.30 eV, width 0.12 eV | peak 2.9 × 10<sup>11</sup> cm<sup>-2</sup> eV<sup>-1</sup>, total 6.4 × 10<sup>10</sup> cm<sup>-2</sup> | assumed: half of the HfO<sub>2</sub>/In<sub>2</sub>O<sub>3</sub> literature value; V<sub>th</sub> effect +11 mV |
| 4 | Fixed charge Q<sub>f</sub> (not a trap) | IWO/Al<sub>2</sub>O<sub>3</sub> interface sheet | none (always charged) | +1.73 × 10<sup>12</sup> / +8.7 × 10<sup>10</sup> / +1.73 × 10<sup>12</sup> cm<sup>-2</sup> | fitted on V<sub>th,cc</sub>; shift -qQ<sub>f</sub>/C<sub>ox</sub> = -0.31 V at 1.73 × 10<sup>12</sup> |

**Not modelled:**
- traps in Al<sub>2</sub>O<sub>3</sub> and HfO<sub>2</sub>;
- traps at the Al<sub>2</sub>O<sub>3</sub>/HfO<sub>2</sub> interface;
- separate air-side surface states;
- donor-like traps.

N<sub>D</sub> = 2.5–3.0 × 10<sup>17</sup> cm<sup>-3</sup> are shallow donors, not traps.

**How ATLAS computes them.**
- DEFECTS CONTINUOUS splits each distribution into 384 acceptor levels.
- At each bias, each level's occupancy f(E) follows from the local electron quasi-Fermi level. In steady state this is the Fermi function; the capture cross sections (10<sup>-15</sup> cm<sup>2</sup>) matter only for transients.
- The trapped charge -q∫g(E)f(E)dE enters Poisson's equation. Trapped electrons do not conduct.
- The filling of the tail as the gate voltage rises therefore sets SS and makes the effective mobility rise with V<sub>G</sub>.
- Example, 2 nm: n<sub>t</sub> = 1.3 × 10<sup>16</sup> cm<sup>-3</sup> at E<sub>F</sub> = E<sub>c</sub> - 0.45 eV (off state) and 9.3 × 10<sup>18</sup> cm<sup>-3</sup> at E<sub>c</sub> - 0.04 eV (near threshold) (`figures/trap_occupancy`).

**Why the interface sheet sits in a 0.25 nm layer.** ATLAS defect densities are volumetric, so the sheet D<sub>it</sub> is placed in this layer: N<sub>GA</sub> = 2.9 × 10<sup>11</sup> / 2.5 × 10<sup>-8</sup> cm = 1.17 × 10<sup>19</sup> cm<sup>-3</sup> eV<sup>-1</sup>. The potential drop across the layer is about 0.2 mV, and halving the layer changes I<sub>D</sub> by <= 0.06 %.
