"""Read-only native DOS/occupied-charge audit for the genuine fit04 2 nm run.

Creates separate diagnostics only; never launches a simulator or changes raw data.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv
import json
import math
import re
import shlex
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RUN = ROOT / 'results/local_session_20260910/runs/20260912T074527_865393_fit_bulk_width04_2nm'
sys.path.insert(0, str(ROOT / 'scripts'))
import rebuild_dos_audit as dos
from rebuild_quantum_check import numeric_export
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    cfg = dos.load(RUN / 'input_config.json')
    manifest = dos.load(RUN / 'execution.json')
    output = (RUN / 'deckbuild.out').read_text(errors='replace')
    assert manifest['returncode'] == 0 and manifest['event'] == 'finish'
    assert re.search(r'ATLAS version 5\.28\.1\.R finished', output)
    capacity_audit = dos.audit(RUN)
    assert capacity_audit['parameter_audit_pass'] and not capacity_audit['warnings']
    assert capacity_audit['groups']['bulk']['enabled']
    assert not capacity_audit['groups']['interface']['enabled']
    group = capacity_audit['groups']['bulk']
    cap = group['exports']['afile']['components']['acceptor_total']['analytic_band_truncated_capacity']
    t_cm = cfg['curves']['2p0']['thickness_nm'] * 1e-7
    q = 1.602176634e-19
    files = ['device.in', 'input_config.json', 'deckbuild.out', 'transfer.log',
             'bulk_acceptor.dat', 'bulk_donor.dat', 'bulk_free_electrons_vg.dat',
             'bulk_ionized_acceptors_vg.dat', 'bulk_ionized_donors_vg.dat']
    hashes = {}
    for name in files:
        actual = dos.digest(RUN / name)
        expected = manifest['outputs'][name]
        assert actual == expected, f'Execution hash mismatch: {name}'
        hashes[name] = dict(sha256=actual, matches_execution_manifest=True)

    # Parse named native LOG probes and its observed terminal-column signature.
    lines = (RUN / 'transfer.log').read_text().splitlines()
    terminals = shlex.split(next(line for line in lines if line.startswith('f ')))[2:]
    names = [shlex.split(line)[2] for line in lines if line.startswith('o ')]
    header = list(map(int, next(line.split()[1:] for line in lines if line.startswith('p '))))
    assert terminals == ['gate', 'source', 'drain']
    assert names == ['channel_mobility', 'channel_electrons', 'bulk_free_electrons',
                     'bulk_ionized_acceptors', 'bulk_ionized_donors']
    assert header == [14, 2, 601, 20, 3, 602, 21, 4, 603, 22, 3000, 3001, 3002, 3003, 3004]
    rows = np.array([list(map(float, line.split()[1:])) for line in lines if line.startswith('d ')])
    assert rows.shape == (121, 14) and np.isfinite(rows).all()
    vg = rows[:, 0]
    assert np.allclose(vg, np.linspace(-3, 3, 121), rtol=0, atol=1e-9)
    assert np.allclose(rows[:, [3, 4]], 0, rtol=0, atol=1e-12)
    assert np.allclose(rows[:, [6, 7]], .7, rtol=0, atol=1e-12)
    n, acc, donor = rows[:, 11], rows[:, 12], rows[:, 13]
    assert np.all(n >= 0) and np.all(acc >= 0) and np.all(donor >= 0)
    assert np.all(acc <= cap * (1 + 1e-10)) and np.all(donor == 0)
    deck = (RUN / 'device.in').read_text()
    for name, selector in [('bulk_free_electrons','n.conc'), ('bulk_ionized_acceptors','concacc.ctrap'),
                           ('bulk_ionized_donors','concdon.ctrap')]:
        required = (f'probe name={name} region=2 average {selector} '
                    'x.min=2 x.max=22 y.min=-0.002 y.max=0')
        assert required in deck
    matching = {}
    for name, values in [('bulk_free_electrons', n), ('bulk_ionized_acceptors', acc), ('bulk_ionized_donors', donor)]:
        export, labels = numeric_export(RUN / (name + '_vg.dat'))
        export = np.asarray(export)
        assert export.shape == (121,2) and np.allclose(export[:,0], vg, rtol=0, atol=1e-9)
        assert np.allclose(export[:,1], values, rtol=5e-6, atol=0)
        nonzero = values != 0
        error = float(np.max(np.abs(export[nonzero,1] / values[nonzero] - 1))) if nonzero.any() else 0.
        matching[name] = dict(all_rows_match_native_log=True, maximum_relative_rounding_difference=error, labels=labels)

    records = []
    for index, gate in enumerate(vg):
        records.append(dict(vg_V=float(gate), free_n_cm3=float(n[index]), ionized_acceptors_cm3=float(acc[index]),
                            ionized_donors_cm3=float(donor[index]), free_sheet_cm2=float(n[index]*t_cm),
                            acceptor_sheet_cm2=float(acc[index]*t_cm), donor_sheet_cm2=float(donor[index]*t_cm),
                            free_charge_C_cm2=float(-q*n[index]*t_cm),
                            acceptor_charge_C_cm2=float(-q*acc[index]*t_cm),
                            donor_charge_C_cm2=float(q*donor[index]*t_cm),
                            acceptor_capacity_occupied_percent=float(100*acc[index]/cap),
                            trapped_fraction_free_plus_acceptor_percent=float(100*acc[index]/(acc[index]+n[index]))))
    table = [record for record in records if any(math.isclose(record['vg_V'], v, abs_tol=1e-9) for v in [.2,.5,1,2,3])]
    native_a = np.asarray(dos.read_ssf(RUN / 'bulk_acceptor.dat', dos.SIGNATURES[('bulk','a')])[0])
    native_d = np.asarray(dos.read_ssf(RUN / 'bulk_donor.dat', dos.SIGNATURES[('bulk','d')])[0])
    assert native_a.shape == (384,4) and native_d.shape == (192,4)
    assert np.all(native_a[:,2] == 0) and np.all(native_d[:,1:] == 0)
    for name, data, columns in [('native_charge_partition.csv',records,None),
                                ('native_bulk_acceptor_dos.csv',native_a,['energy_below_Ec_eV','tail_cm3_eV','gaussian_cm3_eV','total_cm3_eV'])]:
        with (OUT/name).open('w',newline='',encoding='utf-8') as handle:
            if columns is None:
                writer = csv.DictWriter(handle,fieldnames=list(data[0])); writer.writeheader(); writer.writerows(data)
            else:
                writer = csv.writer(handle); writer.writerow(columns); writer.writerows(data)
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(), run_directory=str(RUN.relative_to(ROOT)),
                  status='ACTUAL_NATIVE_DOS_AND_OCCUPIED_BULK_CHARGE_VERIFIED', native_rows=121,
                  capacity_cm3=cap, capacity_cm2=cap*t_cm,
                  native_average_box=dict(region=2,x_um=[2,22],y_um=[-.002,0],thickness_cm=t_cm),
                  native_dos=capacity_audit, hashes=hashes, exports_vs_log=matching, selected_biases=table,
                  all_donors_zero=True, all_acceptors_nonnegative_and_capacity_bounded=True,
                  free_density_range_cm3=[float(n.min()),float(n.max())],
                  ionized_acceptor_range_cm3=[float(acc.min()),float(acc.max())],
                  raw_current_zero_count=int(np.count_nonzero(rows[:,8] == 0)),
                  calibrated_all_point_transfer=False, chemical_species_identified=False,
                  note='Native AFILE is available capacity; solved LOG CONCACC.CTRAP is ionized/occupied acceptor density. '
                       'Sheet values are equivalent channel-average values, not midpoint cutlines or total gate charge.')
    (OUT/'audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')

    plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.labelsize':11,'figure.dpi':150})
    fig, axes = plt.subplots(1,2,figsize=(12,4.4))
    for ax, limit, title in zip(axes, [.4,3.05], ['Near the conduction edge','Full exported bandgap']):
        ax.semilogy(native_a[:,0],native_a[:,3],color='#ad5520',marker='o',markersize=2.6,lw=1.15,label='Native ATLAS total acceptor DOS')
        ax.set(xlim=(0,limit),xlabel=r'Energy below $E_C$ (eV)',ylabel=r'Available DOS (cm$^{-3}$ eV$^{-1}$)',title=title)
        ax.grid(alpha=.22); ax.legend(fontsize=8,loc='upper right')
    axes[0].set_ylim(1e16,1e21)
    axes[0].text(.035,.13,r'$g_A(E)=5.5\times10^{20}\exp[-(E_C-E)/0.04]$'+'\n'+r'Capacity: $2.2\times10^{19}$ cm$^{-3}$',transform=axes[0].transAxes,fontsize=9)
    axes[1].text(.04,.1,'Gaussian and donor DOS = 0\nInterface DOS disabled',transform=axes[1].transAxes,fontsize=9)
    fig.suptitle('2 nm IWO: native available bulk DOS (capacity, not occupancy)',y=.99)
    fig.text(.5,.015,'384 native acceptor samples; exported energy spacing is used directly. No extra degeneracy multiplier.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.055,1,.94)); fig.savefig(OUT/'native_bulk_dos.png',dpi=180); plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(12,4.6))
    axes[0].semilogy(vg,n*t_cm,color='#176c9c',lw=1.8,label='Free electrons')
    axes[0].semilogy(vg,acc*t_cm,color='#ad5520',lw=1.8,label='Ionized / occupied acceptors')
    axes[0].axhline(cap*t_cm,color='#777777',ls='--',label='Available acceptor capacity')
    axes[0].set(xlabel='Gate voltage (V)',ylabel=r'Channel-average sheet number (cm$^{-2}$)',title='Native solved populations')
    axes[0].text(.035,.13,'Ionized donors = 0 at every gate\n(zero is not placed on a logarithmic axis)',transform=axes[0].transAxes,fontsize=8.5)
    axes[1].plot(vg,-q*n*t_cm*1e6,color='#176c9c',lw=1.8,label='Free-electron charge')
    axes[1].plot(vg,-q*acc*t_cm*1e6,color='#ad5520',lw=1.8,label='Ionized-acceptor charge')
    axes[1].plot(vg,q*donor*t_cm*1e6,color='#444444',lw=1.2,ls=':',label='Ionized-donor charge (zero)')
    axes[1].set(xlabel='Gate voltage (V)',ylabel=r'Sheet charge ($\mu$C/cm$^2$)',title='Electrical charge sign retained')
    for ax in axes: ax.set_xlim(-3,3); ax.grid(alpha=.22); ax.legend(fontsize=8,loc='best')
    fig.suptitle('2 nm IWO: actual native free and trapped charge, Vd = 0.7 V',y=.99)
    fig.text(.5,.015,'REGION=2 AVERAGE, x=2..22 um, y=-0.002..0 um; sheet values = native average density × 2 nm.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.055,1,.94)); fig.savefig(OUT/'native_charge_partition.png',dpi=180); plt.close(fig)

    fig,ax=plt.subplots(figsize=(8,4.7))
    ax.plot(vg,100*acc/cap,color='#ad5520',lw=2,label='Acceptor capacity occupied: Nacc / Ncapacity')
    ax.plot(vg,100*acc/(acc+n),color='#6353a2',lw=2,label='Trapped share of counted electrons: Nacc / (Nacc + n)')
    ax.set(xlim=(-3,3),ylim=(0,101),xlabel='Gate voltage (V)',ylabel='Percent',title='Trap filling and electron partition are different quantities')
    ax.grid(alpha=.22); ax.legend(loc='center left',fontsize=8.5)
    fig.text(.5,.015,'Both ratios use native solved average densities. They do not identify an oxygen defect species.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.055,1,1)); fig.savefig(OUT/'native_occupancy_fractions.png',dpi=180); plt.close(fig)
    print(json.dumps({k:report[k] for k in ['status','capacity_cm3','capacity_cm2','selected_biases','exports_vs_log','raw_current_zero_count']},indent=2))


if __name__ == '__main__':
    main()
