"""Hash the pre-registration inputs (run before the V2 launches); writes T0_REGISTRATION.txt."""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
FILES = ['analysis_2026-10-06_V2/T0_PRECHECKS.md', 'analysis_2026-10-06_V2/t0_results.json', 'analysis_2026-10-06_V2/t0_prechecks.py',
         'analysis_2026-10-06_V2/make_v2_model.py', 'config/iwo_material_model_v2.yaml', 'config/iwo_material_model.yaml',
         'config/solver.yaml', 'config/geometry.yaml', 'scripts/build_iwo_decks.py', 'scripts/run_atlas.py', 'scripts/extract_metrics.py']
lines = [f'Registered {datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ} (before the V2 launches)']
for f in FILES:
    lines.append(f'{hashlib.sha256((PKG / f).read_bytes()).hexdigest()}  {f}')
(HERE / 'T0_REGISTRATION.txt').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
