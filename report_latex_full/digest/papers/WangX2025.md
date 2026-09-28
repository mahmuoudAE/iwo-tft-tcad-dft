# WangX2025 (source file Wang2025_TED_IGZO_compact.txt); headings give PRINTED page = cite as p.~<printed>

## printed page 2390  (PDF page 1)

2390 IEEE TRANSACTIONS ON ELECTRON DEVICES, VOL. 72, NO. 5, MAY 2025
A Physics-Based Compact Model for IGZO
Channel FET Toward Subthreshold
Characteristic Dependent Memory Application
Xuebin Wang
 , Student Member, IEEE, Kaifei Chen
 , Yutao Li, Jingsi Qiao
 , Yuanxiao Ma
 ,
Chengji Jin
 , Member, IEEE, Jixuan Wu
 , Member, IEEE, Jiezhi Chen
 , Senior Member, IEEE,
Masaharu Kobayashi
 , Senior Member, IEEE, Guanhua Y ang
 , Member, IEEE,
Ling Li
 , Senior Member, IEEE, Fei Mo
 , Member, IEEE, and Y eliang Wang
 , Member, IEEE
Abstract— InGaZnO (IGZO) transistors and their related
memory applications have recently aroused great interest
among researchers. In this article, we consider a shallow
donor with a Gaussian distribution as positive charge in
the IGZO channel to analyze surface potential (ϕS) for sub-
threshold operation precisely. Meanwhile, a new surface
potential analysis method for the IGZO channel is proposed
considering 1) the effect of the floating body due to the
lack of holes and 2) the effect of enhanced gate charge
due to the electric field from the drain and source in the
short channel. The proposed compact model demonstrates
a good agreement with TCAD simulation and experimental
results regarding device variation in all operation regions.
Finally, a Monte Carlo simulation of IGZO ferroelectric field
electric transistors (FeFET) and 2T0C IGZO FET DRAM,
considering device and material properties variation shows
the potential of this model for circuit-level simulations for
memory applications.
Index Terms— Compact model, InGaZnO (IGZO) channel,
shallow donor, thin-film transistors (TFTs).
I. I NTRODUCTION
R
ECENTLY, InGaZnO (IGZO) channel transistors have
attracted more attention for memory applications by
Received 13 February 2025; revised 28 February 2025; accepted
4 March 2025. Date of publication 20 March 2025; date of current ver-
sion 7 May 2025. This work was supported in part by the National Nat-
ural Science Foundation of China under Grant 62201026. The review of
this article was arranged by Editor Y . Chauhan.(Corresponding authors:
Fei Mo; Y eliang Wang.)
Xuebin Wang, Yutao Li, Jingsi Qiao, Yuanxiao Ma, and Y eliang Wang
are with the School of Integrated Circuits and Electronics,
Beijing Institute of Technology, Beijing 100811, China (e-mail:
yeliang.wang@bit.edu.cn).
Kaifei Chen, Guanhua Y ang, and Ling Li are with the State Key
Laboratory of Fabrication Technologies for Integrated Circuits, Institute
of Microelectronics, Chinese Academy of Sciences, Beijing 100045,
China.
Chengji Jin is with Hangzhou Institute of Technology, Xidian University,
Hangzhou 311231, China.
Jixuan Wu and Jiezhi Chen are with the School of Information Science
and Engineering, Shandong University, Qingdao 250100, China.
Masaharu Kobayashi is with the Institute of Industrial Science, The
University of Tokyo, Tokyo 153-0041, Japan.
Fei Mo is with the School of Integrated Circuits and Electronics,
Beijing Institute of Technology, Beijing 100811, China, and also with
Beijing Institute of Technology (Zhuhai), Zhuhai 519088, China (e-mail:
mofei@bit.edu.cn).
Digital Object Identifier 10.1109/TED.2025.3549745
back-end-of-line (BEOL) process due to its low deposition
temperature (<400 ◦C), high mobility in ultrathin films,
nearly zero low-k interfacial layer, and extremely low OFF-
state current ( Ioff < 3× 10−21 A/µm) [1], [2], [3]. The
IGZO channel transistor-based memories with monolithic 3-D
integration show longer retention, high reliability, and high
density, which has been demonstrated experimentally by sev-
eral groups [4], [5]. For large-scale memory circuit simulation
and design, it is essential to develop a physics-based compact
model of the IGZO channel transistor. The compact model
of IGZO channel transistor is required to describe electri-
cal characteristics in the subthreshold region. In particular,
an accurate description of the drain OFF-current ( Ioff) and
gate charge ( Qg) in subthreshold region is crucial for 2T0C
DRAM cell and IGZO ferroelectric field electric transistors
(FeFET) memory circuit design. There are several previous
works that have focused on a-IGZO channel-based TFT mod-
eling. Xu et al. [32] studied a-IGZO channel-based FeFET
modeling and the temperature dependence characteristics,
Kim et al. [30] carefully investigated the performance and
key parameters of sub-10 nm transistors, Pahwa et al. [31]
conducted a charge-based compact model considering various
effects, which greatly agreed with experimental results for dif-
ferent structure/material transistors, and several physics-based
compact models of IGZO FET have been proposed, accounting
for the electron (negative charge) in tail/extended states [6],
[7]. The models demonstrate a good agreement with experi-
mental data regarding drain current in the all operation regions
and gate charge in the above-threshold region. However, in the
subthreshold region, the ultralow (<1 × 10−19 A/µm) drain
OFF-current ( Ioff) and enhanced gate charge ( Qg) in the
short channel are hard to calculate in terms of the physical
parameters, which prevent the circuit-level simulation results
from matching the experimentally reported findings regarding
the extremely low leakage current values of 2T0C DRAM
cell [2] and the relationship between the memory window
(MW) and the channel length of IGZO FeFET [41], [42].
This is due to the lack of positive charge in the compact
model, which is a key physical characteristic of the IGZO
channel in the depletion region, as illustrated in Fig. 1. In the
IGZO channel, hydrogen-combined oxygen vacancies behave
as shallow donors, providing positive charge in the depletion
1557-9646 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.Authorized licensed use limited to: National Taiwan University. Downloaded on September 17,2026 at 23:24:20 UTC from IEEE Xplore.  Restrictions apply.

## printed page 2391  (PDF page 2)

