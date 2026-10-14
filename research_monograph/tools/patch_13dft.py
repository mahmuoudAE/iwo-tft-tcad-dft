"""Produce chapters/13_dft_rev.tex = report_latex_full/chapters/13_dft.tex (baseline 3fe6627) + verified patches.

Every patch is an exact (old, new) pair that must occur exactly once; the script fails otherwise. Basis of each patch:
evidence/audits/13_dft_patch_plan.md (P1-P11 and status items). Re-run after any change to this list:
    python3 -I research_monograph/tools/patch_13dft.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "report_latex_full/chapters/13_dft.tex"
DST = ROOT / "research_monograph/chapters/13_dft_rev.tex"

NOTE = r"""
\begin{statusbox}{Revision note (monograph, October 2026)}
This chapter is the baseline chapter of 5 October 2026 with verified corrections only
(\file{research_monograph/evidence/audits/13_dft_patch_plan.md}); its structure and labels are unchanged. Corrected:
the sign convention of the valence-band shift (now signed throughout, $\Delta\Eg = \dEc - \Delta E_{\mathrm{v}}$) and
the 1~nm value $\Delta E_{\mathrm{v}} = -0.052$~eV \corr{X2}; the donated electron density of the bulk W cell
($2.7\times10^{21}$\cmcu{}, not $5.5\times10^{21}$); the scope of the ``no dipole'' and ``bulk-like band edge''
statements; the wording of what is computed and what is inferred about W \corr{X1}; the fit basis of every mass
\corr{X6}; and stale ``pending'' statements. Results logged after 5 October are reported in
\cref{ch:mono-masses,ch:mono-w-vac,ch:mono-amorph} and in \cref{sec:mono-dft-thin} below.
\end{statusbox}
"""

PATCHES = [
    # --- revision note after the chapter label
    ("\\chapter{First-principles inputs: density-functional calculations of \\texorpdfstring{\\InO}{In2O3} and IWO films}\n\\label{ch:dft}\n",
     "\\chapter{First-principles inputs: density-functional calculations of \\texorpdfstring{\\InO}{In2O3} and IWO films}\n\\label{ch:dft}\n" + NOTE),
    # --- P7 glossary: scope of the dipole statement
    ("The slabs here have equivalent surfaces and no dipole.",
     "The 1 and 2~nm slabs here have equivalent surfaces and no dipole; the 0.695~nm slab is polar (\\cref{sec:mono-dft-thin})."),
    # --- P6 valence wording (electron counting paragraph)
    ("whereas W in its highest oxidation state gives six (W$^{6+}$), so each W substituted for In adds\nthree electrons that oxygen cannot take.",
     "whereas W in its highest oxidation state gives six (W$^{6+}$), so each W substituted for In adds\nthree electrons that oxygen cannot take (formal electron counting; the computed W--O bond lengths are consistent with\nW$^{6+}$, \\cref{sec:dft-calc-w})."),
    # --- P9 mass basis
    ("where $c_2$ is the slope of $E - E_{\\mathrm{CBM}}$ against $k^2$ in a least-squares fit over $|k| \\le 0.05$~\\AA$^{-1}$.",
     "where $c_2$ is the slope of $E - E_{\\mathrm{CBM}}$ against $k^2$ in a least-squares fit over $|k| \\le 0.05$~\\AA$^{-1}$\n(four points including $\\Gamma$, free intercept: the ``deck basis'' used by the device decks). The band-edge mass of\nthe later re-derivation, a 10-point Kane fit, is lower by up to 3\\,\\% (\\cref{ch:mono-masses})."),
    # --- P1 partition equation: signed convention
    ("Because both surfaces of the slabs are equivalent by symmetry, the potential is the same in the vacuum on both sides and\nno dipole correction \\citep{Neugebauer1992} is needed.",
     "Because both surfaces of the 1 and 2~nm slabs are equivalent by symmetry, the potential is the same in the vacuum on both\nsides and no dipole correction \\citep{Neugebauer1992} is needed (this does not hold for the polar 0.695~nm slab,\n\\cref{sec:mono-dft-thin})."),
    ("\\Delta E_{\\mathrm{v}}(t_1) - \\Delta E_{\\mathrm{v}}(t_2) = \\mathrm{IP}(t_1) - \\mathrm{IP}(t_2) .\n\\end{gathered}",
     "\\Delta E_{\\mathrm{v}}(t_1) - \\Delta E_{\\mathrm{v}}(t_2) = \\mathrm{IP}(t_2) - \\mathrm{IP}(t_1) .\n\\end{gathered}"),
    ("conduction-band minimum by $\\dEc$ and lowers the valence-band maximum by $\\Delta E_{\\mathrm{v}}$, so the gap opens by\n$\\Delta E_{\\mathrm{g}} = \\dEc + \\Delta E_{\\mathrm{v}}$.",
     "conduction-band minimum by $\\dEc$ and shifts the valence-band maximum by $\\Delta E_{\\mathrm{v}}$ (signed; negative means\ndownwards), so the gap opens by $\\Delta E_{\\mathrm{g}} = \\dEc - \\Delta E_{\\mathrm{v}}$."),
    # --- P4 W cell description
    ("that corresponds to about $2.8\\times10^{21}$\\cmcu{}, far above the carrier density of the transistor channel. The cell\ntherefore describes the fully ionized, degenerate limit, and band-edge quantities are read from the dispersion and the\nprojected states, not from the position of $E_F$ alone.",
     "that corresponds to $2.7\\times10^{21}$\\cmcu{} \\fact{043}, far above the carrier density of the transistor channel. The\ncell therefore describes a degenerate filling with three donated electrons per cell; whether W stays ionised at device\ndensities is inferred, not computed (\\cref{ch:mono-w-vac}). Band-edge quantities are read from the dispersion and the\nprojected states, not from the position of $E_F$ alone."),
    # --- status: 2 nm IWO in structure table
    ("& 176 & 1329 & -- & W in a 2~nm film (submitted 4 Oct.) \\\\",
     "& 176 & 1329 & -- & W in a 2~nm film (relaxed; final SCF and projections, cluster 12835211) \\\\"),
    ("\\node[pend, below=of s2] (c2) {2~nm final on CPU\\\\(PDOS), 2~nm IWO};",
     "\\node[st, below=of s2] (c2) {2~nm final on CPU\\\\(PDOS), 2~nm IWO};"),
    ("\\caption{Stages of the study and their dependencies. Solid: finished; dashed: running or queued at the time of\nwriting.",
     "\\caption{Stages of the study and their dependencies, as of 5 October 2026 (all finished by 6 October; later stages are in\n\\cref{ch:mono-masses,ch:mono-w-vac,ch:mono-amorph})."),
    # --- P9 bulk mass paragraph
    ("$\\mstar = 0.159\\,m_0$, as expected for the s-like conduction-band minimum of a cubic crystal.",
     "$\\mstar = 0.159\\,m_0$ on this four-point basis, as expected for the s-like conduction-band minimum of a cubic crystal\n(band-edge Kane basis: $0.1541\\,m_0$ \\fact{004}, \\cref{ch:mono-masses})."),
    ("gives $\\alpha = 0.63$, 0.57 and 0.55~eV$^{-1}$.",
     "gives $\\alpha = 0.63$, 0.57 and 0.55~eV$^{-1}$ (consolidated 10-point value $0.58$~eV$^{-1}$ \\fact{005})."),
    ("far inside the 10~meV criterion; the symmetric, dipole-free slab converges fast.",
     "far inside the 10~meV criterion; the symmetric, dipole-free 1~nm slab converges fast."),
    # --- P10 slab masses
    ("The in-plane mass is $0.281\\,m_0$ along [100] and\n$0.282\\,m_0$ along [110] (\\cref{fig:dft_mass_fit}b), an increment",
     "The in-plane mass (four-point basis) is $0.281\\,m_0$ along [100] and\n$0.282\\,m_0$ along [110] (\\cref{fig:dft_mass_fit}b; band-edge 2-D DOS mass $0.279\\,m_0$, \\cref{ch:mono-masses}), an increment"),
    ("The in-plane mass is $0.206\\,m_0$ along both [100] and [110] (0.2064 and 0.2059), an increment of",
     "The in-plane mass (four-point basis) is $0.206\\,m_0$ along both [100] and [110] (0.2064 and 0.2059; band-edge 2-D DOS\nmass $0.203\\,m_0$ \\corr{X6}), an increment of"),
    # --- P11 laws pointer
    ("and $0.122\\,m_0$. A refit to the computed points will therefore change the laws by a few per cent.",
     "and $0.122\\,m_0$. A refit to the computed points will therefore change the laws by a few per cent. (Thicknesses in\nthis paragraph are those of the baseline analysis; the later laws use the relaxed H--H thickness, 0.930 and 1.962~nm,\nand are given in \\cref{ch:mono-masses}.)"),
    # --- P1 1-2 nm partition (signed)
    ("\\Delta E_{\\mathrm{v}}(1) - \\Delta E_{\\mathrm{v}}(2) = \\mathrm{IP}(1) - \\mathrm{IP}(2) = -0.002~\\mathrm{eV},\n\\end{gathered}\n\\end{equation}\nwhose sum, $+0.565$~eV, equals $\\Delta E_{\\mathrm{g}}(1) - \\Delta E_{\\mathrm{g}}(2)$.",
     "\\Delta E_{\\mathrm{v}}(1) - \\Delta E_{\\mathrm{v}}(2) = \\mathrm{IP}(2) - \\mathrm{IP}(1) = +0.002~\\mathrm{eV},\n\\end{gathered}\n\\end{equation}\nwhose difference, $0.567 - 0.002 = +0.565$~eV, equals $\\Delta E_{\\mathrm{g}}(1) - \\Delta E_{\\mathrm{g}}(2)$\n\\fact{012} \\fact{013}."),
    ("Two\nchecks are open before this is used. First, a top valence level that does not move at all may belong to the surface\n(O--H) rather than to the film interior; a projection of that state onto the atoms will decide this. Second, the shares\nrelative to bulk, $\\dEc(t)$ and $\\Delta E_{\\mathrm{v}}(t)$ themselves, need the bulk potential at the slab's in-plane\nlattice constant (two-step alignment, \\cref{sec:dft-readout}). The CPU cross-check of the final SCF (which also gives\nthe projected density of states) and the 2~nm IWO slab were submitted on 4 October 2026.",
     "Two\nchecks were open at this point and have since been closed (\\cref{sec:dft-partition}): the projection of the top valence\nstate (bulk-like at 2~nm) and the two-step alignment relative to bulk."),
    ("same-termination electron-affinity differences ($+0.567$ and $-0.002$~eV).",
     "same-termination electron-affinity and ionization-potential differences ($\\dEc$: $+0.567$~eV; $\\Delta E_{\\mathrm{v}}$:\n$+0.002$~eV)."),
    ("1~nm & 2~nm value + electron-affinity difference (adopted) & $+0.848$ & $-0.056$ & 0.94\\\\\\bottomrule",
     "1~nm & 2~nm value + EA/IP differences (adopted) & $+0.848$ & $-0.052$ & 0.94\\\\\\bottomrule"),
    ("1~nm $+0.848$, $-0.056$~eV (share 0.94);",
     "1~nm $+0.848$, $-0.052$~eV (share 0.94; corrected from $-0.056$ \\corr{X2});"),
    # --- P6 valence paragraph
    ("the computed means of 1.97--1.98~\\AA{} identify W$^{6+}$. Relative to\nIn$^{3+}$, each W can therefore release three electrons.",
     "the computed means of 1.97--1.98~\\AA{} are consistent with W$^{6+}$ (an ionic-radius argument, not a charge\nanalysis). Relative to In$^{3+}$, each W can then release three electrons. The L\\\"owdin W-5d counts of the occupied\nstates above the valence band (0.09--0.43~e) are not the W charge \\fact{045}."),
    ("\\paragraph{The electrons of W (preliminary).}",
     "\\paragraph{The electrons of W (computed at one filling).}"),
    # --- P3 donated density
    ("Within PBE and for one W per cell (3.1\\,\\% of the cations,\n$5.5\\times10^{21}$ donated electrons per cm$^3$),",
     "Within PBE and for one W per cell (3.1\\,\\% of the cations,\n$2.7\\times10^{21}$ donated electrons per cm$^3$),"),
    ("\\paragraph{Result (PBE, one W position, preliminary).}",
     "\\paragraph{Result (PBE, one W position, one filling).}"),
    ("bulk 80-atom cell with W on 24d (left) and 1~nm slab with W on the central 24d site (right). PBE, preliminary.}",
     "bulk 80-atom cell with W on 24d (left) and 1~nm slab with W on the central 24d site (right). PBE, at the filling of\nthree donated electrons per cell.}"),
    ("and $E_F$ (dashed). That column is preliminary.}",
     "and $E_F$ (dashed). That column is computed at one filling (three donated electrons per cell).}"),
    # --- P3/P5 consequence paragraph
    ("(about $3\\times10^{21}$ and\n$5.5\\times10^{21}$ donated electrons per cm$^3$; in the 1~nm film, about one of the three electrons). The first result\nfor the 2~nm film with 1.8\\,\\% W (last SCF of its relaxation; projections pending) places $E_F$ 1.24~eV above the\nconduction-band bottom and the flat bands that are presumably W-derived 0.07~eV above $E_F$, i.e.\\ just empty. At the\nlower electron densities of working channels, PBE thus predicts that W releases its electrons into the host band;",
     "($3.0\\times10^{21}$ and\n$2.7\\times10^{21}$ donated electrons per cm$^3$; in the 1~nm film, about one of the three electrons by the occupation of\nband 313). In the 2~nm film with 1.8\\,\\% W ($1.4\\times10^{21}$\\cmcu{}; final SCF and projections, cluster 12835211)\nthe W-5d-rich level lies 1.34~eV above the host conduction-band bottom and 0.103~eV above $E_F$ at $\\Gamma$\n\\fact{042}. In every W cell the W-5d-rich level lies within about 0.1~eV of $E_F$ at $\\Gamma$; whether band filling\npins it there would need a density series. At the lower electron densities of working channels it is inferred, not\ncomputed (no lower-density cell, no hybrid functional for the W cells), that W releases its electrons into the host\nband \\claim{C022};"),
    ("A hybrid functional can lower localized d levels, so this\nconclusion is preliminary.",
     "A hybrid functional can lower localized d levels, so this\ninference is provisional."),
    # --- P10 summary table rows
    ("$\\Delta\\mstar$ at about 1~nm & $+0.122\\,m_0$ & computed \\\\",
     "$\\Delta\\mstar$ at about 1~nm & $+0.122\\,m_0$ (four-point basis) & computed \\\\"),
    ("$\\Delta\\mstar$ at about 2~nm & $+0.047\\,m_0$ & computed \\\\",
     "$\\Delta\\mstar$ at about 2~nm & $+0.047\\,m_0$ (four-point basis) & computed \\\\"),
    ("W site, valence & 24d, W$^{6+}$ & computed, converged \\\\",
     "W site, valence & 24d (by 0.258~eV); bond lengths consistent with W$^{6+}$ & computed, converged \\\\"),
    ("& preliminary (PBE); corrected 5 Oct.\\ 2026 \\\\",
     "& computed at one filling (PBE); corrected 5 Oct.\\ 2026 \\corr{X1} \\\\"),
    ("W effect on confinement & \\textit{[to be completed: 2~nm IWO slab; 1~nm IWO slab mass]} & pending \\\\",
     "W effect on confinement & bulk host-CB mass $+5$\\,\\% (0.162~$m_0$, computed); slab masses $+6.5$/$+7.5$\\,\\%\n(estimated from SCF grids); 1~nm gap $-0.069$~eV, EA $+0.141$~eV \\fact{047} \\fact{048} & see \\cref{ch:mono-w-vac} \\\\"),
    # --- status items
    ("(the two-step method of \\citealp{VandeWalle1987,Baldereschi1988}). This\nstep has not yet been done (\\cref{sec:dft-pending}).",
     "(the two-step method of \\citealp{VandeWalle1987,Baldereschi1988}). This\nstep is described in \\cref{sec:dft-partition}."),
    ("The usage to date is about 8\\,300 weighted CPU core-hours",
     "The usage up to 4 October 2026 is about 8\\,300 weighted CPU core-hours"),
    ("gives the wall times of representative steps.",
     "gives the wall times of representative steps. Later jobs (2~nm IWO, sub-nanometre slabs, vacancy cells, hybrid and\namorphous calculations) are not included in these totals; \\cref{app:mono-resources} states what is recorded about them."),
    # --- P8 scope of the surface-state check
    ("\\paragraph{The band edges are not surface states.} An orbital projection of the relaxed 2~nm film",
     "\\paragraph{At 2~nm the band edges are not surface states.} An orbital projection of the relaxed 2~nm film"),
    ("Both band edges are therefore confined, bulk-like states, and the split of \\cref{tab:dft-partition} describes them.",
     "Both band edges of the 2~nm film are therefore confined, bulk-like states, and the split of \\cref{tab:dft-partition}\ndescribes them. The check does not extend to thinner films: at 0.461 and 0.695~nm the valence-band top lies on the OH\noxygens (98 and 75\\,\\% of its weight; \\cref{sec:mono-dft-thin}), and at 1 and 2~nm the two highest valence bands lie\nwithin 3.3 and 9.3~meV of each other \\claim{C040}."),
    # --- status table row for 0.51/0.75 nm
    ("and marks the limit of the recipe & relaxing on CERN (5 Oct.\\ 2026) \\\\",
     "and marks the limit of the recipe. Relaxed: H--H 0.461~nm (exactly In$_8$(OH)$_{24}$) and 0.695~nm (polar)\n(\\cref{sec:mono-dft-thin}) & computed (finished 6 Oct., logged 14 Oct.\\ 2026) \\claim{C021} \\\\"),
    # --- limitations / key result
    ("complexes with oxygen defects and\ncharge states were not computed.",
     "complexes with oxygen defects and\ncharge states were not computed in this chapter (neutral crystalline vacancy cells were computed later,\n\\cref{ch:mono-w-vac}; charge states were not)."),
    ("Between 1 and 2~nm the change of the gap lies entirely in the conduction band, and the band\nedges are bulk-like, not surface states.",
     "Between 1 and 2~nm the change of the gap lies entirely in the conduction band, and at 2~nm the band\nedges are bulk-like, not surface states."),
    ("Tungsten substitutes on the 24d site as W$^{6+}$; within PBE its donated electrons\nfill the host conduction band, and a W-5d-derived level resonant 1.2--1.8~eV above the band bottom takes up electrons\nonly at very high filling (preliminary).",
     "Tungsten substitutes on the 24d site with W--O bonds consistent with W$^{6+}$; within PBE, at the computed filling of\nthree electrons per cell, its donated electrons fill the host conduction band, and a W-5d-rich level resonant\n1.2--1.8~eV above the band bottom lies near $E_F$; that W stays ionised at device densities is inferred, not computed."),
    ("\\cref{ch:v2}. The W effect on confinement is pending.\n\\end{keyresult}",
     "\\cref{ch:v2}. Results logged after 5 October 2026 (masses on a stated basis, sub-nanometre films, the W cells at\n2~nm, oxygen vacancies, hole masses) are in \\cref{sec:mono-dft-thin,ch:mono-masses,ch:mono-w-vac}.\n\\end{keyresult}"),
    # --- new section on the sub-nanometre films, inserted before the status section
    ("% =====================================================================================================================\n\\section{Pending results and changes to the device model}\n\\label{sec:dft-pending}",
     r"""% =====================================================================================================================
