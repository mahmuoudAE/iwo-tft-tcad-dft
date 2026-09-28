# Pandey2025 (source file Pandey2025_TED_SCE_TFT.txt); headings give PRINTED page = cite as p.~<printed>

## printed page 1  (PDF page 1)

IEEE TRANSACTIONS ON ELECTRON DEVICES 1
Analytical Modeling of Short-Channel Effects
in BEOL-Compatible Thin-Film Transistors
Nilesh Pandey
 , Member, IEEE, Ujwal Radhakrishna
 , Senior Member, IEEE,
Jian-Yu Lin
 , Graduate Student Member, IEEE, Chang Niu, Member, IEEE,
Orlando Lazaro
 , Member, IEEE, Gianluca Boselli
 , Senior Member, IEEE,
Luigi Colombo, Fellow, IEEE, Baher Haroun, Life Fellow, IEEE, Peide D. Y e
 , Fellow, IEEE,
Leonard F . Register
 , Life Fellow, IEEE, and Sanjay K. Banerjee, Life Fellow, IEEE
Abstract— This article presents a 2-D analytical model
for the potential and current characteristics of thin-film
transistors (TFTs) using Green’s function approach. The
model accurately incorporates the effects of nonuniform
trap charge distribution in the channel and includes
both top and bottom gate oxide regions with different
thicknesses. Solving 2-D Poisson’s equation, we derive
closed-form 2-D expressions for the potential profile in the
channel. While the model applies to any thin-film tech-
nologies such as indium oxide (In 2O3), indium gallium
zinc oxide (IGZO), graphene, carbon nanotubes (CNTs),
etc., in this work, the model is validated using experi-
mental data and TCAD Sentaurus simulations for In 2O3
TFTs. Key results include analysis of short-channel effects
(SCEs), gate oxide scaling, and channel thickness vari-
ations on device performance. The model successfully
predicts subthreshold characteristics and drain-induced
barrier-lowering (DIBL) while identifying the limitations in
the ON current region due to the absence of various scatter-
ing phenomena, such as surface scattering in the analytical
formulation. An improved mobility model, accounting for
field dependence, enhances the accuracy in the ON region,
ensuring agreement with experimental and TCAD data
across various bias conditions.
Index Terms — Green’s function approach, indium oxide
(In2O3), thin-film transistors (TFTs).
I. I NTRODUCTION
T
HIN-FILM transistors (TFTs) were first reported
in 1962 [1]. Subsequently, TFTs demonstrated remark-
able applications in liquid-crystal displays [2], transpar-
ent indium gallium zinc oxide (IGZO) [3], and flexible
Received 4 December 2024; revised 2 February 2025; accepted
25 February 2025. This work was supported in part by NSF
National Nanotechnology Coordinated Infrastructure (NNCI) under
Grant ECCS2025227. The review of this article was arranged by Editor
B. Iñiguez. (Corresponding author: Nilesh Pandey.)
Nilesh Pandey, Leonard F . Register, and Sanjay K. Banerjee
are with the Microelectronics Research Center, The University of
Texas at Austin, Austin, TX 78703 USA (e-mail: pandey@utexas.edu;
register@austin.utexas.edu; banerjee@ece.utexas.edu).
Ujwal Radhakrishna, Orlando Lazaro, Gianluca Boselli,
Luigi Colombo, and Baher Haroun are with Kilby Labs Texas
Instruments Inc., Dallas, TX 75243 USA.
Jian-Yu Lin, Chang Niu, and Peide D. Y e are with the School of Elec-
trical and Computer Engineering, Purdue University, West Lafayette,
IN 47907 USA.
Digital Object Identifier 10.1109/TED.2025.3546593
electronics [4], [5]. Recently, indium oxide (In 2O3)-based
TFTs have been extensively studied for back-end-of-line
(BEOL) semiconductor manufacturing processes due to their
compatibility with the atomic-layer-deposition (ALD) process,
low thermal budget, and an expectantly high ON/OFF current
ratio [6], [7], [8].
Chakraborty et al. [6] demonstrated the W-doped In 2O3
FET with ION ∼ 370 µA/µm, and ION/IOFF > 109. The
ALD process has recently been used to fabricate TFTs with
channel thickness≤ 1 nm [7]. Exceptionally high ON current
> 1 mA/µm and mobility> 80 cm2/V·s are observed in ALD-
grown TFTs [9], [10]. Furthermore, monolithic 3-D integration
of In 2O3 FETs is reported in [8] and [11].
The charge neutrality level (CNL) in intrinsic (In 2O3)
resides well above the conduction band edge ( Ec) [12], [13].
Consequently, the Fermi level shifts toward the conduc-
tion band maximum, yielding a high electron density
(1019–1020 cm−3) even at zero bias [12], [14]. Oxygen vacan-
cies act as shallow donors, making the channel inherently
n-type. Since the trap density ( Nt) is directly linked to the
electron density, Nt at equilibrium matches the carrier concen-
tration. An increase in Nt effectively enhances n-type doping,
reducing the barrier height. In contrast, in conventional n-p-n
MOSFETs, higher channel doping raises the barrier height.
From a modeling perspective, the initial focus was on the
amorphous silicon FET: A current–voltage and mobility model
is presented by Shur et al. [15], and a SPICE-compatible
circuit model in [16] and [17]. Recently, there have been
reports on IGZO modeling aspects, such as current–voltage
modeling above the threshold region in [18], 1-D surface
potential modeling [19], [20], a drain current model including
trap impact on [21], and a 1-D berkeley short-channel IGFET
model (BSIM)-based TFT model in [22].
These modeling approaches can be broadly divided into two
categories.
1) Surface-potential-based modeling, which considers
1-D Poisson’s equation, incorporating only the
gate-directional electric field into the surface potential
modeling [17], [18], [19], [20]. The conformal mapping
approach to obtain potential distribution is used in [23],
and charge-based modeling is reported in [24].
1557-9646 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination. 
Authorized licensed use limited to: Purdue University. Downloaded on March 13,2025 at 20:21:30 UTC from IEEE Xplore.  Restrictions apply.

## printed page 2  (PDF page 2)

