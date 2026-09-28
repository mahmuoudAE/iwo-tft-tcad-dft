# Januar2026 (source file Januar2026_SmallStruct_IWO.txt); headings give PRINTED page = cite as p.~<printed>

## printed page 1  (PDF page 1)

Unified Analytic Framework for Thickness-Dependent
Transport and Trap-State Modulation in Ultrathin
W:In2O3 Field-Effect Transistors
Mochamad Januar 1 | Zhao-Feng Luo 1 | Kou-Chen Liu 2,3,4,5 | Min-Hung Lee 1,6,7
1Program for Semiconductor Devices, Materials, and Hetero-integration, Graduate School of Advanced Technology, National Taiwan University, Taip ei,
Taiwan | 2Department of Electronic Engineering, Chang Gung University, Taoyuan, Taiwan | 3Division of Pediatric Infectious Disease, Department of
Pediatrics, Chang Gung Memorial Hospital, Linkou, Taiwan | 4Healthy Aging Research Center, Chang Gung University, Taoyuan, Taiwan | 5Department
of Materials Engineering, Ming Chi University of Technology, New Taipei City, Taiwan | 6Institute of Applied Mechanics, National Taiwan University,
Taipei, Taiwan | 7Graduate Institute of Electronics Engineering, National Taiwan University, Taipei, Taiwan
Correspondence: Mochamad Januar ( mochjanuar@ntu.edu.tw) | Min-Hung Lee ( minhunglee@ntu.edu.tw)
Received: 11 November 2025 | Revised: 21 December 2025 | Accepted: 5 January 2026
Keywords: bias-stress stability | IWO FETs | roughness-limited mobility | thickness scaling | trap-limited conduction | trap-state modulation
ABSTRACT
3D integration demands ultrathin oxide transistors that combine strong gate control, high mobility, steep subthreshold swing, and
normally off operation within back-end-of-line (BEOL) thermal budgets below 400°C. Yet, conventional amorphous oxides lose
stability and suffer from disorder-limited transport below ~10 nm, while crystalline or doped In 2O3, though more robust, remains
constrained by trap states, interface dipoles, and surface roughness at 2 –3 nm. This work presents a unified analytical framework
that quantitatively links band transport, trap-tail conduction, interface-trap diffusion, and roughness-limited scattering in In 2O3-
based field-effect transistors (FETs). The model reproduces transfer characteristics from subthreshold to above-threshold and
captures key differences between pristine and W-doped In 2O3 (IWO), including suppressed off-current, improved subthreshold
swing, and mitigation of thickness-dependent mobility degradation. Using sputtered IWO and pristine channels from ~2 to ~13 nm,
the framework introduces two physical descriptors— the volumetric trap density Nt and energetic width Tt— together with a gate-
and thickness-aware mobility law μsrðV ov, tÞ. Extracted flat-band carrier densities and Fermi-level shifts reveal that thermal carrier
suppression in IWO yields a linear reduction in off-current with decreasing thickness. DFT and DOS analyses confirm smoother
IWO/high-κ interfaces and lower trap densities, enabling predictive design of bias-stable, normally off oxide transistors for 3D-inte-
grated BEOL logic.
1 | Introduction
The relentless scaling of silicon complementary metal –
oxide–semiconductor (CMOS) transistors has been the engine
of semiconductor technology for decades, enabling denser and
more power-efficient large-scale integrations [ 1]. Yet, as feature
sizes approach the sub-10 nm regime, short-channel effects,
leakage currents, parasitic resistance, and fabrication complex-
ity have begun to erode the returns of 2D scaling, even with
innovations such as strained silicon, high- κ metal gates, and
FinFET architectures [ 2, 3]. To sustain performance gains,
3D integration has emerged a s a complementary pathway,
wherein back-end-of-line (BEOL) field-effect transistors
(FETs) can be fabricated directly atop finished CMOS layers
Abbreviations: BEOL, back-end-of-line; CBM, conduction band minimum; CMOS, complementary metal –oxide–semiconductor; DFT, density functional theory; FET,
field-effect transistor; IGZO, indium galium zinc oxide; IWO, indium tungsten oxide; PDOS, projected density of states; SS, subthreshold swing.
This is an open access article under the terms of the Creative Commons Attribution License, which permits use, distribution and reproduction in any medium, provided
the original work is properly cited.
© 2026 The Author(s). Small Structures published by Wiley-VCH GmbH.
Small Structures , 2026; 7:e202500807 1o f1 2
https://doi.org/10.1002/sstr.202500807
Small Structures
www.small-structures.com
RESEARCH ARTICLE

## printed page 2  (PDF page 2)