WANG et al.: PHYSICS-BASED COMPACT MODEL FOR IGZO CHANNEL FET 2391
Fig. 1. Schematic illustration of a comparison between the conventional
and the proposed compact models, which consider shallow donors
(positive charge).
region [8], [9]. The shallow donor can be ignored in the
above-threshold region, as they are filled with electrons and
becomes neutral [10], [11]. However, in the subthreshold
region, shallow donors should be accounted for because they
become positively charged due to electron emission. Moreover,
the shallow donors play a critical role in IGZO FET regarding
threshold voltage ( Vth), ON-current ( Ion) and bias temperature
instability (BTI) [12], [13].
Based on the physical phenomenon of the IGZO material,
in this article, we developed a physics-based compact model
of an IGZO channel FET, considering Gaussian distributed
shallow donors as positive charges. This approach can effec-
tively calculate electrical performance in the depletion region.
An approximation using the tanh function was applied to
avoid numerical calculation involving positive shallow donors
with a Gaussian distribution. In addition, we proposed a new
channel potential solution method to avoid complex surface
potential calculations while maintaining the model’s physical
meaning. Moreover, the influence of source/drain electric field
on gate charge in short channel is considered. The proposed
model accurately replicates TCAD simulation results with
variable parameters across all operation regions. Subsequently,
we compared and modified the model with experimental data,
the simulated and experimental results showed a high degree of
consistency. At the same time, we also revealed that our model
could effectively fit in the subthreshold region considering
the influence of shallow donors, and achieved an ultralow
Ioff(<10−19 A/µm). The Ioff value matches the experimental
result [2] very well, without the need for additional leakage
model, for the first time, laying the foundation for subsequent
memory unit applications. Finally, the compact model is evalu-
ated for IGZO FeFET and 2T0C DRAM memory applications
in SPICE using Monte Carlo simulation, which effectively
simulates the impact of variations caused by process condi-
tions in realistic conditions, and is expected to be applied in
the design of large-scale monolithic 3-D integrated memory
circuits.
II. D EVICE MODELING
A. Shallow Donor
Shallow donors in IGZO are considered to be caused
by oxygen vacancies and hydrogen. Oxygen vacancies form
during crystal growth or arise as compensating centers due
Fig. 2. Schematic illustration of a shallow donor in IGZO: (a) becoming
neutral when an electron is filled and (b) becoming positively charge
by emitting an electron. (c) Schematic of the electronic structure and
(d) Gauss–Fermi integral involving numerical integration, the error func-
tion, and the tanh function.
to the presence of unwanted impurities [34]. Some previous
studies have indicated that oxygen vacancies in an oxide semi-
conductor act as a shallow donor by ionizing and bonding with
hydrogen to form O–H bonds [35], [36], [37], [38]. Shallow
donors maintain electrical neutrality when filled with electrons
at the vacant site and become positively charged when elec-
trons are emitted. Whether they maintain an electrically neutral
state varies with the operating conditions of the IGZO channel.
In the accumulation region, the shallow donor traps an electron
and becomes neutral, as shown in Fig. 2(a). In the depletion
region, the shallow donor becomes positively charged because
of electron emission, as shown in Fig. 2(b). Fig. 2(c) shows
the band structure of the Gaussian distributed shallow donor.
The neutral shallow donor with a trapped electron can be
calculated using numerical Fermi–Dirac integration, but it is
difficult to embed this in a compact model. An approximated
error function-based analytical method has been proposed[14].
However, due to the lack of error function in Verilog-A
language, the tanh function is used instead of error function
in our model.
The Gaussian density of states (DOS) Dx(x) considered
here is defined as follows [14]:
D(x)= Nsd
σ
√
2π
exp
(
−(E−µ)2
2σ 2
)
(1)
where Nsd is the total density of shallow donors between the
valence and conduction band, σ is the variance (or width) of
the DOS in Gauss distribution, and µ is the center position of
the maximum density, which represents the expected value in
Gaussian statistics.
Considering that the Fermi–Dirac probability distribution is
not significantly dependent on temperature, it clearly depends
on the two dimensionless coefficients (E− µ)/(kBT) and
(σ)/(k BT), which makes it hard to conduct analytical cal-
culations. We adopt the approach of first calculating the
infinitely narrow distribution (σ), and then further expand the
solution to accommodate the finite width of the Gaussian DOS.
The process can be concluded by assuming that σ and the
concentration value are low in order to obtain a reasonable
approximate solution. The parameter that determines the shift
quantity is (1/2)σ/(kBT)2. This process is not a simple
Authorized licensed use limited to: National Taiwan University. Downloaded on September 17,2026 at 23:24:20 UTC from IEEE Xplore.  Restrictions apply.

## printed page 2392  (PDF page 3)

