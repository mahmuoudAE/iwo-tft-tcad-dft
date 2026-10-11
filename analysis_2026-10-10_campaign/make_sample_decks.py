"""Generate (WITHOUT launching) sample decks of the 2026-10-10 campaign into sample_decks/ and list every solver statement
that is new or changed relative to the primary baseline deck of the same film (S0-01 / S1-01 / S1-02), each mapped to the
syntax reference of GENERATOR_AUDIT.md (manual page / installed example). Any statement without a reference is printed as
UNREVIEWED. Uses campaign_tools.entry_deck (same construction as run_atlas.execute / execute_strip; no simulator call).
  python analysis_2026-10-10_campaign/make_sample_decks.py"""
import difflib
import re
import sys

import campaign_tools as ct

OUT = ct.HERE / 'sample_decks'
MAIN = ['S0-01', 'S0-02', 'S2-14', 'S3-12', 'S3-17']          # 2 smoke runs + 3 representative later runs
EXTRA = ['S2-08', 'S2-10', 'S2-12', 'S3-07', 'S3-24', 'S6-27']  # remaining new statement types (gate FN, oxide TAT, tail split, BQP, in-solver strip)
BASE = {2.0: 'S0-01', 6.3: 'S1-01', 13.2: 'S1-02'}
REF = [   # (regex on a statement line, syntax reference) - GENERATOR_AUDIT.md section / manual PDF page / installed example
    (r'^x\.mesh |^y\.mesh ', 'mesh lines (existing statement; values only)'),
    (r'^ eg300=.* affinity=', 'MATERIAL eg300/affinity (existing; values from the DFT fit3 laws)'),
    (r'^ nc300=', 'MATERIAL nc300 (existing; quasi-2D value via nc300_override, audit 3.1)'),
    (r'^ mun=', 'MATERIAL mun (existing; value)'),
    (r'^ taun0=.* tmun=0', 'MATERIAL taun0/taup0/tmun (existing; tmun declared, state file K)'),
    (r'^ taun0=.* \\$', 'MATERIAL taun0/taup0 + continuation to option parameters (same statement)'),
    (r'^ arichn=', 'MATERIAL ARICHN (A/cm^2/K^2): audit 7.7, PDF p.159 Table 3-32'),
    (r'^ ml=.* mt1=.* mt2=', 'MATERIAL ML/MT1/MT2 (PDF p.1371 MATERIAL list); use as BQP mass tensor UNVERIFIED (audit 7.9)'),
    (r'^doping uniform n\.type conc=', 'DOPING uniform (existing; Nd constant / strip region 8)'),
    (r'^doping region=\d+ uniform tat\.trap conc=.* acceptor sign=.* sigp=.* e\.level=', 'DOPING TAT.TRAP: audit 7.5 table, PDF p.323-327 (Table 3-139 example), quantum/quantumex20'),
    (r'^material region=[34] affinity=.* eg300=.* me\.tunnel=', 'MATERIAL insulator affinity/eg300/me.tunnel: audit 7.5 table + 3.3, PDF p.303 (ME.TUNNEL or MC for the oxide mass)'),
    (r'^material region=(8|9) mun=', 'MATERIAL REGION= mun (region mobility): audit 7.11 B, PDF p.76; on a user.material region UNVERIFIED'),
    (r'^mobility material=IWO igzo\.tokyo mun=.* tmun=.* igzo\.gamma0=.* igzo\.tgamma=.* igzo\.ncrit=', 'MOBILITY IGZO.TOKYO: audit 7.4, PDF p.195-196 Table 3-61, tft/tftex21_aux.in l.124-125; user.material UNVERIFIED'),
    (r'^contact name=gate workfunction=[0-9.]+ qtunn\.cmass=', 'CONTACT QTUNN.CMASS: audit 7.5 table, PDF p.303 Table 3-132, diode/diodeex12'),
    (r'^contact name=(source|drain) workfun=.* surf\.rec( barrier)?( e\.tunnel me\.tunnel=[0-9.]+)? \^ins\.ohmic( exclude_near)?$', 'CONTACT WORKFUN/SURF.REC/BARRIER/E.TUNNEL/ME.TUNNEL/^INS.OHMIC: audit 7.7, PDF p.158-161, p.1151-1159, diode/diodeex10, organic/organicex04 (+ EXCLUDE_NEAR with QTNLSC: PDF p.303, p.1157)'),
    (r'^contact name=(source|drain)( resistance=[0-9.e+-]+)? exclude_near$', 'CONTACT EXCLUDE_NEAR (logical, default False): PDF p.303 "Contact Specifications" (manual text l.13699-13705: NEARFLG automatic for quantum tunnelling; EXCLUDE_NEAR removes an electrode from the nearest-electrode search) + Table 3-132; CONTACT parameter table PDF p.1152 (l.47953) and description p.1157 (l.48137); 5.28.1.R parser key common/atlas.key CONTACTS block "exclude_near LOG 27 f"; 2004 manual p.3-93. No installed example uses it. Added after run_0066 (pad slices booked to S/D)'),
    (r'^models fermi srh temp=300 print qtnlsc\.el qtnl\.derivs', 'MODELS QTNLSC.EL QTNL.DERIVS: audit 7.5, PDF p.301 Tables 3-128/3-129, diode/diodeex12'),
    (r'^qt[xy]\.mesh loc=-?[0-9.e-]+ spac=[0-9.e-]+$', 'QTX.MESH/QTY.MESH (rectangular tunnelling mesh over the insulator): PDF p.302 "Mesh Considerations", Table 3-130; statement 22.50 (PDF p.1542); added after run_0062 ran out of memory'),
    (r'^models fermi srh temp=300 print fnord f\.ae=.* f\.be=', 'MODELS FNORD F.AE F.BE: audit 7.5, PDF p.288 Table 3-126 (F.AE/F.BE on MODELS), eprom/eprmex01'),
    (r'^models fermi srh temp=300 print qtnlsc\.el qtnl\.derivs itat\.sc\.el \^tat\.poisson$', 'MODELS ITAT.SC.EL (+QTNLSC) ^TAT.POISSON: PDF p.323 (manual text l.14541-14548: trap charge out of Poisson, default True), PDF p.327 example "MODELS RTAT.SC TAT.SLICEPTS=21 ^TAT.POISSON"; quantum/quantumex20'),
    (r'^models fermi srh temp=300 print qtnlsc\.el qtnl\.derivs itat\.sc\.el','MODELS ITAT.SC.EL (+QTNLSC): audit 7.5, PDF p.326 Table 3-139, quantum/quantumex20'),
    (r'^models fermi srh temp=300 print bqp\.n bqp\.ngamma=.* bqp\.nalpha=.* bqp\.qdir=', 'MODELS BQP.N BQP.NGAMMA BQP.NALPHA BQP.QDIR: audit 7.9, PDF p.835-836 Table 14-3, quantum/quantumex05, solar/solarex18'),
    (r'^models fermi srh temp=300 print trap\.tunnel trap\.hurkx mass\.tunnel=', 'MODELS TRAP.TUNNEL TRAP.HURKX MASS.TUNNEL (existing solver.models route): audit 7.2, tft/tftex12'),
    (r'^log outf=transfer\.log j\.tun$', 'LOG J.TUN: audit 7.5 table, PDF p.289, p.1307 (J.TUN logical), diode/diodeex12'),
    (r'^extract name="IfnVg" curve\(v\."gate",ifn\."gate"\)', 'EXTRACT ifn."gate": audit 4 (DeckBuild manual printed p.150)'),
    (r'^defects region=(8|9) ', 'DEFECTS region=8/9 (existing statement on the strip bulk / interface-layer regions)'),
    (r'^ (nta|nga|ngd|sigtae|siggae|afile)=', 'DEFECTS continuation (existing; values / file names)'),
    (r'^interface qf=.* x\.min=27', 'INTERFACE QF on the in-solver strip (existing statement, new x range)'),
    (r'^region num=(3|4) material=(Al2O3|HfO2) x\.min=0 x\.max=30', 'REGION (existing; extended under the in-solver strip)'),
    (r'^region num=(8|9|10|11|12) ', 'REGION (existing statement; in-solver strip geometry, audit 7.11 B)'),
    (r'^electrode name=(source|drain) material=Palladium x\.min=(27|29\.5)', 'ELECTRODE same name, second volume: audit 7.11 B, PDF p.44, p.74 (connected, one current)'),
    (r'^method newton trap', 'METHOD (existing; strip acceptance by the transfer switch rule)'),
    (r'^ cr\.toler=', 'METHOD continuation (existing)'),
    (r'^probe |^solve |^log |^save |^output |^extract |^quit', 'SOLVE/LOG/SAVE/EXTRACT/PROBE (existing statements; strip drain sweep: audit 7.11 A)'),
    (r'^region num=7 |^electrode name=(source|drain) ', 'REGION/ELECTRODE (existing; strip length)'),
]