under low thermal budgets ( <400°C) [ 4]. This paradigm
demands semiconductors that combine high electron mobility,
low leakage, and excellent uniformity in low-temperature pro-
cesses [ 3, 5, 6]. Amorphous oxide semico nductors (AOSs), par-
ticularly indium gallium zi nc oxide (IGZO), have gained
traction in display backplanes due to their low-temperature
processability and acceptable mobility [ 7, 8]. However, the
amorphous nature of IGZO intro duces a high density of local-
ized band-tail states and structural disorder, leading to severe
threshold-voltage shifts under bias stress, poor reproducibility
in ultrathin films, and unreliable operation when scaled below
~5–10 nm [ 9]. Moreover, its percolative conduction caps mobi-
lities to ~10 cm 2 V−1 s−1 even under optimized conditions [ 10].
These intrinsic instabilities, combined with limited bias
stability and a mobility ceiling, render IGZO fundamentally
unsuited for high-performance BEOL integration, where
long-term reliability and scalability to ultrathin enhance-
ment-mode channels are mandatory [ 4, 9].
Recently, indium oxide (In 2O3) offers a promising alternative
for BEOL-compatible transistors due to its dispersive In-5s
conduction band, which yields band-like transport with low
effective mass and higher intrinsic mobility compared to the
percolative hopping in amorphous IGZO [ 4, 8, 11–13].
Unlike IGZO, In 2O3 can maintain a crystalline-like conduction
network in Nanometer-thick channels, mitigating mobility col-
lapse at 2–3n mt h i c k n e s s[8, 11, 12]. However, pristine In2O3 com-
monly exhibits excessive oxygen-vacancy donors ( n > 1019 cm−3),
polycrystalline films when sputtered, and normally on behavior.
Two complementary strategies have therefore emerged: (i)
aggressive channel-thickness sca ling, enabling full electrostatic
depletion and positive threshold voltage ( Vth)a tt h ec o s to f
reduced mobility, and (ii) aliovalent doping to suppress native
n-type conductivity without extreme thinning. Tungsten (W)
doping is particularly attractive since W 6+ substitution for
In3+ raises the oxygen-vacancy formation energy, thereby
reducing free carriers while preserving the high-mobility
matrix. Moderate W incorporation (~2 –3a t . % )y i e l d s
enhancement-mode operation wi th steep subthreshold slopes
(~70 mV dec −1) and mobilities above 10 cm 2 V−1 s−1 [14, 15].
Despite notable progress, the combined effects of ultrathin scal-
ing and W doping in In 2O3 remain poorly understood in the
BEOL-relevant 2 –3 nm regime [ 4, 11, 16, 17]. At these dimen-
sions, the channel volume approaches the spatial extent of defect
states and interface dipoles, so small variations in trap density or
dopant distribution can strongly perturb Vth, mobility, and sub-
threshold swing [ 17, 18]. The underlying mechanisms also com-
pete: thinning promotes electrostatic depletion and normally off
operation but sacrifices drive current, whereas W incorporation
suppresses carriers and stabilizes Vth yet risks increased scatter-
ing and mobility loss [ 11, 19]. Whether these effects reinforce or
counteract each other at Nanometer thicknesses remains unre-
solved, leaving a gap in design principles for normally off oxide
FETs [ 17]. In parallel, compact and numerical I –V modeling of
oxide semiconductors has progressed substantially, encompass-
ing IGZO devices to surface-potential formulations, reliability-
aware frameworks, and charge-density-based approaches
[20–29]. Yet, most existing models were developed with
display-oriented oxide TFTs in mind [ 22–29], with only limited
physics-based compact models targeting BEOL-relevant oxide
FETs [ 20, 21]. More critically, they fall short of capturing the
thickness-dependent coupling of transport, trap states, and
electrostatics in crystalline or doped In 2O3 channels [ 17, 30].
This limitation becomes especially acute in the 2 –3n m
regime, where device behavior is disproportionately governed
by tail states, interface dipoles, and dopant distribution
[11, 13, 16, 18, 19, 31]. Bridging this gap calls for a unified com-
pact framework for ultrathin scaling in In2O3 and W-doped In2O3
(IWO), capable of linking materials-level stabilization to device-
level performance.
Here, we propose a unified compact framework that integrates
the coupled effects of thickness scaling, trap –tail states,
interface quality, and surface-roughness scattering in In 2O3
and IWO FETs. Using low-thermal-budget sputtered IWO
channels spanning 2 –13 nm, our approach combines electrical
characterization, density-of-states analysis, and first-principles
calculations to disentangle band transport from trap- and
interface-mediated currents, while embedding gate- and
thickness-dependent confinement effects on both interfacial
traps and carrier mobility. The framework is designed to repro-
duce transfer characteristics across thick and ultrathin regimes,
decompose the measured current into distinct transport compo-
nents, and remain consistent with first-principles evidence of a
smoother, more coherent IWO/HfO 2 interface. It further
provides a basis for interpreting the contrasting bias-stress
responses of thick and ultrathin devices through trap-tail
modification and interface activation, thereby rationalizing
the observed evolution of Vth and SS. Overall, this unified
description provides a predictive link from atomistic stabiliza-
tion to device-level performance metrics — such as low Ioff,
near-thermal SS, and preserved mobility — and defines design
principles for realizing normally off, high-mobility oxide
FETs compatible with BEOL integration.
2 | Results and Discussion
2.1 | Device Fabrication and Characterizations
The FETs (configuration shown in the top inset of Figure 1a)
were fabricated on n + Si substrates in a bottom-gate structure.
A 50-nm TiN gate electrode was deposited by physical vapor
deposition and patterned. The HfO 2/Al2O3 gate dielectric layer
were grown by atomic layer deposition at 250°C, with growth
rates of ~0.92 Å cycle −1 and ~1.04 Å cycle −1, respectively. The
channel layers of In 2O3 or IWO (~2% W) were deposited by
pulsed DC sputtering (30 W, 10 kHz, V on ∶V off = 9∶1), resulting
in smooth and dense films. Diel ectric constants of approxi-
mately 9 were extracted for both In 2O3 and IWO from C –V
measurements (Figure S1), in good agreement with reported
values [ 11, 32]. Cross-sectional high-resolution cross-sectional
transmission electron micros copy (HRTEM) analyses (Figure
S2) confirm that the ultrathin channels lack long-range crys-
tallinity, consistent with predominantly short-range ordering
in the channel region. Plan-view scanning electron microscopy
(SEM, Figure S3) further shows continuous, dense films with
nanoscale grains, with IWO exhibiting a smaller characteristic
grain size than In 2O3 at comparable thickness (Figure S4).
Complementary atomic force mi croscopy (AFM) topography
and roughness statistics (Fig u r eS 5 )c o r r o b o r a t et h es m o o t h
surface morphology and quanti fy the thickness-dependent
root–mean-square roughness (Figure S6), providing an
2o f1 2 Small Structures , 2026
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 3  (PDF page 3)

independent measure of surface quality for the ultrathin
channels. Finally, 70-nm Pd source/drain electrodes were
deposited and patter ned, followed by contact hole opening
and metallization.
Devices were then annealed by rapid thermal annealing at
150°C for 600s, which improves the output characteristics
and shifts Vth toward enhancement-mode operation while
remaining within a BEOL-compatible thermal budget
(Figure S7). At higher annealing temperatures, mobility can fur-
ther increase, but the device becomes harder to turn off due to
crystallinity-driven increases in carrier concentration (Figures
S7 and S8), a typical behavior in metal –oxide semiconductors
[19]. Consistent with the compact-model extractions introduced
below, trap metrics improve at 150°C, whereas annealing at
200°C increases the extracted trap density by nearly two orders
of magnitude (Figure S9), supporting 150°C as the optimal
BEOL-compatible condition.
2.2 | Thickness-Dependent Performance of In 2O3
and IWO FETs
Figure 1a compares transfer curves of In 2O3 (orange) and IWO
(red) at thick (11 –13 nm) and ultrathin (2 –3n m ) t h i c k n e s s e s .
Thick pristine In 2O3 exhibits higher Ion and slightly higher Ioff,
turning on at more negative gate bias (depletion (D)-mode).
Thick IWO shows reduced Ioff and a right-shifted threshold
(enhancement tendency). In the ultrathin regime, differences
sharpen: 3 nm In 2O3 remains depletion-like with elevated
leakage, whereas 2 nm IWO becomes clearly enhancement-
mode (E-mode) with Ioff < 10−13 A μm−1 and a positive Vth,
while retaining substant ial drive current. Figure 1b summa-
rizes thickness trends: as thickness shrinks to 2 –3n m ,
In2O3 suffers severe mobility degradation (from 44.6 to
0.8 cm2 V−1 s−1)a n dS Si n f l a t i o n(>500 mV dec −1), whereas
IWO maintains ~5.1 –27.4 cm 2 V−1 s−1 with near-thermal-limit
SS (60 –70 mV dec −1) and progressively lower Ioff of below 10 −14
A in 2 nm-thick films. These data demonstrate IWO ’su n u s u a l
ability to retain transport while improving electrostatics dur-
ing aggressive thinning.
2.3 | Electronic-Structure Origins of the Observed
Transport
To rationalize the observed device-level differences, we first isolate
the underlying material-level contributions. As shown in Figure1c,
density functional theory (DFT) calculations performed using the
Quantum ESPRESSO package [33] reveal the electronic band struc-
tures and projected density of states (PDOS). The calculations
employed plane-wave basis sets with a kinetic energy cutoff of
71 Ry and a charge-density cutoff of 639 Ry, using PAW pseudopo-
tentials within the PBE –GGA exchange –correlation functional.
While PBE–GGA is known to underestimate absolute bandgap val-
ues [34, 35], it provides a reliable description of relative band-edge
shifts and effective-mass trends, making it sufficient to capture the
qualitative effects introduced by W incorporation. After full struc-
tural relaxation (to forces below 10 −3 Ry Bohr−1), self-consistent
charge densities were computed on a Monkhorst –Pack k-grid of
8 × 8 × 8, followed by band-structure evaluations along high-
symmetry k-paths and orbital-resolved PDOS projections.
In crystalline In 2O3, the conduction band minimum (CBM)
arises predominantly from delocalized In-5s orbitals, resulting
in a highly dispersive band with a steep curvature and low trans-
port effective mass, m∗ = ℏ2=∂2E=∂k2 [36]. This delocalization
facilitates high electron mobility as described by the Drude rela-
tion μ = ehτi=m∗, where hτi is the mean scattering time. Upon
introducing W dopants into the lattice, several key modifications
occur: the band curvature near the CBM flattens due to orbital
perturbation from W-5d states, the bandgap widens, and the
effective mass increases — typically signaling reduced mobility.
These changes reflect a decrease in orbital overlap and increased
carrier localization, which account for the slightly lower peak
mobility in thick IWO devices compared to pristine In 2O3.
However, this band structure view alone cannot fully explain the
superior transport observed in ultrathin IWO channels. As illus-
trated in Figure 1d, the amorphous nature of sputtered oxides
introduces a continuum of subgap states, broadly classified as
metallic tail states (arising from structural disorder and partial
delocalization) and deeper states (associated with oxygen coordi-
nation defects). These subgap states give rise to trap-limited con-
duction and steep subthreshold swing in ultrathin pristine In 2O3.
FIGURE 1 | Comparative transport and electronic-structure signatures of In 2O3 and IWO FETs. (a) Transfer characteristics of pristine In 2O3 and
IWO FETs, highlighting threshold-voltage modulation and suppressed off-state current in IWO devices. Inset: schematic of the FET stack with variab le
channel thickness. (b) Thickness-dependent evolution of field-effect mobility (top), subthreshold swing (middle), and off-state current (botto m) for both
In2O3 and IWO channels. (c) DFT-calculated band structures and PDOS of crystalline In 2O3 and IWO, illustrating how W incorporation perturbs the
CBM. (d) Empirical representation of the amorphous IWO DOS, capturing broadened tail states that dominate trap-limited transport.
Small Structures, 2026 3o f1 2
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 4  (PDF page 4)

