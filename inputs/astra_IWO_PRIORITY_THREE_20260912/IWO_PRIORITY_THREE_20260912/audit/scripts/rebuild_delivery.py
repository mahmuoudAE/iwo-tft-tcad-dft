"""Package explicitly selected, verified native runs; never run a simulator.

Only ATLAS output filenames, matching EXTRACT input references, TonyPlot calls,
and intermediate DeckBuild QUIT delimiters may differ from evaluated inputs.
An electrically acceptable run is not automatically a calibrated model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

import rebuild_check as check
from rebuild_report import MASK_DEFINITIONS, metrics as report_metrics

ROOT = Path(__file__).resolve().parents[1]
KEY_ORDER = ('2p0', '6p3', '13p2', '31p8')
FILE_TOKEN = re.compile(
    r'(?<![\w.])(?P<key>outf|outfile|afile|dfile|tfile|infile)\s*=\s*'
    r'(?P<value>"[^"\r\n]*"|\'[^\'\r\n]*\'|[^\s\\]+)', re.I)
OUTPUT_KEYS = {'save': {'outf', 'outfile'}, 'log': {'outf', 'outfile'},
               'defects': {'afile', 'dfile'}, 'intdefects': {'afile', 'dfile', 'tfile'},
               'extract': {'outfile'}}
LEAF = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]*\Z')


def sha_text(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def logical_records(deck):
    """Retain original bytes/line wrapping for every logical command."""
    records, current = [], ''
    for line in deck.splitlines(keepends=True):
        current += line
        if not line.rstrip().endswith('\\'):
            records.append(current)
            current = ''
    if current:
        raise ValueError('Unterminated ATLAS continuation')
    return records


def command_name(record):
    stripped = record.lstrip()
    return '' if not stripped or stripped.startswith('#') else stripped.split()[0].lower()


def leaf_value(token):
    value = token[1:-1] if token[:1] in ('"', "'") else token
    if not LEAF.fullmatch(value) or '..' in value:
        raise ValueError('Only plain project-local output filenames are supported: ' + value)
    return value


def output_inventory(deck):
    """Reject unknown filename semantics instead of globally replacing text."""
    outputs, plots, references = {}, [], []
    records = logical_records(deck)
    names = [command_name(record) for record in records if command_name(record)]
    if names.count('go') != 1 or names[0] != 'go' or names[-1] != 'quit' or names.count('quit') != 1:
        raise ValueError('Expected one standalone ATLAS block ending with QUIT')
    if 'tonyplot' in names:
        raise ValueError('Source must be the evaluated batch input, without TonyPlot additions')
    for record in records:
        cmd = command_name(record)
        if not cmd:
            continue
        for match in FILE_TOKEN.finditer(record):
            key, value = match['key'].lower(), leaf_value(match['value'])
            if key == 'infile' and cmd == 'extract' and re.match(r'\s*extract\s+init\b', record, re.I):
                if value not in outputs:
                    raise ValueError('EXTRACT references a file not produced earlier: ' + value)
                references.append(value)
            elif key in OUTPUT_KEYS.get(cmd, set()):
                if value in outputs:
                    raise ValueError('Repeated output would overwrite earlier evidence: ' + value)
                outputs[value] = cmd
                if cmd in ('save', 'log'):
                    if Path(value).suffix.lower() not in ('.str', '.log'):
                        raise ValueError('Unexpected structure/log filename: ' + value)
                    plots.append(value)
            else:
                raise ValueError('Unsupported filename command: ' + record.strip())
    if not outputs or not plots:
        raise ValueError('No native output files found')
    return outputs, plots, references


def replace_filenames(deck, mapping):
    """Only replace parsed filename assignments; titles and physics stay intact."""
    result = []
    for record in logical_records(deck):
        if not command_name(record):
            result.append(record)
            continue
        def replace(match):
            old = leaf_value(match['value'])
            if old not in mapping:
                raise ValueError('Unmapped filename assignment: ' + old)
            token = match['value']
            quote = token[0] if token[:1] in ('"', "'") else ''
            new_token = quote + mapping[old] + quote
            return match.group(0)[:match.start('value') - match.start()] + new_token
        result.append(FILE_TOKEN.sub(replace, record))
    return ''.join(result)


def canonical_commands(deck):
    return check.commands(deck)


def verify_equivalence(source, delivered, mapping, intermediate=False):
    """Reverse only approved filename changes and account for added UI/control."""
    outputs, plot_sources, _ = output_inventory(source)
    if set(mapping) != set(outputs) or len(set(mapping.values())) != len(mapping):
        raise ValueError('Filename mapping must be a one-to-one complete output map')
    inverse = {value: key for key, value in mapping.items()}
    kept, plotted = [], []
    for record in logical_records(delivered):
        if command_name(record) == 'tonyplot':
            words = record.strip().split()
            if len(words) != 2:
                raise ValueError('Unexpected TonyPlot options or expression')
            plotted.append(words[1])
        else:
            kept.append(record)
    if plotted != [mapping[name] for name in plot_sources]:
        raise ValueError('TonyPlot must cover every saved STR/log exactly once in order')
    restored = replace_filenames(''.join(kept), inverse)
    if intermediate:
        if 'quit' in [command_name(record) for record in logical_records(restored)]:
            raise ValueError('Intermediate combined block must not terminate DeckBuild')
        restored = restored.rstrip() + '\nquit\n'
    if canonical_commands(source) != canonical_commands(restored):
        raise ValueError('Non-output ATLAS commands changed during delivery construction')
    return sha_text('\n'.join(canonical_commands(source)) + '\n')


def delivery_block(source, prefix, intermediate=False):
    if not LEAF.fullmatch(prefix) or '..' in prefix:
        raise ValueError('Unsafe output prefix')
    outputs, plot_sources, _ = output_inventory(source)
    mapping = {name: prefix + '_' + name for name in outputs}
    renamed = replace_filenames(source, mapping)
    result = []
    for record in logical_records(renamed):
        if command_name(record) == 'quit':
            result.append('# Delivery UI: show each native saved structure and transfer log.\n')
            result += ['tonyplot ' + mapping[name] + '\n' for name in plot_sources]
            if not intermediate:
                result.append(record)
        else:
            result.append(record)
    text = ''.join(result)
    digest = verify_equivalence(source, text, mapping, intermediate=intermediate)
    return text, mapping, digest


def measured_metrics(run):
    """Use the scientific report's signed-positive policy without divergence."""
    _, _, _, regions, diagnostic, endpoint = report_metrics(run)
    return dict(
        mask_definitions=MASK_DEFINITIONS,
        positive_log_policy='log10(native signed ID/W / measurement) only where native ID/W > 0. '
        'Zero and negative points have no logarithmic residual; read every positive-only RMSE with '
        'its explicit denominator. A region with no positive native points has a null log RMSE. '
        'Nonpositive points remain in signed linear residuals and native sign counts.',
        regions=regions, endpoint=endpoint,
        guarded_all_log_diagnostic=diagnostic)


