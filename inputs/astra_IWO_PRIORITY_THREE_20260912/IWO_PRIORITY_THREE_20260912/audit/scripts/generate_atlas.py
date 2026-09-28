#!/usr/bin/env python3
"""Generate structured ATLAS .in decks; this command never launches a simulator.

Configuration and model helpers live in iwo_model.py; rendering lives in
iwo_deck.py. Public imports below preserve existing workflow/test callers.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from iwo_model import (
    ROOT, EPS0, Q, cox, key_from_thickness,
    load_config, mobility_at, read_data, validate,
)
from iwo_deck import defect_lines, generate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default=str(ROOT / 'config/model_seed.json'))
    parser.add_argument('--thickness', type=float, choices=[2., 6.3, 13.2, 31.8])
    parser.add_argument('--out', type=Path, default=ROOT / 'decks')
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--constant-mobility', action='store_true')
    parser.add_argument('--refine', type=float, default=1., help='Mesh spacing multiplier, e.g. 0.5')
    args = parser.parse_args()
    if not math.isfinite(args.refine) or args.refine <= 0:
        parser.error('--refine must be finite and positive')
    cfg = load_config(args.config)
    cfg['numerics']['x_mesh_scale'] *= args.refine
    cfg['numerics']['y_mesh_scale'] *= args.refine
    if args.constant_mobility:
        cfg['mobility']['mode'] = 'constant'
    keys = (
        [key_from_thickness(args.thickness)]
        if args.thickness is not None else list(cfg['curves'])
    )
    # Validate/render all requested decks before writing any of them.
    rendered = [(key, *generate(cfg, key, smoke=args.smoke)) for key in keys]
    for key, text, metadata in rendered:
        label = f'iwo_{key}nm' + ('_smoke' if args.smoke else '')
        destination = args.out / label
        destination.mkdir(parents=True, exist_ok=True)
        deck_path = destination / (label + '.in')
        deck_path.write_text(text, encoding='ascii')
        (destination / 'deck_metadata.json').write_text(json.dumps(metadata, indent=2))
        print(deck_path)


if __name__ == '__main__':
    main()