Importantly, W doping suppresses both classes of disorder: it pas-
sivates oxygen vacancies, thereby reducing deep traps, and pro-
motes smoother charge delocalization, lowering the density of
tail states. The upward shift of the mobility edge Ec and narrow-
ing of the tail-state distribution effectively minimize carrier trap-
ping and enhance electrostatic control. Thus, despite an intrinsic
penalty in band dispersion, the W-induced suppression of disor-
der more than compensates — enabling IWO to sustain high
mobility and low off-state leakage even at sub-3 nm thickness.
These electronic structure insights underscore that in the
ultrathin regime, transport is no longer limited by bulk band
curvature but is instead governed by the interplay between
disorder-induced states and channel –interface quality.
2.4 | Unified Multistate Transport Model Linking
Disorder, Interface Effects, and Thickness
A picture of these mechanisms can be constructed and quantita-
tively extracted from the transfer characteristics of the device. We
model the total drain current using a Matthiessen-like blended-
channel formulation that captures extended-state conduction,
percolative tail-state transport, and interface-trap diffusion
ID = Iblend + Ioff (1a)
Iblend = m 1
IDc
/C18/C19m
+ 1
IDt
/C18/C19m
+ 1
IDit
/C18/C19m/C20/C21 − 1=m
(1b)
IDc = W
L Γc V 2ov (1c)
IDt = W
L Γt V γ
ov (1d)
IDit = Ioff exp V G − V FB
SS ln 10
/C18/C19
(1e)
Ioff = W
L qDntsnFB e − qV D
kT − 1
/C16/C17
(1f)
where V ov = 1
κ ln 1 + eκðV G − V FB Þ/C0/C1
is the gate overdrive voltages
ensures continuity across threshold. Full details of the model
derivation and fitting methodology are given in the
Supplementary Information (Equations S3-S22). Here, IDc cap-
tures band-like transport through extended states, IDt represents
percolative conduction across tail states, and IDit accounts for dif-
fusion currents mediated by interface traps. The subthreshold
swing SS = ln 10 × kT
q 1 + q2 Dit
Cox
/C16/C17
provides an estimate of Dit.
From measured ID(VG), the free-carrier density can be recon-
structed and linked to the Fermi level
nc V GðÞ = 2CoxL
μcεskTW ID V GðÞ
EF − Ec
kT ≈ ln nc
Nc
/C18/C19
+ nc
2
ﬃﬃ ﬃ
2
p
Nc
(2)
Moreover, the tail-channel strength Γt maps to an effective tail-
state density via
Nt = C2ox
2 θt εs kTt
μcNc εs kT
Γt Cox γ − 1ðÞ
/C18/C19 2=γ
(3)
These relations quantitatively link transfer curves to the under-
lying electronic landscape and enable extraction of Ntail, Ndeep,
and nc, revealing how W doping mitigates disorder-driven trans-
port degradation in ultrathin IWO.
2.5 | Fitting Confidence, Parameter Correlation,
and Identifiability Analysis
Figure2a validates the blended-current transport framework against
experimental IWO FET transfer characteristics across representative
channel thicknesses. The close agreement in both the subthreshold
and on-state regimes indicates that a single compact model captures
the crossover from near-band transport in thicker channels to dis-
order- and interface-limited transport in ultrathin films.
Since multiple transport mechanisms are fitted simultaneously,
we assess parameter identifiability and potential multicollinear-
ity using Monte Carlo (MC) refitting together with Pearson cor-
relation and variance inflation factor (VIF) analyses (methods in
Supplementary Information Section S7; Equations S23 –S27) [37].
From an ensemble of N = 200 MC refits, we compute the Pearson
correlation matrix R to quantify pairwise linear dependence
among the fitted parameters (Figure 2b). While several
FIGURE 2 | Model validation and parameter identifiability. (a) Measured (symbols) and modeled (lines) transfer characteristics for representative
channel thicknesses. (b) Pearson correlation matrix of the eight fitted model parameters obtained from Monte Carlo sampling (2.0 nm IWO device).
(c) Corresponding variance inflation factors (VIFs). All parameters exhibit VIF < 5, indicating low multicollinearity and robust parameter identifiability.
4o f1 2 Small Structures , 2026
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 5  (PDF page 5)

parameter pairs show strong correlations, consistent with shared
physical contributions to transport and electrostatics, pairwise
correlation alone does not imply degeneracy.
We therefore evaluate multiparameter coupling using VIF values
derived from R − 1 (Figures 2c and S10). The fitted parameters
exhibit uniformly low VIFs: V FB = 2.23, Γc = 2.41, Γt = 2.42,
γ = 2.16, SS = 1.22, Ileak = 1.07, and Δsr = 2.28, with a maximum
VIF of 2.42 for Γt . Under standard statistical criteria (VIF <5)
[38], these values indicate low multicollinearity and a well-
conditioned fitting problem.
Consistent with these insights, the MC distributions obtained
under 5% relative noise (Figure S10) are narrow, unimodal, and
centered near the baseline fit values, demonstrating robustness
against realistic measurement uncertainty. The trap metrics Tt
and Nt are derived quantities— computed from the fitted parame-
ter set rather than independently optimized — and are therefore
presented without associated VIF values. Their tightly peaked dis-
tributions further confirm that these trap-related descriptors are
stable, physically meaningful outcomes of the fitting procedure,
rather than artifacts arising from parameter degeneracy.
2.6 | Deconvolving Band, Tail, and Interface
Contributions
To elucidate the physical origin of current transport in ultrathin
oxide channels, we deconvolve the measured transfer characteristics
into band-like, tail-state, and interface-trap –assisted components
using the blended-current fra mework. This approach enables a
quantitative separation of transport mechanisms that are otherwise
convoluted in total-current measurements. As shown in Figure3a,b
(3 nm ultrathin In2O3) and (2 nm ultrathin IWO), the model repro-
duces the measured transfer characteristics with excellent fidelity on
both linear and logarithmic scales, while simultaneously resolving
the total current into band-like ( IDc), tail-state (IDt), and interface-
trap–assisted (IDit)c o n t r i b u t i o n s .
Figure 3c maps the reconstructed density of states (DOS) to the
Fermi-level position relative to the mobility edge ( EF–Ec) for a
3n m I n2O3 FET (left) and a 2 nm IWO FET (right). The In 2O3
channel exhibits a broader tail and a larger deep-state back-
ground, whereas IWO shows a narrowed tail and suppressed
deep states — consistent with the smaller trap-mediated current
fractions in Figure 3a,b. Figure 3d compiles the integrated
metrics, comparing the extracted tail-state density Ntail and
deep-state density Ndeep between the two channels; both are sub-
stantially reduced in IWO, evidencing effective trap passivation.
DFT-based interface energetics in Figure 3e further support this
picture: the valence-band offset ΔEv and the interface formation/
adhesion energy γinterface indicate a more favorable and chemi-
cally stable IWO/HfO 2 interface than In 2O3/HfO2, consistent
with reduced interfacial perturbations. Figure 3f–h visualize
the atomistic origin of these trends: (f ) shows relaxed interface
structures for In 2O3/HfO2 and IWO/HfO 2; (g) presents planar-
averaged electrostatic potentials across the oxide/high-k junction
FIGURE 3 | Model-based deconvolution of carrier transport and trap states. Modeled and experimental current components — total (Itot), free-carrier
conduction ( Ic), tail-state channel (I Dt), and interface-trap diffusion ( IDit)— for ultrathin channels of (a) In 2O3 FETs (3 nm) and (b) IWO FET (2 nm).
(c) Extracted DOS profiles for ultrathin In 2O3 and IWO, highlighting reduced tail and deep traps in IWO. (d) Quantitative comparison of extracted Ntail
and Ndeep. (e) Surface-potential-dependent evolution of nfree, ntail, and nit. (f ) Atomic cross-sections of the oxide/high-κ interface and (g) planar-averaged
potentials highlighting smoother electrostatics in IWO. (h) Cross-sectional view of charge density distribution at the atomic interface region be tween
oxide and high-k layers.
Small Structures, 2026 5o f1 2
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 6  (PDF page 6)

