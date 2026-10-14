"""Synthetic QE 7.3.1-format relax.out cases for the D-24 tests (toy 3-atom cell; geometry g has In x = 5.00 + 0.01 g A).

usage: python3 make_cases.py <outdir>   -> <outdir>/relax.in and <outdir>/<case>.out, plus expected.txt
expected.txt: <case> <status> <expected In x in relax.in after the segment> <guard: armed|empty>
"""
import os
import sys

HEAD = """
     Program PWSCF v.7.3.1 starts on 11Oct2026 at  1:00:00

     number of atoms/cell      =            3
     number of electrons       =        25.00
"""


def pos(g, final=False):
    x = 5.0 + 0.01 * g
    return ("ATOMIC_POSITIONS (angstrom)\n"
            f"In            {x:.10f}        5.0000000000       15.0000000000\n"
            "O             6.0000000000        5.0000000000       15.0000000000\n"
            "O             4.0000000000        5.0000000000       15.0000000000\n")


def iters(n):
    return "".join(f"\n     iteration #{i:3d}     ecut=    60.00 Ry     beta= 0.20\n"
                   "     Davidson diagonalization with overlap\n"
                   f"     total energy              =    -100.0{i:02d}00000 Ry\n"
                   "     estimated scf accuracy    <       0.00100000 Ry\n" for i in range(1, n + 1))


def scf_ok(e, n=12):
    return (iters(n) + "\n     End of self-consistent calculation\n\n     the Fermi energy is     5.0000 ev\n\n"
            f"!    total energy              =  {e:15.8f} Ry\n"
            "     estimated scf accuracy    <       0.00000005 Ry\n"
            f"\n     convergence has been achieved in {n:3d} iterations\n\n"
            "     Forces acting on atoms (cartesian axes, Ry/au):\n\n"
            "     atom    1 type  1   force =     0.01000000    0.00000000    0.00000000\n"
            "     Total force =     0.010000     Total SCF correction =     0.000010\n")


def scf_fail(n=200):
    return (iters(3) + "\n     End of self-consistent calculation\n\n"
            f"     convergence NOT achieved after {n} iterations: stopping\n")


def bfgs_step(g, e):
    return ("\n     BFGS Geometry Optimization\n\n"
            f"     number of scf cycles    = {g:3d}\n     number of bfgs steps    = {g-1:3d}\n\n"
            f"     energy   new            =  {e:15.10f} Ry\n\n     new trust radius        =       0.0500000000 bohr\n"
            "     new conv thresholds     =       0.0000100000\n\n" + pos(g) + "\n\n\n"
            "     Writing output data file ./tmp/rlx.save/\n")


def final_block(g, msg):
    return (f"\n{msg}\n     (criteria: energy <  1.0E-04 Ry, force <  1.0E-03 Ry/Bohr)\n\n"
            "     End of BFGS Geometry Optimization\n\n     Final energy   =    -100.0000000000 Ry\n\n"
            "     File ./tmp/rlx.bfgs deleted, as requested\nBegin final coordinates\n\n" + pos(g, True) +
            "End final coordinates\n")


def tail_timelimit():
    return ("\n     Maximum CPU time exceeded\n\n     max_seconds     =   70184.00\n     elapsed seconds =   70185.12\n")


END = "\n     PWSCF        :     19h30m CPU     19h30m WALL\n\n   JOB DONE.\n"

CASES = {
    # name: (text, status, expected In-x geometry index, guard)
    'T1_bfgs_converged': (HEAD + scf_ok(-100.0) + bfgs_step(1, -100.0) + scf_ok(-100.2) + bfgs_step(2, -100.2) +
                          scf_ok(-100.25) + final_block(2, "     bfgs converged in   3 scf cycles and   2 bfgs steps") + END,
                          'CONVERGED', 2, 'empty'),
    'T2_bfgs_failed_finalcoords': (HEAD + scf_ok(-100.0) + bfgs_step(1, -100.0) + scf_ok(-100.3) + bfgs_step(2, -100.3) +
                                   scf_ok(-100.1) + bfgs_step(3, -100.1) + scf_ok(-100.2) + bfgs_step(4, -100.2) +
                                   final_block(4, "     bfgs failed after   4 scf cycles and   3 bfgs steps, convergence not achieved") + END,
                                   'CONTINUE', 1, 'empty'),
    'T2b_maxsteps_finalcoords': (HEAD + scf_ok(-100.0) + bfgs_step(1, -100.0) + scf_ok(-100.3) + bfgs_step(2, -100.3) +
                                 scf_ok(-100.1) + bfgs_step(3, -100.1) +
                                 final_block(3, "     The maximum number of steps has been reached.") + END,
                                 'CONTINUE', 1, 'empty'),
    'T3_scf_not_achieved_after_steps': (HEAD + scf_ok(-100.0) + bfgs_step(1, -100.0) + scf_ok(-100.2) + bfgs_step(2, -100.2) +
                                        scf_fail() + END, 'FAILED', 0, 'armed'),
    'T4_timelimit_midscf_with_steps': (HEAD + scf_ok(-100.0) + bfgs_step(1, -100.0) + scf_ok(-100.2) + bfgs_step(2, -100.2) +
                                       scf_ok(-100.15) + bfgs_step(3, -100.15) + iters(40) + tail_timelimit() + END,
                                       'CONTINUE', 1, 'empty'),
    'T5_no_new_validated_step': (HEAD + scf_ok(-100.0) + bfgs_step(1, -100.0) + iters(150) + tail_timelimit() + END,
                                 'FAILED', 0, 'armed'),
    'T5b_first_scf_cut': (HEAD + iters(150) + tail_timelimit() + END, 'FAILED', 0, 'armed'),
    'T5c_no_output': ('', 'FAILED', 0, 'armed'),
}

if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'relax.in'), 'w') as f:
        f.write("&CONTROL\n  calculation = 'relax', prefix = 'rlx', outdir = './tmp', pseudo_dir = './pseudo'\n"
                "  verbosity = 'low', tprnfor = .true., max_seconds = 1.0d8\n"
                "  nstep = 400, etot_conv_thr = 1.0d-4, forc_conv_thr = 1.0d-3\n/\n"
                "&SYSTEM\n  ibrav = 0, nat = 3, ntyp = 2, ecutwfc = 60, ecutrho = 480\n"
                "  occupations = 'smearing', smearing = 'mv', degauss = 0.01\n/\n"
                "&ELECTRONS\n  conv_thr = 1.0d-7, mixing_beta = 0.2, electron_maxstep = 200\n/\n&IONS\n  ion_dynamics = 'bfgs'\n/\n"
                "ATOMIC_SPECIES\n  In 114.818 In.pbe-dn-kjpaw_psl.1.0.0.UPF\n  O 15.999 O.pbe-n-kjpaw_psl.1.0.0.UPF\n"
                "CELL_PARAMETERS angstrom\n  10.0 0.0 0.0\n  0.0 10.0 0.0\n  0.0 0.0 30.0\n"
                "ATOMIC_POSITIONS angstrom\n  In 5.0000000000 5.0000000000 15.0000000000\n"
                "  O 6.0000000000 5.0000000000 15.0000000000\n  O 4.0000000000 5.0000000000 15.0000000000\n"
                "K_POINTS automatic\n  2 2 1 0 0 0\n")
    with open(os.path.join(out, 'expected.txt'), 'w') as ex:
        for name, (text, st, g, guard) in CASES.items():
            if text:
                with open(os.path.join(out, name + '.out'), 'w') as f:
                    f.write(text)
            ex.write(f"{name} {st} {5.0 + 0.01 * g:.10f} {guard}\n")
