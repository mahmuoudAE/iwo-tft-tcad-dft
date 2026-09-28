# Selected IWO ATLAS delivery

These decks reproduce explicitly selected completed native runs. The packager
does not launch Silvaco or claim a new calibration. See DELIVERY_MANIFEST.json
for source run IDs, original evidence, current residuals, and verification scope.
The original title and all physics commands are preserved even if a title says
"uncalibrated". Numerical convergence and fit acceptance require their separate
evidence; electrical checks alone do not establish them.

Open an individual .in file to run one thickness, or
combined/IWO_SELECTED_ALL.in to run the included thicknesses sequentially.
Use a fresh working directory for execution, and run with that deck's directory
as the working directory. Each block uses unique output filenames. TonyPlot
opens every saved STR and transfer LOG. The combined deck preserves each
evaluated ATLAS block and removes intermediate QUIT commands so later blocks
execute; its assembled form has not been executed by this packager.

All evidence/ files are copies of actual completed runs, not outputs generated
by these renamed delivery decks. Keep them separate from subsequent executions.
The data/ files are unchanged original measurement CSVs. Raw signed currents
are retained; no fitted leakage floor is added. Divide raw terminal current by
the simulation width_um in each manifest entry before comparing with A/um
measurements. Multiply that normalized current by the physical device width
to obtain total device amperes; do not normalize twice.
Main logarithmic metrics use only positive native signed current, with explicit
counts and null metrics when no positive values exist. Zero and negative
currents are not fitted leakage. Any guarded-magnitude aggregate is labeled
DIAGNOSTIC_ONLY, separate from those metrics. Original comparison CSVs in
evidence/ retain their historical fields; use the manifest's recomputed
signed-positive metrics for this delivery's scientific summary.
No licensed manual or simulator
installation files are included. Running these .in files consumes simulator
time and requires the user's legitimate installation and execution allowance.
