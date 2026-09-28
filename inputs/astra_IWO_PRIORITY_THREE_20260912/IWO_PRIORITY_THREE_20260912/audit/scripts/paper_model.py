"""Paper-supported DOS revision with native interface traps; no simulator launch."""
import argparse,json,re,math
from pathlib import Path
from generate_picture_transfer import render as baseline
from iwo_model import ROOT, load_config,cox,Q


def render(cfg, key, smoke=False):
    p=cfg['paper_traps']
    for field in ('interface_levels_a','interface_levels_d'):
        if not isinstance(p[field],int) or isinstance(p[field],bool) or p[field]<1:
            raise ValueError(field+' must be a positive integer')
    if cfg.get('electrical_domain') not in (None,'full_stack','screened_active_stack'):
        raise ValueError('Unknown electrical domain')
    if cfg.get('substrate_electrical_model') not in (None,'ideal_equipotential'):
        raise ValueError('Unknown substrate electrical approximation')
    for field in ('bulk_acceptor_width_eV','oxygen_donor_width_eV','interface_acceptor_width_eV','capture_cm2'):
        if not math.isfinite(p[field]) or p[field]<=0:raise ValueError(field+' must be finite and positive')
    for field in ('bulk_acceptor_center_below_Ec_eV','oxygen_donor_center_below_Ec_eV','interface_acceptor_center_below_Ec_eV'):
        if not 0<=p[field]<=cfg['shared']['eg_eV']:raise ValueError(field+' must lie inside the bandgap')
    if not math.isfinite(p['oxygen_donor_peak_cm3_eV']) or p['oxygen_donor_peak_cm3_eV']<0:raise ValueError('Invalid oxygen donor peak')
    if p['back_surface_acceptor_peak_cm2_eV']!=0:raise ValueError('Back-surface DOS is not implemented/verified; do not silently enable it')
    if cfg.get('athena_structure_path') and any(cfg['numerics'][k]!=1 for k in ('x_mesh_scale','y_mesh_scale')):
        raise ValueError('Imported ATHENA mesh refinement requires a newly generated source mesh')
    if cfg.get('athena_structure_path') and cfg['curves'][key]['thickness_nm']!=cfg.get('athena_source_thickness_nm',2.0):
        raise ValueError('Requested channel thickness differs from the saved ATHENA source mesh')
    text, meta = baseline(cfg, key)
    precision=cfg['numerics'].get('precision_bits',64)
    if precision not in (64,80,128):raise ValueError('Only default and locally documented 80/128-bit launch modes are supported')
    if precision!=64:
        text=text.replace('go atlas\n',f'go atlas simflags="-{precision}"\n',1)
    meta['requested_precision_bits']=precision
    for axis in ('x','y'):
        scale=cfg['numerics'][axis+'_mesh_scale']
        text=re.sub(r'(^'+axis+r'\.mesh .*?spac=)([^\s]+)',lambda m:m.group(1)+f'{float(m.group(2))*scale:.10g}',text,flags=re.M)
    text = text.replace('Transfer test: constant mobility, no DOS traps.', 'Paper-based trial: constant mobility, bulk DOS and native interface Gaussian.')
    text = text.replace('NOT EXECUTED OR CALIBRATED. Convergence and current accounting require verification.',
        'DIAGNOSTIC INPUT. Numerical validation and calibration are not accepted; consult run records.')
    text = text.replace('# No interface/bulk DOS, tunnelling or quantum model in this debug baseline.', '# Bulk/interface DOS below; quantum/roughness/kinetic defect creation remain unvalidated.')
    p, c, s = cfg['paper_traps'], cfg['curves'][key], cfg['shared']
    sig = p['capture_cm2']
    dose = [
        '# Bulk tail + deep acceptor + oxygen-related Gaussian donor.',
        '# Peak amplitudes cm^-3/eV; widths eV. ND is a separate residual shallow term.',
        f'defects region=2 continuous numa={s["dos_levels_a"]} numd={s["dos_levels_d"]} \\',
        f' nta={c["nta_cm3_eV"]:.9g} wta={c["wta_eV"]:.9g} ntd=0 wtd=0.1 \\',
        f' nga={c["nga_cm3_eV"]:.9g} ega={p["bulk_acceptor_center_below_Ec_eV"]} wga={p["bulk_acceptor_width_eV"]} \\',
        f' ngd={p["oxygen_donor_peak_cm3_eV"]:.9g} egd={s["eg_eV"]-p["oxygen_donor_center_below_Ec_eV"]:.9g} wgd={p["oxygen_donor_width_eV"]} \\',
        f' sigtae={sig} sigtah={sig} sigtde={sig} sigtdh={sig} \\',
        f' siggae={sig} siggah={sig} siggde={sig} siggdh={sig} \\',
        ' afile=bulk_acceptor.dat dfile=bulk_donor.dat',
        '# Native IWO/Al2O3 Gaussian: no artificial interface volume.',
        '# MAX.GAUSSIAN explicitly selects peak amplitudes cm^-2/eV.',
        'intdefects continuous s.i intnumber="2/3" max.gaussian \\',
        f' nta=0 ntd=0 nga={c["interface_gaussian_peak_cm2_eV"]:.9g} ega={p["interface_acceptor_center_below_Ec_eV"]} wga={p["interface_acceptor_width_eV"]} \\',
        f' ngd=0 egd=0.4 wgd=0.1 numa={p["interface_levels_a"]} numd={p["interface_levels_d"]} \\',
        f' siggae={sig} siggah={sig} siggde={sig} siggdh={sig} \\',
        f' x.min=0 x.max={meta["x_bounds_um"][-1]:g} y.min=-1e-6 y.max=1e-6 \\',
        ' afile=interface_acceptor.dat dfile=interface_donor.dat tfile=interface_dos.dat',
        f'interface qf={-cox(cfg)*c["delta_vfb_V"]/Q:.9g} x.min=0 x.max={meta["x_bounds_um"][-1]:g} y.min=-1e-6 y.max=1e-6',
    ]
    if smoke:
        dose = ['# Trap-free geometric/parser diagnostic. Not a fit.']
    pos = text.index('method newton')
    text = text[:pos] + '\n'.join(dose) + '\n' + text[pos:]
    if cfg['numerics'].get('carrier_equations')=='electrons':
        text=text.replace('method newton','method newton carriers=1 electrons')
        meta['carrier_equations']='Electron continuity only; negligible-hole approximation requiring comparison'
    label=f'iwo_{key}nm_transfer'
    replacements={f'{label}_equilibrium.str':'equilibrium.str',f'{label}_off.str':'off.str',f'{label}_on.str':'final.str',f'{label}.log':'transfer.log',f'{label}_drain_signed.dat':'idvg.dat',f'{label}_source_signed.dat':'isvg.dat',f'{label}_gate_signed.dat':'igvg.dat',f'{label}_substrate_signed.dat':'ibvg.dat',f'{label}_drain_bias.dat':'vdvg.dat',f'{label}_source_bias.dat':'vsvg.dat',f'{label}_substrate_bias.dat':'vbvg.dat'}
    for a,b in replacements.items():text=text.replace(a,b)
    meta['current_exports']={name:replacements.get(value,value) for name,value in meta['current_exports'].items()}
    # Batch variants omit interactive TonyPlot only; raw structures/logs are retained.
    text='\n'.join(line for line in text.splitlines() if not line.startswith('tonyplot '))+'\n'
    if cfg.get('electrical_domain')=='screened_active_stack':
        if cfg.get('athena_structure_path'):
            raise ValueError('Screened active domain uses direct construction; full ATHENA mesh remains a separate process artifact')
        bottom=meta['y_boundaries_um'][-2]
        kept=[]
        for line in text.splitlines():
            if line.startswith('y.mesh ') and float(re.search(r'loc=([^ ]+)',line).group(1))>bottom:continue
            if line.startswith('region num=6 ') or line=='doping uniform n.type conc=1e19 region=6':continue
            if line.startswith('electrode num=4 ') or line.startswith('contact name=substrate '):continue
            if line.startswith('extract ') and 'substrate' in line:continue
            kept.append(line)
        text='\n'.join(kept)+'\n'
        text=text.replace('# Assume the wafer backside is connected to the gate bias.',
            '# Electrical domain ends at ideal TiN. The screened Si support remains in the ATHENA process structure.')
        text=text.replace('# Gate workfunction is an unfitted seed and also affects the TiN/Si interface.',
            '# Gate workfunction is an unfitted seed; substrate transport is outside this ideal-gate domain.')
        text=text.replace('# Current conservation must include source, drain, gate AND substrate.',
            '# Current conservation includes all three electrical terminals: Id + Is + Ig.')
        text=text.replace('# COMMON ties voltages; omit SHORT so substrate current remains separately observable.',
            '# No substrate current export exists in this explicitly truncated electrical domain.')
        text=text.replace('# Additional backside terminal on the explicit Si substrate.',
            '# The silicon support is represented in the separate full ATHENA process structure.')
        text=text.replace('Substrate shown as a 200 nm slice.', 'Electrical domain ends at TiN; full support is in the process deck.')
        text=text.replace('# n+Si doping=1e19 cm^-3 is a display assumption. IWO values are unfitted seeds.',
            '# The screened substrate is excluded from this electrical solve. IWO values are unfitted seeds.')
        meta['electrical_domain']='IWO/dielectrics/Pd/TiN; Si support screened by ideal gate, retained in separate ATHENA structure'
        meta['current_exports']={k:v for k,v in meta['current_exports'].items() if 'substrate' not in k}
        meta['current_conservation']='Id + Is + Ig; no substrate terminal in truncated electrical domain'
        meta['substrate_connection']='Excluded below ideal TiN gate'
        meta['y_boundaries_um']=meta['y_boundaries_um'][:-1]
    if cfg.get('athena_structure_path'):
        # Use the actual process mesh and embedded gate/source/drain electrodes.
        # Its coordinate origin is the original Si surface, not IWO/Al2O3.
        start=text.index('# 1. Mesh:')
        end=text.index('# 4. Doping and user material declaration.')
        prefix=(f'mesh infile=source_athena.str width={cfg["geometry"]["simulation_width_um"]:g}\n'
                '# Imported region5 is the custom IWO semiconductor.\n'
                'region modify num=5 user.material=IWO user.group=semiconductor\n'
                'electrode num=4 name=substrate bottom\n\n')
        text=text[:start]+prefix+text[end:]
        text=text.replace('conc=1e19 region=6','conc=1e19 region=1')
        text=text.replace('region=2','region=5').replace('intnumber="2/3"','intnumber="5/4"')
        if cfg.get('substrate_electrical_model')=='ideal_equipotential':
            text=text.replace('electrode num=4 name=substrate bottom',
                '# Ideal equipotential support; original n+Si process structure is preserved.\n'
                '# Gate and ideal support form one connected electrode, not two touching terminals.\n'
                f'electrode num=1 name=gate material=Conductor x.min=0 x.max={meta["x_bounds_um"][-1]:g} y.min={-cfg["geometry"]["gate_metal_nm"]/1000:g} y.max=0.2')
            text=text.replace('doping uniform n.type conc=1e19 region=1\n','')
            text='\n'.join(l for l in text.splitlines() if not l.startswith('contact name=substrate') and not (l.startswith('extract ') and 'substrate' in l))+'\n'
            meta['substrate_electrical_model']='Entire support is an ideal electrode; no substrate resistance/depletion/contact transport'
            meta['current_exports']={k:v for k,v in meta['current_exports'].items() if 'substrate' not in k}
            meta['current_conservation']='Id + Is + Ig; ideal support belongs to the gate'
            text=text.replace('# Current conservation must include source, drain, gate AND substrate.',
                '# Current conservation includes source, drain and the single gate/support electrode.')
        boundary=-(cfg['geometry']['gate_metal_nm']+cfg['geometry']['hfo2_nm']+cfg['geometry']['al2o3_nm'])/1000
        text=text.replace('y.min=-1e-6 y.max=1e-6',f'y.min={boundary-1e-6:.10g} y.max={boundary+1e-6:.10g}')
        meta['geometry_source']='Actual saved ATHENA mesh; source hash retained in execution record'
        meta['imported_region_map']={'Si':1,'gate':2,'HfO2':3,'Al2O3':4,'IWO':5,'source':6,'drain':7}
    meta.update(status='PAPER_DOS_TRIAL_NOT_CALIBRATED',smoke=smoke,electrical_model='Bulk tail/deep acceptor/oxygen donor plus native front-interface Gaussian',paper_traps=p)
    return text,meta