(methods detailed in Section S8), with IWO exhibiting a smoother
potential profile; and (h) displays charge-density maps highlight-
ing enhanced interfacial delocalization in IWO. Together, the
transport fits, DOS reconstructions, and first-principles interface
analyses converge on the same conclusion: W incorporation sup-
presses tail and deep traps and improves interface coherence,
enabling near-ideal, ultrathin IWO FET operation.
2.7 | Thickness Dependence of Ioff, VFB, and SS in
IWO FETs
Figure 4 shows how channel thickness governs trap-assisted dif-
fusion, Fermi-level positioning, and electrostatic control in IWO
FETs. The extracted flat-band carrier density nFB scales linearly
with the off current Ioff [Figure 4a], consistent with the analytic
relation in the subthreshold regime (Equation ( 1f ))
Ioff ∝ tsnFB (4)
This trend is also reproducible from literature data (blue scatter
points), confirming the robustness of the approach. Ultrathin
channels around 2 nm exhibit markedly lower nFB and thus sup-
pressed Ioff, reflecting reduced thermal carrier availability near
flat-band. This reduction is directly linked to the equilibrium
Fermi level EF0 [Figure 4b], which shifts progressively deeper
below the conduction band edge Ec as thickness decreases. A
deeper EF0 signifies that fewer interfacial-localized and deep
states are thermally accessible at equilibrium — indicating that
less trap filling is required before conduction turns on. In con-
trast, thicker channels exhibit an EF0 that lies closer to Ec, imply-
ing that a larger fraction of interface and bulk-related trap states
must be filled to reach the onset of conduction, thereby increas-
ing Ioff and degrading the subthreshold swing.
The schematic band diagrams further illustrate this behavior
(Figure 4c): near flat-band, carriers are predominantly captured
by interface traps, and the position of EF0 reflects the degree of
interfacial state occupancy. With increasing gate bias, electrons
sequentially fill deeper bulk states and eventually reach tail states
and extended conduction-band states. In ultrathin channels,
where the entire film lies within the electrostatic influence of
the dielectric interface, even small variations in interface trap
density, tail-state distribution, or dopant placement can signifi-
cantly perturb V th and SS. This thickness-dependent progression
shows why aggressive scaling heightens sensitivity to traps and
interfaces, underscoring the role of W doping in mitigating inter-
facial disorder. By passivating traps and suppressing disorder
states, W enables low Ioff, near-thermal SS, and stable normally
off operation in the sub-5 nm regime.
The extracted trap density of states in Figure 4e reveals two dom-
inant regimes: interface-localized states near midgap ( Nit) and
tail states extending toward the conduction band edge ( Nt). As
expected, the ultrathin 2.0, nm device exhibits a lower Nit,
suggesting reduced interfacial state density due to diminished
interface area. However, this advantage is offset by a broader
and denser distribution of tail states near Ec, indicating enhanced
structural disorder and insufficient relaxation at the oxide –
semiconductor boundary. These shallow traps are energetically
close to the conduction band yet spatially dense, exerting strong
influence over device electrostatics and transport. Figure 4f
further quantifies this behavior by plotting the integrated trap
occupancy as a function of surface potential bending qϕ.
Although the device exhibits fewer trapped carriers under small
band bending due to the lower Nit, the ultrathin 2.0 nm channel
FIGURE 4 | Correlations of interfacial/tail traps states and device parameters in IWO FETs with varying thickness. (a) Flat-band trap density ( nFB)
vs. off current with thickness variation and literature comparison. (b) Equilibrium Fermi level position ( EF0) as a function of thickness. (c) Band
diagrams at low gate bias (left) and high gate bias (right). (d) Correlation of EF0 with flat-band voltage ( VFB) and subthreshold swing (SS).
(e) Trap density-of-states (DOS) vs. Fermi-level position for 2.0 nm and 13.2 nm IWO channels; inset: schematic of a disordered metal –oxide band
structure. (f ) Total trapped carrier density as a function of surface potential ( qϕ).
6o f1 2 Small Structures , 2026
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 7  (PDF page 7)

accumulates substantially more trapped charge in the qϕ > 0.3 eV
regime, where tail states dominate. This elevated trap population
not only degrades carrier mobility through trap-limited hopping
conduction but also induces additional flat-band voltage shifts
due to enhanced trap charging — an effect that further impacts
bias stability, as discussed in the following section.
2.8 | Thickness-Dependent Tail-State –Limited
Mobility
Figure 5a shows an inverse correlation between peak mobility
μmax and the tail-state density Nt across IWO thicknesses: as
the channel is thinned from 13.2 to 2 nm, μmax drops from
~27.4 to ~5.1 cm 2 V−1 s−1 while Nt increases by roughly a factor
of four. This trend indicates that thinner channels suffer dispro-
portionately from disorder-induced localization near the mobility
edge. Consistent with this picture, Figure 5b partitions the total
charge nall into free carriers nfree and trapped populations in tail
and interface states ( ntail, nit), and we model the effective
(injection) mobility as
μeff V GðÞ = nfree V GðÞ
nfree V GðÞ + ntail V GðÞ + nit V GðÞ μmax (5)
Because only nfree contributes to band-like transport, enhanced
occupation of tail/interface states at ultrathin thickness directly
suppresses μeff via the carrier-partition term in Equation ( 5).
These results identify tail-state occupation as a primary driver
of thickness-induced mobility degradation and establish the
baseline upon which additional extrinsic mechanisms ( e.g., sur-
face roughness) must be superimposed.
2.9 | Unified Surface Scattering Model: Gate- and
Thickness-Dependent Mobility
Carrier mobility in ultrathin oxides is governed by two coupled
mechanisms: intrinsic tail-state disorder and extrinsic surface-
roughness scattering. As discussed above, disorder-induced tail
states near the mobility edge reduce the fraction of free carriers
and limit mobility via multiple-trap –trap-release dynamics. At
the same time, when the channel thickness is reduced to just
a few nanometers, electrostatic confinement forces the carrier
wavefunction closer to the dielectric interface, thereby enhancing
scattering from atomic-scale roughness. To capture the combined
impact of gate-field confinement and thickness scaling, we intro-
duce an analytic mobility term [ 36],
μsr V ov, tðÞ = μ0
1 + θr V ov
1 − Δsr
t
/C18/C19 2
(6)
where μ0 is the bulk-limit mobility, θr quantifies the reduction in
mobility with increasing carrier sheet density, and Δsr defines an
effective roughness threshold for ultrathin films. The first factor,
μ0=ð1 + θr V ovÞ, embodies the Ando surface-roughness model
[39], in which μ ∝ 1=ðΔ2NsÞ and Ns ∝ V ov, capturing the gate-
bias-induced mobility roll-off. The second factor, ð1 − Δsr=tÞ2,
accounts for the quadratic suppression of mobility as the channel
thickness approaches the roughness scale, reproducing the
observed collapse in the ultrathin limit. Incorporating this
mobility expression into the compact current model modifies
Equation ( 1c)a s
IDc = W
L Γc V 2ov ⋅ μsr V ov, tðÞ
μ0
(7)
FIGURE 5 | Surface-roughness-limited mobility in IWO and In 2O3 FETs with varying thickness. (a) Inverse correlation between tail-state density
and mobility across channel thickness. (b) Carrier-partition model of mobility vs. surface potential in 2 nm IWO FETs. (c) Modeled transfer curve
decomposed into mobility components: μeff (total), μfree (band), and μtail (trap-limited). (d) Gate-dependent mobility for 2 and 13 nm IWO FETs, showing
high-field degradation from roughness scattering. (e) Scattering parameter θr as a function of thickness. (f ) Extracted effective roughness Δsr in IWO and
In2O3; inset: mobility vs. thickness used for extraction.
Small Structures, 2026 7o f1 2
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 8  (PDF page 8)

