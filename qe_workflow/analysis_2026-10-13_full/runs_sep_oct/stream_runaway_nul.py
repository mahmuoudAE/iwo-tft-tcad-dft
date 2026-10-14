"""Second pass over the runaway scf.out: exact NUL-byte count and any pw.x marker lines (Program PWSCF, JOB DONE, '!').
Appends to out/iwo_slab1_W24d_x1_runaway_scf.json. Read-only."""
import json, tarfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
TB = HERE.parents[1] / 'cern_htcondor' / 'results' / 'iwo_slab1_W24d_x1' / 'iwo_slab1_W24d_x1_results.tar.gz'
nul = 0; marks = {b'Program PWSCF': 0, b'JOB DONE': 0, b'!    total energy': 0, b'Error in routine': 0, b'UCX  ERROR': 0}
first_nul = None; pos = 0
with tarfile.open(TB, 'r:gz') as t:
    f = t.extractfile('scf.out')
    tail = b''
    while True:
        b = f.read(1 << 24)
        if not b:
            break
        c = b.count(b'\x00')
        if c and first_nul is None:
            first_nul = pos + b.index(b'\x00')
        nul += c
        buf = tail + b
        for k in marks:
            marks[k] += buf.count(k)
        tail = b[-32:]
        pos += len(b)
p = HERE / 'out' / 'iwo_slab1_W24d_x1_runaway_scf.json'
r = json.loads(p.read_text())
r.update({'nul_bytes': nul, 'first_nul_offset': first_nul, 'marker_counts_approx': {k.decode(): v for k, v in marks.items()}})
p.write_text(json.dumps(r, indent=1))
print(nul, first_nul, r['marker_counts_approx'])