if __name__=='__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--config',type=Path,default=ROOT/'config/paper_revision.json')
    cli.add_argument('--out',type=Path,default=ROOT/'decks_paper_revision')
    cli.add_argument('--key',choices=['2p0','6p3','13p2','31p8'])
    args=cli.parse_args()
    if not args.out.resolve().is_relative_to(ROOT):raise ValueError('Generated decks must remain in this project')
    cfg=load_config(args.config)
    for key in [args.key] if args.key else cfg['curves']:
        dest=args.out/key;dest.mkdir(parents=True,exist_ok=True)
        text,meta=render(cfg,key)
        # User-facing copy opens every retained structure and log.
        text=text.rsplit('quit',1)[0]+'tonyplot equilibrium.str\ntonyplot off.str\ntonyplot final.str\ntonyplot transfer.log\nquit\n'
        (dest/f'iwo_{key}nm_paper.in').write_text(text,encoding='ascii')
        (dest/'metadata.json').write_text(json.dumps(meta,indent=2))
        if cfg.get('athena_structure_path'):
            import shutil
            source=(ROOT/cfg['athena_structure_path']).resolve()
            if not source.is_relative_to(ROOT):raise ValueError('ATHENA source must stay in project')
            shutil.copy2(source,dest/'source_athena.str')
        print(dest/f'iwo_{key}nm_paper.in')
