"""Consistency checks of the npj manuscript framework. Run:  python3 -I check_manuscript.py  (from this folder or anywhere)

1. Every evidence tag in main.tex (\\ev{...}) resolves: MS-nn in CLAIMS_USED.tsv; C0nn and M0nn in
   evidence/CLAIM_SOURCE_MAP.tsv; Fnnn[a-z] in evidence/FACT_REGISTRY.tsv. Ranges "Fxxx--Fyyy" check both ends.
2. Every MS-nn of CLAIMS_USED.tsv is used in main.tex, and every evidence ID listed there resolves.
3. Every placeholder number \\pending{Nnn} is listed in DECISIONS.md.
4. Forbidden phrases (superseded or overclaiming statements) do not occur in main.tex.
5. No amorphous cell name is followed by a number on the same line (blind-data guard; cell names may appear only in
   protocol statements).
Exit status 1 on any failure.
"""
import csv
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
EV = HERE.parent / "evidence"
tex = (HERE / "main.tex").read_text()
body = "\n".join(l.split("%", 1)[0] if not l.lstrip().startswith("%") else "" for l in tex.splitlines())


def ids(path, col):
    with open(path) as f:
        return {r[col] for r in csv.DictReader(f, delimiter="\t")}


facts = {i.replace("FACT-", "F") for i in ids(EV / "FACT_REGISTRY.tsv", "fact_id")}
claims = ids(EV / "CLAIM_SOURCE_MAP.tsv", "claim_id")
with open(HERE / "CLAIMS_USED.tsv") as f:
    used = list(csv.DictReader(f, delimiter="\t"))
ms = {r["ms_id"] for r in used}
decisions = set(re.findall(r"^\| (N\d\d) \|", (HERE / "DECISIONS.md").read_text(), re.M))
fail = []


def resolve(tok, where):
    tok = tok.strip()
    if not tok:
        return
    if "--" in tok:
        a, b = tok.split("--", 1)
        if not b.startswith("F") and a.startswith("F"):
            b = a[: len(a) - len(b)] + b
        for t in (a, b):
            resolve(t, where)
        return
    if re.fullmatch(r"MS-\d\d", tok):
        ok = tok in ms
    elif re.fullmatch(r"[CM]\d{3}", tok):
        ok = tok in claims
    elif re.fullmatch(r"F\d{3}[a-z]?", tok):
        ok = tok in facts
    else:
        ok = None  # free text (e.g. a section name); not checked
    if ok is False:
        fail.append(f"{where}: unresolved evidence ID {tok}")


tags = re.findall(r"\\ev\{([^}]*)\}", body)
for t in tags:
    for tok in re.split(r"[;,]", t):
        resolve(tok, "main.tex")
used_ms = set(re.findall(r"MS-\d\d", " ".join(tags)))
for m in sorted(ms - used_ms):
    fail.append(f"CLAIMS_USED.tsv: {m} not used in main.tex")
for r in used:
    for tok in re.split(r"[;,]", r["evidence"]):
        tok = tok.strip()
        if tok.startswith("FACT-"):
            base = tok.replace("FACT-", "F")
            if re.fullmatch(r"F\d{3}[a-z]-[a-z]", base):  # FACT-026a-d
                for c in "abcd"[: "abcd".index(base[-1]) + 1]:
                    resolve(base[:4] + c, r["ms_id"])
            else:
                resolve(base, r["ms_id"])
        elif re.fullmatch(r"[CM]\d{3}", tok):
            resolve(tok, r["ms_id"])
for n in sorted(set(re.findall(r"\\pending\{(N\d\d)\}", body))):
    if n not in decisions:
        fail.append(f"main.tex: placeholder {n} missing from DECISIONS.md")

FORBIDDEN = [r"H-L supported", r"publication-ready", r"\bvalidat(e|ed|es|ion)\b(?! amorphous)",
             r"crossover (was|is) (observed|found|confirmed)", r"no crossover (was|is) (observed|found)",
             r"below the (host )?conduction band.{0,40}pinn", r"5\.5\s*\\times\s*10\^\{21\}"]
for pat in FORBIDDEN:
    for m in re.finditer(pat, body, re.I):
        line = body[: m.start()].count("\n") + 1
        fail.append(f"main.tex:{line}: forbidden phrase /{pat}/: {m.group(0)!r}")
for i, line in enumerate(body.splitlines(), 1):
    if re.search(r"a(IO|IWO)_[0-9a-z_]+\}?[^\n]{0,30}?[=:]\s*[-+]?\d", line):
        fail.append(f"main.tex:{i}: amorphous cell name followed by a value")

print(f"evidence tags {len(tags)}, MS claims {len(ms)} (used {len(used_ms)}), facts known {len(facts)}, "
      f"claims known {len(claims)}, placeholders {len(set(re.findall(r'pending\{(N\d\d)', body)))}, "
      f"sealed blocks {len(re.findall(r'sealed\{', body))}")
if fail:
    print("\n".join(fail))
    sys.exit(1)
print("OK")
