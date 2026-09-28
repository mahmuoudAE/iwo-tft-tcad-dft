"""Stage 6: Overleaf-ready ZIP of the report. Excludes digest/ (copyrighted paper/manual excerpts), the extracted
manual text, caches and scratch previews."""
import zipfile
from pathlib import Path
R = Path(__file__).resolve().parents[1]
Z = R.parent / 'results' / 'IWO_TCAD_full_report_latex_2026-09-25.zip'
skip_dirs = {'digest', '__pycache__'}
skip_files = {'atlas_manual_fulltext.json', 'contact_sheet.png'}
n = 0
with zipfile.ZipFile(Z, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(R.rglob('*')):
        rel = p.relative_to(R)
        if p.is_dir() or skip_dirs & set(rel.parts) or p.name in skip_files: continue
        z.write(p, Path('IWO_TCAD_Report') / rel); n += 1
print(Z, f'{Z.stat().st_size / 1e6:.1f} MB', n, 'files')