\section{Sub-nanometre films: the limit of the slab recipe}
\label{sec:mono-dft-thin}
% Added in the monograph revision. Source: RESULTS_LOG 2026-10-14 entry "0.51 nm and 0.75 nm slabs logged" (claim C021),
% re-derived from the raw outputs in qe_workflow/analysis_2026-10-13_full (f05, f08, f06).

The recipe of \cref{sec:dft-slabstruct} was applied with two and one cation planes (nominal 0.75 and 0.51~nm). Both
films were relaxed on one H100 NVL GPU each (QE 7.3.1, \texttt{cell\_dofree = '2Dxy'}, $10^{-3}$~Ry/bohr, $3\times3\times1$
$k$ points) and recomputed with the CPU build of QE 7.5 (SCF to $10^{-9}$~Ry, bands along [100] and [110], planar
average, projections), with the settings of the 1 and 2~nm films and no dipole correction (cluster 12835386, finished
6 October 2026). \Cref{tab:mono-dft-thin} lists the results \claim{C021}.

\begin{table}[htbp]\centering\small
\caption{Relaxed sub-nanometre \InO{}(001) films (PAW-PBE, 71/568~Ry). Gaps are the HOMO--LUMO differences of the SCF;
$\Delta\Eg$ is relative to the bulk gap of 0.8887~eV \fact{002}; $\dEc$ and $\Delta E_{\mathrm{v}}$ follow from the 2~nm
two-step value and the EA/IP differences (signed convention). Masses: in-plane, four-point basis.}
\label{tab:mono-dft-thin}
\begin{tabular}{lcc}\toprule
 & nominal 0.51~nm & nominal 0.75~nm \\\midrule
