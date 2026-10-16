"""Build evidence/REFERENCE_INDEX.tsv from the baseline bibliography (report_latex_full/references.bib,
bib/extra_DFT.bib) and the monograph's own bib (research_monograph/bib/monograph.bib, if present).

For every entry with a DOI, Crossref metadata is fetched and compared with the bib entry (first-author family name,
year, and title-word overlap). Results are cached in evidence/derived/crossref_cache.json so each DOI is fetched
once. Page-exact citation status is taken from report_latex_full/digest/papers (printed page headings) when the key
is one of the digested papers. No paper text is copied into the index.
Run from the repository root:  python3 -I research_monograph/tools/build_reference_index.py
"""
import csv
import json
import pathlib
import re
import time
import unicodedata
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
BIBS = [ROOT / "report_latex_full/references.bib", ROOT / "report_latex_full/bib/extra_DFT.bib",
        ROOT / "research_monograph/bib/monograph.bib"]
CACHE = ROOT / "research_monograph/evidence/derived/crossref_cache.json"
OUT = ROOT / "research_monograph/evidence/REFERENCE_INDEX.tsv"
# DOI candidates for entries whose bibliographic search fails; each is checked against Crossref metadata.
DOI_CANDIDATES = {"Thain2005": "10.1002/cpe.938", "Harris2020": "10.1038/s41586-020-2649-2"}
# Documented manual acceptances (reason recorded in the index).
MANUAL_ACCEPT = {"Mott1969": "Crossref title truncated to the series title; author, year, volume 19 and pages 835-852 match"}
DIGESTED = {p.stem for p in (ROOT / "report_latex_full/digest/papers").glob("*.md")}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", s.lower())


def parse_bib(path):
    if not path.exists():
        return []
    text = path.read_text(errors="replace")
    entries = []
    for chunk in re.split(r"(?m)^@", text)[1:]:
        m = re.match(r"(\w+)\s*\{\s*([^,\s]+)\s*,(.*)", chunk, re.S)
        if not m:
            continue
        kind, key, body = m.group(1).lower(), m.group(2), m.group(3)
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\"[^\"]*\"|\d+)", body):
            v = fm.group(2).strip()
            if v[0] in "{\"":
                v = v[1:-1]
            fields[fm.group(1).lower()] = re.sub(r"\s+", " ", v)
        entries.append((path.name, kind, key, fields))
    return entries