2392 IEEE TRANSACTIONS ON ELECTRON DEVICES, VOL. 72, NO. 5, MAY 2025
Fig. 3. Schematic illustration of channel backside potential of IGZO
FETs under different channel conditions: (a) VGB= 0 V equilibrium,
(b) VGB > 0 V accumulation, (c) VGB < 0 V partial depletion, and
(d) VGB< 0 V full depletion.
numerical approximation, but has physical meanings, as has
been demonstrated by previous work [14], [39], [40].
By combining the degenerate and nondegenerate cases
corresponding to room temperature T → 0 and T →∞,
respectively, the analytical solution for the Gaussian DOS
distribution is obtained [14]
p= Nsd
(1
2− 1
2erf
( E f−µ√
2σ
))
(2)
where p is the positive charge and erf is the Gaussian error
function, this method demonstrates good fitting performance.
Unfortunately, the error function cannot be directly embedded
in the Verilog-A language, so we used the hyperbolic tan-
gent function tanh for approximation. Subsequently, the final
expression for the positive charge p is obtained
p= Nsd
(1
2− 1
2tanh
( E f−µ√
2σ
))
. (3)
Numerical and approximate calculation methods for positive
shallow donors are compared, as shown in Fig. 2(d). The tanh
function shows a good agreement with numerical method,
which provides a feasible approach for applying the shallow
donor model to Verilog-A language.
B. Channel Potential Calculation Method
In the IGZO channel, the 2-D Poisson equation, which
considers extended, localized, and donor-like states, is given
below ( ∂2
∂ x 2+ ∂2
∂ y2
)
ϕs= q
εigzo
(n− p) (4)
n(x)= ne(x)+ nlocal(x) (4.1)
where x and y represent the vertical and horizontal directions
of the channel layer, respectively, as shown in Fig. 3. εigzo is
the dielectric constant of the IGZO channel layer. ne and nlocal
are the extended and localized electron states, respectively. p
is the positive charge given in (3).
In amorphous oxide semiconductors, charge transport is
often described by a multiple-trapping and de-trapping model.
Therefore, the total electron carrier concentration n(x) in
the channel is equivalent to the sum of electron densities
in extended state ne(x) and localized state nlocal(x). The
description of the two carrier concentrations has been provided
by previous works [18], [19], [20], [21], [22], [23], [29], [30],
[31], and detailed descriptions of them are given below
ne(x)=τ0ν0 Ntexp
( EF− EC
kBT
)
(5.1)
nlocal(x)= NtθT exp
( EF− EC
kBTTA
)
(5.2)
θT=
π T
TTA
sin
(
π T
TTA
) (TTA< T) (5.3.1)
θT= T
T− TTA
(TTA≥ T) (5.3.2)
where Nt is the total density of trap states per unit volume, TTA
is the characteristic temperature of the localized states, and Ec
is the conduction band energy level.
Meanwhile, the extended states density was obtained
in (5.1), where τ0 is the lifetime of carriers, and v0 is the
attempt-to-escape frequency. Moreover,T is the environmental
temperature.
Here, we assume the gradual channel approximation to
neglect the y-dependence of ϕs (x, y) in (4) after obtaining
an accurate expression for the carrier density.
At the same time, we consider the surface potential in the
metal–insulation–semiconductor (MIS) structure and the bend-
ing of the energy band after applying voltage. The electrons
and positive shallow donors are rewritten as follows, where
Vch is the voltage applied across the drain and source:
ne(x)=τ0ν0 Ntexp
( E f 0+ qϕs− q Vch
kBT
)
(6.1)
nlocal= NtθT exp
( E f 0+ qϕs− q Vch
kBTTA
)
(6.2)
p= Nsd
(1
2− 1
2 tanh
( E f 0+ qϕs− q Vch−µ√
2σ
))
. (6.3)
By substituting (6.1)–(6.3) into (4) and integrating (4) from
the channel surface to the backside, we can obtain a general
expression for the surface potential ϕs.
Regarding the left-hand side of (4), we replace it with the
relationship:
dϕs= Esd x
∫ϕs
ϕb
∂2
∂ X 2ϕSdϕ=
∫Tch
0
∂
∂ X
(∂ϕs
∂ X
)
Esd x
=
∫
E
b
E
s Esd Es= 1
2
(
E 2
s− E 2
b
)
(7)
where ϕb is the potential of the channel backside, Tch is the
thickness of channel, and Es and Eb are the electrical field on
the surface and backside of the channel layer, respectively.
Regarding the right-hand side of (4), we can integrate it
normally, and the integral result is obtained
∫ϕs
ϕb
(n− p)
= q
εigzo
(x1+ x2− x3) (8)
Authorized licensed use limited to: National Taiwan University. Downloaded on September 17,2026 at 23:24:20 UTC from IEEE Xplore.  Restrictions apply.

## printed page 2393  (PDF page 4)

WANG et al.: PHYSICS-BASED COMPACT MODEL FOR IGZO CHANNEL FET 2393
x1=
( kBT
q τ0V0 Ntexp
( E F0+ qϕs− Vch
kBT
)
− kBT
q τ0V0 Nt exp
( E F0+ qϕb− Vch
kBT
))
(8.1)
x2= kBT
q NtθT exp
( E F0+ qϕs− Vch
kBTTA
)
− kBT
q NtθT exp
( E F0+ qϕb− Vch
kBTTA
)
(8.2)
x3=
(1
2 Nsd(ϕS−ϕb)+ T(ϕs)
)
(8.3)
T(ϕs)=− σ
q
√
2
NsdIn
(
cos
( E F0+ qϕs− Vch− E0
σ
√
2
))
+ σ
q
√
2
NsdIn
(
cos
( E F0+ qϕb− Vch− E0
σ
√
2
))
(8.4)
Vch= Vs or Vd. (8.5)
By combining (7) and (8), we can obtain a general expres-
sion for surface potential ϕs
Es=±
√
E 2
b+ 2q
εigzo
(x1+ x2− x3). (9)
Here, Gauss’s law is applied to the gate oxide layer.
Cox(VGB− VFB−ϕS)=εigzo ES (10)
where Cox represents the capacitance per unit area of the oxide
layer.
By substituting (10) into (9), we can obtain the final form
of the solution for the surface potential ϕs, taking into account
the shallow donor.
Moreover, the backside potential of the channel ϕb needs
to be considered. In a previous work on the IGZO compact
model, the majority of authors believed that the potential on
the back of the channel layer was the reference value, which
is 0. The floating body effect phenomenon in IGZO channel
transistors was revealed through experiments, emphasizing the
need to consider the influence of donor like states, which
confirmed our work from the experimental perspective [28].
Due to full depletion of the channel in the subthreshold
region, the channel becomes floating and ϕb is not 0. It is
important to find the correlation between the surface and
backside potential for solving ϕs. The calculation of backside
potential is divided into four conditions, as shown in Fig. 3,
which are Fig. 3(a) zero bias, Fig. 3(b) accumulation, Fig. 3(c)
partial depletion, and Fig. 3(d) full depletion. The references
can be explained by the fact that thin film transistors (TFTs)
work in accumulation mode because IGZO FET is an n-type
junctionless transistor. We believe that the TFT is in an OFF
state when the channel is in a fully depletion region, and the
Vg at this time can be considered as the threshold voltage.
Therefore, we can define the TFT operating modes based on
the presence of electrons and holes in the channel, as shown
in Fig. 3.
In condition Fig. 3(a)–(c),ϕb and Eb are given as follows:
ϕb= Vch
Eb= 0. (11)
Fig. 4. Calculation results of the proposed compact model versus TCAD
for long-channel IGZO FETs. (a) Surface electric field (E s) at the drain
and source. (b) Surface and backside potential at the drain and source.
In condition Fig. 3(d) full depletion, the potential differ-
ence between the backside and surface potential consists of
two parts: 1) positive charge and 2) electric field from the
drain/surface. Because of the lack of holes in the IGZO
channel, the positive charge is only from shallow donors,
which are uniformly distributed in the channel. Thus, the
potential difference induced by the positive charge is constant.
The potential at the ends of the depletion region can be
obtained by solving the width of depletion region, as given
in the following equation:
ϕdep=− q NsdT 2
ch
2εigzo
. (12)
The electric field-induced potential difference is calculated
using a semiempirical method, which is illustrated in Fig. 3(d),
and is given as follows:
ϕb= αL
(
ϕs−ϕdep
)
+ TchVch
αL+ Tch
. (13)
Moreover, due to the electric field from the drain/source,
the electric field at the backside ( Eb) is not zero again, which
is given as follows:
Eb= Vch−ϕb
αL . (14)
In the above equation, L is the length of the channel layer,
and α is the coefficient, taking into account the influence of
the short-channel effect. Finally, by decomposing the backside
potential of the channel layer (11)–(14), into surface potential
expression (9), an analytical solution for the surface poten-
tial can be obtained. We use the Newton–Raphson iteration
method to solve the equation here.
The behaviors of the surface electric field and surface poten-
tial compared with TCAD have been conducted, as shown in
Fig. 4.
Due to the floating body effect, in the subthreshold region,
surface electric field ( Es) of long-channel IGZO FETs is
independent on VG, as shown in Fig. 4(a), we can see that the
electric fields at the drain and source are equal and constant
in subthreshold operation region because of the lack of holes,
which are in good agreement with a previous report [12].
Fig. 4(b) shows the surface and backside potential of the
channel, with the inset providing an enlargement of the detail.
The difference between surface and backside potential at the
drain and source is constant.
Authorized licensed use limited to: National Taiwan University. Downloaded on September 17,2026 at 23:24:20 UTC from IEEE Xplore.  Restrictions apply.

