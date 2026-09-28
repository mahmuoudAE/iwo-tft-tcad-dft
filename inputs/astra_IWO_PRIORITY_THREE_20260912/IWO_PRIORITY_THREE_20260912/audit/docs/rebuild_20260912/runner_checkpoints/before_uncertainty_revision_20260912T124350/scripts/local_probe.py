"""Bounded genuine DeckBuild probe. No synthetic simulation outputs."""
import argparse, hashlib, json, os, re, shutil, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
from owned_process_lifecycle import ensure_no_pending_owned, wait_owned_tree
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results/local_session_20260910'
def now(): return datetime.now(timezone.utc).isoformat()
def remaining_budget_seconds():
    budget=json.loads((BASE/'session_budget.json').read_text())
    deadline=datetime.fromisoformat(budget['deadline_utc']).timestamp()
    return deadline-time.time()

def run(*args,**kwargs):
    # Hold through observed owned descendants and bounded output draining.
    import msvcrt
    lockpath=ROOT/'tmp/atlas_single_process.lock';lockpath.parent.mkdir(exist_ok=True)
    with lockpath.open('a+b') as lock:
        lock.seek(0,2)
        if lock.tell()==0:lock.write(b'0');lock.flush()
        lock.seek(0)
        try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        except OSError as exc:raise RuntimeError('Another task-owned simulator run holds the project lock') from exc
        try:return _run(*args,**kwargs)
        finally:lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)

