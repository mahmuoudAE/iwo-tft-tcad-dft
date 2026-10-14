"""Frozen DFT read-out of the IWO amorphous-slab project (register section 1, H-G, H-H, H-I, H-K, H-N / A27).

Python 3 standard library + numpy. Entry point: python -m analysis --help (run from compute/amorph).
Modules: register (thresholds), smearing (QE occupation functions), qeio (parsers), data (container + loaders),
geometry (regions), section1 (definitions), readout (per-cell tests), compare (multi-cell tests, controls, outcome
rules), report (JSON + text), crystalline (reproduction check), cli.
"""
__version__ = '1.0.0-rc7'