2 IEEE TRANSACTIONS ON ELECTRON DEVICES
2) SPICE-compatible circuit modeling based on 1-D Pois-
son’s equation [16], [17], [22].
However, none of these models incorporates 2-D Poisson’
equation to obtain the potential distribution in the channel,
which has a 2-D spatial dependence (x, y). Solving 2-D
Poisson’s equation is necessary to accurately capture the
impact of oxide/channel scaling on threshold voltage roll-off
and drain-induced barrier-lowering (DIBL) [25], [26], [27],
[28], [29]. Furthermore, 1-D Poisson’s equation only considers
the gate-directed electric field (in the y-direction), neglect-
ing the drain-to-source electric field, which means it cannot
capture short-channel effects (SCEs) [25], [27]. Solution to
2-D Poisson’s equation is required to predict threshold voltage
roll-off, subthreshold slope degradation, and DIBL, which are
crucial for studying device (technology) scaling analysis.
Therefore, this work focuses on the 2-D analytical modeling
of TFTs, including the impact of the gate and drain electric
fields in deriving the 2-D channel potential. The derived model
can predict the impact of scaling of physical parameters such
as oxide thickness, channel thickness, and channel length on
the device’s SCEs and DIBL.
Fundamentally, there are two analytical approaches avail-
able in the literature to solve 2-D Poisson’s equations:
1) scale-length modeling [25] and 2) Green’s function
approach [26]. Both the models are consistent with TCAD.
However, the scale-length model cannot handle a nonuniform
doping profile in the channel [26]. On the other hand, the
scale-length model requires fewer terms than Green’s function
approach. Since TFTs have trap charges in the channel, which
possess a 2-D spatial distribution, this work adapts Green’s
function approach to model the SCEs in TFTs [26].
The 2-D analytical model provides deeper insights into
device physics, as the potential equation directly reveals
first-order approximations of how physical parameter scaling
impacts the electrostatic barrier. In addition, we simplify the
analytical model into a unified potential equation (54). The
surface potential at the mid-channel can be obtained by setting
x = L/2 and y = tox1, which serves as a foundation for
circuit-level or SPICE-level modeling. A key advantage of the
analytical model over TCAD simulations is its computational
efficiency. It generates Id–Vg curves within seconds, whereas
TCAD simulations can take significantly longer depending on
the setup. Furthermore, the analytical model always converges
due to its compact formulation, whereas TCAD simulations
can face convergence challenges.
II. T RAP PROFILE MODELING
Fig. 1 shows the schematic of the double-gate thin film
transistor considered in this work with different top and bottom
gate oxide thicknesses. The 2-D trap distribution can be
analytically modeled as
ρ(x, y)= f(x) f(y). (1)
The In 2O3 material exhibits bulk trap density [12], [13],
leading to f(y) = q Nt/ϵ, where q, Nt, and ϵ are the
electron charge, peak value of trap concentration (constant),
and channel permittivity, respectively.
The function f(x) includes the variation in the trap distri-
bution along the x-direction [source to drain direction (S-D)].
Fig. 1. Schematic of In 2O3 TFT. Default parameters: Channel thickness
(tch = 1 nm), back-gate oxide thickness ( tox2 = 5 nm), front-gate
oxide thickness (tox1= 4 nm), channel length (L = 40 nm), drain bias
(Vds= 0.5 V), top gate voltage (V gs1 = 0 V), SiO 2 relative permittiv-
ity= 3.9, and HfO2 relative permittivity= 15.
Fig. 2. Comparison between approximated and Gaussian trap profile in
the channel. Default parameters: λ= 8 nm, W0= 4 nm, and peak trap
density= 1× 1020 cm−3.
In general, for numerical modeling purposes, it is reasonable
to assume the Gaussian trap distribution [29], [30], [31].
Furthermore, the model validation section shows that assuming
Gaussian trap distribution leads to model consistency with the
experimental and TCAD data. However, an exact Gaussian
function will not produce analytical solutions for 2-D Pois-
son’s equation. Since this work aims to derive an analytical
model, it is imperative to approximate the Gaussian distribu-
tion in a closed-form equation. Fig. 2 shows comparison of the
approximated function f(x) and the exact Gaussian function.
The function f(x) is defined in the Fourier series form
f(x)= a0
2+
∑
j
A j cos
(
k j x
)
. (2)
Note that there will not be sine terms in (2) due to the even
symmetry of the function f(x). Here, a0 is the zero-order
Fourier series coefficient, TD is the period, and A j is the jth
series coefficient, calculated below
a0= 2
TD
∫
TD
f(x) d x =
( 2
TD
)
(λ+ W0) (3)
A j= 2
TD
∫
TD
cos
(
k j x
)
f(x) d x
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination. 
Authorized licensed use limited to: Purdue University. Downloaded on March 13,2025 at 20:21:30 UTC from IEEE Xplore.  Restrictions apply.

## printed page 3  (PDF page 3)

