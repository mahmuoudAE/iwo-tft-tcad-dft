#!/usr/bin/env python3
"""Render docs/FULL_REPORT.md to docs/FULL_REPORT.html (print CSS, key figures embedded) and to docs/FULL_REPORT.pdf
using the installed Microsoft Edge in headless mode (no other converter is available on this machine).
No simulator call; nothing in the report text is changed."""
import base64, html, re, subprocess, sys, tempfile
from pathlib import Path
import markdown
ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / 'docs' / 'FULL_REPORT.md'; HTML = ROOT / 'docs' / 'FULL_REPORT.html'; PDF = ROOT / 'docs' / 'FULL_REPORT.pdf'
EDGE = [p for p in [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'] if Path(p).is_file()]

FIGS = [('plots/2p0/overlay_log.png', 'Figure F1. 2.0 nm: measured (workbook) vs ATLAS run_0012, log scale.'),
        ('plots/13p2/overlay_log.png', 'Figure F2. 13.2 nm: measured vs ATLAS run_0013, log scale.'),
        ('plots/6p3_validation/overlay_log.png', 'Figure F3. 6.3 nm validation with the shared parameters: measured vs ATLAS run_0014 (threshold miss of 0.29 V).'),
        ('plots/6p3/overlay_log.png', 'Figure F3b. 6.3 nm tuned (device-specific flat-band offset + band mobility): measured vs ATLAS run_0015.'),
        ('plots/6p3/residual.png', 'Figure F3c. 6.3 nm tuned residuals (run_0015).'),
        ('plots/2p0/residual.png', 'Figure F4. 2.0 nm residuals (log and linear).'),
        ('plots/13p2/residual.png', 'Figure F5. 13.2 nm residuals.'),
        ('plots/metrics_vs_thickness.png', 'Figure F6. Device metrics vs thickness, experiment vs ATLAS, identical extraction.'),
        ('plots/thickness_laws_overview.png', 'Figure F7. The thickness laws of the material model with their evidence points.'),
        ('plots/sensitivity_overview.png', 'Figure F7b. No-confinement counterfactual overlays (top) and one-at-a-time sensitivities at 2 nm (bottom), runs 0016-0027.'),
        ('plots/2p0/band_diagram_vth.png', 'Figure F8. 2.0 nm band diagram near threshold across the stack (channel centre).'),
        ('plots/13p2/band_diagram_vth.png', 'Figure F9. 13.2 nm band diagram near threshold.'),
        ('plots/2p0/electron_density_vs_vg.png', 'Figure F10. 2.0 nm free-electron density vs VG (channel centre and film average; VG = 0 value is n_FB).'),
        ('plots/13p2/mobility_vs_vg.png', 'Figure F11. 13.2 nm: native probe mobility vs the measured apparent field-effect mobility.')]

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
body { font-family: Calibri, 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; line-height: 1.38; color: #111; max-width: 100%; }
h1 { font-size: 20pt; margin: 0 0 4pt 0; } h2 { font-size: 14.5pt; margin-top: 18pt; border-bottom: 1px solid #999; padding-bottom: 2pt; page-break-after: avoid; }
h3 { font-size: 12pt; margin-top: 12pt; page-break-after: avoid; }
p { margin: 5pt 0; text-align: justify; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 8pt 0; font-size: 8.6pt; page-break-inside: auto; }
th, td { border: 1px solid #bbb; padding: 2.5pt 4pt; vertical-align: top; text-align: left; }
th { background: #eaeaea; } tr { page-break-inside: avoid; }
code { font-family: Consolas, 'Courier New', monospace; font-size: 8.8pt; background: #f3f3f3; padding: 0 2pt; }
pre { background: #f3f3f3; border: 1px solid #ccc; padding: 6pt; font-size: 8.4pt; white-space: pre-wrap; word-wrap: break-word; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
hr { border: 0; border-top: 1px solid #aaa; margin: 10pt 0; }
ol, ul { margin: 4pt 0 4pt 18pt; } li { margin: 2pt 0; }
figure { margin: 8pt 0; page-break-inside: avoid; text-align: center; } figure img { max-width: 92%; height: auto; }
figcaption { font-size: 9pt; color: #333; margin-top: 3pt; }
.cover { margin-bottom: 14pt; } .small { font-size: 9pt; color: #444; }
h2.fig { page-break-before: always; }
"""

def main():
    md_text = MD.read_text(encoding='utf-8')
    body = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'sane_lists'])
    figs = ['<h2 class="fig">Appendix D. Figures</h2>', '<p class="small">Rendered from plots/ of the package; every simulated curve is a real ATLAS run (run id in the title).</p>']
    for rel, cap in FIGS:
        p = ROOT / rel
        if not p.exists(): figs.append(f'<p class="small">[{html.escape(rel)} not present]</p>'); continue
        b64 = base64.b64encode(p.read_bytes()).decode()
        figs.append(f'<figure><img src="data:image/png;base64,{b64}" alt="{html.escape(rel)}"><figcaption>{html.escape(cap)} ({html.escape(rel)})</figcaption></figure>')
    doc = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>IWO thickness-aware ATLAS model - full report</title><style>{CSS}</style></head><body>{body}{"".join(figs)}</body></html>'
    HTML.write_text(doc, encoding='utf-8'); print('HTML', HTML, len(doc) // 1024, 'kB')
    # Word-flavoured copy (images by absolute file path; Word's HTML import does not take data: URIs) for the
    # Microsoft Word COM route used when headless Edge is unavailable (an interactive Edge session swallows it).
    wfigs = ['<h2 class="fig">Appendix D. Figures</h2>']
    for rel, cap in FIGS:
        p = ROOT / rel
        if p.exists(): wfigs.append(f'<p style="text-align:center"><img src="{html.escape(p.resolve().as_uri())}" width="560"></p><p class="small" style="text-align:center">{html.escape(cap)} ({html.escape(rel)})</p>')
    (ROOT / 'docs' / 'FULL_REPORT_word.html').write_text(f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>IWO thickness-aware ATLAS model - full report</title><style>{CSS}</style></head><body>{body}{"".join(wfigs)}</body></html>', encoding='utf-8')
    if '--word' in sys.argv:
        ps = f'''$w = New-Object -ComObject Word.Application; $w.Visible = $false
$d = $w.Documents.Open("{(ROOT / 'docs' / 'FULL_REPORT_word.html')}", $false, $true)
$d.PageSetup.TopMargin = 50; $d.PageSetup.BottomMargin = 50; $d.PageSetup.LeftMargin = 45; $d.PageSetup.RightMargin = 45
$d.SaveAs2("{PDF}", 17); $d.Close($false); $w.Quit()'''
        r = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', ps], capture_output=True, text=True, timeout=600)
        ok = PDF.exists() and PDF.stat().st_size > 10000
        print('PDF (Word COM)', PDF, PDF.stat().st_size // 1024 if PDF.exists() else 0, 'kB', 'OK' if ok else 'FAILED', r.returncode, (r.stderr or '')[-400:])
        return 0 if ok else 2
    if not EDGE: print('Edge not found; PDF not produced'); return 1
    with tempfile.TemporaryDirectory() as prof:
        cmd = [EDGE[0], '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', f'--user-data-dir={prof}', '--no-pdf-header-footer', f'--print-to-pdf={PDF}', HTML.resolve().as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    ok = PDF.exists() and PDF.stat().st_size > 10000
    print('PDF', PDF, PDF.stat().st_size // 1024 if PDF.exists() else 0, 'kB', 'OK' if ok else 'FAILED', r.returncode)
    return 0 if ok else 2

if __name__ == '__main__': sys.exit(main())