## printed page 2394  (PDF page 5)

2394 IEEE TRANSACTIONS ON ELECTRON DEVICES, VOL. 72, NO. 5, MAY 2025
Fig. 5. Calculation results of the proposed compact model for
long-channel IGZO FETs. (a) Result of electron density at the drain
and source compared to TCAD simulations. (b) Drift and diffusion
components of the drain current.
C. Analytical Drain Current/Gate Charge Model
The drain current ID can be determined by expressing it as
the sum of drift and diffusion components, using the charge
sheet-based formulation
ID=µW Q dϕs
d x−µWϕt
d Q(ϕs)
d x . (15)
Here, W represents the width of the channel layer, and µ
denotes the carrier mobility in the IGZO channel. We assume
that carrier mobility is constant, and Q represents the amount
of charge in the channel layer, as shown in the following
equation [24]:
Q= Cox(VGB− VFB−ϕS)+ q NsdTch+εigzo
Vch−ϕb
αL . (16)
By integrating (15) from the source to the drain, a general
expression for the drain current ID can be derived
ID=µ W
L Cox
(
2ϕt(y2− y1)− 1
2
(
y2
1− y2
2
))
(17)
y1= VGB− VFB−ϕSd+ q NsdTch
Cox
+εigzo
Vd−ϕbd
CoxαL (17.1)
y2= VGB− VFB−ϕSS+ q NsdTch
Cox
+εigzo
Vs−ϕbs
CoxαL . (17.2)
Fig. 5 shows the contribution of charge density and current
in the accumulation and depletion regions. Fig. 5(a) illustrates
that in the subthreshold region, the electron concentration at
the source is several orders of magnitude higher than that at
the drain. The result is verified by TCAD simulation. Conse-
quently, the drift and diffusion current is plotted in Fig. 5(b).
The diffusion current dominates in subthreshold region, while
the drift current dominates in above-threshold region.
For transient simulation, it is essential to consider not only
the behavior of the drain current but also the node charges.
The short-channel IGZO FeFET has an enhanced gate charge,
which has not been effectively discussed in related works.
However, it is crucial for the memory operation of FeFET, as it
affects the inversion voltage and MW of the ferroelectric tran-
sistor [25], [26]. The formula for gate charge presented here is
usually derived from Ward’s charge-partitioning scheme [27].
However, this results in excessively complex charge calcu-
lations for IGZO TFT, which are time-consuming and not
suitable for large-scale memory circuit simulations. Therefore,
we adopt a semiempirical formula for approximation
Qg= W LCox
y3+ y4
2 (18)
y3= VGB− VFB−ϕsd (18.1)
y4= VGB− VFB−ϕss. (18.2)
Here, Qi represents the amount of charge per unit distance
in the channel layer, as given by (16). The results are then
verified in conjunction with the drain current in Section III.
D. DIBL Model
We consider the effect of drain-induced barrier lowering
(DIBL), which significantly affects the threshold voltage in
short-channel transistors. According to the physical definition,
it is necessary to solve the 2-D potential distribution in the
channel layer to analyze the dependence of the threshold
voltage and subthreshold swing on the channel length L in
the subthreshold region. A widely used model for analyzing
channel potential and its dependence on channel length L has
been developed [6]
ϕs(0, x)=ϕss+ c1sinh(r(L− x))
sinh(r L) + c2 sinh(r x)
sinh(r L) (19)
c1= Vbi−ϕss (19.1)
c2= Vds+ Vbi−ϕss (19.2)
r=
√
Cox
εigzoTch
. (19.3)
Here, ϕs(0, x) represents the surface potential at a specific
point along the channel direction of the surface channel layer.
Vbi is the built-in potential between the source-substrate and
drain-substrate junctions. r is the characteristic length, L is the
length of the channel, and x is the distance from the source to
the point where the potential solution is obtained (0≤ x≤ L).
The minimum potential value in the channel layer appears
at x0 and can be determined by solving (dϕ)/(d x)= 0
x0= 1
2r ln
( c1er L− c2
c2− c1e−r L
)
. (20)
By substituting (20) into (19), the minimum potential value
can be obtained as follows:
ϕs(0, x)min=ϕss− c2e−r L+ 2
√
c1c2e
−r L
2 . (21)
The minimum value ϕs(0, x)min increases with the shortening
of the channel length and the increase of the drain voltage.
Vth0 is defined as the threshold voltage that causes ϕs(0, x)min
to equal ϕs(on)(ON state)
ϕon=ϕdep. (22)
In this case, the drift of the threshold voltage is derived
from the following equation [17]:
1Vth0= 3
(
Vbi−ϕdep
)
+ Vds
er L
+
2
√(
Vds+ Vbi−ϕdep
)(
Vbi−ϕdep
)
e
r L
2
. (23)
III. M ODEL VALIDATION
A TCAD simulation framework of IGZO FET has been
developed to validate the proposed compact model [15],
which includes extended states, localized states, and shallow
donors. Fig. 6 shows a good agreement between our compact
model and the TCAD simulation of long-channel IGZO FETs
Authorized licensed use limited to: National Taiwan University. Downloaded on September 17,2026 at 23:24:20 UTC from IEEE Xplore.  Restrictions apply.

## printed page 2395  (PDF page 6)