PANDEY et al.: ANAL YTICAL MODELING OF SHORT -CHANNEL EFFECTS IN BEOL-COMPATIBLE TFTs 3
= 1
λ
(
cos
(
k j xb
)
− cos
(
k j xa
)
k2
j
+ λ sin
(
k j xb
)
k j
)
+ 1
λ
(
cos
(
k j xc
)
− cos
(
k j xd
)
k2
j
− sin
(
k j xc
)
k j
)
+ sin
(
k j xc
)
− sin
(
k j xb
)
k j
(4)
xa= L/2− W0/2− λ; xb= L/2− W0/2; (5)
xc= L/2+ W0/2; xd= L/2+ W0/2+ λ
TD= 2λ+ W0+ k0 L; k j= 2π j
TD
(6)
where k0 > 1 ensures that the function f(x) does not repeat
in the channel twice, signifying a correct distribution function
(see Fig. 2).
III. 2-D A NALYTICAL POTENTIAL PROFILE MODELING
The 2-D Poisson’s equation in the oxide and channel regions
can be expressed as
∂2φox
1 (x, y)
∂ x 2 +∂2φox
1
∂ y2 = 0
[
Top oxide
]
(7)
∂2φ(x, y)
∂ x 2 +∂2φ(x, y)
∂ y2 =ρ(x, y) [Channel] (8)
∂2φox
2 (x, y)
∂ x 2 +∂2φox
2
∂ y2 = 0 [Bottom oxide]. (9)
We consider a generic device with different top and gate
oxide thicknesses as tox1 and tox2, respectively, as well as
materials with different permittivities. The model will also
apply to symmetric cases by replacing tox1= tox2= tox.
Green’s identity is a well-established method for obtaining
analytical closed-form solutions to electrostatics boundary-
value problems, which can handle nonuniform charge distribu-
tion in 2-D Poisson’s equation [26], [32]. In a bounded region,
Green’s identity is expressed as
φ(x, y)=
∫ ∫(
ρ
(
x′, y′)
ϵ
)
G
(
x, y; x′, y′)
d x′d y′
+
∮
l
{
G
(
x, y; x′, y′)∂φ
∂n′−φ∂G
(
x, y; x′, y′)
∂n′
}
dl′.
(10)
The first step is to derive Green’s functions[G(x, y; x′, y′)]
for the various regions using the Dirichlet and Neumann
boundary conditions. A detailed methodology for calculating
Green’s functions is provided in our earlier work [33]. The fol-
lowing potential profiles are obtained by substituting Green’s
functions into Green’s identity.
A. Channel Region
The impact of trap charge distribution on the potential
profile is primarily included in the first term of(10). For n̸= 0,
substituting the channel region Green’s function (60) into (10)
results in a zero value due to the cosine integration term
∫tox1+tch
tox1
cos
[
nπ
(
tox1+ tch− y′)
tch
]
d y′= 0.
Green’s function for the n= 0 term is calculated as
G I I
y
(
x, y; x′, y′)
n=0= 1
tch L
{(
L− x′)
x 0< x < x′
x′(L− x) x′< x < L
}
. (11)
Using (11) in (10), we derive the following potential profile:
φtrap(x)= Nt(L− x)
∫x′
0
x′ f
(
x′)
d x′
+ Nt x
∫L
x′
(
L− x′)
f
(
x′)
d x′. (12)
Substituting f(x) from (2) into (12) and simplifying
φtrap(x)
= 2
TD
(q Nt
ϵ L
) a0
4 L x(L−x)
+ 2
TD
(q Nt
ϵ L
)


∑
j
A j
(
L cos
(
k j x
)
−x cos
(
k j L
)
+x− L
)
k2
j


.
(13)
Top gate oxide and bottom gate oxide interfaces exhibit
the Neumann boundary conditions. Hence, the second term
from (10) derives the following potential function at the top
and bottom interfaces:
φT,B(x, y)=
∮
l
G
(
x, y; x′, y′)∂φ
∂n′ dl′. (14)
Plugging Green’s function (59) into the above equation
φT,B(x, y)= 2
L
∑
m
sin(km x)
kmϵ sinh(kmtch)
×
{
Dsf cosh(km(tox1+ tch− y))− Dsb cosh(km(tox1− y))
}
(15)
where km= mπ/ L, Dsf, and Dsb are the Fourier coefficients
for the top and bottom interfaces, respectively, defined as
Dsf=−ϵ
∫L
0
sin
(
km x′)∂φ
∂ y′ d x′ at y= tox1 (16)
Dsb=−ϵ
∫L
0
sin
(
km x′)∂φ
∂ y′ d x′ at y= tox1+ tch. (17)
The left and right boundary interfaces, x= 0 and x= L,
exhibit the Dirichlet boundary conditions, leading to the fol-
lowing potential profile:
φ L,R(x, y)=−
∮
l
φ(x, y)∂G
(
x, y; x′, y′)
∂n′ dl′. (18)
Using Green’s function (60) in the above equation
φ L,R(x, y)= 2
tch
∑
n
cos
(
kII
n(tox1+ tch− y)
)
sinh
(
kIIn L
)
×
(
Bn
s sinh
(
kII
n(L− x)
)
+ Bn
d sinh
(
kII
n x
))
.
(19)
Here, kII
n = nπ/t ch, Bns, and Bn
2 are the left and right
boundaries’ Fourier series coefficients. All the necessary series
coefficients are derived in Section IV. The net potential
equation in the channel is followed as:
φch(x, y)=φtrap(x)+φT,B(x, y)+φ L,R(x, y). (20)
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination. 
Authorized licensed use limited to: Purdue University. Downloaded on March 13,2025 at 20:21:30 UTC from IEEE Xplore.  Restrictions apply.

## printed page 4  (PDF page 4)