composition & In$_8$O$_{24}$H$_{24}$ = In$_8$(OH)$_{24}$ & In$_{16}$O$_{36}$H$_{24}$ \\
thickness H--H / O--O (nm) & 0.461 / 0.305 & 0.695 / 0.542 \\
in-plane cell (\AA) & $10.696\times10.019$ & $10.428\times10.293$ \\
symmetry operations & 8 & 4 \\
BFGS steps; largest force component (Ry/bohr) & 82; $5.4\times10^{-4}$ & 78; $9.9\times10^{-4}$ \\
gap (eV) & 3.1401 \fact{016} & 2.1986 \fact{017} \\
$\Delta\Eg$ (eV) & $+2.251$ & $+1.310$ \\
EA / IP (eV) & 3.192 / 6.332 & 3.717 / 5.916 (mean vacuum level) \\
$\dEc$ / $\Delta E_{\mathrm{v}}$ (eV) & $+1.585$ / $-0.667$ & $+1.059$ / $-0.251$ \\
in-plane CB mass [100] / [110] ($m_0$) & 0.428 / 0.445 & 0.335 / 0.338 \\
$E_2 - E_1$ at $\Gamma$ (eV) & 1.887 & 1.815 \\
VB-top character & O 2p, 98\,\% on OH oxygens & O 2p, 75\,\% on OH oxygens \\\bottomrule
\end{tabular}
\end{table}