WANG et al.: PHYSICS-BASED COMPACT MODEL FOR IGZO CHANNEL FET 2395
Fig. 6. Comparison between compact model and TCAD simulation of
long-channel IGZO FET for (a) Id–Vg curves and (b) Id–Vd curves under
different voltage bias.
Fig. 7. Comparison between the compact model and TCAD sim-
ulation for long-channel IGZO FETs in terms of Id–Vg curves, with
variations in (a) gate oxide thickness (T ox= 5, 7, 10, 12, and 15 nm),
(b) channel thickness (T ch = 7, 9, 11, 13, and 15 nm), (c) shallow
donor concentration (N sd= [1.2, 3.3, 5.4, 7.5, 9.6] × 1018 cm−3), and
(d) channel length (L= 10µm, 1 µm, 100 nm, and 40 nm). The inset
shows the extracted SS as a function of VG.
across all operating regions and different voltage bias for
Id–Vg and Id–Vd curves. The proposed compact model can
accurately calculate the ultralow drain current with good SS
and Vth agreement, eliminating the need for an additional drain
off-leakage current model.
Moreover, Fig. 7 presents a comparison between the com-
pact model and the TCAD simulation for variations in gate
oxide thickness ( Tox), channel thickness ( Tch), shallow donor
concentration ( Nsd), and channel length ( L).
The results show good agreement across all the operating
regions for the varied parameters. Increasing the thickness
of the gate oxide layer ( Tox) leads to the decrease in Vth
and Ion, while Ioff increase. This is because the gate control
capability is weakened, as shown in Fig. 7(a). When the
channel thickness ( Tch) increases, Vth decreases because a
thicker channel requires a lower gate voltage to form a
fully depleted region, which results in a higher Ioff as Tch
increases. Meanwhile, Ion increases with Tch in a linear-
like relationship, as thicker channel layers can accommodate
more charges, leading to higher conductance, as shown in
Fig. 7(b). In Fig. 7(c), as Nsd increases, Vth decreases and Ion
increases. In Fig. 7(d), we simulated Id–Vg curves from long
to short channels, and it can be seen that our proposed model
accurately replicates the Id–Vg curves for both short and long
channels. In particularly, the 40 nm short-channel length shows
Fig. 8. Comparison between the compact model and TCAD simulations
for gate charge with L variation (L= 10µm, 1µm, 100 nm, and 40 nm).
The inset shows the extracted gate charge as a function of L at VGB=
−2 V.
Fig. 9. Calibration of the compact model with experimental data at
Vds= 50 mV. The inset shows the SEM image of the fabricated IGZO
FET with a channel length of L= 100 nm.
correct Vth and SS change compared to TCAD simulation. The
inserted graph shows the extracted subthreshold swing, which
demonstrates the good fit between the model and TCAD in
the subthreshold region.
The TCAD and simulated results of Qg against VG with
channel length ( L) variation are illustrated in Fig. 8, with the
inset showing the extracted Qg versus L.
The gate charge ( Qg) of long-channel IGZO FETs remains
almost unchanged at negative VG values, due to the lack of
holes in the depletion region of IGZO channel, which means
that the Qg is primarily determined by the donor concentration.
In contrast, in short-channel IGZO FETs, Qg decreases as
VG decreases, because the electric field from the drain/source
enhances the gate charge ( Qg).
IV. M EMORY SIMULATION
The proposed model is calibrated using experimental data,
as shown in Fig. 9, with the inset displaying the SEM image
of the fabricated IGZO FET. The devices feature an IGZO
film thickness of 10 nm and a ZrO 2 film thickness of 10 nm,
with channel lengths of 1000, 300, and 100 nm.
A good fitting result is achieved for both long- and
short-channel IGZO FETs. The proposed compact model
demonstrates the potential to analyze ultralow drain currents
(<10−19 A/µm), which matches the reported experimental
results for the first time using SPICE [2]. This indicates that
Authorized licensed use limited to: National Taiwan University. Downloaded on September 17,2026 at 23:24:20 UTC from IEEE Xplore.  Restrictions apply.

## printed page 2396  (PDF page 7)

2396 IEEE TRANSACTIONS ON ELECTRON DEVICES, VOL. 72, NO. 5, MAY 2025
Fig. 10. (a) Definition of Ion and Ioff for the IGZO FET. (b) Illustration
of the variation of physical parameter following Gaussian distribution.
(c) Illustration of the operation of the 2T0C cell.
Fig. 11. Extracted Ion and Ioff of a single IGZO FET using Monte Carlo
simulation (400 transistors) in SPICE. The 3σ for Tox, Tch, and Nsd
are (a) 0.25 nm, 0.25 nm, and 0.5 × 1017 cm−3, (b) 0.5 nm, 0.5 nm,
and 0.5× 1017 cm−3, (c) 0.25 nm, 0.25 nm, and 1 × 1017 cm−3, and
(d) 0.5 nm, 0.5 nm, and 1× 1017 cm−3.
the proposed model can be integrated into SPICE due to its
great fit with experimental data.
A. 2T0C DRAM Cell
The memory characteristics of the 2T0C DRAM cell are
studied using the calibrated compact model of the IGZO
FET with L = 100 nm. The channel thickness ( Tch) and
gate oxide thickness ( Tox) are both 10 nm, and the shallow
donor concentration ( Nsd) is 5× 1017 cm−3. Fig. 10(a) shows
the definition of Ion and Ioff for the IGZO FET. Fig. 10(b)
illustrates the Gaussian distribution of Tox, Tch, and Nsd.
Fig. 10(c) depicts the structure and operation of 2T0C DRAM
cell, which consists of an access transistor and a read transistor.
First, the Monte Carlo simulation of a single IGZO FET is
characterized by considering variations in Tox, Tch, and Nsd.
The extracted Ion and Ioff are shown in Fig. 11.
The Monte Carlo simulation results for a single IGZO FET
show an expected Ion and Ioff variation. The reason for the
variation in Tox, Tch, and Nsd and their effects on Ion and
Ioff have been discussed in Section III. When the range of
variation for Tox, Tch, and Nsd is doubled, that is, the variation
range of the channel thickness and the oxide layer thickness
is from 0.25 to 0.5 nm, and the variation range of the donor
Fig. 12. Extracted Iread_max and RT of the 2T0C DRAM cell through
Monte Carlo simulation (400 times) in SPICE. The 3σ value for Tox, Tch,
and Nsd are (a) 0.25 nm, 0.25 nm, and 0.5 × 1017 cm−3, (b) 0.5 nm,
0.5 nm, and 0.5× 1017 cm−3, (c) 0.25 nm, 0.25 nm, and 1× 1017 cm−3,
and (d) 0.5 nm, 0.5 nm, and 1× 1017 cm−3.
state concentration is from 0.5 × 1017 to 1 × 1017 cm−3.
The current changes in variation corresponding to the each
parameter in Fig. 11(d) are10.201× 10−19 A/µm for Ioff and
10.059 A/µm for Ion(Tox variation),10.616× 10−19 A/µm
for Ioff and 10.016 A/µm for Ion(Tch variation), 10.746×
10−19A/µm for Ioff and 10.14 A/µm for Ion(Nsd variation),
respectively. Compared to Nsd, Tox, and Tch have a relatively
minor effect on Ion and Ioff, and the decisive parameter is Nsd.
Next, we evaluate 2T0C cell regarding Tox, Tch, and Nsd
variation. The extracted Iread_max versus retention time (RT) of
the 2T0C cell, obtained through Monte Carlo simulations in
SPICE, is shown in Fig. 12. The RT is defined as the time
during which Iread_max < 10µA. A failed cell is characterized
by RT< 80 s. Since the random variations follow a Gaussian
distribution, the RT is primarily determined by the Iread_max of
the read transistor and Ioff of the access transistor. There are
four possible scenarios: a high Iread_max value coupled with a
low Ioff value, and a low Iread_max value paired with a low
Ioff value, both of which correspond to a high RT value;
conversely, a low Iread_max value combined with a high Ioff
value, and a high Iread_max value coupled with a high Ioff value,
both of which correspond to a low RT value.
In Fig. 12, the parameter changes are similar to those in
Fig. 11, and the design target is set to the default value used in
the Monte Carlo simulation. As the variations in Tox, Tch, and
Nsd increase, both the range of variation for Iread_max and RT
will increase, leading to a higher proportion of failed devices.
However, compared to Tox and Tch, an increased variation in
Nsd has a more significant impact on RT and results in a greater
number of failed devices. The impact on RT is primarily due
to the substantial effect on Ioff, as shown in Fig. 11. The
impact on the proportion of failed devices is attributed to
the simultaneous impact on both Ion and Ioff, which leads to
larger variations in Iread_max for the read transistor and Ioff for
the access transistor, as shown in Fig. 12(c) and (d). This is
consistent with the findings presented in Figs. 7 and 11.
B. IGZO FeFET
The IGZO FeFET compact model is developed by com-
bining ferroelectric layer (FE-layer) compact model [15].
The P–V hysteretic curve of FE-layer is calibrated by
experimental data, as shown in Fig. 13. The calibrated param-
eters demonstrate that the device modeling in this work
Authorized licensed use limited to: National Taiwan University. Downloaded on September 17,2026 at 23:24:20 UTC from IEEE Xplore.  Restrictions apply.