4 IEEE TRANSACTIONS ON ELECTRON DEVICES
B. T op Gate Oxide Region
Oxide regions do not have any free charge. Hence,
ρ( x, y)= 0. Due to the known applied voltage Vgs1, the top
interface is at the Dirichlet boundary condition. Plugging (58)
into Green’s identity and simplifying
φT
ox1(x, y)
=
∫L
0
φT
ox1(x, y)
(
x′, 0
)(∂GI
x
∂ y′
)
y>y′
d x′
= 2
L
∑
m
sin(km x) cosh
(
km
(
tox1− y
))
V1
(
1+(−1)m+1)
km cos
(
kmtox1
) .
(21)
Here, V1= Vgs1− Vfb, and Vfb is the flat band voltage.
The interface along the oxide/channel (or bottom interface
of the top gate oxide region) uses the Neumann boundary
condition, using GI
x into (10) with y= tox1
φ B
ox1(x, y)=
∮
l
G
(
x, y; x′, y′)∂φ
∂ y′ d x′
φ B
ox1(x, y)=− 2
L
∑
m
sin(km x) sinh(km y)Dsf
kmϵox1 cosh
(
kmtox1
) . (22)
The left and right interfaces are at the Dirichlet boundary
conditions since these gap potentials can be approximated as
the linear profile [26]. Using (57) in (10), and simplifying
φ L,R
ox1 (x, y)= 2
tox1
∑
n
sin
(
kI
n y
)
sinh
(
kIn L
)
×
(
An
s sinh
(
kI
n(L− x)
)
+ An
d· sinh
(
kI
n x
))
(23)
where, kI
n=(2n− 1)π/t ox1.
C. Bottom Gate Oxide Region
Since the top and bottom gate oxide thicknesses are differ-
ent, leading to Dsf̸=− Dsb, we follow a similar approach used
for the top gate oxide region to derive the potential function
of the bottom gate oxide region:
φox2(x, y)
= 2
L
∑
m
sin(km x)Dsb sinh(km(t0− y))
ϵox2 km cos
(
kmtox2
)
+ 2
L
∑
m
sin(km x) cosh(km(t1− y))V2
(
1+(−1)m+1)
km cos
(
kmtox2
)
+ 2
tox2
∑
n
sin
(
kIII
n (t0− y)
)
sinh
(
kIIIn L
)
×
(
C n
s sinh
(
kIII
n (L− x)
)
+ C n
d sinh
(
kIII
n x
))
(24)
where, t0= tox1+ tch+ tox2, and kIII
n = (2n−1)π
tox2
.
IV. F OURIER SERIES COEFFICIENTS CALCULATION
The coefficients Dsf and Dsb are defined such that electric
displacement continuity is maintained at the oxide/channel
interface [26]. The next step is to ensure potential continuity
at the interfaces, after which Dsf and Dsb are determined using
standard Fourier series coefficient calculations [26]
∫L
0
φox1
(
x, tox1
)
sin(km x)d x=
∫L
0
φch
(
x, tox1
)
sin(km x)d x
(25)
∫L
0
φch(x, t1) sin(km x)d x=
∫L
0
φox1(x, t1) sin(km x)d x
(26)
where, t1= tox1+ tch, and t2= t1+ tox2. Solving the above
two equations for Dsf and Dsb
Dsf= dλd m
0− dγ d m
1
(
d m
0
)2
− d m
2 d m
1
(27)
Dsb= dλd m
2− dγ d m
0
(
d m
0
)2
− d m
2 d m
1
(28)
dγ= d m
3+ d m,n
4 − d m,n
5 − dtrap (29)
dλ= d m,n
6 + d m,n
7 + d m
8− dtrap (30)
dtrap= 2
TD
(q Nt
ϵ L
)∑
j
A j
k2
j
(
d m, j
a + d m, j
b
)
(31)
d m, j
a = L
(
1+(−1)m+1 cos
(
k j L
))
(
km
k2m− k2
j
− 1
km
)
(32)
d m, j
b = (λ+ W0)L
(
1+(−1)m+1)
4 (33)
d m
0 = 1
ϵkm sinh(kmtch) (34)
d m
1 = 1
ϵkm tanh(kmtch)+ tanh
(
kmtox2
)
kmϵox2
(35)
d m
2 = 1
ϵkm tanh(kmtch)+ tanh
(
kmtox1
)
kmϵox1
(36)
d m
3 = V1
(
1+(−1)m+1)
km cosh
(
kmtox1
) (37)
d m,n
4 = 2
tox1
∑
n
sin
(
kI
ntox1
)
km
(
An
s+ An
d(−1)m+1)
k2m+
(
kIn
)2 (38)
d m,n
5 = 2
tch
∑
n
cos
(
kII
n tch
)
km
(
Bn
s+ Bn
d(−1)m+1)
k2m+
(
kIIn
)2 (39)
d m,n
6 = 2
tox2
∑
n
sin
(
kIII
n tox2
)
km
(
C n
s+ C n
d(−1)m+1)
k2m+
(
kIIIn
)2 (40)
d m,n
7 = 2
tch
∑
n
(
Bn
s+ Bn
d(−1)m+1)
km
k2m+
(
kIIn
)2 (41)
d m
8 = V2
(
1+(−1)m+1)
km cosh
(
kmtox2
). (42)
The boundary gaps ( x = 0/L) Fourier coefficients are
calculated by assuming a linear potential profile, a valid
approximation consistent with the TCAD [26]. Along line
x= 0, the following linear potential profiles can be written in
the various regions:
φox1
(
0, y′)
= c1 y′+ c2; φch
(
0, y′)
= c3 y′+ c4
φox2
(
0, y′)
= c5 y′+ c6 (43)
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination. 
Authorized licensed use limited to: Purdue University. Downloaded on March 13,2025 at 20:21:30 UTC from IEEE Xplore.  Restrictions apply.

## printed page 5  (PDF page 5)