which provides a unified description of band conduction and
roughness-limited transport in ultrathin oxide FETs. Together
with Equation ( 1), this yields a holistic framework that captures
the coupled effects of thickness scaling, interface states, tail-state
disorder, intrinsic band transport, and surface roughness.
As shown in Figure 5c,d, the unified model reproduces both the
gate-voltage roll-off and the thickness-driven collapse of μeff .I n
undoped In 2O3, μeff < 1cm2 V − 1 s − 1 at t = 2 nm due to the com-
bined impact of disorder and interfacial roughness, whereas IWO
retains ~5 cm2 V−1 s−1, consistent with a lower trap density and a
smoother channel –dielectric interface. The fitted confinement-
scattering coefficient ( θr ) decreases with increasing thickness
[Figure 5e], consistent with weaker wavefunction –interface
overlap in thicker channels. The same framework yields quanti-
tative roughness metrics [Figure 5f]: the extracted effective
roughness is smaller for IWO, Δsr ≈ 2.87 Å, than for In 2O3,
Δsr ≈ 3.75 Å, indicating reduced interfacial scattering in IWO.
This trend is independently supported by AFM measurements
(Figure S6), which show substantially lower RMS surface rough-
ness for IWO than for In 2O3 at the same thickness (10 nm), and a
higher RMS roughness for ultrathin IWO (2 nm) compared with
thicker IWO (10 nm). The consistency between the extracted Δsr
and the AFM RMS roughness further supports the interpretation
that surface/interface roughness is a key contributor to the
thickness-dependent mobility degradation. In addition, the
reduced interfacial scattering in IWO compared with In 2O3 is
consistent with DFT predictions of a smoother IWO/HfO 2
interface and enhanced interfacial charge delocalization (see
Figure 3e–h).
2.10 | Trap-State Metrics, Threshold Shift, and
Subthreshold Slope Evolution under Bias Stress
To evaluate long-term device reliability, we conducted positive
bias stress (PBS) measurements on IWO and pristine In 2O3
FETs with channel thicknesses of 2 nm (IWO) and 10 nm
(IWO and In 2O3).
Figure 6a–c presents the evolution of transfer characteristics
under a 6 V gate bias for stress durations ranging from 0 to
1200 s. Among the 10 nm devices, IWO exhibits markedly
enhanced stability, with only a modest threshold voltage shift
( ΔV th /C24 0.72 V). In contrast, the ultrathin 2 nm IWO — although
still more stable than 10 nm pristine In 2O3— shows a slightly
larger positive shift in Vth (up to ~1.2 V) under prolonged stress.
These trends are well captured within a unified compact
model, which attributes the instabilities to stress-induced mod-
ifications in the trap-tail prefactor Nt and the characteristic tail
temperature Tt.
FIGURE 6 | Positive-bias-stress response and trap-state correlations in In 2O3 and IWO FETs of different thicknesses. Transfer characteristics under
positive bias stress (0–1200 s, VStress = 6 V) for (a) 10 nm In2O3, (b) 10 nm IWO, and (c) 2 nm IWO. (d) Evolution of threshold shift ( ΔV th, left panels) and
extracted trap density ( Nt, right panels). (e) Subthreshold swing (SS, left panels) and trap-tail broadening ( ΔTt , right panels).
8o f1 2 Small Structures , 2026
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 9  (PDF page 9)

