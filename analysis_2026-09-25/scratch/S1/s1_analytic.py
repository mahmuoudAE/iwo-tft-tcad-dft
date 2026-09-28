"""S1 analytic dimensional electrostatics (order-of-magnitude). Constants from EVIDENCE_BRIEF sec.1 and config/iwo_material_model.yaml."""
import numpy as np
q = 1.602176634e-19; eps0 = 8.8541878128e-14; kT = 0.025852
COX = 8.955369814335959e-7; CQ = COX / q; es = 9.3 * eps0
T = [2.0, 6.3, 13.2, 31.8]
print(f"Cox/q = {CQ:.3e} cm^-2/V ; q/Cox = {1e12/CQ:.4f} V per 1e12 cm^-2")
print('\n1) Debye length L_D = sqrt(eps kT/(q^2 n)) [nm]')
for n in [1e16, 2.5e17, 3e17, 1e18, 3e18, 1e19]:
    print(f"   n = {n:.1e}: L_D = {np.sqrt(es*kT/(q*n))*1e7:6.2f} nm")
print('   trap-screening length L_t = sqrt(eps WTA/(q n_t)), WTA = 0.040 V (exponential tail, E_F below the tail states)')
for nt in [1e18, 2e18, 5e18, 7e18]:
    print(f"   n_t = {nt:.1e}: L_t = {np.sqrt(es*0.040/(q*nt))*1e7:5.2f} nm")
print('\n2) Depletion width W = Q_s/N_d [nm] (full depletion if W >= t)')
for Nd in [2.5e17, 1e18, 3e18]:
    print(f"   Nd {Nd:.1e}: " + ', '.join(f"Qs {Qs:.2g}: {Qs/Nd*1e7:7.1f}" for Qs in [1e11, 5e11, 1e12, 1.64e12, 3e12]))
print('   Donor sheet N_d*t (cm^-2) of the V1 law and its Vth weight q Nd t/Cox:')
for t in T:
    Nd = 2.5e17 * (1 + (t/20)**4)
    print(f"   t {t}: Nd {Nd:.2e}, Nd t = {Nd*t*1e-7:.2e} cm^-2, qNdt/Cox = {Nd*t*1e-7/CQ:.3f} V, qNd t^2/(2 eps) = {q*Nd*(t*1e-7)**2/(2*es):.3f} V")
print('\n3) Lever arm of a sheet charge [V per 1e12 cm^-2]: front 1/Cox ; back-surface referenced to the back (1/Cox + t/eps_s)')
for t in T:
    r = COX * t * 1e-7 / es
    print(f"   t {t}: front {1e12/CQ:.3f} ; back {1e12/CQ*(1+r):.3f} (x{1+r:.2f}) ; IWO 'EOT' t*3.9/9.3 = {t*3.9/9.3:.2f} nm vs stack EOT 3.86 nm")
print('\n4) Gate depletion capacity between Vth and Vg = -3 V: Cox (Vth+3)/q')
for t, v in [(2.0, 0.662), (6.3, 0.644), (13.2, 0.083)]:
    print(f"   t {t}: {(v+3)*CQ:.2e} cm^-2  (-> a neutral layer of sheet density above this is not depletable at -3 V)")
print('   31.8 nm always on: Id(-3 V) >= 2.6e-7 A/um needs free sheet n = I L/(q mu Vd):')
for mu in [50.2, 82.5]:
    print(f"   mu {mu}: n_s = {2.6e-7*1e4*20e-4/(q*mu*0.7):.2e} cm^-2")
print('\n5) Measured Vth_cc steps expressed as sheet charge (q/Cox = 0.179 V per 1e12):')
for name, dv in [('2 -> 6.3', 0.644-0.662), ('6.3 -> 13.2', 0.083-0.644), ('2 -> 13.2', 0.083-0.662), ('6.3 validation miss', 0.644-0.350), ('6.3 tuned Vth_lin miss', 1.820-1.471)]:
    print(f"   {name}: dV {dv:+.3f} V = {dv*CQ:+.2e} cm^-2 ; over 6.3 nm {dv*CQ/6.3e-7:+.2e} cm^-3 ; over 13.2 nm {dv*CQ/13.2e-7:+.2e} cm^-3")
print('\n6) Confinement difference predicted between 2 and 6.3 nm: V1 law dEc(2)-dEc(6.3) = %.3f eV; infinite well h^2/(8 m* t^2): %.3f eV' % (
    0.9205*2**-1.3815 - 0.9205*6.3**-1.3815, 0.3760/(0.257*4) - 0.3760/(0.218*6.3**2)))