PANDEY et al.: ANAL YTICAL MODELING OF SHORT -CHANNEL EFFECTS IN BEOL-COMPATIBLE TFTs 5
where c1, c2, c3, c4, c5, and c6 are the constants calculated by
the boundary conditions
φox1(0, 0)= V1 (44)
φox1
(
0, tox1
)
=φch
(
0, tox1
)
(45)
φfe
(
0, tox1+ tch
)
=φox2
(
0, tox1+ tch
)
(46)
φox2
(
0, tox1+ tch
)
= V2 (47)
−ϵ(c3)+σ
(
0, tox1
)
=−ϵ ox1(c1) (48)
−ϵ(c3)+σ
(
0, tox1+ tch
)
=−ϵ ox2(c5). (49)
σ(0, tox1) = σ(0, tox1+ tch) = Nt× (tch) is the surface
trap concentration. Subsequently, the series coefficients are
calculated as
As
n=
∫tox1
0
φox1
(
0, y′)
sin
(
kI
n y′)
d y′
= V1
kIn
+ c1
sin
(
kI
ntox1
)
(
kIn
)2 (50)
Bs
n=
∫t1
tox1
φch
(
0, y′)
cos
(
kII
n
(
t1− y′))
d y′
= c3
1+(−1)n+1
(
kIIn
)2 (51)
C s
n=
∫t2
t1
φox2
(
0, y′)
sin
(
kIII
n y′)
d y′
= c5
(
tox2
kIIIn
+(−1)n
(
kIIIn
)2
)
+ c6
kIIIn
(52)
where t1= tox1+ tch and t2= tox1+ tch+ tox2.
V. S IMPLIFIED CHANNEL POTENTIAL MODEL
The analytical model is derived for a double-gate (DG)
TFT where the body is not grounded. Therefore, the elec-
trostatic boundary conditions closely resemble those of
silicon-based DG-MOSFET [26]. Hence, the channel’s gap
potential can be approximated similar to the reports for DG-
MOSFET [26], [27] as
φch(0, y)= Eg
2q, and φch(L, y)= Eg
2q+ Vds. (53)
The above approximation significantly simplifies the mathe-
matics by forcing
d m,n
5 = d m,n
7 = 0.
The channel potential is expressed as
φch(x, y)= Eg
2q+ x
L Vds+φT,B(x, y)+φtrap(x). (54)
Fig. 3 shows a comparison between the exact potential
model (20) and the approximate model (54). The approximate
channel potential model accurately captures the barrier height,
which is the primary factor in the subthreshold region.
Furthermore, the calculation of boundary gaps Fourier coef-
ficients is also simplified: for As
n, Bs
n, and C s
n,φch(0, y′)= Eg
2q ,
and for Ad
n, Bd
n , and C d
n ,φch(L, y′)= Eg
2q+ Vds is used.
Fig. 3. Comparison between exact potential model [see 20] and
approximate potential model [see 54]. Even with the approximation,
maximum barrier height is predicted correctly, leading to a correct
prediction in the OFF current.
VI. M ODEL VALIDATION
A. Constant Mobility Drain Current Model
The current equation in the channel is derived by following
the current continuity equation [26]:
Ids= qµW Vt ni(1− exp(−Vds/Vt))
∫L
0
d x∫tox1+tch
tox1 exp(φch(x,y)/Vt) d y
(55)
where q is the electron charge, µ is the constant mobility =
9 cm 2/V-s, W is the device width = 1 µm, Vt is the thermal
voltage, and Vds is the drain bias. The intrinsic charge density
ni= 5× 1019 cm−3, consistent with typical observations in
undoped In 2O3 material [12], [14].
Fig. 4 presents the validation of the developed model
against experimental and TCAD data. The In 2O3 TFT was
fabricated and measured at Purdue University, with the exper-
imental data collected in collaboration with Texas Instruments.
The TCAD Sentaurus simulations were first calibrated using
the experimental data. The key parameters for the TCAD setup
are as follows.
1) The trap concentration in the channel is 1 × 1020 cm−3,
located 0.4 eV above the conduction band edge.
2) The trap density in the source and drain is
4× 1020 cm−3.
3) A Gaussian trap distribution is assumed along the
source–drain direction.
4) The mobility model includes surface scattering, phonon
scattering, and high-field saturation effects.
Fig. 4(a) shows comparison of the analytical model with
the experimental and TCAD data for Vds= 0.5 V . While the
analytical model with constant mobility accurately captures
the subthreshold region, it underpredicts the ON current. This
is expected because the inversion charge density in the channel
has not been incorporated into the solution of 2-D Poisson’s
equation (8). Including the inversion charge density in the
analytical solution is complex and outside the scope of this
work [26].
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination. 
Authorized licensed use limited to: Purdue University. Downloaded on March 13,2025 at 20:21:30 UTC from IEEE Xplore.  Restrictions apply.

## printed page 6  (PDF page 6)

6 IEEE TRANSACTIONS ON ELECTRON DEVICES
Fig. 4. (a) Field-dependent mobility mode improves the ON region matching. (b) and (c) Validation of the analytical model for low and high drain
voltages with the experimental data and calibrated TCAD deck with Vgs1= 0 V. Default parameters are taken fromFig. 1.
Fig. 5. (a) and (b) 3-D surface potential distribution in the device for Vds= 0 V, and Vds= 1 V, respectively. Note that potential continuity is
maintained at both top oxide/channel interfaces. For Vds= 1 V, the highest potential drop is observed near the drain region following the applied
bias condition. (a) Parameters: Vgs1=−0.5 V and Vgs2= 0 V. The source side potential is taken as a reference point, i.e.,= 0 V.
VII. R ESULTS AND DISCUSSION
A. Improved Mobility Model
The constant mobility model tends to underestimate the
ON current. To address this, an analytical mobility model is
used, where mobility increases with gate bias and saturates
at higher values, similar to current saturation. A robust and
straightforward approach to deriving such a model is through
a hyperbolic function, which provides a smooth transition and
ensures physical accuracy. The effective mobility is derived
µeff=µ0
(
1+ tanh
(
Vg− V0
))
(56)
where µ0 = 7.2 cm 2/V-s, and V0 is the minimum applied
gate voltage. With the updated mobility model, the analytical
model shows consistency in the ON region, as demonstrated
in Fig. 4(a). Fig. 4(b) and (c) further validates the analytical
model against experimental data for both low and high drain
voltages, incorporating the improved mobility model.
However, due to the limitations of the analytical approach,
it is not feasible to incorporate extensive empirical mobility
models or account for effects such as surface scattering
and phonon scattering. As a result, some discrepancies are
observed between the analytical model in the moderate inver-
sion region. It is important to note that this work is not pri-
marily focused on modeling the ON current region in the TFTs.
Nonetheless, we have enhanced the mobility model to reflect
the requirement for BEOL TFTs to operate effectively as
current drivers, where the ON current plays a crucial role.
Note: The model is validated for a gate length
of L= 40 nm. While validation across multiple gate lengths
would further assess the model’s robustness, we limit our vali-
dation to a single gate length due to data availability. However,
the calculated subthreshold swing (SS) and threshold voltage
roll-off as a function of channel length scaling align with
physical expectations, demonstrating the model’s capability to
capture SCEs accurately.
Fig. 5(a) and (b) shows the 3-D surface potential distribu-
tion for the entire device for Vds = 0 V , and Vds = 1 V ,
respectively. The top and bottom gates are at −0.5 and 0 V ,
respectively. The potential continuity is maintained at the
bottom and top gate oxide with the channel interface, including
the impact of drain bias, signifying the model’s accuracy.
Fig. 6 presents the conduction band profile at the back-gate
oxide and channel interface. The analytical model effectively
predicts the maximum barrier height in the channel, accurately
capturing the DIBL effect.
Fig. 7 shows the Ids− Vgs characteristics for various gate
oxide thicknesses at L= 15 and 40 nm. Increasing the gate
oxide thickness weakens the gate control over the channel,
leading to an increase in the OFF current value. Furthermore,
due to the reduced gate capacitance, the ON current also
decreases at higher gate oxide thickness.
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination. 
Authorized licensed use limited to: Purdue University. Downloaded on March 13,2025 at 20:21:30 UTC from IEEE Xplore.  Restrictions apply.