In the subthreshold regime, carrier transport is governed by a
trap-limited band-tail model, where the occupation of localized
states is determined by
nt ≈ θt Nt exp EF − Ec
kTt
/C18/C19
EF < EcðÞ (8)
indicating that larger values of Nt or Tt increase subthreshold
carrier density, thereby modulating both the apparent threshold
voltage and subthreshold slope (SS). The shift in V th arises from
electrostatic contributions of trapped charge
ΔV th ≃ ΔQtrap
Cox
, ΔQtrap ≈ q ΔNt teff (9)
where ΔNt is the change in volumetric trap density, and teff rep-
resents an effective trapping depth near the gate dielectric
interface.
For the 2 nm IWO device, Vth increases nearly linearly with stress
time ( /C24 0→1.2 V), accompanied by a significant rise in Nt from
5.3 × 1019 to 1.05 × 1020 cm − 3. This behavior suggests stress-
induced activation of border/interface traps, contributing posi-
tive charge and shifting the onset of conduction to higher gate
bias. Similarly, 10 nm pristine In 2O3 shows strong instability:
Vth increases from ~2.29 to ~3.22 V as Nt escalates by over
two orders of magnitude ( 1.63 × 1018 → 2.24 × 1020 cm − 3), likely
due to oxygen-vacancy –related trap buildup. In contrast, 10 nm
IWO shows only a modest positive ΔV th (0 →0.72 V), despite a
slight reduction in Nt ( 3.39 × 1018 → 3.20 × 1017 cm − 3). This
apparent decoupling may arise from (i) stress-assisted passivation
of shallow tail/interface states, which reduces Nt and sharpens
the subthreshold response, and (ii) a small amount of fixed or
border charge located closer to the gate, exerting stronger elec-
trostatic leverage and causing a net positive shift in Vth.
Within this framework, the energetic width of the tail, character-
ized by Tt, plays a crucial role in determining SS. A wider tail
( Tt ") leads to poorer SS, while a narrower tail ( Tt #) sharpens
the switching characteristics. These trends are consistent with
the PBS results: 10 nm IWO shows a marked improvement in
SS ( /C24 119→70 − 80 mV dec −1) along with a substantial decrease
in Tt (down to ΔTt = − 139 K), reflecting tail-state passivation.
Similarly, 10 nm In 2O3 improves from ~113 to 92 –101 mV dec −1,
with ΔTt ≈− 111 to −137 K. Conversely, 2 nm IWO exhibits deg-
radation: SS worsens from 62 to ~89 mV dec −1, with a slight pos-
itive ΔTt ( +0.8 to +1.7 K), indicating increased energetic disorder
and trap activation at the dielectric interface.
Equations (8) and ( 9) provide a simplified description of the PBS
response in terms of two orthogonal trap metrics: the volumetric
density Nt and the energetic width Tt of the tail manifold.
In thicker films (10 nm), stress primarily narrows the tail
(ΔTt < 0), which sharpens the subthreshold branch and improves
SS; the accompanying threshold shift ΔVth is modest and reflects
a balance between trap passivation and any residual border/fixed
charge. In ultrathin channels (2 nm), interface/border phenom-
ena dominate: stress creates or activates traps, driving tail broad-
ening ( ΔTt < 0), SS degradation, and a rise in Nt, which together
yield a larger positive ΔVth. In compact form, the bias –stability
rules are
ΔTt < 0 ⇒ SS improves
ΔTt > 0 ⇒ SS degrades
ΔV th ∝ ΔQtrap ∝ ΔNt teff
(10)
These relations rationalize the divergent PBS trends across thick-
ness and composition within a single, physically consistent
framework.
In addition to PBS, the extracted trap metrics reveal clear
polarity- and temperature-dependent signatures, as summarized
in the Supplementary Information (see Figures S11 and S12).
Under PBS, the behavior is largely dominated by electron trap-
ping and progressive trap creation, leading to a predominantly
monotonic evolution of ΔVth, Nt, and SS, as shown in
Figure 6. In contrast, under NBS (Figure S11), the evolution is
distinctly nonmonotonic, consistent with two competing pro-
cesses acting on different time scales: at early stress times,
hole-assisted trap neutralization reduces Nt and improves SS,
whereas prolonged stress promotes net trap generation and
tail-state broadening, driving increases in Nt and ΔTi and ulti-
mately degrading SS. The crossover between these mechanisms
naturally produces the observed turning-point behavior in
ΔVth(t), Nt(T ), and SS(t). This stress-polarity-dependent interpre-
tation is consistent with recent reports on defect-engineered
ultrathin oxide transistors [ 40]. Additionally, temperature-
dependent measurements (Figure S12) further validate the same
framework: the systematic changes in ΔVth(T ), Nt(T ), SS(T ), and
ΔTi(T ) are captured without modifying the model structure,
because temperature enters directly through the trap statistics
and tail-state occupation (Equations ( 8)–(10)), i.e., through the
extracted trajectories ΔNt(T ) and ΔTt(T ).
3 | Conclusions
We developed and validated a unified framework that ties ultra-
thin scaling, oxide composition, and interface quality to the mea-
sured transport, switching, and bias stability of BEOL-compatible
In2O3-based FETs. By combining transfer-curve deconvolution
with DOS-based modeling and first-principles analysis, we show
that the device response is governed by two trap –tail metrics —
the volumetric density Nt and energetic width Tt— together with
a roughness-aware mobility μsrðV ov, tÞ that captures gate- and
thickness-induced confinement. This framework quantitatively
links microscopic disorder to macroscopic figures of merit:
reduced N t and narrowed Tt correlate with near-ideal SS and
low Ioff; thicker channels exhibit tail narrowing under PBS
(ΔTt < 0) and modest ΔVth, whereas ultrathin channels are
interface-dominated, showing tail broadening ( ΔTt < 0), SS deg-
radation, and larger positive ΔVth. DFT and interfacial charge
mapping further reveal a smoother, more coherent channel/
HfO2 interface in the modified In 2O3 films, consistent with
the extracted lower effective roughness Δsr and diminished
trap-mediated current fractions.
This framework highlights the essential design trade-off for
BEOL logic: thinning channels enhances electrostatics but ampli-
fies interface sensitivity, while appropriate chemical stabilization
suppresses disorder and extends the thickness scaling limits. By
reconciling these effects within a single physical description, we
define actionable design rules for defect-tolerant ultrathin oxide
Small Structures, 2026 9o f1 2
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 10  (PDF page 10)

transistors, offering a pathway toward reproducible, high-
mobility, and bias-stable 3D-integrated electronics.
Author Contributions
Mochamad Januar : conceptualization (lead), formal analysis (lead),
investigation (lead), software lead), validation (equal), visualization
(lead), writing – original draft (lead), writing – review and editing (lead).
Zhao-Feng Luo : data curation (lead), formal analysis (supporting),
investigation (supporting), methodology (equal). Kou-Chen Liu :
conceptualization (supporting), methodology (supporting), resources
(supporting). Min-Hung Lee: funding acquisition (lead), project admin-
istration (lead), resources (lead), supervision (lead), validation (support-
ing), writing – review and editing (equal).
Funding
This work was supported and funded in part by the Semiconductor
Research Corporation (SRC, 2024-LM-3236); the National Science and
Technology Council (NSTC, 114-2221-E-002-212-MY3, 112-2221-
E-002-252-MY3, 114- 2218-E-A49-031-MBK, 114-2640-E-002-007, and
114-2622-8-002-016); the Powerchip Semiconductor Manufacturing
Corporation (PSMC, 114H1004-C11 and 114H1004-C12); MATek
(2025-T-007); the United Microelectronics (UMC) Fellowship; and
National Taiwan University (NTU-CC-115L890306). Processes were sup-
ported by the Taiwan Semiconductor Research Institute (TSRI) and the
Nano Facility Center (NFC), Taiwan.
Conflicts of Interest
The authors declare no conflicts of interest.
Data Availability Statement
The data that support the findings of this study are available from the
corresponding author upon reasonable request.
References
1. S. B. Rahi and Y. S. Song, Scaling and Challenge of Si-Based CMOS,
Chapter 1 (John Wiley & Sons, Ltd., 2025), 1 –26. ISBN 9781394287307.
2. S.-X. Guan, T. H. Yang, C.-H. Yang, et al., “Monolithic 3D Integration
of Back-End Compatible 2D Material FET on Si FinFET, ” npj 2D
Materials and Applications 7, no. 1 (2023): 9.
3. S. Datta, S. Dutta, B. Grisafe, J. Smith, S. Srinivasa, and H. Ye, “Back-
End-of-Line Compatible Transistors for Monolithic 3-D Integration, ”
IEEE Micro 39, no. 6 (2019): 8.
4. S. Yuvaraja, H. Faber, M. Kumar, et al., “Three-Dimensional Integrated
Metal-Oxide Transistors, ” Nature Electronics 7, no. 9 (2024): 768.
5. S. Conti, “Metal Oxide Transistors 3D Integration on Low-Thermal
Budget,” Nature Reviews Electrical Engineering 1, no. 8 (2024): 495.
6. S. Datta, E. Sarkar, K. Aabrar, et al., “Amorphous Oxide
Semiconductors for Monolithic 3D Integrated Circuits, ” 2024 IEEE
Symposium on VLSI Technology and Circuits (VLSI Technology and
Circuits) (2024), IEEE, 1 –2.
7. K. Nomura, H. Ohta, A. Takagi, T. Kamiya, M. Hirano, and H. Hosono,
“Room-Temperature Fabrication of Transparent Flexible Thin-Film
Transistors Using Amorphous Oxide Semiconductors, ” Nature 432, no.
7016 (2004): 488,
8. Y. Magari, T. Kataoka, W. Yeh, and M. Furuta, “High-Mobility
Hydrogenated Polycrystalline In 2O3 (In2O3:H) Thin-Film Transistors, ”
Nature Communications 13, no. 1 (2022): 1078.
9. J. Lee, S. Bae, S. Shin, and S.-Y. Lee, “Mitigating Electrical Degradation
in Ultra-Thin IGZO TFTs through Contact Engineering with Al 2O3
Interlayer,” Applied Surface Science Advances 29 (2025): 100827.
10. C. Chen, K. Abe, H. Kumomi, and J. Kanicki, “Density of States
of a-InGaZnO From Temperature-Dependent Field-Effect Studies, ”
IEEE Transactions on Electron Devices 56, no. 6 (2009): 1177.
11. M. Si, Y. Hu, Z. Lin, et al., “Why In2O3 Can Make 0.7 nm Atomic Layer
Thin Transistors, ” Nano Letters 21, no. 1 (2021): 500.
12. H. Jang, T. Kim, W. Lee, et al., “InGaZnO4 and In2O3 Mobility Trend:
The Role of Structural Disorder from Amorphous to Crystalline States, ”
ACS Materials Letters 7, no. 6 (2025): 2024.
13. A. Charnas, Z. Zhang, Z. Lin, et al., “Review— Extremely Thin
Amorphous Indium Oxide Transistors, ” Advanced Materials 36, no. 9
(2024): 2304044.
14. C. Yoo, J. Hartanto, B. Saini, et al., “Atomic Layer Deposition of
WO3-Doped In 2O3 for Reliable and Scalable BEOL-Compatible
Transistors,” Nano Letters 24, no. 19 (2024): 5737.
15. E. Sarkar, C. Zhang, D. Chakraborty, et al., “First Demonstration of
High-Performance and Extremely Stable W-Doped In 2O3 Gate-All-
Around (GAA) Nanosheet FET, ” IEEE Transactions on Electron
Devices 72, no. 5 (2025): 2662.
16. L. Xu, L. Xu, J. Lan, et al., “Sub-5 nm Ultrathin In 2O3 Transistors for
High-Performance and Low-Power Electronic Applications, ” ACS
Applied Materials & Interfaces 16, no. 18 (2024): 23536.
17. K. Anusha and A. Dwivedi, “Review and Analysis on Numerical
Simulation and Compact Modeling of InGaZnO Thin-Film Transistor
for Display SENSOR Applications, ” Measurement: Sensors 36 (2024):
101391.
18. Z. Wang, Z. Lin, M. Si, and P. D. Ye, “Characterization of Interface and
Bulk Traps in Ultrathin Atomic Layer-Deposited Oxide Semiconductor
MOS Capacitors With HfO 2/In2O3 Gate Stack by C-V and
Conductance Method, ” Frontiers in Materials 9 (2022): 850451.
19. M. Si, Z. Lin, Z. Chen, X. Sun, H. Wang, and P. D. Ye, “Scaled Indium
Oxide Transistors Fabricated Using Atomic Layer Deposition, ” Nature
Electronics 5, no. 3 (2022): 164.
20. N. Pandey, U. Radhakrishna, J.-Y. Lin, et al., “Analytical Modeling of
Short-Channel Effects in BEOL-Compatible Thin-Film Transistors, ”
IEEE Transactions on Electron Devices 72, no. 5 (2025): 2381
21. X. Wang, K. Chen, Y. Li, et al., “A Physics-Based Compact Model for
IGZO Channel FET Toward Subthreshold Characteristic Dependent
Memory Application, ” IEEE Transactions on Electron Devices 72, no. 5
(2025): 2390.
22. M. J. Kim, S. Lee, E. H. Kim, J. H. Lim, and J. K. Jeong, “Theoretical
Modeling of a Temperature-Dependent Threshold-Voltage Shift in Self-
Aligned Coplanar IZTO Thin-Film Transistors, ” ACS Applied Electronic
Materials 5, no. 6 (2023): 3010.
23. A. Sharma, P. G. Bahubalindruni, M. Bharti, and
P. Barquinha, “Physical Parameters Based Analytical IV Model of
Long and Short Channel a-IGZO TFTs, ” Solid-State Electronics 192
(2022): 108273.
24. X. Wang and A. Dodabalapur, “Modeling of Thin-Film Transistor
Device Characteristics Based on Fundamental Charge Transport
Physics,” Journal of Applied Physics 132, no. 4 (2022): 044501.
25. M. Januar, C.-W. Cheng, W.-K. Lin, et al., “Correlating the Density of
Trap-States and the Field-Effect Performance in Metal-Oxide Thin-Film
Transistors With High- κ Gate Dielectrics via a Trap-Limited Conduction
Method,” IEEE Transactions on Nanotechnology 20 (2021): 321.
26. M. Ghittorelli, F. Torricelli, and Z. M. Kovács-Vajna, “Physical
Modeling of Amorphous InGaZnO Thin-Film Transistors: The Role of
Degenerate Conduction, ” IEEE Transactions on Electron Devices 63,
no. 6 (2016): 2417.
10 of 12 Small Structures , 2026
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 11  (PDF page 11)

