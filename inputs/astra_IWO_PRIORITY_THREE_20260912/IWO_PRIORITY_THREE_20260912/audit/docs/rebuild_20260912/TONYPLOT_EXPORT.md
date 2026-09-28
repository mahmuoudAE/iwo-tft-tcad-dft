# Installed TonyPlot native PNG export

The installed TonyPlot 3.10.22.R manual documents `-png <file>` to render all loaded plots to PNG and exit automatically. `-noexit` disables that exit behavior and should be omitted for a one-shot export. `-nosplash` suppresses the splash screen. This provides a documented native export path without GUI interaction; execution on this Windows host remains untested by this audit.

The read-only filesystem inspection found the binary at:

```text
C:\sedatools\lib\tonyplot\3.10.22.R\x86_64-windows\tonyplot.exe
```

For the actual saved quantum-control geometry, the following PowerShell command launches the exporter hidden, with all outputs inside the project and outside the immutable raw-run directory:

```powershell
$iwoProject = 'C:\Users\moham\Downloads\IWO_Local_Codex_Handoff (1)\IWO_ATLAS_Model'
$iwoTonyPlot = 'C:\sedatools\lib\tonyplot\3.10.22.R\x86_64-windows\tonyplot.exe'
$iwoArguments = @(
    '-nosplash'
    'results/local_session_20260910/runs/20260912T074348_745974_quantum_charge_bound_2nm/qbound_geometry.str'
    '-png'
    'results/rebuild_20260912/quantum_audits/plots/native_qbound_geometry.png'
)
Start-Process -FilePath $iwoTonyPlot -WorkingDirectory $iwoProject -ArgumentList $iwoArguments -WindowStyle Hidden -PassThru
```

The named output directory already exists. The caller should bound this specific process, retain its own exit/error evidence, and verify a newly written nonempty PNG before displaying it. This command is prepared from installed documentation, not an executed or verified rendering. The manual does not promise independence from Windows graphics facilities, so `-png` must not be relabeled an established headless renderer before execution.

The input can be replaced by any actual `final.str`, saved bias structure or native log. A `.set` file controls its display; it must appear **after** the data filename as `-set <file>` because the option applies to already loaded files. Without a set file, the native default view is used. A successful structure image verifies the renderer's view of a genuine STR; it does not by itself verify physical parameters, mesh convergence or device calibration.

For more explicit material/mesh display, documented TPCS can read commands on standard input when invoked with `-tpcs`. Appendix A supports `show materials on`, `show mesh on`, `show electrodes on`, `show contours off`, `draw all`, and `save <plot-index> "filename" 4` (PNG). The plot index and termination should be verified in the actual invocation before building a longer automation. The CLI `-png` route above is the shorter documented first attempt.

Primary references: local `C:\sedatools\lib\tonyplot\3.10.22.R\docs\tonyplot_users1.pdf`, p.13 (CLI `-png`, `-jpg`, `-noexit`, `-set`, `-tpcs`), pp.136-137 (TPCS image saving and view controls). TPCS `print "file.ps"` is explicitly Linux-only on p.136; this audit does not recommend it for Windows. No TonyPlot or simulator process was launched by this audit.

## Subsequent actual Windows export

The parent workflow subsequently used the installed native PNG route on the genuine fit04 `geometry.str`. It created [geometry.png](../../results/rebuild_20260912/native_geometry/geometry.png), which the parent visually inspected. Its native legend identifies Air, IWO, Al2O3, HfO2, Conductor and Palladium; no SiO2 overlayer appears. The exact source, output hashes, executable, arguments and timing are preserved in [tonyplot_export_manifest.json](../../results/rebuild_20260912/native_geometry/tonyplot_export_manifest.json).

The wrapper's 30-second wait reached its timeout near process termination; the subsequent Stop-Process attempt found that the specific PID had already ended. A fresh PNG appeared, stdout/stderr were empty, and the subsequent process inspection found no running TonyPlot. **The native image was created and the process ended, but its exit code was not captured.** This confirms actual native Windows rendering for that input without claiming a recorded clean exit. No further exporter launch was performed for this documentation update.