\begin{figure}[htbp]\centering
\includegraphics[width=\linewidth]{fig05_slab_series_levels}
\caption{Relaxed \InO{}(001) films from 0.461 to 1.962~nm (H--H thickness), PAW-PBE. (a) Conduction-band minimum and
valence-band maximum on the vacuum scale. (b) Planar-averaged electrostatic potential relative to the vacuum level,
centred on each film. The 0.695~nm film shows a vacuum asymmetry (its two vacuum plateaus differ by 106~meV; ramp
$-13.6$~meV/\AA), because it is polar and was computed without a dipole correction. Source:
\file{qe_workflow/analysis_2026-10-13_full/f05_slab_series.py}.}
\label{fig:mono-dft-thin-levels}
\end{figure}

\paragraph{The 0.461~nm film is not an oxide film.} After relaxation every O atom is bonded to an H atom and every In is
six-fold coordinated: the film is exactly In$_8$(OH)$_{24}$, an indium-hydroxide-like layer. The recipe, which removes
oxygen and adds hydrogen until the electron count closes, has reached its limit. The point is reported, but it lies
outside the termination model of the thicker films and is excluded from every thickness law \claim{C021}.

\paragraph{The 0.695~nm film is polar.} With two cation planes the recipe cannot produce two equivalent faces: the film
keeps 4 of the 8 symmetry operations, and the operation that maps one face onto the other is lost. Without a dipole
correction \citep{Bengtsson1999} the vacuum potential has a ramp of $-13.6$~meV/\AA, i.e.\ $-347$~meV across the vacuum
gap, and the two vacuum-side plateaus differ by 106~meV (against 27~meV recorded earlier). EA, IP and therefore $\dEc$
depend on which vacuum reference is used: $\dEc(0.695~\mathrm{nm}) = 1.059$~eV with a reference-choice sensitivity of
$\pm0.17$~eV (half the ramp; an assumed sensitivity, not an error bound) \fact{018}. The gap does not depend on the
vacuum reference, but how the artificial field changes it has not been tested. The point is therefore excluded from any
new primary fit of $\dEc$ until a dipole-corrected SCF exists; the frozen laws that already include it are kept with this
caveat (\cref{ch:mono-masses}).

\paragraph{Character of the valence-band top.} In the two thinnest films the highest valence state lies mainly on the
OH oxygens (98 and 75\,\%; \texttt{projwfc.x}, $k$-weighted), unlike the 2~nm film, where it is a bulk-like confined
state. In these films the valence-band shift therefore measures the termination as much as confinement, and only the
gap and the conduction-band quantities are used further.

% =====================================================================================================================
\section{Pending results and changes to the device model}
\label{sec:dft-pending}"""),
    # 47: the monograph redefines \file as a breakable \nolinkurl, which cannot take "#" inside a tabularx.
    ("projwfc.x output and \\file{pdos/*(W)_wfc#*(d)} files",
     "projwfc.x output and \\texttt{pdos/*(W)\\_wfc\\#*(d)} files"),
]


def main():
    text = SRC.read_text()
    for i, (old, new) in enumerate(PATCHES, 1):
        n = text.count(old)
        if n != 1:
            sys.exit(f"patch {i}: expected 1 occurrence, found {n}: {old[:90]!r}")
        text = text.replace(old, new)
    DST.write_text(text)
    print(f"{len(PATCHES)} patches applied -> {DST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