27. S. Lee, D. Striakhilev, S. Jeon, and A. Nathan, “Unified Analytic Model
for Current –Voltage Behavior in Amorphous Oxide Semiconductor
TFTs,” IEEE Electron Device Letters 35, no. 1 (2014): 84.
28. S. Lee, K. Ghaffarzadeh, A. Nathan, et al., “Trap-Limited and
Percolation Conduction Mechanisms in Amorphous Oxide
Semiconductor Thin Film Transistors, ” Applied Physics Letters 98, no.
20 (2011): 203508.
29. H.-H. Hsieh, T. Kamiya, K. Nomura, H. Hosono, and C.-C. Wu,
“Modeling of Amorphous InGaZnO 4 Thin Film Transistors and Their
Subgap Density of States, ” Applied Physics Letters 92, no. 13 (2008):
133503.
30. H. Kim, H.-S. Choi, G. Yun, W.-J. Cho, and H. Park, “Understanding
Thickness-Dependent Stability of Tungsten-Doped Indium Oxide
Transistors,” Applied Physics Letters 125, no. 17 (2024): 173507.
31. Z. Lin, M. Si, V. Askarpour, et al., “Nanometer-Thick Oxide
Semiconductor Transistor with Ultra-High Drain Current, ” ACS Nano
16, no. 12 (2022): 21536.
32. M. Stokey, R. Korlacki, S. Knight, et al., “Optical Phonon Modes, Static
and High-Frequency Dielectric Constants, and Effective Electron Mass
Parameter in Cubic In 2O3,” Journal of Applied Physics 129, no. 22
(2021): 225102.
33. P. Giannozzi, S. Baroni, N. Bonini, et al., “QUANTUM ESPRESSO: A
Modular and Open-Source Software Project for Quantum Simulations of
Materials,” Journal of Physics: Condensed Matter 21, no. 39 (2009): 395502.
34. A. Schleife, M. D. Neumann, N. Esser, et al., “Optical Properties of
In2O3 from Experiment and First-Principles Theory: Influence of
Lattice Screening, ” New Journal of Physics 20, no. 5 (2018): 053016.
35. M. Januar, S. P. Prakoso, C.-W. Zhong, et al., “Room-Temperature
Fabrication of p-Type SnO Semiconductors Using Ion-Beam-Assisted
Deposition,” ACS Applied Materials & Interfaces 14, no. 41 (2022): 46726.
36. S. M. Sze and K. K. Ng, Physics of Semiconductor Devices , 3rd ed.
(Wiley-Interscience, 2007).
37. D. Luengo, L. Martino, M. Bugallo, V. Elvira, and S. Särkkä, “A Survey
of Monte Carlo Methods for Parameter Estimation,” EURASIP Journal on
Advances in Signal Processing 2020, no. 1 (2020): 25.
38. D. C. Montgomery, E. A. Peck, and G. G. Vining, Introduction to
Linear Regression Analysis , 6th ed. (John Wiley & Sons, 2021).
39. T. Ando, A. B. Fowler, and F. Stern, “Electronic Properties of Two-
Dimensional Systems, ” Reviews of Modern Physics 54 (1982): 437.
40. J. Li, L. Zheng, P. Hong, et al., “High-Stability Ultrathin Oxide
Transistors via Defect Engineering for High-Performance Capacitorless
DRAM,” Advanced Functional Materials . (2025): e14194.
Supporting Information
Additional supporting information can be found online in the Supporting
Information section. Supporting Fig. S1 : Capacitance–voltage (C –V)
characteristics and dielectric constant extraction. a C–V curves of
M/HfO2/M (MIM) and M/HfO 2/semiconductor/M (MISM; IWOand
In2O3) stacks. The dashed line denotes the extracted oxide capacitance
Cox; markers indicatethe accumulation-region data points used in the
analysis. b Relative dielectric constants εr of HfO 2, IWO, and In 2O3
obtained from the series-capacitance model. Supporting Fig. S2 :
Cross-sectional HRTEM images and corresponding FFT magnitu-
demaps of ultrathin FET channels. a 3nm In2O3 and b 2nm IWO devi-
ces. FFTs arecomputed from (i) the full field of view and (ii) a selected
local ROI within each image. Supporting Fig. S3 : Plan-view SEM
images and grain-size distributions of IWO and In 2O3 films. a,b
2-nm and 10-nm IWO films and c a 10-nm In 2O3 film. The corresponding
grain-sizedistributions extracted from the SEM images are shown along-
side the micrographs. Supporting Fig. S4 : Average grain extracted
from SEM images. a Grain size comparison between IWO and In 2O3
at 10 nm, showing the smoother surface of IWO. b thickness-dependent
grainsize of IWO films (2 and 10 nm). Supporting Fig. S5 : AFM topog-
raphy of IWO and In2O3 thin films. a IWO (2 nm), b IWO(10 nm), and
c In2O3 (10 nm). The reported RMS and average roughness values are
extractedfrom the corresponding height maps/profiles. Supporting
Fig. S6 : RMS surface roughness extracted from AFM images. a
RMS roughnesscomparison between IWO and In 2O3 at 10 nm, showing
the smoother surface of IWO. b thickness-dependent RMS roughness of
IWO films (2 and 10 nm). Supporting Fig. S7 : Electrical characteris-
tics before and after rapid thermal annealing(RTA). a Transfer
curves (ID –VG) for the as-deposited device and after RTA at 150°C
and 200°C for 600 s. b Output curves (ID –VD) measured at selected gate
biases for the as-depositeddevice and the device after 150°C RTA.
Supporting Fig. S8 : Trade-off between off-state leakage and mobil-
ity with annealing temperature. a Off-state current Ioff and b maxi-
mum field-effect mobility μmax as a function ofannealing temperature.
Supporting Fig. S9 : RTA-temperature-induced evolution of trans-
fer characteristics and extractedparameters in an IWO FET. a,b
Measured and modeled transfer curves afterRTA at room temperature
(RT) and 150°C, with band, tail, and subthreshold contributionsindicated.
c–f Annealing-temperature dependence of the extracted ΔVth, Nt, SS, and
ΔTt. Supporting Fig. S10: Monte Carlo uncertainty and identifiabil-
ity analysis of the fitted modelparameters (2 nm IWO device).
Histograms show the parameter distributions obtainedfrom 200 Monte
Carlo iterations with 5% relative noise: (a) VFB, (b) Γc, (c) Γt, (d) γ,
(e)S, (f ) Ileak, and (g) Δsr, together with the derived quantities (h) Tt and
(i) Nt. Dashedlines indicate the baseline fit values. The narrow, unimodal
distributions and consistently lowvariance inflation factors (VIF< 5) dem-
onstrate robust parameter stability and the absence of significant multi-
parameter degeneracy. Supporting Fig. S11 : NBS-induced evolution
of transfer characteristics and extracted parametersin a 2n m
IWO FET . a,b Measured and modeled transfer curves after 120 s and
600 s of negative bias stress, with band, tail-state, and subthreshold contri-
butions indicated. c–f Stress-time dependence of the extractedΔVth, Nt, SS,
and ΔTt. Supporting Fig. S12: Device-temperature-induced evolution
of transfer characteristics andextracted parameters in a 2 nm IWO
FET. a,b Measured and modeled transfer curves atelevated temperatures of
65°C and 85°C, with band, tail-state, and subthreshold contributionsindi-
cated. c–f Temperature dependence of the extractedΔVth, Nt, SS, and ΔTt.
Biographies
Mochamad Januar (Member, IEEE) is a
Postdoctoral Research Fellow in the Program for
Semiconductor Devices, Materials, & Hetero-
Integration at the Graduate School of Advanced
Technology, National Taiwan University (NTU).
Previously, he was a postdoctoral fellow at Chang
Gung University (2023 –2025) and a full-time lecturer at Atma Jaya
Catholic University of Indonesia (2017 –2019). He received his Ph.D.
(2023) and M.S. (2015) degrees in Electronic Engineering from Chang
Gung University, Taiwan, and his B.Sc. in Physics (2011) from Universitas
Indonesia. His research interests include oxide semiconductor devices,
ferroelectric and neuromorphic electronics, and physics-based modeling
of electronic and optoelectronic devices using DFT/TCAD approaches.
Zhao-Feng Lou received his M.S. degree from the
Institute and Undergraduate Program of Electro-
Optical Engineering, National Taiwan Normal
University (NTNU), Taipei, Taiwan, in 2022. He is
currently pursuing a Ph.D. in the Program for
Semiconductor Devices, Materials, and Hetero-inte-
gration (DMHI) at the Graduate School of Advanced Technology (GSAT),
National Taiwan University (NTU), Taipei, Taiwan. His research interests
include FeFETs, FeRAM, metal oxide transistors, 2T0C architecture, and
synaptic devices.
Small Structures, 2026 11 of 12
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License