## printed page 2397  (PDF page 8)

WANG et al.: PHYSICS-BASED COMPACT MODEL FOR IGZO CHANNEL FET 2397
Fig. 13. Comparison between the HZO compact model and experimen-
tal data for a thickness of 10 nm.
Fig. 14. Simulated transient Id–Vg curves of the IGZO FeFET compact
model for a long and short channels, with a Vg sweep range of±5 V.
The inset shows the extracted MW as a function of channel length (L).
exhibits comparable ferroelectric characteristics. The inset
image shows the structure of the FeFET.
Fig. 14 shows the simulated Id− Vg curves of the IGZO
FeFET compact model for channel length of L= 30 nm
and 1 µm. The inset shows the extracted MW as a function
of L. A shorter L results in a larger MW, because the electric
field from the source/drain affects the gate charge in vertical
direction as the channel length decreases. This effect increases
the difficulty of polarization reversal, which agrees with the
results shown in Fig. 8. In the case of negative voltage, the
gate of a short-channel transistor accumulates a large amount
of negative charge, whereas for a long-channel, there is almost
no charge.
As a result, an enhanced Qg can switch the polarization of
the FE-layer during the erase operation. The MW increases
exponentially as the channel length decreases.
This is consistent with the results reported in previous
experiments [41], [42]. The relationship between the MW
and the channel length is not only due to the fact that the
back-gate structure provides more fringing fields in short-
channel devices [42], but is also influenced by the impact of
the source-drain electric field in the vertical direction on the
gate charge accumulation in short-channel devices, as shown
in Fig. 8.
The relationship between the MW and the threshold voltage
(Vth) is investigated by considering variations in THZO, Tch,
and Nsd using Monte Carlo simulation in SPICE, as shown in
Fig. 15. Devices are considered to have failed if the MW is
less than 0.51 V .
Unlike the 2T0C cell, the memory performance of the IGZO
FeFET is largely unaffected by Nsd. This is because the polar-
ization state of the FE layer controls the electrical behavior
Fig. 15. Extracted MW and Vth of the IGZO FeFET through Monte Carlo
simulation (400 times) in SPICE. The 3σ values for THZO, Tch, and Nsd
are (a) 0.25 nm, 0.25 nm, and 0.5 × 1017 cm−3, (b) 0.5 nm, 0.5 nm,
and 0.5× 1017 cm−3, (c) 0.25 nm, 0.25 nm, and 1 × 1017 cm−3, and
(d) 0.5 nm, 0.5 nm, 1× 1017 cm−3.
of the channel layer in FeFET, which is closely related to
the electric field. Therefore, Nsd is not a key factor affecting
storage performance. In comparison, THZO significantly affects
the variation of MW and Vth, as its thickness has a significant
impact on the electric field of the FE layer. Variations in
Tch also influence the electrical behavior of the channel, but
the variations in MV and Vth are not as significant. The
results indicate that suppressing variation in THZO is crucial
for controlling memory variation in IGZO FeFET.
The Monte Carlo analysis of the 2T0C DRAM cell and the
IGZO FeFET provides valuable insights into the impact of
variations on device performance during industrial production.
V. C ONCLUSION
A new physics-based compact model of the IGZO FETs,
considering shallow donors, has been successfully developed.
By employing a improved surface potential solution method,
the subthreshold operation of the IGZO FET is accurately
analyzed taking into account physical parameter variations,
ultralow drain current, and enhanced Qg in short channel.
Our work enables the compact model of IGZO transistors to
be more suitable for circuit-level simulations, such as 2T0C
DRAM cell and the IGZO FeFET. This model has been veri-
fied by TCAD simulations and experimental results, showing
good agreement across all operation regions. Most importantly,
for the first time, Monte Carlo simulations of the 2T0C DRAM
cell and the IGZO FeFET, incorporating variations in device
and material properties, have been achieved in SPICE. The
proposed compact model should be useful for the design and
optimization of BEOL monolithic IGZO FET-based memory
circuit.
REFERENCES
[1] K. Nomura, H. Ohta, A. Takagi, T. Kamiya, M. Hirano, and H. Hosono,
“Room-temperature fabrication of transparent flexible thin-film transis-
tors using amorphous oxide semiconductors,” Nature, vol. 432, no. 7016,
pp. 488–492, Nov. 2004, doi: 10.1038/nature03090.
[2] A. Belmonte et al., “Lowest I O F F < 3×10−21 A/µm in capacitor-
less DRAM achieved by reactive ion etch of IGZO-TFT,” in Proc.
IEEE Symp. VLSI Technol. Circuits (VLSI Technol. Circuits) , Kyoto,
Japan, Jun. 2023, pp. 1–2, doi: 10.23919/VLSITECHNOLOGY AND-
CIR57934.2023.10185398.
[3] F. Mo et al., “Low-voltage operating ferroelectric FET with
ultrathin IGZO channel for high-density memory application,”
IEEE J. Electron Devices Soc., vol. 8, pp. 717–723, 2020, doi:
10.1109/JEDS.2020.3008789.
Authorized licensed use limited to: National Taiwan University. Downloaded on September 17,2026 at 23:24:20 UTC from IEEE Xplore.  Restrictions apply.

