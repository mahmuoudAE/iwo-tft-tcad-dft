"""Small helpers used on the HTCondor worker (standard library only).

  python qeio.py newgeom <template.in> <relax.out> > <new.in>
      Copies the template and replaces its CELL_PARAMETERS and ATOMIC_POSITIONS cards with the final
      geometry of a relax / vc-relax run ("Begin final coordinates" block; if the run did not finish,
      the last geometry printed). Cell vectors are converted to angstrom.
  python qeio.py converged <relax.out>
      Exit status 0 if the relaxation finished ("End final coordinates" present), 1 otherwise.
  python qeio.py fermi <scf.out>
      Prints the Fermi energy (eV) or, for fixed occupations, the highest occupied level.
"""
import re
import sys

BOHR_A = 0.529177210903


def _blocks(lines, key):
    """All (header, body) blocks starting with a card name, body = following non-empty lines."""
    out = []
    for n, line in enumerate(lines):
        if line.strip().startswith(key):
            body = []
            for nxt in lines[n + 1:]:
                s = nxt.strip()
                if not s or s.startswith(('End', 'ATOMIC', 'CELL', 'Writing', 'number', 'new', 'Begin')):
                    break
                body.append(s)
            out.append((line.strip(), body))
    return out


def final_geometry(text):
    lines = text.splitlines()
    if 'Begin final coordinates' in text:
        start = next(n for n, l in enumerate(lines) if 'Begin final coordinates' in l)
        lines = lines[start:]
    cells, poss = _blocks(lines, 'CELL_PARAMETERS'), _blocks(lines, 'ATOMIC_POSITIONS')
    cell = None
    if cells:
        head, body = cells[-1]
        m = re.search(r'alat\s*=\s*([0-9.]+)', head)
        if m:
            f = float(m.group(1)) * BOHR_A
        elif 'bohr' in head.lower():
            f = BOHR_A
        else:
            f = 1.0
        vec = [[float(x) * f for x in row.split()[:3]] for row in body[:3]]
        cell = ['CELL_PARAMETERS angstrom'] + ['  %.10f %.10f %.10f' % tuple(v) for v in vec]
    head, body = poss[-1]
    unit = re.sub(r'[(){}]', ' ', head).split()[1] if len(head.split()) > 1 or '(' in head else 'alat'
    pos = ['ATOMIC_POSITIONS ' + unit] + ['  ' + b for b in body]
    return cell, pos


def replace_card(text, key, new):
    lines = text.splitlines()
    out, skip = [], False
    for line in lines:
        s = line.strip()
        if s.startswith(key):
            out.extend(new)
            skip = True
            continue
        if skip:
            if not s or s.startswith(('ATOMIC_', 'CELL_', 'K_POINTS', '&', 'OCCUPATIONS', 'CONSTRAINTS', 'HUBBARD')):
                skip = False
            else:
                continue
        out.append(line)
    return '\n'.join(out) + '\n'


def main():
    cmd = sys.argv[1]
    if cmd == 'newgeom':
        tmpl = open(sys.argv[2]).read()
        cell, pos = final_geometry(open(sys.argv[3]).read())
        if cell is not None and 'CELL_PARAMETERS' in tmpl:
            tmpl = replace_card(tmpl, 'CELL_PARAMETERS', cell)
        sys.stdout.write(replace_card(tmpl, 'ATOMIC_POSITIONS', pos))
    elif cmd == 'converged':
        sys.exit(0 if 'End final coordinates' in open(sys.argv[2]).read() else 1)
    elif cmd == 'fermi':
        text = open(sys.argv[2]).read()
        m = re.findall(r'the Fermi energy is\s+(-?[0-9.]+)', text) or \
            re.findall(r'highest occupied(?:, lowest unoccupied)? level \(ev\):\s+(-?[0-9.]+)', text)
        print(m[-1])
    else:
        sys.exit('unknown command ' + cmd)


if __name__ == '__main__':
    main()