## printed page 7  (PDF page 7)

PANDEY et al.: ANAL YTICAL MODELING OF SHORT -CHANNEL EFFECTS IN BEOL-COMPATIBLE TFTs 7
Fig. 6. Electrostatic conduction band validation with the TCAD. The
model accurately captures the maximum barrier height and DIBL effect.
Default parameters from Fig. 1.
Fig. 7. Impact of oxide thickness scaling on SCEs and threshold voltage
roll-off. A higher gate oxide thickness reduces the gate control and
increases the OFF current. Default parameters are taken from Fig. 1.
Default parameters are taken from Fig. 1.
A comparison between L= 15 and 40 nm provides insight
into threshold voltage roll-off. The gate voltage required to
achieve a current level of 1 nA/µm at tox2 = 5 nm is
approximately−0.3959 V for L= 40 nm and −0.5976 V
for L = 15 nm, resulting in a reduction of approximately
200 mV in Vth. This threshold voltage roll-off increases to
approximately 630 mV for tox2 = 10 nm. Therefore, the
device’s electrostatic integrity diminishes significantly with
increasing oxide thickness and shorter channel lengths.
Fig. 8 shows the impact of channel length scaling on the
SCEs and ION. Severe SCEs are observed for L= 15 nm,
while increasing the channel length improves gate control
by reducing the influence of the drain electric field. The
long-channel limit is observed around L= 80 nm. Beyond
this gate length, saturation in the OFF current is observed due
to the long-channel barrier height, which is not affected by the
channel length modulation.
Fig. 8. Impact of channel length scaling on the device’s threshold
voltage roll-off. The increasing channel length weakens the drain electric
field control on the channel, enhancing the gate control. The long
channel limit is∼80 nm. Default parameters are taken from Fig. 1.
Fig. 9. Increasing channel thickness raises the OFF current due to
reduced gate directional field gradient. Default parameters are taken
from Fig. 1.
Fig. 9 shows the impact of channel thickness scaling on
the device’s OFF and ON currents. For L= 20 nm, stronger
drain electric field effects are observed, which is ideal for
studying severe SCEs. Increasing channel thickness weakens
gate control due to the reduced gate field gradient (∂ E/∂ y↓).
The analytical model does not include scattering or mobility
degradation effects. As the channel thickness increases, the
gate’s ability to control the channel diminishes, increasing
the OFF current. However, higher channel thickness allows for
greater charge density, which raises the ON current.
Fig. 10 shows the impact of trap density on the ON/OFF
current characteristics. The source/drain (S/D) trap density is
fixed at 4 × 1020 cm−3. Increasing the trap density within
the channel reduces the effective barrier at equilibrium, lead-
ing to a rise in the OFF current. While the ON current also
increases due to the enhanced electron density in the channel,
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination. 
Authorized licensed use limited to: Purdue University. Downloaded on March 13,2025 at 20:21:30 UTC from IEEE Xplore.  Restrictions apply.

## printed page 8  (PDF page 8)

8 IEEE TRANSACTIONS ON ELECTRON DEVICES
Fig. 10. Increasing channel trap density reduces the effective bar-
rier, raising both ON and OFF currents. Default parameters are taken
from Fig. 1.
Fig. 11. SS with the channel length for the various combina-
tions of oxide and channel thicknesses. Default parameters are taken
from Fig. 1.
this improvement comes at the expense of higher OFF current
levels. When the channel trap density matches that of the S/D,
the barrier is almost suppressed, and the series resistances
primarily limit the current.
Fig. 11 shows the SS characteristics with channel length for
various oxide and channel thicknesses. The SS at L= 15 nm
and tch= 1 nm is 107, 138, and 202 mV/decade for tox2= 5,
7, and 10 nm, respectively. On the other hand, the SS at
L= 15 nm and tox2= 5 nm is 116, 126, and 153 mV/decade
for tch= 1.5, 2, and 3 nm, respectively. Increasing the oxide
thickness by 2× causes a∼ 95-mV/decade increase in the SS,
while increasing the channel thickness by 3× raises the SS
only by∼ 37 mV/decade. Therefore, the device’s SS is much
more sensitive to oxide scaling than to channel thickness
scaling.
Fig. 12 shows the threshold voltage roll-off plot with
channel length at different oxide and channel thicknesses.
As observed in the SS plot, scaling in the oxide thickness
causes a significantly larger threshold voltage roll-off than the
Fig. 12. Threshold voltage roll-off is more sensitive to the gate oxide
scaling than the channel thickness scaling. Default parameters are taken
from Fig. 1.
channel thickness scaling. From the SS and threshold voltage
roll-off plots, it can be concluded that the device’s short-
channel characteristics are more prone to gate oxide scaling
than to channel length scaling. Note that the constant current
method at the 1-nA/µm current level is used to calculate the
Vth roll-off.
VIII. C ONCLUSION
We have developed an analytical model for In 2O3 TFTs
using Green’s function approach by solving 2-D Poisson’s
equation. Model validation against experimental and TCAD
data demonstrates good agreement for both high and low drain
voltages. The model accurately reflects critical phenomena
such as threshold voltage roll-off, SCEs, and DIBL, with the
results highlighting the tradeoffs involved in scaling gate oxide
thickness, channel thickness, and channel length. Although the
ON current region shows some discrepancy due to the exclu-
sion of inversion charge density, an improved field-dependent
mobility model ensures consistency in the ON region. The
framework can act as a fast analytical tool to aid in the design
of the device by relating its performance metrics with key
geometry and material parameters.
IX. G REEN ’S FUNCTION
GI
y
(
x, y; x′, y′)
= 2
tox1
∑
n
sin
(
kI
n y
)
sin
(
kI
n y′)
kInsinh
(
kIn L
)
×
{sinh
(
kI
n
(
L− x′))
sinh
(
kI
n x
)
0< x < x′
sinh
(
kI
n x′)
sinh
(
kI
n(L− x)
)
x′< x < L
}
(57)
GI
x
(
x, y; x′, y′)
= 2
L
∑
m
sin(km x)sin
(
km x′)
kmcosh
(
kmtox1
)
{sinh(km y)cosh
(
km
(
tox1− y′))
0< y< y′
sinh
(
km y′)
cosh
(
km
(
tox1− y
))
y′< y< tox1
}
(58)
GII
x
(
x, y; x′, y′)
= 2
L
∑
m
sin(km x)sin
(
km x′)
kmsinh(kmtch)
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination. 
Authorized licensed use limited to: Purdue University. Downloaded on March 13,2025 at 20:21:30 UTC from IEEE Xplore.  Restrictions apply.

