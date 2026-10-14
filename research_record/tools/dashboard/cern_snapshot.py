#!/usr/bin/env python3
# Read-only snapshot of the CERN ML+DFT pipeline (~/iwo_amorph) as JSON lines. Runs ON lxplus (python3.9, stdlib only).
# Never writes anything. Every external command has a timeout. One JSON object per line, field "k" = record kind.
import glob, json, os, re, socket, subprocess, time

T0 = time.time()
R = os.path.expanduser('~/iwo_amorph')
TAIL = 8192


def emit(k, **d):
    d['k'] = k
    print(json.dumps(d, separators=(',', ':'), default=str))


def sh(cmd, timeout=8):
    t = time.time()
    try:
        p = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, universal_newlines=True)
        return p.stdout, p.returncode, round(time.time() - t, 3)
    except Exception as e:  # timeout or missing binary
        return None, repr(e)[:120], round(time.time() - t, 3)


def st(path):
    try:
        s = os.stat(path)
        return {'size': s.st_size, 'mtime': int(s.st_mtime)}
    except OSError:
        return None


def rd(path, tail=None):
    try:
        with open(path, 'rb') as f:
            if tail:
                f.seek(0, 2)
                f.seek(max(0, f.tell() - tail))
            return f.read().decode('utf-8', 'replace')
    except OSError:
        return None


def jl(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


emit('meta', host=socket.gethostname(), now=int(time.time()), schema=1, root=R)

# ---- HTCondor queue (own jobs only; ~0.15 s) ----
QA = ('ClusterId,ProcId,JobBatchName,IWOJob,DAGNodeName,DAGManJobId,Cmd,Args,JobStatus,JobUniverse,QDate,'
      'JobCurrentStartDate,EnteredCurrentStatus,NumJobStarts,RequestGpus,RequestCpus,RequestMemory,JobFlavour,'
      'RemoteHost,AssignedGPUs,GPUsMemoryUsage,GPUsAverageUsage,ResidentSetSize,HoldReason,HoldReasonCode,ServerTime,'
      'DAG_Status,DAG_InRecovery,DAG_NodesTotal,DAG_NodesDone,DAG_NodesFailed,DAG_NodesQueued,DAG_NodesReady,'
      'DAG_NodesUnready,DAG_JobsIdle,DAG_JobsRunning,DAG_JobsHeld,DAG_JobsCompleted')
out, rc, dt = sh(['condor_q', '-json', '-attributes', QA])
ads = []
if out is not None and rc == 0:
    try:
        ads = json.loads(out) if out.strip() else []
    except ValueError:
        rc = 'badjson'
for a in ads:
    emit('job', **a)
emit('src', name='condor_q', rc=rc, sec=dt, n=len(ads))

# ---- HTCondor history (last 30 of own jobs; ~1 s) ----
HA = ('ClusterId,ProcId,JobBatchName,IWOJob,DAGNodeName,DAGManJobId,Cmd,JobStatus,ExitCode,ExitBySignal,'
      'CompletionDate,EnteredCurrentStatus,RemoteWallClockTime,NumJobStarts,RemoveReason,LastHoldReason,LastRemoteHost')
out, rc, dt = sh(['condor_history', os.environ.get('USER', 'melrashe'), '-limit', '30', '-json', '-attributes', HA])
hist = []
if out is not None and rc == 0:
    try:
        hist = json.loads(out) if out.strip() else []
    except ValueError:
        rc = 'badjson'
for a in hist:
    emit('hist', **a)
emit('src', name='condor_history', rc=rc, sec=dt, n=len(hist))

# ---- pipeline state files ----
state = {}
try:
    _state_files = os.listdir(os.path.join(R, 'state'))
except OSError:
    _state_files = []
for f in _state_files:
    if '.' in f:
        n, ext = f.rsplit('.', 1)
        state.setdefault(n, []).append(ext)
old = sorted(os.listdir(os.path.join(R, 'state', 'old'))) if os.path.isdir(os.path.join(R, 'state', 'old')) else []
mlout = {os.path.basename(p)[:-len('_ml.tar.gz')]: st(p) for p in glob.glob(os.path.join(R, '*_ml.tar.gz'))}
names = sorted(set(mlout) | {n for n in state if n != 'val'} |
               {os.path.basename(p) for p in glob.glob(os.path.join(R, 'results', '*'))})
QCK = ('QC', 'QC_reasons', 'n_atoms', 'composition', 't_eq_A', 't_span_A', 't_cat_A', 'vacuum_A', 'lateral_min_A',
       'water_removed', 'n_water', 'n_short_OO', 'W_W_min_A', 'W_depth_A', 'H_per_nm2_top_bottom',
       'unpaired_undercoordinated_cations', 'final_max_force_eV_A', 'md_ps')
for n in names:
    qc = jl(os.path.join(R, 'results', n, n + '_qc.json')) or {}
    drv = rd(os.path.join(R, 'results', n, n + '_driver.log')) or ''
    m = re.search(r'mace_amorph\.py exit (\d+)', drv)
    emit('struct', name=n, ml_tgz=mlout.get(n), state=sorted(state.get(n, [])),
         old=[o for o in old if o.startswith(n + '.')], ml_exit=int(m.group(1)) if m else None,
         **{('qc_' + key): qc.get(key) for key in QCK if key in qc})

# ---- DFT run directories ----
RE_SEG = re.compile(r'segment (\d+) finished with status (\w+)')
RE_BFGS = re.compile(r'BFGS steps this segment: (\d+)')
RE_RETRY = re.compile(r'Retrying node (\w+) \(retry #(\d+) of (\d+)\)')
RE_DST = re.compile(r'DAG status: (\d+) \((\w+)\)')
RE_EXIT = re.compile(r'EXITING WITH STATUS (\d+)')
RE_TAB = re.compile(r'^\S+ \S+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$', re.M)
for d in sorted(glob.glob(os.path.join(R, 'runs', '*/'))):
    n = os.path.basename(d.rstrip('/'))
    rs = rd(os.path.join(d, 'RELAX_STATUS'))
    segs = []
    for p in sorted(glob.glob(os.path.join(d, 'logs', 'relax_s*.out'))):
        mm = re.match(r'relax_s(\d+)\.(\d+)\.out$', os.path.basename(p))
        txt = rd(p, 4096) or ''
        a, b = RE_SEG.search(txt), RE_BFGS.search(txt)
        segs.append({'seg': int(mm.group(1)) if mm else None, 'cluster': int(mm.group(2)) if mm else None,
                     'status': a.group(2) if a else None, 'bfgs': int(b.group(1)) if b else None,
                     'mtime': (st(p) or {}).get('mtime')})
    tg = {os.path.basename(p): st(p) for p in glob.glob(os.path.join(d, 'relax_s*_results.tar.gz'))}
    # the DAG of this run: <name>.dag, or a later one in the same directory (e.g. <name>_pilot.dag): newest dagman.out
    dmos = glob.glob(os.path.join(d, '*.dag.dagman.out'))
    dmo = max(dmos, key=lambda p: (st(p) or {}).get('mtime') or 0) if dmos else os.path.join(d, n + '.dag.dagman.out')
    dag = dmo[:-len('.dagman.out')]
    dm = rd(dmo, TAIL) or ''
    r_ = RE_RETRY.findall(dm)
    s_ = RE_DST.findall(dm)
    e_ = RE_EXIT.findall(dm)
    t_ = RE_TAB.findall(dm)
    emit('run', name=n, relax_status=rs.strip() if rs else None, relax_status_mtime=(st(os.path.join(d, 'RELAX_STATUS')) or {}).get('mtime'),
         segs=segs, seg_tgz=tg, final_tgz=st(os.path.join(d, 'final_results.tar.gz')),
         final_out=sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, 'logs', 'final.*.out'))),
         rescue=sorted(os.path.basename(p) for p in glob.glob(dag + '.rescue*')),
         lock=os.path.exists(dag + '.lock'), dag_file=os.path.basename(dag),
         dagman_out=st(dmo),
         last_retry=list(r_[-1]) if r_ else None, dag_status=list(s_[-1]) if s_ else None,
         dag_exit=int(e_[-1]) if e_ else None, dag_done='All jobs Completed!' in dm,
         node_table=[int(x) for x in t_[-1]] if t_ else None)

