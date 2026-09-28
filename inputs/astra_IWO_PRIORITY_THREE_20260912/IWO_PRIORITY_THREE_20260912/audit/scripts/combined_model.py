"""Render one self-contained ATHENA -> ATLAS IWO process/electrical input."""
import argparse,copy,json,re
from pathlib import Path
import numpy as np
from iwo_model import ROOT,load_config
from paper_model import render as electrical

def render(cfg,key='2p0',probe=False,plots=False):
    cfg=copy.deepcopy(cfg)
    nm=cfg['curves'][key]['thickness_nm']
    for field,expected in [('channel_length_um',20),('contact_length_um',2),('gate_metal_nm',50),('hfo2_nm',15),('al2o3_nm',2),('source_drain_metal_nm',70)]:
        if cfg['geometry'][field]!=expected:raise ValueError(f'Process template does not implement changed {field}')
    if any(cfg['numerics'][axis+'_mesh_scale']!=1 for axis in ['x','y']):
        raise ValueError('Use a changed ATHENA process mesh, not an ignored electrical mesh scale')
    process_path=ROOT/f'decks_paper_revision/athena/iwo_{key}nm_process.in'
    process=process_path.read_text(encoding='utf-8').split('# Batch deck')[0]
    actual_um=float(re.search(r'^deposit material=IWO thick=([^ ]+)',process,re.M).group(1))
    if abs(actual_um*1000-nm)>1e-10:raise ValueError('Configured channel thickness differs from the ATHENA template')
    if re.search(r'^\s*quit\s*(?:#.*)?$',process,re.M|re.I):raise ValueError('Intermediate quit would prevent the ATLAS stage')
    if cfg.get('process_mesh',{}).get('mode','original')=='lateral_refined':
        from athena_mesh_candidate import lateral_candidate
        process=lateral_candidate(process,cfg['process_mesh'].get('center_spacing_um',0.2))
    elif cfg.get('process_mesh',{}).get('mode','original')!='original':
        raise ValueError('Unknown ATHENA process mesh mode')
    structure=f'iwo_{key}nm_athena_device.str'
    cfg['athena_structure_path']=structure
    cfg['athena_source_thickness_nm']=nm
    boundary_mode=cfg['contacts']['mode']
    if boundary_mode not in ('ohmic','schottky'):raise ValueError('Unknown contact boundary condition')
    render_cfg=copy.deepcopy(cfg)
    render_cfg['contacts']['mode']='ohmic'  # Geometry renderer; selected boundary is applied explicitly below.
    text,meta=electrical(render_cfg,key)
    if boundary_mode=='schottky':
        barrier=cfg['contacts']['effective_electron_barrier_eV']
        if not np.isfinite(barrier) or not 0<barrier<cfg['shared']['eg_eV']:raise ValueError('Invalid effective Schottky barrier')
        workfunction=cfg['shared']['affinity_eV']+barrier
        contact=('# Finite thermionic contact sensitivity. Richardson constants remain unvalidated priors.\n'
                 f'contact name=source workfunction={workfunction:.9g} surf.rec\n'
                 f'contact name=drain workfunction={workfunction:.9g} surf.rec\n')
        text=text.replace('# No interface/bulk DOS',contact+'# No interface/bulk DOS') if '# No interface/bulk DOS' in text else text.replace('models srh',contact+'models srh',1)
        text=text.replace('# Pd/IWO is assumed Ohmic here; no measured barrier is claimed.',
            '# Pd/IWO effective Schottky barrier sensitivity; not a measured bare Pd workfunction.')
        meta['sd_contacts']='Effective Schottky barrier sensitivity; not measured Pd/IWO contact physics'
        meta['effective_contact_barrier_eV']=barrier
    text=text.replace('mesh infile=source_athena.str',f'mesh infile={structure}')
    text=text.replace('Paper-based trial: constant mobility, bulk DOS and native interface Gaussian.',
                      'Paper-based trial: selected native mobility, bulk DOS and interface Gaussian.')
    if cfg.get('substrate_electrical_model')=='ideal_equipotential':
        text=text.replace('# Gate workfunction is an unfitted seed and also affects the TiN/Si interface.',
                          '# Gate workfunction is an unfitted seed at the gate/dielectric boundary.')
        text=text.replace('# Assume the wafer backside is connected to the gate bias.\n'
                          '# COMMON ties voltages; omit SHORT so substrate current remains separately observable.',
                          '# The screened support shares one ideal gate electrode; three terminal currents are exported.')
    # Both engines run in the same DeckBuild input and directory. ATLAS reads
    # only the structure freshly created above, with no external source mesh.
    transport=cfg.get('transport',{})
    if transport.get('mode')=='tokyo_percolation':
        if not all(np.isfinite(transport[k]) for k in ['gamma0','tgamma_K','ncrit_cm3']) or transport['ncrit_cm3']<=0:
            raise ValueError('Transport coefficients must be finite and Ncrit positive')
        mu=cfg['curves'][key]['mu_band_cm2Vs']
        card=(f'mobility region=5 igzo.tokyo mun={mu:.9g} tmun={transport.get("tmun",1.5):.9g} '
              f'igzo.gamma0={transport["gamma0"]:.9g} '
              f'igzo.tgamma={transport["tgamma_K"]:.9g} '
              f'igzo.ncrit={transport["ncrit_cm3"]:.9g} print\n')
        text=text.replace('method newton',
            '# Density-dependent percolation mobility; IWO remains a custom material.\n'
            '# The keyword IGZO.TOKYO names the transport law, not the composition.\n'
            '# This is not an extra n_free/n_total mobility multiplier.\n'+card+'method newton',1)
    elif transport.get('mode','constant')!='constant':raise ValueError('Unknown transport law')
    diagnostics=cfg.get('diagnostics',{})
    probe_x=diagnostics.get('channel_probe_x_um',12)
    probe_fraction=diagnostics.get('channel_probe_depth_fraction',0.5)
    if not np.isfinite(probe_x) or not 2<probe_x<22:
        raise ValueError('Channel probe must lie between the Pd contacts')
    if not np.isfinite(probe_fraction) or not 0<probe_fraction<1:
        raise ValueError('Channel probe depth must lie strictly inside IWO')
    center=-(.067+nm*probe_fraction/1000)
    text=text.replace('output con.band val.band e.mobility',
        'output con.band val.band e.mobility\n'
        f'probe name=channel_mobility x={probe_x:.10g} y={center:.10g} n.mob dir=0\n'
        f'probe name=channel_electrons x={probe_x:.10g} y={center:.10g} n.conc')
    text=text.replace('extract init infile="transfer.log"',
        'extract init infile="transfer.log"\n'
        'extract name="channel_mobility_vs_vg" curve(v."gate",probe."channel_mobility") outfile="mobility_vg.dat"\n'
        'extract name="channel_electrons_vs_vg" curve(v."gate",probe."channel_electrons") outfile="electrons_vg.dat"')
    if diagnostics.get('compare_original_vertex',False):
        vertex_y=-(.067+nm/2000)
        extra=(f'probe name=vertex_mobility x=12 y={vertex_y:.10g} n.mob dir=0\n'
               f'probe name=vertex_electrons x=12 y={vertex_y:.10g} n.conc\n')
        text=text.replace('solve init',extra+'solve init',1)
        text=text.replace('extract init infile="transfer.log"',
            'extract init infile="transfer.log"\n'
            'extract name="vertex_mobility_vs_vg" curve(v."gate",probe."vertex_mobility") outfile="vertex_mobility_vg.dat"\n'
            'extract name="vertex_electrons_vs_vg" curve(v."gate",probe."vertex_electrons") outfile="vertex_electrons_vg.dat"')
    if probe:
        start=text.index('log outf=transfer.log')+len('log outf=transfer.log')
        end=text.index('log off',start)
        targets=np.linspace(-3,3,25)
        text=text[:start]+'\n'+'\n'.join(f'solve vgate={v:g}' for v in targets)+'\n'+text[end:]
        text=text.replace('All 121 workbook gate targets are explicit.','25-point execution/physics probe; not the full measured grid.')
    else:targets=np.arange(-3,3.00001,.05)
    header=('# Self-contained ATHENA + ATLAS IWO model. One file, two sequential engines.\n'
        '# Evidence: Januar2026 target process/DOS; Fan2021 IWO oxygen/percolation priors;\n'
        '# Abe2011 density-dependent drift transport. Other supplied models audited in accompanying notes.\n'
        '# Dark unstressed non-ferroelectric target: no HZO polarization or NBIS-generated defects.\n'
        '# Parameters are physical hypotheses; successful execution is not a calibrated fit.\n')
    text=header+process+'\n# Switch engines. Do not put QUIT between ATHENA and ATLAS.\n'+text
    text=text.replace('quit\n','')
    if plots:
        for name in (f'iwo_{key}nm_athena_channel.str',structure,'equilibrium.str','off.str','final.str','transfer.log'):
            text+=f'tonyplot {name}\n'
    text+='quit\n'
    meta.update(single_input=True,external_input_mesh_required=False,process_generated_mesh=structure,
        selected_thickness_nm=nm,requested_gate_points=targets.tolist(),probe=probe,
        transport=transport,process_mesh=cfg.get('process_mesh',{'mode':'original'}),
        channel_probe_xy_um=[probe_x,center],
        status='COMBINED_PROCESS_AND_ELECTRICAL_DIAGNOSTIC_NOT_CALIBRATED')
    return text,meta,cfg

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',type=Path,default=ROOT/'config/combined_schottky.json')
    p.add_argument('--key',default='2p0',choices=['2p0','6p3','13p2','31p8'])
    p.add_argument('--probe',action='store_true');p.add_argument('--batch',action='store_true')
    p.add_argument('--out',type=Path,default=ROOT/'decks_combined/IWO_ATHENA_ATLAS.in')
    a=p.parse_args();dest=a.out.resolve()
    if not dest.is_relative_to(ROOT):raise ValueError('Output must stay in project')
    text,meta,cfg=render(load_config(a.config),a.key,a.probe,not a.batch)
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='ascii')
    dest.with_suffix('.metadata.json').write_text(json.dumps(meta,indent=2))
    print(dest)

if __name__=='__main__':main()