## printed page 9  (PDF page 9)

PANDEY et al.: ANAL YTICAL MODELING OF SHORT -CHANNEL EFFECTS IN BEOL-COMPATIBLE TFTs 9
{cosh
(
km
(
tox1− y
))
cosh
(
km
(
t1− y′))
tox1 < y< y′
cosh
(
km
(
tox1− y′))
cosh(km(t1− y)) y′< y< t1
}
(59)
GII
y
(
x, y; x′, y′)
= 2
tch
∑
n
cos
(
kII
n(t1− y)
)
cos
(
kII
n
(
t1− y′))
kIIn sinh
(
kIIn L
)
×
{sinh
(
kII
n
(
L− x′))
sinh
(
kII
n x
)
0< x < x′
sinh
(
kII
n x′)
sinh
(
kII
n(L− x)
)
x′< x < L
}
(60)
GIII
y
(
x, y; x′, y′)
= 2
tox2
∑
n
sin
(
kIII
n (t2− y)
)
sin
(
kIII
n
(
t2− y′))
kIIIn sinh
(
kIIIn L
)
×
{sinh
(
kIII
n
(
L− x′))
sinh
(
kIII
n x
)
0< x < x′
sinh
(
kIII
n x′)
sinh
(
kIII
n (L− x)
)
x′< x < L
}
(61)
GIII
x
(
x, y; x′, y′)
= 2
L
∑
m
sin(km x)sin
(
km x′)
kmcosh
(
kmtox2
)
×
{cosh(km(t1− y))sinh
(
km
(
t2− y′))
t1< y< y′
cosh
(
km
(
t1− y′))
sinh(km(t2− y)) y′< y< t2
}
.
(62)
REFERENCES
[1] P. Weimer, “The TFT a new thin-film transistor,” Proc. IRE, vol. 50,
no. 6, pp. 1462–1469, Jun. 1962.
[2] H. Kawamoto, “The history of liquid-crystal display and its industry,” in
Proc. 3rd IEEE Hist. ELectro-Technol. Conf. (HISTELCON), Sep. 2012,
pp. 1–6.
[3] E. M. C. Fortunato et al., “Fully transparent ZnO thin-film transistor
produced at room temperature,” Adv. Mater ., vol. 17, no. 5, pp. 590–594,
Mar. 2005, doi: 10.1002/adma.200400368.
[4] H. S. Kim, P. D. Byrne, A. Facchetti, and T. J. Marks, “High perfor-
mance solution-processed indium oxide thin-film transistors,” J. Amer .
Chem. Soc., vol. 130, no. 38, pp. 12580–12581, Sep. 2008, doi:
10.1021/ja804262z.
[5] M.-G. Kim, M. G. Kanatzidis, A. Facchetti, and T. J. Marks,
“Low-temperature fabrication of high-performance metal oxide thin-
film electronics via combustion processing,” Nature Mater ., vol. 10,
pp. 382–388, Apr. 2011, doi: 10.1038/nmat3011.
[6] W. Chakraborty, B. Grisafe, H. Ye, I. Lightcap, K. Ni, and S. Datta,
“BEOL compatible dual-gate ultra thin-body W-doped indium-oxide
transistor with ion = 370µA/µm, SS = 73 mV/dec and ion /Ioff
ratio > 4×10 9,” in Proc. IEEE Symp. VLSI Technol., Jun. 2020,
pp. 1–2.
[7] T. Kamiya, K. Nomura, and H. Hosono, “Origins of high mobility and
low operation voltage of amorphous oxide TFTs: Electronic structure,
electron transport, defects and doping,” J. Display Technol., vol. 5, no. 7,
pp. 273–288, Jul. 2009.
[8] W. Tang et al., “Monolithic 3D integration of vertically stacked
CMOS devices and circuits with high-mobility atomic-layer-deposited
In2O3 n-FET and polycrystalline Si p-FET: Achieving large
noise margin and high voltage gain of 134 V/V ,” in IEDM
Tech. Dig., Dec. 2022, pp. 483–486, doi: 10.1109/IEDM45625.2022.
10019410.
[9] J. Zhang et al., “Back-end-of-line-compatible scaled InGaZnO transis-
tors by atomic layer deposition,” IEEE Trans. Electron Devices, vol. 70,
no. 12, pp. 6651–6657, Dec. 2023.
[10] P.-Y . Liao et al., “Transient thermal and electrical co-optimization
of BEOL top-gated ALD In 2O3 FETs on various thermally conduc-
tive substrates including diamond,” in IEDM Tech. Dig., Dec. 2022,
pp. 12.4.1–12.4.4.
[11] S. Yamazaki et al., “High-performance single-crystalline In 2O3 field
effect transistor toward three-dimensional large-scale integration cir-
cuits,” Commun. Mater ., vol. 5, no. 1, p. 184, Sep. 2024, doi:
10.1038/s43246-024-00625-x.
[12] P. D. C. King, T. D. Veal, D. J. Payne, A. Bourlange, R. G. Egdell,
and C. F. McConville, “Surface electron accumulation and the charge
neutrality level in In 2O3,” Phys. Rev. Lett., vol. 101, no. 11, Sep. 2008,
Art. no. 116808, doi: 10.1103/physrevlett.101.116808.
[13] L. Liu et al., “Theoretical study of oxygen-vacancy distribution in
In2O3,” J. Phys. Chem. C , vol. 125, no. 13, pp. 7077–7085, Apr. 2021,
doi: 10.1021/acs.jpcc.1c01462.
[14] J. H. W. De Wit, G. Van Unen, and M. Lahey, “Electron concentra-
tion and mobility in In 2O3,” J. Phys. Chem. Solids, vol. 38, no. 8,
pp. 819–824, Jan. 1977, doi: 10.1016/0022-3697(77)90117-2.
[15] M. Shur, M. Hack, and J. G. Shaw, “A new analytic model for
amorphous silicon thin-film transistors,” J. Appl. Phys., vol. 66, no. 7,
pp. 3371–3380, Oct. 1989, doi: 10.1063/1.344481.
[16] M. D. Jacunski, M. S. Shur, A. A. Owusu, T. Ytterdal, M. Hack, and
B. Iniguez, “A short-channel DC SPICE model for polysilicon thin-film
transistors including temperature effects,” IEEE Trans. Electron Devices,
vol. 46, no. 6, pp. 1146–1158, Jun. 1999.
[17] H. Tsuji et al., “A new surface potential based poly-Si TFT model
for circuit simulation,” in IEDM Tech. Dig., San Francisco, CA, USA,
Dec. 2006, pp. 1–4.
[18] Y . Hernández-Barrios, A. Cerdeira, M. Estrada, and B. Iñíguez, “Analyti-
cal current–voltage model for double-gate a-IGZO TFTs with symmetric
structure for above threshold,” IEEE Trans. Electron Devices, vol. 67,
no. 5, pp. 1980–1986, May 2020.
[19] W. Deng, J. Huang, X. Ma, and T. Ning, “An explicit surface-potential-
based model for amorphous IGZO thin-film transistors including both
tail and deep states,” IEEE Electron Device Lett., vol. 35, no. 1,
pp. 78–80, Jan. 2014.
[20] Z. Zong, L. Li, J. Jang, N. Lu, and M. Liu, “Analytical surface-
potential compact model for amorphous-IGZO thin-film transistors,”
J. Appl. Phys., vol. 117, no. 21, Jun. 2015, Art. no. 215705, doi:
10.1063/1.4922181.
[21] M. Ghittorelli, F. Torricelli, L. Colalongo, and Z. M. Kovács-Vajna,
“Accurate analytical physical modeling of amorphous InGaZnO thin-
film transistors accounting for trapped and free charges,” IEEE Trans.
Electron Devices, vol. 61, no. 12, pp. 4105–4112, Dec. 2014.
[22] G. Pahwa, S. Salahuddin, and C. Hu, “An all-region BSIM thin-film
transistor model for display and BEOL 3-D integration applications,”
IEEE Trans. Electron Devices, vol. 71, no. 8, pp. 4701–4709, Aug. 2024.
[23] J. Pruefer et al., “Compact modeling of short-channel effects in staggered
organic thin-film transistors,” IEEE Trans. Electron Devices, vol. 67,
no. 11, pp. 5082–5090, Nov. 2020, doi: 10.1109/TED.2020.3021368.
[24] F. Torricelli, Z. M. Kovács-Vajna, and L. Colalongo, “A charge-based
OTFT model for circuit simulation,” IEEE Trans. Electron Devices,
vol. 56, no. 1, pp. 20–30, Jan. 2009, doi: 10.1109/TED.2008.2007717.
[25] X. Liang and Y . Taur, “A 2-D analytical solution for SCEs in
DG MOSFETs,” IEEE Trans. Electron Devices, vol. 51, no. 9,
pp. 1385–1391, Sep. 2004, doi: 10.1109/TED.2004.832707.
[26] N. Pandey, H.-H. Lin, A. Nandi, and Y . Taur, “Modeling of short-channel
effects in DG MOSFETs: Green’s function method versus scale length
model,” IEEE Trans. Electron Devices, vol. 65, no. 8, pp. 3112–3119,
Aug. 2018, doi: 10.1109/TED.2018.2845875.
[27] Q. Xie, J. Xu, and Y . Taur, “Review and critique of analytic models of
MOSFET short-channel effects in subthreshold,” IEEE Trans. Electron
Devices, vol. 59, no. 6, pp. 1569–1579, Jun. 2012.
[28] N. Pandey and Y . S. Chauhan, “Dynamics and modeling of multidomains
in ferroelectric tunnel junction—Part I: Mathematical framework,” IEEE
Trans. Electron Devices, vol. 69, no. 12, pp. 7147–7155, Dec. 2022.
[29] B. G. Streetman and S. Banerjee, Solid State Electronic Devices, vol. 4.
Upper Saddle River, NJ, USA: Prentice-Hall, 2000.
[30] W. J. Chang, M. P. Houng, and Y . H. Wang, “Simulation of stress-
induced leakage current in silicon dioxides: A modified trap-assisted
tunneling model considering Gaussian-distributed traps and electron
energy loss,” J. Appl. Phys., vol. 89, no. 11, pp. 6285–6293, Jun. 2001,
doi: 10.1063/1.1367399.
[31] H. S. Bennett, M. Gaitan, P. Roitman, T. J. Russell, and J. S. Suehle,
“Modeling MOS capacitors to extract Si—SiO 2 interface trap densities
in the presence of arbitrary doping profiles,” IEEE Trans. Electron
Devices, vol. ED-33, no. 6, pp. 759–765, Jun. 1986.
[32] J. D. Jackson, Electrodynamics, Classical . Hoboken, NJ, USA: Wiley,
2003, doi: 10.1002/3527600434.eap109.
[33] N. Pandey, “Modeling of ferroelectric memories and transistors
including multi-domain effects,” Ph.D. dissertation, Dept. Elect.
Eng., Indian Inst. Technol. Kanpur, Kanpur, India, 2023, doi:
10.13140/RG.2.2.22419.45603.
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination. 
Authorized licensed use limited to: Purdue University. Downloaded on March 13,2025 at 20:21:30 UTC from IEEE Xplore.  Restrictions apply.