# ---- ML force-check (val) ----
vj = rd(os.path.join(R, 'val', 'val_jobs.txt'))
for j in (vj or '').split():
    emit('val', name=j, results=st(os.path.join(R, 'val', j, 'val_results.tar.gz')),
         outs=sorted(os.path.basename(p) for p in glob.glob(os.path.join(R, 'val', j, 'logs', 'val.*.out'))))
emit('valstate', submitted=os.path.exists(os.path.join(R, 'state', 'val.submitted')), n_jobs=len((vj or '').split()))
emit('failed_dirs', dirs=sorted(os.listdir(os.path.join(R, 'runs_failed'))) if os.path.isdir(os.path.join(R, 'runs_failed')) else [])

# ---- AFS quota (~0.02 s) ----
out, rc, dt = sh(['fs', 'lq', os.path.expanduser('~')], 5)
m = re.search(r'^(\S+)\s+(\d+)\s+(\d+)\s+(\d+)%\s+(\d+)%', out or '', re.M)
emit('quota', fs='afs', volume=m.group(1) if m else None, quota_kb=int(m.group(2)) if m else None,
     used_kb=int(m.group(3)) if m else None, pct=int(m.group(4)) if m else None,
     partition_pct=int(m.group(5)) if m else None, rc=rc, sec=dt)

emit('done', sec=round(time.time() - T0, 3))
