# IWO priority-three delivery

Read ASSESSMENT.md and PRIORITY_MANIFEST.json for actual residuals, run IDs,
numerical scope and unresolved physical limits. The 31.8 nm model is deferred.

- Complete sequential input: decks/combined/IWO_SELECTED_ALL.in (three devices).
- Individual inputs: decks/individual/iwo_2p0nm.in, iwo_6p3nm.in, iwo_13p2nm.in.
- Every saved STR and transfer LOG has a TonyPlot command in those inputs.
- Fresh scientific reports: reports/; four PNG/PDF overview pairs: overview/.
- Exact evaluated configurations: config/; unchanged measured CSVs: data/.
- Copied renderer: scripts/rebuild_model.py; verified batch reproductions: reproduction/.
- Selected native evidence and filename-equivalence manifest: decks/evidence/ and
  decks/DELIVERY_MANIFEST.json. This nested base package is preserved unchanged.

The helper launches no simulator. Reproduced inputs are code, not new ATLAS
results. To regenerate one batch input using Python with NumPy, run from this
delivery root and choose a new output path:

```powershell
python scripts/rebuild_model.py --config config/iwo_2p0nm.json --key 2p0 --out reproduced/iwo_2p0nm.in --batch
```

The copied generator was actually imported from this delivery and its generated
commands compared with each of the three evaluated source inputs. Only original
gate targets are read during generation; measured current is not used to create
the device. The assembled delivery inputs differ only in checked output filenames,
TonyPlot calls and intermediate QUIT delimiters.

Actual simulator execution requires a fresh working directory and the user's
legitimate Silvaco installation and current execution allowance. Keep future
outputs separate from the copied evidence. Divide signed native current by the
evaluated simulation width for A/µm; multiply by physical width for total amperes.
Do not divide a width-one current again by the 290 µm physical device width.

No numerical scope is inferred from a good fit, no full low-current fit is
inferred from positive-only logarithms, and no predictive/process-physics
certificate is granted. No licensed installation files or manuals are bundled.