def _run(argv_template, deck_text, label, timeout=900, dest=None, config=None, verbose=True, input_artifacts=None):
    BASE.mkdir(exist_ok=True)
    index=BASE/'run_index.jsonl'
    events=[json.loads(s) for s in index.read_text().splitlines()] if index.exists() else []
    starts=[e for e in events if e['event']=='start']
    budget=json.loads((BASE/'session_budget.json').read_text())
    maximum_launches=budget.get('maximum_launches',60)
    families=re.findall(r'^\s*go\s+(\w+)',deck_text,re.M|re.I)
    reserved_launches=max(1,len(families))
    used_launches=sum(e.get('reserved_simulator_launches',1) for e in starts)
    if used_launches+reserved_launches>maximum_launches:
        raise RuntimeError(f'{maximum_launches}-launch cumulative budget exhausted or insufficient for {reserved_launches} simulator stages')
    remaining=remaining_budget_seconds()
    if remaining<=0:
        raise RuntimeError('Overall session wall-time budget exhausted. Additional runtime requires explicit user approval; do not reset the budget automatically.')
    timeout=min(float(timeout),remaining)
    if timeout<=0:raise RuntimeError('No positive runtime remains for a simulator launch')
    lifecycle_guard=ROOT/'tmp/atlas_owned_process_pending.json'
    ensure_no_pending_owned(lifecycle_guard)
    runid=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%f')+'_'+label
    dest=Path(dest) if dest is not None else BASE/'runs'/runid
    if not dest.resolve().is_relative_to(ROOT):raise RuntimeError('Run destination must stay in project')
    dest.mkdir(parents=True,exist_ok=False)
    artifact_records={}
    for name,source in (input_artifacts or {}).items():
        if Path(name).name!=name:raise RuntimeError('Artifact name must be a plain filename')
        source=Path(source).resolve()
        if not source.is_relative_to(ROOT):raise RuntimeError('Artifact source must stay in project')
        shutil.copy2(source,dest/name)
        artifact_records[name]={'source':str(source),'sha256':hashlib.sha256((dest/name).read_bytes()).hexdigest()}
    config=config or json.loads((ROOT/'config/model_seed.json').read_text())
    (dest/'input_config.json').write_text(json.dumps(config,indent=2))
    (dest/'device.in').write_text(deck_text,encoding='ascii')
    argv=[s.replace('{deck}','device.in').replace('{stdout}','deckbuild.out') for s in argv_template]
    family=re.search(r'^go\s+(\w+)',deck_text,re.M|re.I)
    record=dict(run_id=runid,event='start',timestamp=now(),command=argv,cwd=str(dest),deck_sha256=hashlib.sha256((dest/'device.in').read_bytes()).hexdigest(),config_sha256=hashlib.sha256((dest/'input_config.json').read_bytes()).hexdigest(),declared_simulator=family.group(1) if family else 'unknown',version_evidence='See fresh raw simulator banner; no version inferred from path',input_artifacts=artifact_records,parameters={'diagnostic':label,'curves':config['curves']},timeout_seconds=timeout)
    record.update(declared_simulators=families,reserved_simulator_launches=reserved_launches)
    env=os.environ.copy();env['TEMP']=str(ROOT/'tmp');env['TMP']=str(ROOT/'tmp')
    env['PATH']='C:\\sedatools\\exe;'+env['PATH']
    with (dest/'launcher_stdout.txt').open('wb') as out,(dest/'launcher_stderr.txt').open('wb') as err:
        # Preparation is part of the global allowance. Anchor before the fresh
        # UTC read, and never extend this deadline after bookkeeping or Popen.
        started=time.monotonic()
        remaining=remaining_budget_seconds()
        if remaining<=0:
            raise RuntimeError('Overall wall-time budget expired during preparation; no simulator launched')
        timeout=min(timeout,remaining);deadline=started+timeout
        record['timeout_seconds']=timeout
        record['deadline_monotonic']=deadline
        lifecycle_guard.parent.mkdir(parents=True,exist_ok=True)
        # Persist before Popen: any later crash/write error must block a second
        # engine until process ownership is reviewed or cleanly resolved.
        with lifecycle_guard.open('w',encoding='utf-8') as marker:
            json.dump(dict(run_id=runid,owned_processes=[],unobserved_children_possible=True,
                           status='LAUNCH_LIFECYCLE_NOT_YET_RESOLVED'),marker)
            marker.flush();os.fsync(marker.fileno())
        with index.open('a') as f:f.write(json.dumps(record)+'\n')
        status='LAUNCH_FAILED';code=None;lifecycle=None;proc=None;bookkeeping_error=None
        try:
            if time.monotonic()>=deadline:
                lifecycle_guard.unlink()  # no Popen occurred; no process can be owned
                status='BUDGET_EXPIRED_BEFORE_LAUNCH'
            else:
                proc=subprocess.Popen(argv,cwd=dest,stdout=out,stderr=err,env=env,creationflags=subprocess.CREATE_NO_WINDOW)
                try:
                    with index.open('a') as f:f.write(json.dumps(dict(event='spawn',run_id=runid,timestamp=now(),pid=proc.pid))+'\n')
                except OSError as exc:
                    bookkeeping_error=str(exc)
                # A spawn-index failure cannot bypass bounded owned cleanup.
                waited=wait_owned_tree(proc,dest,deadline,lifecycle_guard)
                code,status,lifecycle=waited['returncode'],waited['status'],waited['lifecycle']
                if bookkeeping_error is not None:
                    code,status=None,'POST_LAUNCH_BOOKKEEPING_FAILED'
                    lifecycle['bookkeeping_error']=bookkeeping_error
        except OSError as exc:err.write(str(exc).encode())
    raw=(dest/'deckbuild.out').read_text(errors='replace') if (dest/'deckbuild.out').exists() else ''
    record.update(process_lifecycle=lifecycle)
    record.update(actual_started_simulator_stages=re.findall(r'Version:\s*(atlas|athena)\s+[0-9]',raw,re.I))
    record.update(event='finish',timestamp=now(),elapsed_seconds=time.monotonic()-started,returncode=code,status=status,outputs={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir() if p.is_file()})
    (dest/'execution.json').write_text(json.dumps(record,indent=2))
    with index.open('a') as f:f.write(json.dumps(record)+'\n')
    print(dest,flush=True)
    if verbose:
        for name in ['launcher_stdout.txt','launcher_stderr.txt','deckbuild.out']:
            p=dest/name
            if p.exists(): print(name+'\n'+p.read_text(errors='replace')[-6000:])
    return dest
MINIMAL='''# Genuine silicon resistor diagnostic; not an IWO result.
go atlas
mesh width=1
x.mesh loc=0 spac=0.1
x.mesh loc=1 spac=0.1
y.mesh loc=0 spac=0.05
y.mesh loc=0.1 spac=0.05
region num=1 material=silicon
electrode num=1 name=source x.min=0 x.max=0 y.min=0 y.max=0.1
electrode num=2 name=drain x.min=1 x.max=1 y.min=0 y.max=0.1
doping uniform n.type conc=1e16
models srh print
solve init
save outf=equilibrium.str
log outf=probe.log
solve vdrain=0.01
solve vdrain=0.02
solve vdrain=0.03
log off
save outf=final.str
extract init infile="probe.log"
extract name="IdVd" curve(v."drain",i."drain") outfile="idvd.dat"
quit
'''
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--gui-batch',action='store_true');p.add_argument('--deck',type=Path);p.add_argument('--label',default='minimal');p.add_argument('--timeout',type=int,default=900);a=p.parse_args()
    argv=['C:/sedatools/exe/deckbuild.exe','-run']
    if not a.gui_batch:argv.append('-ascii')
    argv+=['{deck}','-outfile','{stdout}']
    run(argv,a.deck.read_text() if a.deck else MINIMAL,a.label,a.timeout)