## printed page 12  (PDF page 12)

Kou-Chen Liu received the Ph.D. degree in electrical
engineering from the University of Texas, Austin,
USA. In 2002, he joined the Graduate Institute of
Optoelectronics, Chang Gung University, Taiwan, and
received the Full Professorship with the Department
of Electronic Engineering in 2012. He is a Full
Professor and a Former Chairperson with the Department of Electronic
Engineering, Chang Gung University, Taiwan. He is also affiliated with
the Division of Pediatric Infectious Disease, Department of Pediatrics,
Chang Gung Memorial Hospital, and the Department of Materials
Engineering, Ming Chi University of Technology, Taiwan. His recent
research interests include the area of thin-film transistor devices, organic
electronics, polymer LED, and portable SPR biosensor for various bio-
medical applications. He received several top national research grants
from the Ministry of Science and Technology (MOST, Taiwan) for
engineering and biosensor research, and also from Chang Gung
Memorial Hospital for clinical research and biosensor applications. He
has several patents for thin film technology and biosensing platforms. He
is also a Routine Reviewer in several reputable international journals in
the field of thin solid film, organic electronics, and biosensor applications.
He has several years of research experience in the Industrial Technology
Research Institute, Motorola, and the University of Texas-Austin. His past
research works were related to ASIC design, the deep development of
nano/submicron Si & SiGe vertical MOSFET, Si & SiGe Poly-TFT, and
SOI devices.
Min-Hung Lee (Senior Member, IEEE) received the
Ph.D. degree in Electrical Engineering from National
Taiwan University, Taiwan, 2002. Currently, he is a
Professor in the Program for Semiconductor Devices,
Materials, and Hetero-integration (DMHI), Graduate
School of Advanced Technology (GSAT) at National
Taiwan University (NTU). Prior to joining NTU in 2023, he was a
Distinguished Professor, Director of Graduate Institute of Electro-Optical
Science and Technology (IEO) at National Taiwan Normal University
(NTNU). He was a Research Visiting Scholar at University of California,
Berkeley in 2019. He worked at the Industrial Technology Research
Institute (ITRI) on Strained-Si and Flexible Display technology in 2002 –
2007. His research themes focus on Ferroelectric Memory and Logic
devices, Neural-network devices, GaN-based devices, Oxide-
Semiconductor devices, Flexible Electronics, and Strained Engineering.
He has authored or co-authored over 200 publications and holds 11 U.S.
patents.
12 of 12 Small Structures , 2026
 26884062, 2026, 2, Downloaded from https://onlinelibrary.wiley.com/doi/10.1002/sstr.202500807 by National Taiwan University, Wiley Online Library on [05/09/2026]. See the Terms and Conditions (https://onlinelibrary.wiley.com/terms-and-conditions) on Wiley Online Library for rules of use; OA articles are governed by the applicable Creative Commons License
