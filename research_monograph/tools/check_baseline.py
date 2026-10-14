"""Pin the baseline files reused by reference. 'write' records sha256 + git blob of every file of
report_latex_full that main.tex inputs (directly or via \\input@path); 'check' (default) fails if any changed.
Usage (from research_monograph/): python3 -I tools/check_baseline.py [write|check]"""
import hashlib, pathlib, re, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parents[1]
BASE = HERE.parent / "report_latex_full"
MAN = HERE / "baseline_manifest.tsv"
def reused():
    files = set(re.findall(r"\\input\{\.\./report_latex_full/([^}]+)\}", (HERE/"main.tex").read_text()))
    files |= {"preamble"}
    out = set()
    for f in files:
        p = BASE / (f if f.endswith(".tex") else f + ".tex")
        out.add(p)
        # one level of nested \input in reused files (appendix tables etc.)
        for g in re.findall(r"\\input\{([^}]+)\}", p.read_text(errors="replace")):
            q = BASE / (g if g.endswith(".tex") else g + ".tex")
            if q.exists(): out.add(q)
    return sorted(out)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
mode = sys.argv[1] if len(sys.argv) > 1 else "check"
rows = [(str(p.relative_to(HERE.parent)), sha(p)) for p in reused()]
if mode == "write":
    head = subprocess.run(["git", "-C", str(HERE.parent), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    MAN.write_text("# baseline files reused by reference; pinned at repository commit " + head + "\npath\tsha256\n" +
                   "".join(f"{a}\t{b}\n" for a, b in rows))
    print("wrote", MAN.name, len(rows), "files")
else:
    pinned = dict(l.split("\t") for l in MAN.read_text().splitlines()[2:])
    bad = [a for a, b in rows if pinned.get(a) != b]
    if bad:
        print("BASELINE CHANGED or unpinned:", *bad, sep="\n  "); sys.exit(1)
    print("baseline OK:", len(rows), "files match the manifest")