def ref(line):
    for rx, r in REF:
        if re.search(rx, line): return r
    return None


def main():
    mx = ct.matrix(); runs = {r['id']: r for r in mx['runs']}; OUT.mkdir(exist_ok=True); (OUT / 'extra').mkdir(exist_ok=True)
    base = {t: ct.statements(ct.entry_deck(runs[i]['campaign_entry'], ct.V3)[0]) for t, i in BASE.items()}
    md = ['# New or changed solver statements in the sample decks (generated by make_sample_decks.py; no launch)', '',
          'Model file: config/iwo_material_model_v3.yaml + the matrix overrides. Each deck is compared with the primary baseline deck of the same film '
          '(S0-01 / S1-01 / S1-02, itself compared with the V2 final run decks in IMPLEMENTATION.md). Only `+` lines are listed; `UNREVIEWED` = no syntax reference.', '']
    unreviewed = 0
    for i in MAIN + EXTRA:
        if i == 'S6-27':   # after-calibration entry: illustrative build at the S4 START values (13.2 nm baseline overrides) + in-solver strip
            e = dict(runs['S1-02']['campaign_entry'], id='S6-27', label='c10_s6_27_13p2_ILLUSTRATIVE_start_values')
            e['overrides'] = e['overrides'] + ['solver.physics_options.strip.mode=in_solver']
        else:
            e = runs[i]['campaign_entry']
        text, meta = ct.entry_deck(e, ct.V3); t = float(e['thickness'])
        sub = OUT if i in MAIN else OUT / 'extra'
        name = f'{i}_{e["label"]}' + ('_strip' if e.get('mode') == 'strip' else '') + '.in'
        (sub / name).write_text(text, encoding='ascii')
        new = [l[1:] for l in difflib.unified_diff(base[t], ct.statements(text), lineterm='', n=0) if l.startswith('+') and not l.startswith('+++')]
        md += [f'## {i} ({t:g} nm{", strip deck" if e.get("mode") == "strip" else ""}) -> `{sub.name}/{name}`', '', runs[i]['purpose'] if i in runs else '', '']
        if i == 'S6-27': md += ['ILLUSTRATIVE: S6-27 is an after-calibration entry; built here at the S4 start values with the default (W/L)_par 1e-4 /um.', '']
        md += ['| new / changed statement | syntax reference |', '|---|---|']
        for l in new:
            r = ref(l); unreviewed += r is None
            md.append(f'| `{l.strip()[:160]}` | {r or "UNREVIEWED"} |')
        md.append('')
        print(f'{i:6s} {t:>5} nm  {len(text.splitlines()):4d} lines  new/changed statements {len(new):3d}  -> {sub.name}/{name}')
    (OUT / 'NEW_STATEMENTS.md').write_text('\n'.join(md), encoding='utf-8')
    print('unreviewed statements:', unreviewed)
    return 1 if unreviewed else 0


if __name__ == '__main__':
    sys.exit(main())