def output_location(out, sources):
    out = Path(out).resolve()
    if out == ROOT or not out.is_relative_to(ROOT) or out.exists():
        raise ValueError('Output must be a new, nonexistent directory inside this project')
    # An active run has no completion manifest yet. Protect the entire reserved
    # evidence namespace, including unfinished runs that were not selected.
    if out.is_relative_to((ROOT / 'results/local_session_20260910/runs').resolve()):
        raise ValueError('Delivery output cannot be inside the reserved raw-run namespace')
    for source in sources:
        if out.is_relative_to(source) or source.is_relative_to(out):
            raise ValueError('Delivery output cannot contain or modify a source run')
    if any((parent / 'execution.json').is_file() for parent in out.parents if parent.is_relative_to(ROOT)):
        raise ValueError('Delivery output cannot be inside any native run evidence directory')
    return out


def package(run_paths, out):
    if not run_paths:
        raise ValueError('Choose at least one explicit evaluated run; none are selected automatically')
    sources = [Path(path).resolve() for path in run_paths]
    out = output_location(out, sources)
    # All real evidence is checked before any output directory is created.
    selected = [check.load_run(path) for path in sources]
    if any(not run['summary']['run_acceptable'] for run in selected):
        raise ValueError('A selected run fails recomputed native electrical checks')
    keys = [run['key'] for run in selected]
    if len(set(keys)) != len(keys) or any(key not in KEY_ORDER for key in keys):
        raise ValueError('Select exactly one run per included known thickness')
    selected.sort(key=lambda run: KEY_ORDER.index(run['key']))
    prepared, combined = [], []
    for index, run in enumerate(selected):
        key = run['key']
        prefix = 'iwo_' + key + 'nm'
        individual, mapping, digest = delivery_block(run['deck'], prefix)
        block, combined_mapping, combined_digest = delivery_block(run['deck'], prefix, index < len(selected) - 1)
        if mapping != combined_mapping or digest != combined_digest:
            raise ValueError('Individual and combined physics fingerprints disagree')
        combined.append('# Source run: ' + run['summary']['run_id'] + '\n' + block.rstrip() + '\n\n')
        prepared.append((run, individual, mapping, digest))
    combined_text = ''.join(combined)
    if sum(command_name(record) == 'quit' for record in logical_records(combined_text)) != 1:
        raise ValueError('Combined delivery must terminate exactly once')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'individual').mkdir()
    (out / 'combined').mkdir()
    (out / 'data').mkdir()
    manifest = dict(status='REPRODUCIBLE_FROM_COMPLETED_ATLAS_RUNS_NOT_A_NEW_SIMULATION',
                    includes_all_four_thicknesses=set(keys) == set(KEY_ORDER),
                    verification_scope='Recomputed native electrical checks and canonical filename-only command equivalence. '
                    'This does not automatically certify mesh/DOS convergence, unique physical parameters, or measurement-fit acceptance.',
                    combined_file='combined/IWO_SELECTED_ALL.in',
                    combined_execution_status='NOT_EXECUTED_BY_PACKAGER', runs=[])
    for run, individual, mapping, digest in prepared:
        key = run['key']
        source = Path(run['summary']['directory'])
        evidence = out / 'evidence' / key
        evidence.mkdir(parents=True)
        # Only already verified actual artifacts; no installation files/manuals.
        names = set(run['summary']['raw_output_sha256']) | {'execution.json', 'device.in',
                    'input_config.json', 'comparison_all_measurements.csv'}
        hashes = {}
        for name in sorted(names):
            original = (source / name).resolve()
            if not original.is_relative_to(source):
                raise ValueError('Evidence path escaped selected source run')
            target = evidence / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
            hashes[name] = check.sha(target)
            expected = run['summary']['raw_output_sha256'].get(name, run['summary']['evidence_sha256'].get(name))
            if hashes[name] != expected:
                raise ValueError('Source evidence changed while packaging: ' + name)
        relative_data = check.DATA[key]
        shutil.copyfile(ROOT / relative_data, out / relative_data)
        if check.sha(out / relative_data) != run['summary']['measurement_sha256']:
            raise ValueError('Original measurements changed while packaging')
        name = 'individual/iwo_' + key + 'nm.in'
        (out / name).write_text(individual, encoding='utf-8', newline='\n')
        manifest['runs'].append(dict(key=key, source_run_id=run['summary']['run_id'],
                                    source_directory=str(source), evidence_directory='evidence/' + key,
                                    individual_file=name, output_filename_mapping=mapping,
                                    canonical_original_commands_sha256=digest,
                                    filename_only_equivalence_pass=True,
                                    combined_control_change='Intermediate QUIT removed; final block QUIT retained.',
                                    copied_evidence_sha256=hashes, native_verification=run['summary'],
                                    recomputed_measurement_metrics=measured_metrics(run)))
    (out / manifest['combined_file']).write_text(combined_text, encoding='utf-8', newline='\n')
    readme = '''# Selected IWO ATLAS delivery

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
'''
    (out / 'README.md').write_text(readme, encoding='utf-8', newline='\n')
    manifest['delivery_sha256'] = {path.relative_to(out).as_posix(): check.sha(path)
                                   for path in sorted(out.rglob('*')) if path.is_file()}
    (out / 'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest, indent=2, allow_nan=False), encoding='utf-8')
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='append', required=True, help='Explicit selected native run directory; repeat per thickness')
    parser.add_argument('--out', required=True, help='New project-local output directory (must not already exist)')
    args = parser.parse_args(argv)
    try:
        result = package(args.run, args.out)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, 'Delivery rejected: ' + str(exc) + '\n')
    print(json.dumps(dict(output=str(Path(args.out).resolve()), status=result['status'],
                          included_thicknesses=[run['key'] for run in result['runs']])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
