"""Render an explicitly unvalidated lateral-mesh sensitivity candidate.

This changes only LINE X commands in the existing 24 um ATHENA geometry.
It does not launch Silvaco or claim to fix current conservation.
"""
from pathlib import Path
import argparse
import re

ROOT = Path(__file__).resolve().parents[1]


def lateral_candidate(text: str, center_spacing_um: float = 0.2) -> str:
    """Cap the previous ~1 um channel spacing while resolving contact edges.

    The assumed source occupies 0..2 um; drain occupies 22..24 um. Every
    deposition thickness, vertical mesh, electrode and physical card remains
    unchanged. The previous process output had an IWO maximum lateral triangle
    span of 1.00624 um and maximum side ratio ~4025, so this is a controlled
    discretization comparison, not an arbitrary material adjustment.
    """
    if not 0.05 <= center_spacing_um <= 0.5:
        raise ValueError("Keep the bounded sensitivity spacing between 0.05 and 0.5 um")
    pattern = re.compile(r"(?m)^line\s+x\s+loc=([-+\d.eE]+)\s+spac=([-+\d.eE]+)\s*$", re.I)
    matches = list(pattern.finditer(text))
    positions = {float(m.group(1)) for m in matches}
    if not {0.0, 2.0, 12.0, 22.0, 24.0}.issubset(positions):
        raise ValueError("Expected the explicit 0/2/12/22/24 um process template")
    lines = [
        "# UNVALIDATED lateral-mesh sensitivity: geometry and physics unchanged.",
        f"line x loc=0 spac={center_spacing_um:g}",
        "line x loc=1.8 spac=0.05",
        "line x loc=2 spac=0.02",
        "line x loc=2.2 spac=0.05",
        f"line x loc=12 spac={center_spacing_um:g}",
        "line x loc=21.8 spac=0.05",
        "line x loc=22 spac=0.02",
        "line x loc=22.2 spac=0.05",
        f"line x loc=24 spac={center_spacing_um:g}",
    ]
    first, last = matches[0].start(), matches[-1].end()
    block = text[first:last]
    if any(line.strip() and not pattern.fullmatch(line) for line in block.splitlines()):
        raise ValueError("Refuse to replace a noncontiguous or annotated LINE X block")
    return text[:first] + "\n".join(lines) + text[last:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--center-spacing", type=float, default=0.2)
    args = parser.parse_args()
    source, output = args.input.resolve(), args.output.resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT):
        parser.error("Keep all inputs and outputs inside this project")
    if source == output or output.exists():
        parser.error("Choose a fresh output path; do not overwrite an existing input")
    candidate = lateral_candidate(source.read_text(), args.center_spacing)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(candidate, encoding="ascii")
    print(output)


if __name__ == "__main__":
    main()