def crossref_search(f, cache):
    """Bibliographic search for an entry without DOI; returns the best hit's metadata."""
    q = " ".join([f.get("author", "").split(" and ")[0], f.get("title", ""), f.get("journal", ""),
                  f.get("year", "")])
    q = re.sub(r"[{}\\\"$]", "", q)
    ck = "Q:" + q
    if ck in cache:
        return cache[ck]
    url = ("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.request.quote(q))
    req = urllib.request.Request(url, headers={"User-Agent": "iwo-monograph-reference-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            items = json.load(r)["message"]["items"]
        hits = []
        for msg in items:
            hits.append({"doi": msg.get("DOI", ""), "title": " ".join(msg.get("title", [])),
                         "family": (msg.get("author") or [{}])[0].get("family", ""),
                         "year": (msg.get("issued", {}).get("date-parts") or [[None]])[0][0],
                         "container": " ".join(msg.get("container-title", [])), "volume": msg.get("volume", ""),
                         "page": msg.get("page", msg.get("article-number", ""))})
        rec = {"hits": hits}
    except Exception as e:
        return {"error": str(e)[:120]}
    cache[ck] = rec
    time.sleep(0.25)
    return rec


def crossref(doi, cache):
    if doi in cache:
        return cache[doi]
    url = "https://api.crossref.org/works/" + urllib.request.quote(doi)
    req = urllib.request.Request(url, headers={"User-Agent": "iwo-monograph-reference-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            msg = json.load(r)["message"]
        rec = {"title": " ".join(msg.get("title", [])), "family": (msg.get("author") or [{}])[0].get("family", ""),
               "year": (msg.get("issued", {}).get("date-parts") or [[None]])[0][0],
               "container": " ".join(msg.get("container-title", [])), "volume": msg.get("volume", ""),
               "page": msg.get("page", msg.get("article-number", ""))}
    except Exception as e:  # network or 404: not cached, retried next run
        return {"error": str(e)[:120]}
    cache[doi] = rec
    time.sleep(0.2)
    return rec


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    cache = {k: v for k, v in cache.items() if "error" not in v}
    rows = []
    seen = set()
    for bib in BIBS:
        for src, kind, key, f in parse_bib(bib):
            if key in seen:
                rows.append([key, src, kind, "", "", "", "", "DUPLICATE KEY", ""])
                continue
            seen.add(key)
            doi = f.get("doi", "").strip() or DOI_CANDIDATES.get(key, "")
            author = f.get("author", "")
            first = norm(author.split(" and ")[0].split(",")[0]).strip().split(" ")[-1] if author else ""
            year = f.get("year", "")
            status, detail = "no-doi", ""
            if doi:
                rec = crossref(doi, cache)
                if "error" in rec:
                    status, detail = "crossref-error", rec["error"]
                else:
                    tw = set(norm(f.get("title", "")).split()) - {"the", "of", "and", "a", "in", "for", "on", "with"}
                    cw = set(norm(rec["title"]).split())
                    overlap = len(tw & cw) / max(1, len(tw))
                    fam_ok = first and first in norm(rec["family"])
                    yr_ok = str(rec["year"]) == str(year)
                    yr_near = rec["year"] and year.isdigit() and abs(int(rec["year"]) - int(year)) <= 1
                    if fam_ok and overlap >= 0.6 and yr_ok:
                        status = "doi-verified"
                    elif fam_ok and yr_near and overlap >= 0.45:
                        status = "doi-verified (benign: online-first year or formula markup in title)"
                    elif key in MANUAL_ACCEPT:
                        status = "doi-verified (manual: " + MANUAL_ACCEPT[key] + ")"
                    else:
                        status = "doi-MISMATCH"
                    detail = (f"crossref: {rec['family']} {rec['year']} {rec['container']} {rec['volume']} "
                              f"{rec['page']}; title overlap {overlap:.2f}; author {'ok' if fam_ok else 'X'}; "
                              f"year {'ok' if yr_ok else 'X'}")
            if not doi and kind == "article" and f.get("journal"):
                rec = crossref_search(f, cache)
                status, detail = "search-no-match", ""
                for h in rec.get("hits", []):
                    vol_ok = str(h["volume"]) == str(f.get("volume", ""))
                    pg = str(f.get("pages", "")).split("-")[0].split("--")[0].strip()
                    pg_ok = bool(pg) and (str(h["page"]).split("-")[0] == pg or pg in str(h["page"]))
                    yr_ok = abs(int(h["year"] or 0) - int(re.sub(r"\D", "", year) or 0)) <= 1
                    if vol_ok and pg_ok and yr_ok:
                        status = "metadata-verified (crossref search)"
                        detail = f"doi {h['doi']}; {h['family']} {h['year']} {h['container']} {h['volume']} {h['page']}"
                        break
                if status == "search-no-match" and rec.get("hits"):
                    h = rec["hits"][0]
                    detail = f"best hit: {h['doi']} {h['family']} {h['year']} {h['container']} {h['volume']} {h['page']}"
                if "error" in rec:
                    status, detail = "crossref-error", rec["error"]
            page_status = "page-checkable (digest)" if key in DIGESTED else ""
            rows.append([key, src, kind, author[:80], year, f.get("journal", f.get("publisher", ""))[:60], doi,
                         status, (detail + ("; " + page_status if page_status else ""))[:300]])
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=1))
    with open(OUT, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["key", "bib_file", "type", "author", "year", "venue", "doi", "status", "detail"])
        w.writerows(rows)
    from collections import Counter
    print(OUT.relative_to(ROOT), len(rows), "entries;", dict(Counter(r[7] for r in rows)))
    for r in rows:
        if r[7] in ("doi-MISMATCH", "crossref-error", "DUPLICATE KEY", "search-no-match"):
            print(" ", r[0], r[7], r[8][:160])


if __name__ == "__main__":
    main()
