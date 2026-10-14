"""Stream the 9.4 GB runaway scf.out inside iwo_slab1_W24d_x1_results.tar.gz without writing it to disk:
size, sha256, line count, line-length statistics, the first/last lines (each truncated to 300 characters), the most
frequent line patterns (digits masked, first 160 characters) with the line where each first appears.
Output: out/iwo_slab1_W24d_x1_runaway_scf.json (compact). Read-only."""
import collections
import hashlib
import json
import re
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TB = HERE.parents[1] / 'cern_htcondor' / 'results' / 'iwo_slab1_W24d_x1' / 'iwo_slab1_W24d_x1_results.tar.gz'
mask = re.compile(r'[-+]?\d+(\.\d+)?([eEdD][-+]?\d+)?')
cnt = collections.Counter()
first_seen = {}
head, tail = [], collections.deque(maxlen=60)
n = nbytes = maxlen = maxlen_line = long_lines = 0
h = hashlib.sha256()
with tarfile.open(TB, 'r:gz') as t:
    m = t.getmember('scf.out')
    f = t.extractfile(m)
    while True:
        raw = f.readline(1 << 20)          # at most 1 MiB per read: a giant line is counted in pieces
        if not raw:
            break
        h.update(raw)
        nbytes += len(raw)
        if raw.endswith(b'\n'):
            n += 1
        if len(raw) > maxlen:
            maxlen, maxlen_line = len(raw), n
        if len(raw) > 10000:
            long_lines += 1
        line = re.sub('\x00+', lambda mm: f'<{len(mm.group(0))} NUL>', raw[:300].decode('utf-8', 'replace').rstrip('\n'))
        if n <= 80:
            head.append(line)
        tail.append(line)
        key = mask.sub('#', line.strip())[:160]
        if key not in first_seen and len(first_seen) < 200000:
            first_seen[key] = n
        cnt[key] += 1
        if len(cnt) > 300000:
            cnt = collections.Counter(dict(cnt.most_common(5000)))
res = {'tarball': TB.name, 'member_size_bytes': m.size, 'bytes_read': nbytes, 'sha256': h.hexdigest(), 'newline_count': n,
       'max_read_chunk_bytes': maxlen, 'max_chunk_at_line': maxlen_line, 'chunks_over_10k_bytes': long_lines,
       'top_patterns': [[k, c, first_seen.get(k)] for k, c in cnt.most_common(25)], 'head': head, 'tail': list(tail)}
(HERE / 'out' / 'iwo_slab1_W24d_x1_runaway_scf.json').write_text(json.dumps(res, indent=1))
print(n, nbytes, maxlen, res['top_patterns'][:5])