## printed page 2398  (PDF page 9)

2398 IEEE TRANSACTIONS ON ELECTRON DEVICES, VOL. 72, NO. 5, MAY 2025
[4] W. Lu et al., “First demonstration of dual-gate IGZO 2T0C DRAM
with novel read operation, one bit line in single cell, I O N=1500
µA/µm@VDS =1 V and retention time>300s,” in IEDM Tech. Dig.,
San Francisco, CA, USA, Dec. 2022, pp. 26.4.1–26.4.4, doi:
10.1109/IEDM45625.2022.10019488.
[5] Z. Liang et al., “A novel high-endurance FeFET memory device
based on ZrO 2 anti-ferroelectric and IGZO channel,” in IEDM Tech.
Dig., San Francisco, CA, USA, Dec. 2021, pp. 17.3.1–17.3.4, doi:
10.1109/IEDM19574.2021.9720627.
[6] J. Guo et al., “A new surface potential and physics based compact model
for a-IGZO TFTs at multinanoscale for high retention and low-power
DRAM application,” in IEDM Tech. Dig., San Francisco, CA, USA,
Dec. 2021, pp. 8.5.1–8.5.4, doi: 10.1109/IEDM19574.2021.9720700.
[7] M. Ghittorelli, Z. M. Kovács-Vajna, and F. Torricelli, “Physical-based
analytical model of amorphous InGaZnO TFTs including deep, tail,
and free states,” IEEE Trans. Electron Devices, vol. 64, no. 11,
pp. 4510–4517, Nov. 2017, doi: 10.1109/TED.2017.2755098.
[8] M. Nakashima et al., “Origin of major donor states in In–Ga–Zn oxide,”
J. Appl. Phys., vol. 116, no. 21, Dec. 2014, Art. no. 213703, doi:
10.1063/1.4902859.
[9] T. Kamiya, K. Nomura, and H. Hosono, “Origins of high mobility and
low operation voltage of amorphous oxide TFTs: Electronic structure,
electron transport, defects and doping,” J. Display Technol., vol. 5, no. 7,
pp. 273–288, Jul. 2009.
[10] L. Colalongo, “A new analytical model for amorphous-silicon thin-film
transistors including tail and deep states,” Solid-State Electron., vol. 45,
no. 9, pp. 1525–1530, Sep. 2001, doi: 10.1016/s0038-1101(01)00183-6.
[11] Y . Hernández-Barrios, A. Cerdeira, M. Estrada, and B. Iñíguez, “Analyti-
cal current–voltage model for double-gate a-IGZO TFTs with symmetric
structure for above threshold,” IEEE Trans. Electron Devices, vol. 67,
no. 5, pp. 1980–1986, May 2020, doi: 10.1109/TED.2020.2983380.
[12] Y . Zhao et al., “Fundamental understanding of NBTI degradation
mechanism in IGZO channel devices,” in Proc. IEEE Int. Rel.
Phys. Symp. (IRPS), Grapevine, TX, USA, Apr. 2024, pp. 1–7, doi:
10.1109/irps48228.2024.10529352.
[13] G. Yan et al., “First demonstration of true 4-bit memory with
record high multibit retention >10 3s and read window >10 5 by
hydrogen self-adaptive-doping for IGZO DRAM arrays,” in IEDM
Tech. Dig., San Francisco, CA, USA, Dec. 2023, pp. 1–4, doi:
10.1109/iedm45741.2023.10413762.
[14] G. Paasch and S. Scheinert, “Charge carrier density of organics
with Gaussian density of states: Analytical approximation for the
Gauss–Fermi integral,” J. Appl. Phys., vol. 107, no. 10, May 2010,
Art. no. 104501, doi: 10.1063/1.3374475.
[15] S. Kumar, O. Prakash, Y . S. Chauhan, and H. Amrouch, “BEOL FeFET
SPICE-compatible model for benchmarking 3-D monolithic in-memory
TCAM computation,” IEEE Trans. Electron Devices, vol. 70, no. 12,
pp. 6286–6292, Dec. 2023, doi: 10.1109/TED.2023.3327034.
[16] B. Jiang, “Computationally efficient ferroelectric capacitor model for cir-
cuit simulation,” in Proc. Symp. VLSI Technol., Jun. 1997, pp. 141–142,
doi: 10.1109/VLSIT.1997.623738.
[17] Z.-H. Liu et al., “Threshold voltage model for deep-submicrometer
MOSFETs,” IEEE Trans. Electron Devices, vol. 40, no. 1, pp. 86–95,
Jan. 1993, doi: 10.1109/16.249429.
[18] J.-H. Park, Y . Kim, S. Kim, H. Bae, D. H. Kim, and D. M. Kim,
“Surface-potential-based analytic DC I –V model with effective electron
density for a-IGZO TFTs considering the parasitic resistance,” IEEE
Electron Device Lett., vol. 32, no. 11, pp. 1540–1542, Nov. 2011, doi:
10.1109/LED.2011.2163810.
[19] M. Ghittorelli, F. Torricelli, and Z. M. Kovács-Vajna, “Physical modeling
of amorphous InGaZnO thin-film transistors: The role of degenerate con-
duction,” IEEE Trans. Electron Devices, vol. 63, no. 6, pp. 2417–2423,
Jun. 2016, doi: 10.1109/TED.2016.2553963.
[20] M. Bae, Y . Kim, S. Kim, D. M. Kim, and D. H. Kim, “Extraction
of subgap donor states in a-IGZO TFTs by generation–recombination
current spectroscopy,” IEEE Electron Device Lett., vol. 32, no. 9,
pp. 1248–1250, Sep. 2011, doi: 10.1109/LED.2011.2160835.
[21] M. Bae et al., “Analytical models for drain current and gate capaci-
tance in amorphous InGaZnO thin-film transistors with effective carrier
density,” IEEE Electron Device Lett., vol. 32, no. 11, pp. 1546–1548,
Nov. 2011, doi: 10.1109/LED.2011.2164229.
[22] Z. Zong, L. Li, J. Jang, N. Lu, and M. Liu, “Analytical surface-
potential compact model for amorphous-IGZO thin-film transistors,”
J. Appl. Phys., vol. 117, no. 21, Jun. 2015, Art. no. 215705, doi:
10.1063/1.4922181.
[23] M. C. J. M. Vissenberg and M. Matters, “Theory of the field-effect
mobility in amorphous organic transistors,” Phys. Rev. B, Condens.
Matter, vol. 57, no. 20, pp. 12964–12967, May 1998, doi: 10.1103/phys-
revb.57.12964.
[24] W. D. Edward, “Charge based modeling of capacitance in MOS transis-
tor,” Ph.D. dissertation, Dept. Elect. Eng., Standford Univ., Standford,
CA, USA, 1981.
[25] K. Lee, J. Bae, S. Kim, J. Lee, B. Park, and D. Kwon, “Ferroelectric-gate
field-effect transistor memory with recessed channel,” IEEE Elec-
tron Device Lett., vol. 41, no. 8, pp. 1201–1204, Aug. 2020, doi:
10.1109/LED.2020.3001129.
[26] K. Toprasertpong, M. Takenaka, and S. Takagi, “Memory window in
ferroelectric field-effect transistors: Analytical approach,” IEEE Trans.
Electron Devices, vol. 69, no. 12, pp. 7113–7119, Dec. 2022, doi:
10.1109/TED.2022.3215667.
[27] D. E. Ward and R. W. Dutton, “A charge-oriented model for MOS
transistor capacitances,” IEEE J. Solid-State Circuits, vol. SSC-13, no. 5,
pp. 703–708, Oct. 1978, doi: 10.1109/JSSC.1978.1051123.
[28] J. Park et al., “Floating body effect in indium–gallium–zinc–oxide
(IGZO) thin-film transistor (TFT),” Sci. Rep., vol. 14, no. 1, p. 10067,
May 2024, doi: 10.1038/s41598-024-60288-z.
[29] Z. Zong et al., “A new surface potential-based compact model
for a-IGZO TFTs in RFID applications,” in IEDM Tech. Dig.,
San Francisco, CA, USA, Dec. 2014, pp. 35.5.1–35.5.4, doi:
10.1109/IEDM.2014.7047176.
[30] M. J. Kim, H. J. Park, S. Yoo, M. H. Cho, and J. K. Jeong, “Effect
of channel thickness on performance of ultra-thin body IGZO field-
effect transistors,” IEEE Trans. Electron Devices, vol. 69, no. 5,
pp. 2409–2416, May 2022, doi: 10.1109/TED.2022.3156961.
[31] G. Pahwa, S. Salahuddin, and C. Hu, “An all-region BSIM thin-film
transistor model for display and BEOL 3-D integration applications,”
IEEE Trans. Electron Devices, vol. 71, no. 8, pp. 4701–4709, Aug. 2024,
doi: 10.1109/TED.2024.3416083.
[32] L. Xu et al., “A surface potential based compact model for ferroelectric
a-InGaZnO-TFTs toward temperature dependent device characteriza-
tion,” IEEE Electron Device Lett., vol. 44, no. 3, pp. 412–415,
Mar. 2023, doi: 10.1109/LED.2022.3233824.
[33] L. Li, G. Meller, and H. Kosina, “Transport energy in organic
semiconductors with partially filled localized states,” Appl. Phys.
Lett., vol. 92, no. 1, Jan. 2008, Art. no. 013307, doi: 10.1063/
1.2829863.
[34] J. F. Wager, D. A. Keszler, and R. E. Presley, “Materials,” in Transparent
Electronics Boston, MA, USA: Springer, 2008, doi: 10.1007/978-0-387-
72342-6_4.
[35] R. L. Weiher, “Electrical properties of single crystals of indium
oxide,” J. Appl. Phys. , vol. 33, no. 9, pp. 2834–2839, Sep. 1962, doi:
10.1063/1.1702560.
[36] S. B. Zhang, S.-H. Wei, and A. Zunger, “Intrinsicn-type versusp-
type doping asymmetry and the defect physics of ZnO,” Phys. Rev.
B, Condens. Matter, vol. 63, no. 7, Jan. 2001, Art. no. 075205, doi:
10.1103/physrevb.63.075205.
[37] S. A. Studenikin, N. Golego, and M. Cocivera, “Optical and electrical
properties of undoped ZnO films grown by spray pyrolysis of zinc nitrate
solution,” J. Appl. Phys., vol. 83, no. 4, pp. 2104–2111, Feb. 1998, doi:
10.1063/1.366944.
[38] Y . Nam et al., “Beneficial effect of hydrogen in aluminum oxide
deposited through the atomic layer deposition method on the elec-
trical properties of an indium–gallium–zinc oxide thin-film transis-
tor,” J. Inf. Display, vol. 17, no. 2, pp. 65–71, Apr. 2016, doi:
10.1080/15980316.2016.1160003.
[39] S. M. Sze, Physics of Semiconductor Devices, 3rd ed., New York, NY ,
USA: Wiley, 2007.
[40] G. Paasch and S. Scheinert, “Space charge layers in organic field-
effect transistors with Gaussian or exponential semiconductor density
of states,” J. Appl. Phys., vol. 101, no. 2, Jan. 2007, Art. no. 024514,
doi: 10.1063/1.2424397.
[41] Z. Lin et al., “High-peformance BEOL-compatible atomic-layer-
deposited In 2O3 Fe-FETs enabled by channel length scaling down
to 7 nm: Achieving performance enhancement with large memory
window of 2.2 V , long retention > 10 years and high endurance >
108 cycles,” in IEDM Tech. Dig., San Francisco, CA, USA, Dec. 2021,
pp. 17.4.1–17.4.4, doi: 10.1109/IEDM19574.2021.9720652.
[42] A. A. Sharma et al., “High speed memory operation in channel-
last, back-gated ferroelectric transistors,” in IEDM Tech. Dig.,
Dec. 2020, pp. 18.5.1–18.5.4, doi: 10.1109/IEDM13553.2020.
9371940.
Authorized licensed use limited to: National Taiwan University. Downloaded on September 17,2026 at 23:24:20 UTC from IEEE Xplore.  Restrictions apply.
