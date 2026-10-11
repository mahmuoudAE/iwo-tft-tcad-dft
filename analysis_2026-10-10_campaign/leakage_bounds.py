"""Order-of-magnitude bounds for leakage mechanisms vs the measured off-state floors (A/um)."""
import math
q = 1.602176634e-19; h = 6.62607015e-34; hb = h / (2 * math.pi); m0 = 9.1093837015e-31; kT = 0.025852
floors = {2.0: 4.61e-15, 6.3: 1.53e-13, 13.2: 6.60e-12}
ni = {2.0: 1.48e-10, 6.3: 2.99e-8, 13.2: 7.18e-8}       # ATLAS-printed (runs 0038/0039/0040, deckbuild.out)
Nt = {2.0: 2.0e19, 6.3: 2.0e19 * (2 / 6.3) ** 0.75, 13.2: 2.0e19 * (2 / 13.2) ** 0.75}   # NTA*WTA (V1 law), cm^-3
L_cm = 20e-4; W_cm = 1e-4; sig = 1e-15; vth = 1.08e7
print('--- SRH generation bound: G <= ni/(tau_n+tau_p), tau = 1/(sigma v_th N_t)')
for t in floors:
    tau = 1 / (sig * vth * Nt[t]); G = ni[t] / (2 * tau); vol = L_cm * t * 1e-7 * W_cm
    I = q * G * vol
    print(f't={t:5.1f} nm  tau_min={tau:.2e} s  G_max={G:.2e} cm^-3 s^-1  I_SRH<= {I:.1e} A/um  floor {floors[t]:.2e}  ratio {I/floors[t]:.1e}')
    # even with a field enhancement of 1e10 (far above Hurkx/Dirac values at <= 4 MV/cm)
    print(f'            x1e10 TAT/PF enhancement -> {I*1e10:.1e} A/um')
print('--- Fowler-Nordheim from the gate, V_G = -3 V, all voltage across the stack')
eps = {'hf': 19.57, 'al': 9.0}; d_hf = 15e-7; d_al = 2e-7
E_hf = 3 / (d_hf + d_al * eps['hf'] / eps['al']); E_al = E_hf * eps['hf'] / eps['al']
print(f'E_HfO2 = {E_hf:.3e} V/cm, E_Al2O3 = {E_al:.3e} V/cm')
for phi, mr in [(2.2, 0.11), (2.2, 0.2), (2.7, 0.2), (1.8, 0.11)]:
    A = q ** 3 / (8 * math.pi * h * phi * q) / mr          # A/V^2 (SI)
    B = 8 * math.pi * math.sqrt(2 * mr * m0) * (phi * q) ** 1.5 / (3 * q * h)   # V/m
    E = E_hf * 100   # V/m
    J = A * E ** 2 * math.exp(-B / E) / 1e4    # A/cm^2
    I = J * 24e-4 * W_cm
    print(f'phi={phi} eV m*={mr}: B={B/100:.2e} V/cm  J={J:.1e} A/cm^2  I(24 um gate x 1 um)={I:.1e} A/um')
print('--- WKB direct tunnelling through 17 nm (rectangular barrier, upper bound)')
for phi, mr in [(1.8, 0.11), (2.2, 0.2)]:
    k = math.sqrt(2 * mr * m0 * phi * q) / hb
    print(f'phi={phi} m*={mr}: exp(-2 k d)={math.exp(-2*k*17e-9):.1e}')
print('--- FLDMOB relevance: lateral field and drift velocity')
for mu in (12, 60):
    E = 0.7 / L_cm; print(f'mu={mu}: E_lat={E:.0f} V/cm  v={mu*E:.2e} cm/s vs vsat~1e7')
print('--- ohmic strip needed for the floors: G = I/V_D')
for t in floors:
    print(f't={t}: G_par = {floors[t]/0.7:.2e} S/um ; R_par = {0.7/floors[t]:.2e} ohm.um')
