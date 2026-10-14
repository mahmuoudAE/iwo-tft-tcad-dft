#!/usr/bin/env python3
"""f9_writers.py: blind writers of the D-42 F9 evidence records (draft v15, 2026-10-14). Standard library only.

Every record is a pure function of its bound sources and its parameters:
    {'schema': 'iwo-f9-evidence/2', 'type': ..., 'params': {...}, 'sources': {...{file, sha256}...},
     'derived': derive(type, params, sources), 'writer': VERSION, 'writer_sha256': writer_fingerprint()}
The checker (cert_assert.py) resolves the sources by sha256, calls the SAME derive() again (and re-derives every
record the sources reference) and rejects any difference.

v4 (Codex 2026-10-12T20:25Z, FIX_FIRST):
  1. force blocks: atom indices 1..N exactly once, types equal to the input (f9_common.read_qe_output);
  2. lineage: separate assertions for the registered ionic thresholds (forc_conv_thr 1e-3 AND etot_conv_thr 1e-4)
     and the final residual; terminal SCF failures of the active (last) epoch are preserved and veto convergence;
     failures of earlier epochs are disclosed separately;
  3. every input and output a writer uses must be the exported file itself (listed in the run's export manifest,
     sha256); FINAL / companion / reference manifests must also contain every certified run file;
  4. the C3 inventory is derived from the frozen F10 plan and one HTCondor user log per slot: every submitted
     attempt (fresh or density-seeded) is accounted for, and every attempt with an export has exactly one report;
  5. A31(f) role selection is derived from bound relaxation_lineage status records at the (extension-aware) cutoff;
  6. HTCondor 'MM/DD HH:MM:SS' event headers with year and zone from bound offset evidence (f9_common).
v5 (Codex 20:44Z): no-output attempts need an explained disposition in their user log; FINAL / companion /
  reference inputs must be the as-run scf.in recorded in the certified lineage file; both C3 endpoints'
  start modes are derived; D-24 exp/MANIFEST format and archive members recomputed from listed archives.
v9 (Codex v8 review, FIX_FIRST): (1) every relaxation segment must be the registered fresh start (restart_mode,
  startingpot, startingwfc with QE defaults resolved); (2) a bestvalid member must be the validated minimum of the
  segment's own bound evaluations; a paused CONTINUE resumes from the returned geometry, only a FAILED segment may
  restart from its verified best validated geometry; (3) a section-3 rescue needs a registered authorization (once,
  remaining executions preserved, exhaustion or a prospective suspension rule) and no reset or rescue follows a
  terminal failure after a rescue start; label splits only in the A25/A30/A34 scope; (4) final_run derives the
  registered-template key (cert_assert checks it).
v15 (Codex 2026-10-14T08:59Z): the A43 dry-run arguments are parsed with HTCondor's quoting rules and unsupported submit
  directives are refused (f9_common).
v14 (Codex v13 review, FIX_FIRST): (1) the A43 submission binding (f9_common.a43_submission_problem) is mandatory for a
  continuation-amendment rescue; (2) the execution budget counts every cluster, but the scientific position is anchored
  at the authorized rescue (the last pw.x position + 1) and advances only with pw.x segments of the new attempt, and a
  guard-only first execution carries its pending rescue transition (geometry rule included) to the first actual SCF.
v13 (Codex v12 review, FIX_FIRST): registered transitions use the scientific position (node executions before the
  segment, guard-only included) so an A36 rescue resumed as a2.s0 after the pause is still "s1"; the [infra] bestvalid
  exception is disabled; a continuation-amendment rescue binds the A43 DAG set (original DAG, config, dry run, optional
  dagman.out) and its RETRY must equal remaining - 1.
v12 (Codex v11 review, FIX_FIRST): guard-only rescues keep their authorization record and the terminal-status checks
  (_no_revival) run at every administrative boundary in execution order; no pw.x continuation follows a D-24 FAILED [scf]
  after a rescue start; the [infra] bestvalid exception needs its registered chain and a rollback (restoration) record
  logged before the reset; resource predicates are structural (f9_common).
v11 (Codex v10 review, FIX_FIRST): (1) an attempt change at a guard-only first execution needs the verified rescue
  record (authorization, budget, rescue file) like any other; (2) partial splits fail; (3) G* applies the registered
  minimum and tie rules to all eligible evaluations before deduplication. Answers: rescue files bound (remaining RETRY
  within the preserved budget); historical_rescue basis (contemporaneous authorization, never A39's +9); resource-route
  evidence from the split segment's own cluster; A34's bestvalid rollback exception for [infra].
v10 (Codex v9 review, FIX_FIRST): the DAG allowance (9 node executions, one per cluster, guard-only included) is bound
  from attempt 1 and grows only by an authorized rescue (A39 +9 after exhaustion; a suspension or a result-informed
  continuation amendment grants nothing); the suspension rule must predate the pause start; a continuation amendment is
  logged after the pause start and before resumption and states the preserved remaining executions, prior rescue use and
  terminal status; a split needs its resource route and unsplit input (registered construction); an [infra] failure
  reset keeps the segment input (ruling b).
v6 (Codex 2026-10-13 ~01:45Z): (1) a C3 attempt with a non-success termination is 'no_output' only with a bound,
  verified artifact inventory of its export directory showing no export; otherwise the inventory is unresolved;
  (2) a relaxation segment's input is the saved relax_s<k>_input.in of the verified job relax_s<k>, never the
  returned relax.in (replaced by the next / final geometry).

Sources: pw.x inputs, QE text through the A39(a6) allowlist, export manifests (sha256sum format), HTCondor user logs,
offset evidence, snapshot metadata, certify stdout (allowlisted keys), sealed rc7 reports (allowlisted keys),
certificates, other F9 records, the F10 C3 plan, and for the extension the redacted confirmation and work-chat entry.

CLI:  python -I -B f9_writers.py <type> --spec SPEC.json --out RECORD.json
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import f9_common as F  # noqa: E402

VERSION = 'f9_writers 0.15.0-draft (D-42 F9 v15, 2026-10-14)'
FILE_KEYS = ('relax_in', 'relax_out', 'joblog', 'snapshot_out', 'snapshot_meta', 'scf_in', 'scf_out', 'final_in',
             'certify_output', 'ref_in', 'comp_in', 'comp_certify_output', 'ref_certify_output', 'audit_report',
             'parent', 'parent_certificate', 'polish_lineage', 'qualification', 'reused_final', 'lineage',
             'offset_evidence', 'confirmation', 'work_chat_entry', 'extension', 'export_manifest',
             'ref_export_manifest', 'comp_export_manifest', 'plan', 'primary', 'backup', 'lineage_file',
             'ref_lineage_file', 'comp_lineage_file', 'artifact_inventory', 'reset_evidence',
             'transition_record', 'job_history', 'unsplit_input', 'rescue_file', 'resource_history', 'rollback_record', 'original_dag', 'dag_config', 'dry_run_sub',
             'dagman_out', 'submit_record', 'dagman_ad')
FILE_LIST_KEYS = ('c3_reports', 'archives', 'ref_archives', 'comp_archives')
SCALAR_KEYS = ('segment', 'cluster', 'slot', 'attempt', 'resource_route')
TYPES = ('relaxation_lineage', 'qualification_scf', 'final_run', 'c3_companion_run', 'c4_polish', 'a15_provisional',
         'readout_manifest', 'cutoff_selection', 'cern_extension')
A15_STATUS = 'provisional (EA not evaluated)'
A15_ROLE_CELLS = {'aIO': ('aIO_2p0_s1', 'aIO_2p0_s2'), 'aIWO': ('aIWO_2p0_s1', 'aIWO_2p0_s2'),
                  'compensated': ('aIWO_2p0_comp_s1', None)}
PLAN_SCHEMA = 'iwo-f10-c3-plan/2'          # v7: + export_root and the runs of every slot
RUN_NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.+-]*$')


def writer_fingerprint():
    h = hashlib.sha256()
    for name in ('f9_common.py', 'f9_writers.py'):
        h.update(name.encode())
        with open(os.path.join(HERE, name), 'rb') as f:
            h.update(f.read())
    return h.hexdigest()


# ---------------------------------------------------------------- source references
def to_refs(src, base_dir):
    def ref(p):
        p = os.path.abspath(p)
        try:
            rel = os.path.relpath(p, base_dir).replace(os.sep, '/')
        except ValueError:
            rel = p
        return {'file': rel, 'sha256': F.sha256_file(p)}
    out = {}
    for k, v in src.items():
        if v is None:
            continue
        if k in FILE_KEYS:
            out[k] = ref(v)
        elif k in FILE_LIST_KEYS:
            out[k] = [ref(x) for x in v]
        elif k in SCALAR_KEYS:
            out[k] = v
        elif isinstance(v, list):
            out[k] = [to_refs(x, base_dir) for x in v]
        elif isinstance(v, dict):
            out[k] = to_refs(v, base_dir)
        else:
            raise ValueError(f'unknown source key {k!r}')
    return out


def resolve(refs, base_dir):
    """refs -> paths, every file sha256-checked. Raises DeriveError('source_...') on any failure."""
    def one(r):
        if not isinstance(r, dict) or not isinstance(r.get('file'), str) or not isinstance(r.get('sha256'), str):
            raise F.DeriveError('source_reference_malformed')
        p = r['file'] if os.path.isabs(r['file']) else os.path.join(base_dir, r['file'])
        if not os.path.isfile(p):
            raise F.DeriveError('source_file_missing')
        if F.sha256_file(p) != r['sha256']:
            raise F.DeriveError('source_sha256_mismatch')
        return p
    if not isinstance(refs, dict):
        raise F.DeriveError('sources_malformed')
    out = {}
    for k, v in refs.items():
        if k in FILE_KEYS:
            out[k] = one(v)
        elif k in FILE_LIST_KEYS:
            if not isinstance(v, list):
                raise F.DeriveError('sources_malformed')
            out[k] = [one(x) for x in v]
        elif k in SCALAR_KEYS:
            out[k] = v
        elif isinstance(v, list):
            out[k] = [resolve(x, base_dir) for x in v]
        elif isinstance(v, dict):
            out[k] = resolve(v, base_dir)
        else:
            raise F.DeriveError('sources_unknown_key')
    return out


def referenced_files(paths):
    """Every resolved file path in a resolved sources structure (for recursive re-derivation by the checker)."""
    out = []
    for k, v in paths.items():
        if k in FILE_KEYS and isinstance(v, str):
            out.append(v)
        elif k in FILE_LIST_KEYS and isinstance(v, list):
            out += [x for x in v if isinstance(x, str)]
        elif k in SCALAR_KEYS:
            continue
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, dict):
                    out += referenced_files(x)
        elif isinstance(v, dict):
            out += referenced_files(v)
    return out


def load_json(path):
    with open(path, 'rb') as f:
        try:
            o = json.loads(f.read().decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise F.DeriveError('source_not_json')
    if not isinstance(o, dict):
        raise F.DeriveError('source_not_object')
    return o


def load_record(path, rtype):
    o = load_json(path)
    if o.get('schema') != F.RECORD_SCHEMA or o.get('type') != rtype:
        raise F.DeriveError(f'source_not_{rtype}')
    return o


def bound(d):
    return {k: v for k, v in (d or {}).items() if isinstance(k, str) and not k.startswith('_')}


def _tz(paths):
    return F.read_offset_evidence(paths['offset_evidence']) if paths.get('offset_evidence') else None


# ---------------------------------------------------------------- segments (bound to exports or snapshots)
SEGMENT_OUTPUT = 'relax.out'                                    # D-24 segment output member (d24_transition.sh:49)
SCF_INPUT, SCF_OUTPUT = 'scf.in', 'scf.out'                     # D-24 FINAL / qualification member names


def _identity_manifest(path, what):
    """v7 (Codex v6 review item 3): returned archives are listed in an archive-identity record (run, cluster, k per
    archive; f9_common._read_identity). A sha256sum list without job identity is refused."""
    man = F.read_export_manifest(path)
    if man['format'] != 'identity':
        raise F.DeriveError(f'{what}_archive_record_without_run_and_cluster_identity')
    return man


def _identified_archive(man, archives, name, cluster, k, what):
    """The one listed archive called `name` (sha256 and size in the record); its identity line must name this cluster
    (and segment k). None if no listed archive has that name."""
    arcs = [a for a in archives or [] if F._basename(a) == name and F._listed(man, a)]
    if len(arcs) != 1:
        return None
    ident = man['identity'].get(name)
    if ident is None or ident[0] != int(cluster) or (k is not None and ident[1] != k):
        raise F.DeriveError(f'{what}_archive_identity_differs_from_the_job')
    return arcs[0]


def _geometry_of(data):
    return F.input_geometry_hash(F.read_pw_input_bytes(data)) if data is not None else None


def _bind_segment(s, k, tz):
    """v6 (Codex 2026-10-13 blocking 2) and v7 (Codex v6 review items 2 and 3; rulings on pre-item-B inputs and
    guard-only attempts). Segment k (its verified index, contiguous from 0, historical indices kept) is job relax_s<k>.
      * Identity: exactly one listed relax_s<k>_results.tar.gz whose identity line names this run, cluster and k; every
        member written in-job carries a tar mtime inside that cluster's last execution (bound user log).
      * Guard-only attempt (relax_node.sh:19-34): the archive has relax_s<k>_driver.log 'stopped before pw.x' and no
        relax.out; no input or output may be claimed for it.
      * Item-B segment: relax_s<k>_lineage.log names the job; relax_in = member relax_s<k>_input.in; never the returned
        relax.in (replaced by the next / final geometry).
      * Pre-item-B segment: relax_in = relax.in of the attempt's EOS checkpoint relax_s<k>_<cluster>.tar.gz (or its
        --to-eos copy relax_s<k>_ckpt_<cluster>.tar.gz), listed with the same run, cluster and k, whose relax.out is
        the returned relax.out (same attempt).
      * relax_out = member relax.out of the job archive. The returned relax.in gives the geometry the next segment
        must start from (_segments).
    A running segment may instead be pinned by its snapshot metadata. No other provenance is accepted."""
    job = F.segment_job(k)
    if s.get('export_manifest'):
        man = _identity_manifest(s['export_manifest'], 'segment')
        cl = s.get('cluster')
        if cl is None:
            raise F.DeriveError('segment_cluster_missing')
        if not s.get('joblog'):
            raise F.DeriveError('segment_joblog_missing')
        arc = _identified_archive(man, s.get('archives'), F.SEGMENT_ARCHIVE.format(job=job), cl, k, 'segment')
        if arc is None:
            raise F.DeriveError('relax_in_not_bound_to_the_historical_export')
        win = F.job_window(s['joblog'], cl, tz)
        returned = F.archive_member_bytes(arc, F.SEGMENT_RETURNED_RELAX_IN)
        base = {'job': job, 'run': man['run'], 'cluster': int(cl), 'archive_sha256': F.sha256_file(arc),
                'archive_name': F._basename(arc), 'returned_geometry_sha256': _geometry_of(returned),
                'bestvalid_geometry_sha256': _geometry_of(F.archive_member_bytes(arc, f'{job}_bestvalid.in')),
                'status': None, 'category': None}
        out_sha = F.archive_member_sha256(arc, SEGMENT_OUTPUT)
        drv = F.SEGMENT_DRIVER_LOG.format(job=job)
        first = F.archive_member_first_line(arc, drv)
        if out_sha is None and first is not None and F.RX_GUARD_STOP.match(first):
            if s.get('relax_in') or s.get('relax_out'):
                raise F.DeriveError('guard_only_attempt_with_a_claimed_input_or_output')
            F.check_members_in_window(arc, [drv], win, 'segment')
            return dict(base, kind='guard_only', input_member=None)
        if not s.get('relax_in') or not s.get('relax_out'):
            raise F.DeriveError('segment_input_provenance_missing')
        if out_sha != F.sha256_file(s['relax_out']):
            raise F.DeriveError('relax_out_not_bound_to_the_historical_export')
        if returned is None:
            raise F.DeriveError('segment_returned_relax_in_missing')
        h = F.sha256_file(s['relax_in'])
        member, lin = F.SEGMENT_SAVED_INPUT.format(job=job), F.SEGMENT_LINEAGE_LOG.format(job=job)
        if F.archive_member_first_line(arc, lin) is not None or F.archive_member_sha256(arc, member) is not None:
            _, st, cat = F.segment_lineage_job(arc, job)                      # item-B
            saved = F.archive_member_sha256(arc, member)
            if saved is None:
                raise F.DeriveError('segment_saved_input_missing_from_the_job_archive')
            if h != saved:
                if h == hashlib.sha256(returned).hexdigest():
                    raise F.DeriveError('relax_in_is_the_returned_next_geometry_not_the_saved_input')
                raise F.DeriveError('relax_in_not_bound_to_the_historical_export')
            F.check_members_in_window(arc, [member, SEGMENT_OUTPUT, lin], win, 'segment')
            return dict(base, kind='item_b', input_member=member, status=st, category=cat)
        cks = [c for c in (_identified_archive(man, s.get('archives'), n.format(k=k, cluster=int(cl)), cl, k,
                                               'segment') for n in F.CHECKPOINT_NAMES) if c is not None]
        if len(cks) != 1:                                                     # pre-item-B: the EOS checkpoint
            raise F.DeriveError('pre_item_b_segment_without_its_checkpoint_input')
        ck = cks[0]
        if F.archive_member_sha256(ck, F.SEGMENT_RETURNED_RELAX_IN) != h:
            if h == hashlib.sha256(returned).hexdigest():
                raise F.DeriveError('relax_in_is_the_returned_next_geometry_not_the_saved_input')
            raise F.DeriveError('relax_in_not_bound_to_the_checkpoint_input')
        if F.archive_member_sha256(ck, SEGMENT_OUTPUT) != out_sha:
            raise F.DeriveError('checkpoint_output_differs_from_the_returned_output')
        F.check_members_in_window(arc, [SEGMENT_OUTPUT], win, 'segment')
        F.check_members_in_window(ck, [SEGMENT_OUTPUT], win, 'segment')
        return dict(base, kind='pre_item_b', input_member=F._basename(ck) + ':relax.in')
    if s.get('snapshot_meta'):
        meta = load_json(s['snapshot_meta'])
        if not s.get('relax_in') or not s.get('relax_out') or \
                meta.get('snapshot_sha256') != F.sha256_file(s['relax_out']) or \
                meta.get('relax_in_sha256') != F.sha256_file(s['relax_in']):
            raise F.DeriveError('snapshot_meta_does_not_pin_these_files')
        return {'job': job, 'run': None, 'cluster': s.get('cluster'), 'archive_sha256': None, 'archive_name': None,
                'kind': 'snapshot', 'input_member': None, 'returned_geometry_sha256': None,
                'bestvalid_geometry_sha256': None, 'status': None, 'category': None}
    raise F.DeriveError('segment_input_provenance_missing')


def _validated_minimum(q):
    """v9 (Codex v8 item 2): the lowest-energy validated evaluation(s) of a segment's own bound output (geomsel rule)."""
    ev = q['evaluations']
    if not ev:
        return set()
    low = min(e['F_Ry'] for e in ev)
    return {e['geometry_sha256'] for e in ev if e['F_Ry'] == low}


def _best_valid(prev):
    """The previous segment's best validated geometry, RECOMPUTED from its bound evaluations; a relax_s<k>_bestvalid.in
    member (D-24 FAILED) must equal it (checked when the segment is bound, _segments) and is never trusted by name."""
    pe, pb, pq = prev
    allowed = _validated_minimum(pq)
    if pb['bestvalid_geometry_sha256']:
        if pb['bestvalid_geometry_sha256'] not in allowed:
            raise F.DeriveError('bestvalid_member_is_not_the_validated_minimum')
        return {pb['bestvalid_geometry_sha256']}
    return allowed


def _verify_d24_reset(s, prev, entry, last_end, t_first):
    """v7: the scripted D-24 transition reset (d24_transition.sh:63-67, 82) of a pre-D-24 segment. v8: its log line
    lies between the previous segment's end and this segment's first execution (when the job read relax.in)."""
    pe, pb, pq = prev
    if pb['kind'] != 'pre_item_b':
        raise F.DeriveError('reset_evidence_for_a_segment_that_ran_the_d24_steps')
    hits = [t for t, kk in F.d24_resets(s['reset_evidence']) if kk == pe['k']]
    if len(hits) != 1:
        raise F.DeriveError('reset_evidence_does_not_name_the_previous_segment')
    if hits[0] is None or not (last_end <= hits[0] <= t_first):
        raise F.DeriveError('reset_evidence_time_not_between_the_segments')
    if entry['start_geometry_sha256'] not in _best_valid(prev):
        raise F.DeriveError('reset_geometry_is_not_the_lowest_energy_validated_geometry')


def _verify_rescue_authorization(rec, run, last, state, t_first, prev):
    """v9/v10 (Codex v8 item 3, v9 cases 1-2 and ruling a): a section-3 rescue (rescue DAG) needs a registered or built-in
    (A39) authorization, used once. The DAG allowance is bound from attempt 1 (F.DAG_NODE_EXECUTIONS) and grows only by
    the authorization's additional executions: the record restates remaining_before = allowance - executions used and
    remaining_after = remaining_before + additional (HTCondor's rescue retry reset is never inherited). Bases:
      exhausted               remaining_before == 0; A39 also needs the last pw.x segment CONTINUE or FAILED non-[scf];
      suspension              a rule logged no later than the actual pause start (pause before the resumption); +0;
      continuation_amendment  result-informed, logged after the pause start and before the resumed first execution,
                              stating the preserved remaining executions, prior rescue use and terminal status; +0."""
    a = rec.get('auth')
    if a and a['ref'] in state['refs']:                                   # once-use (A39: once per chain)
        raise F.DeriveError('rescue_authorization_already_used')
    reg = None
    if a:
        reg = F.BUILTIN_RESCUE_AUTHORIZATIONS.get(a['ref']) or F.REGISTERED_RESCUE_AUTHORIZATIONS.get(a['ref'])
    if not a or not isinstance(reg, dict) or (reg.get('run') is not None and reg.get('run') != run) or \
            (reg.get('after_attempt') is not None and reg.get('after_attempt') != last['attempt']):
        raise F.DeriveError('rescue_without_a_registered_authorization')
    if a['prior_rescues'] != len(state['refs']):
        raise F.DeriveError('rescue_prior_use_not_preserved')
    if a['remaining_before'] != state['allowance'] - state['executions']:
        raise F.DeriveError('rescue_budget_not_preserved')
    add = reg.get('additional_executions', 0)
    if not isinstance(add, int) or add < 0 or a['remaining_after'] != a['remaining_before'] + add:
        raise F.DeriveError('rescue_resets_the_remaining_executions')
    if a['remaining_after'] < 1:
        raise F.DeriveError('rescue_budget_exhausted')
    basis = reg.get('basis')
    if basis == 'exhausted':
        if a['remaining_before'] != 0:
            raise F.DeriveError('rescue_without_exhaustion_of_the_previous_attempt')
        if reg.get('trigger') == 'a39':
            st, cat = prev[1].get('status'), prev[1].get('category')
            if not (st == 'CONTINUE' or (st == 'FAILED' and cat not in (None, 'scf'))):
                raise F.DeriveError('a39_trigger_not_met')
    elif basis in ('suspension', 'continuation_amendment'):
        if add != 0:
            raise F.DeriveError('suspension_grants_no_additional_executions')
        tp, tl = F.parse_utc(reg.get('pause_started_utc')), F.parse_utc(reg.get('rule_logged_utc'))
        if tp is None or tl is None or tp > t_first:
            raise F.DeriveError('pause_time_not_bound')
        if basis == 'suspension':
            if tl > tp:
                raise F.DeriveError('suspension_rule_not_prospective')
        else:
            if reg.get('result_informed') is not True:
                raise F.DeriveError('continuation_amendment_not_labelled_result_informed')
            if tl <= tp:
                raise F.DeriveError('continuation_amendment_backdated')
            if tl > t_first:
                raise F.DeriveError('continuation_amendment_logged_after_resumption')
            pres = reg.get('preserved') or {}
            if pres.get('remaining_executions') != a['remaining_before'] or \
                    pres.get('prior_rescues') != len(state['refs']) or pres.get('terminal_failure') is not False:
                raise F.DeriveError('continuation_does_not_preserve_the_state')
    elif basis == 'historical_rescue':                 # v11 (Codex v10 answer 2): e.g. the A15-era rescue DAG
        tl = F.parse_utc(reg.get('rule_logged_utc'))
        if not str(reg.get('authorization_ref') or '').strip() or tl is None or tl > t_first:
            raise F.DeriveError('historical_rescue_without_its_contemporaneous_authorization')
    else:
        raise F.DeriveError('rescue_without_a_registered_authorization')
    state['refs'].append(a['ref'])
    state['allowance'] += add
    return reg


def _verify_rescue_boundary(rec, s, prev, att, k, t_first, run, last, moved_before, state):
    """v11 (Codex v10 case 1): the administrative boundary of a new attempt, checked for its FIRST execution whether that
    is a pw.x segment or a guard-only node attempt: a section3_rescue record naming the previous pw.x segment, logged
    between the previous attempt's end and this first execution, moving exactly the previous attempt's archives, with a
    registered authorization and its rescue file (remaining RETRY within the preserved budget)."""
    pe = prev[0]
    if rec['kind'] != 'section3_rescue':
        raise F.DeriveError('attempt_change_without_rescue_record')
    if rec['run'] != run:
        raise F.DeriveError('transition_record_for_another_run')
    if rec['after'] != pe['job'] or rec['attempt'] != pe['attempt']:
        raise F.DeriveError('transition_record_does_not_name_the_previous_segment')
    if not (last['end'] <= rec['logged_utc'] <= t_first):
        raise F.DeriveError('transition_record_time_not_between_the_segments')
    if att != last['attempt'] + 1 or k != 0:
        raise F.DeriveError('rescue_does_not_start_a_new_attempt_at_s0')
    if rec['moved'] != moved_before:
        raise F.DeriveError('rescue_move_record_differs_from_the_previous_attempt')
    reg = _verify_rescue_authorization(rec, run, last, state, t_first, prev)
    if reg.get('basis') == 'continuation_amendment':      # v13/v14: the A43 count-enforcement files and submission binding
        if not all(s.get(x) for x in ('rescue_file', 'original_dag', 'dag_config', 'dry_run_sub', 'submit_record',
                                      'dagman_ad', 'dagman_out')):
            raise F.DeriveError('a43_count_enforcement_files_missing')
        p = F.a43_dag_problem(s['original_dag'], s['rescue_file'], s['dag_config'], s['dry_run_sub'], None,
                              rec['auth']['remaining_after'])
        p = p or F.a43_submission_problem(s['dry_run_sub'], s['rescue_file'], run, s['submit_record'], s['dagman_ad'],
                                          s['dagman_out'], s['cluster'], rec['auth']['remaining_after'] - 1)
        if p:
            raise F.DeriveError(p)
    if not s.get('rescue_file'):
        raise F.DeriveError('rescue_without_its_rescue_file')
    if F.rescue_file_retry(s['rescue_file']) + 1 > rec['auth']['remaining_after']:
        raise F.DeriveError('rescue_file_retry_exceeds_the_preserved_budget')


def _verify_transition(rec, prev, entry, run, last, moved_before, state=None, s=None, cell=None):
    """v8 (Codex v7 rulings; README_D24_BD.txt section 3, lines 70-87): a section-3 reset (same attempt) or rescue
    (the old tarballs moved to attempt<N>/, the rescue DAG restarting at s0) is an explicit administrative transition.
    The record names the run and the previous pw.x segment, is logged between the last attempt's end and this
    segment's first execution, a rescue lists exactly the archives of the previous attempt, and the new start is the
    returned or the best validated geometry of the previous segment."""
    pe, pb, pq = prev
    if rec['kind'] == 'section3_rescue' or entry['attempt'] != last['attempt']:
        _verify_rescue_boundary(rec, s or {}, prev, entry['attempt'], entry['k'], entry['_first'], run, last,
                                moved_before, state)
    elif rec['run'] != run:
        raise F.DeriveError('transition_record_for_another_run')
    elif rec['after'] != pe['job'] or rec['attempt'] != pe['attempt']:
        raise F.DeriveError('transition_record_does_not_name_the_previous_segment')
    elif not (last['end'] <= rec['logged_utc'] <= entry['_first']):
        raise F.DeriveError('transition_record_time_not_between_the_segments')
    elif entry['attempt'] != last['attempt']:
        raise F.DeriveError('attempt_change_without_rescue_record')
    elif rec.get('auth') is not None:
        raise F.DeriveError('reset_record_with_a_rescue_authorization')
    _verify_start_geometry(rec, prev, entry, run, last, s, cell)


def _verify_start_geometry(rec, prev, entry, run, last, s=None, cell=None):
    """v14: the start-geometry rules of an administrative boundary (returned relax.in after a CONTINUE; returned or the
    verified bestvalid after a FAILED segment; [infra] keeps the input), applied at the first actual pw.x segment - also
    when the boundary itself was a guard-only first execution (Codex v13 item 2)."""
    pe, pb, pq = prev
    start, returned = entry['start_geometry_sha256'], pb['returned_geometry_sha256']
    if pb.get('status') == 'FAILED' and pb.get('category') == 'infra' and start != returned:
        # v10 ruling (b) / A30 rollback: an [infra] reset keeps the segment input; v11/v12: A34's documented exception (a
        # fatal GPU error after a new validated geometry archives relax_s<k>_bestvalid.in) only on the registered chains and
        # with the restoration (rollback) record logged between the failure and the reset
        if not (pb.get('bestvalid_geometry_sha256') and start == pb['bestvalid_geometry_sha256']):
            raise F.DeriveError('infra_failure_reset_must_keep_the_input_geometry')
        if not F.INFRA_BESTVALID_ENABLED:                    # v13 (Codex v12 item 2): disabled pending restoration evidence
            raise F.DeriveError('infra_bestvalid_exception_disabled')
        if cell not in F.INFRA_BESTVALID_CELLS:
            raise F.DeriveError('infra_bestvalid_exception_outside_its_registered_scope')
        rb = F.read_rollback_record((s or {})['rollback_record']) if (s or {}).get('rollback_record') else None
        if rb is None or rb['run'] != run or rb['after'] != pe['job'] or \
                not (last['end'] <= rb['logged_utc'] <= rec['logged_utc']):
            raise F.DeriveError('infra_bestvalid_exception_without_restoration_evidence')
    if str(pb.get('status') or '').startswith('FAILED'):    # v9 ruling: a failure reset may use the verified bestvalid
        if start not in {returned} | _best_valid(prev):
            raise F.DeriveError('reset_geometry_is_not_the_returned_or_best_valid_geometry')
    elif start != returned:                                   # a paused CONTINUE resumes from the returned relax.in
        if start in _best_valid(prev):
            raise F.DeriveError('paused_continue_must_resume_from_the_returned_geometry')
        raise F.DeriveError('reset_geometry_is_not_the_returned_or_best_valid_geometry')


def _segments(paths, tz, cell=None):
    """The pw.x segments in order (guard-only attempts kept apart with their historical index), each bound by
    _bind_segment, all of one run, executed in order (v8: each attempt's first execution after the previous attempt's
    terminal event, guard-only attempts included), and linked: segment k starts from the geometry the previous pw.x
    segment returned, or crosses an explicit transition (D-24 transition reset; section-3 reset or rescue with its
    record). Attempts (v8): 'attempt' N >= 1, k contiguous from 0 inside each attempt; labels 's<k>' (attempt 1) or
    'a<N>.s<k>'. Returns (segments, parsed, guard_only, run, sources)."""
    segs = paths.get('segments')
    if not isinstance(segs, list) or not segs:
        raise F.DeriveError('segments_missing')
    pre = None
    out, parsed, guard, runs, srcs, prev, last, moved = [], [], [], set(), [], None, None, {}
    state = {'executions': 0, 'by_attempt': {}, 'refs': [], 'allowance': F.DAG_NODE_EXECUTIONS, 'clusters': set()}
    sci = {'att': 1, 'base': None, 'n': 0}      # v14: scientific position anchored at the authorized rescue (not the budget)
    pending = None                             # v14: a guard-only rescue start waiting for its first actual SCF

    def count(cl):                                     # v10: one node execution per cluster, from attempt 1
        if cl in state['clusters']:
            raise F.DeriveError('two_segments_claim_one_cluster')
        state['clusters'].add(cl)
        state['executions'] += 1
        state['by_attempt'][att] = state['by_attempt'].get(att, 0) + 1
        if state['executions'] > state['allowance']:
            raise F.DeriveError('executions_exceed_the_dag_allowance')
    for s in segs:
        letter, k = F.segment_index(s.get('segment'))
        att = s.get('attempt', 1)
        exp_k = 0 if last is None or att != last['attempt'] else last['k'] + 1
        if letter is None or (pre is not None and letter != pre) or not isinstance(att, int) or k != exp_k or \
                (last is None and att != 1) or (last is not None and att not in (last['attempt'], last['attempt'] + 1)):
            raise F.DeriveError('segments_not_contiguous_from_0')
        pre = letter
        b = _bind_segment(s, k, tz)
        if b['run'] is not None:
            runs.add(b['run'])
        if not s.get('joblog') or s.get('cluster') is None:
            raise F.DeriveError('segment_order_not_verifiable')
        t_first = F.first_execution_utc(s['joblog'], s['cluster'], tz)
        t_end = F.terminal_utc(s['joblog'], s['cluster'], tz)
        if t_first is None:
            raise F.DeriveError('segment_order_not_verifiable')
        if last is not None:                                   # v8 (Codex v7 item 3): ordered execution
            if last['end'] is None:
                raise F.DeriveError('segment_after_a_running_segment')
            if t_first < last['end']:
                raise F.DeriveError('segment_started_before_the_previous_segment_ended')
        label = s['segment'] if att == 1 else f'a{att}.{s["segment"]}'
        moved_before = moved.get(att - 1, set())
        if b['archive_name']:
            moved.setdefault(att, set()).add((b['archive_name'], b['archive_sha256']))
        if b['kind'] == 'guard_only':
            cont, grec = None, None
            if last is not None and att != last['attempt']:      # v11 (Codex v10 case 1): validate the boundary first
                if not s.get('transition_record'):
                    raise F.DeriveError('attempt_change_without_rescue_record')
                if prev is None:
                    raise F.DeriveError('transition_record_without_a_previous_segment')
                grec = F.read_transition_record(s['transition_record'])
                _verify_rescue_boundary(grec, s, prev, att, k, t_first,
                                        b['run'] if b['run'] is not None else (next(iter(runs)) if runs else None),
                                        last, moved_before, state)
                cont = 'section3_rescue'
                pending = {'rec': grec, 'att': att, 'last': last}
                sci = {'att': att, 'base': prev[0]['position'] + 1, 'n': 0}
            elif s.get('transition_record') or s.get('reset_evidence'):
                raise F.DeriveError('transition_record_on_a_guard_only_attempt')
            guard.append({'segment': label, 'attempt': att, 'k': k, 'job': b['job'], 'cluster': b['cluster'],
                          'archive_sha256': b['archive_sha256'], 'continuation': cont,      # v12: authorization kept
                          'rescue_record': dict(grec['auth']) if grec and grec.get('auth') else None, '_after_pw': len(out)})
            last = {'attempt': att, 'k': k, 'end': t_end}
            count(int(s['cluster']))
            continue
        inp = F.read_pw_input(s['relax_in'])
        q = F.read_qe_output(s['relax_out'], inp)
        start_eff, fresh = F.registered_start(inp)                 # v9 (Codex v8 item 1), defaults resolved
        if not fresh:
            raise F.DeriveError('segment_start_is_not_the_registered_fresh_start')
        if b['bestvalid_geometry_sha256'] and b['bestvalid_geometry_sha256'] not in _validated_minimum(q):
            raise F.DeriveError('bestvalid_member_is_not_the_validated_minimum')     # v9 (Codex v8 item 2)
        lsp = F.label_split_problem(cell, inp)                     # v9/v10 rulings: scope and construction
        if lsp:
            raise F.DeriveError(lsp)
        res_route = None
        if F.is_split(inp):                                        # v10: route evidence and the registered construction
            if prev is not None and parsed and parsed[-1][0]['labels'] == inp['labels'] and not s.get('unsplit_input'):
                res_route = prev[0]['resource_route']              # the same split continues
            else:
                if not s.get('resource_route') or not s.get('unsplit_input'):
                    raise F.DeriveError('label_split_without_construction_evidence')
                cp = F.split_construction_problem(cell, s['resource_route'], inp, F.read_pw_input(s['unsplit_input']))
                if cp:
                    raise F.DeriveError(cp)
                res_route = s['resource_route']
            if not s.get('resource_history'):                     # v11: every split segment's own cluster
                raise F.DeriveError('label_split_without_resource_evidence')
            rp = F.resource_route_problem(res_route, s['cluster'], s['resource_history'])
            if rp:
                raise F.DeriveError(rp)
        try:
            t, src = F.terminated_utc(s['joblog'], s['cluster'], tz), 'htcondor_job_log'
        except F.DeriveError as e:
            if str(e) != 'joblog_no_termination_event':
                raise
            t, src = None, None
        if t is None and s.get('snapshot_meta'):       # a running segment: its pinned snapshot's completion time
            t = F.parse_utc(load_json(s['snapshot_meta']).get('transfer_completed_utc'))
            if t is None:
                raise F.DeriveError('snapshot_meta_malformed')
            src = 'snapshot_completed_utc'
        fc, ec, srcs_ = F.ionic_thresholds(inp)
        entry = {'segment': label, 'attempt': att, 'k': k, 'cluster': s.get('cluster'), 'job': b['job'],
                 'kind': b['kind'], 'input_member': b['input_member'], 'settings_sha256': F.settings_sha256(inp),
                 'epoch_key': F.epoch_key(inp), 'smearing': F.family(inp['fields'].get('system.smearing')),
                 'degauss_Ry': inp['fields'].get('system.degauss'),
                 'start_geometry_sha256': F.input_geometry_hash(inp), 'n_validated': len(q['evaluations']),
                 'end_utc': F.fmt_utc(t), 'timing_source': src, 'bfgs_converged': q['bfgs_converged'],
                 'scf_failures': q['scf_fail'], 'd24_status': b['status'], 'd24_category': b['category'],
                 'bestvalid_geometry_sha256': b['bestvalid_geometry_sha256'],
                 'ionic_thresholds': {'forc_conv_thr': fc, 'etot_conv_thr': ec, 'sources': srcs_},
                 'continuation': None, 'rescue_start': False, 'start_settings': start_eff,
                 'rescue_record': None, 'resource_route': res_route, 'position': None, '_first': t_first}
        run = b['run'] if b['run'] is not None else (next(iter(runs)) if runs else None)
        if prev is None:
            if s.get('transition_record') or s.get('reset_evidence'):
                raise F.DeriveError('transition_record_without_a_previous_segment')
        elif s.get('transition_record'):
            if pending is not None and pending['att'] == att:
                raise F.DeriveError('transition_record_after_a_guard_only_rescue_start')
            rec = F.read_transition_record(s['transition_record'])
            _verify_transition(rec, prev, entry, run, last, moved_before, state, s, cell)
            entry['continuation'] = rec['kind']
            if rec['auth'] is not None:
                entry['rescue_record'] = dict(rec['auth'])
            if att != last['attempt']:                                 # v14: a pw.x first execution anchors the rescue
                sci = {'att': att, 'base': prev[0]['position'] + 1, 'n': 0}
        elif s.get('reset_evidence'):
            _verify_d24_reset(s, prev, entry, last['end'], t_first)
            entry['continuation'] = 'd24_transition_reset'
        elif pending is not None and pending['att'] == att:           # v14: the guard-only rescue start's pending transition
            _verify_start_geometry(pending['rec'], prev, entry, run, pending['last'], s, cell)
            entry['continuation'] = 'section3_rescue'
        elif att != last['attempt']:
            raise F.DeriveError('attempt_change_without_rescue_record')
        elif prev[1]['kind'] == 'snapshot':
            raise F.DeriveError('segment_after_a_running_segment')
        elif entry['start_geometry_sha256'] == prev[1]['returned_geometry_sha256']:
            entry['continuation'] = 'returned_geometry'
        else:
            raise F.DeriveError('segment_does_not_continue_the_previous_segment')
        pending = None
        if att == 1:                                   # v14: attempt-1 numbering is the registered numbering (k)
            entry['position'] = k
        elif sci['att'] == att and sci['base'] is not None:
            entry['position'] = sci['base'] + sci['n']
            sci['n'] += 1
        else:
            raise F.DeriveError('attempt_change_without_rescue_record')
        out.append(entry)
        parsed.append((inp, q))
        srcs.append(s)
        prev = (entry, b, q)
        last = {'attempt': att, 'k': k, 'end': t_end}
        count(int(s['cluster']))
    if not out:
        raise F.DeriveError('segments_without_a_pw_x_run')
    if len(runs) > 1:
        raise F.DeriveError('segments_from_different_runs')
    if len({p[0]['nat'] for p in parsed}) != 1 or len({tuple(p[0]['species']) for p in parsed}) != 1:
        raise F.DeriveError('segments_atom_order_differs')          # v8: elements per atom (label splits allowed)
    for e in out:
        del e['_first']
    return out, parsed, guard, (runs.pop() if runs else None), srcs


def _gate(b, segs, parsed):
    a, c = b.split('->')
    names = [s['segment'] for s in segs]
    ia, ic = names.index(a), names.index(c)
    carried = segs[ic]['start_geometry_sha256']
    prev = [e for e in parsed[ia][1]['evaluations'] if e['geometry_sha256'] == carried]
    nxt = parsed[ic][1]['evaluations']
    if not prev:
        return {'boundary': b, 'error': 'carried_geometry_not_among_previous_evaluations'}
    if not nxt or nxt[0]['geometry_sha256'] != carried:
        return {'boundary': b, 'error': 'first_scf_of_next_segment_missing'}
    dF, dmax, n = F.compare_evaluations(prev[-1], nxt[0])
    return {'boundary': b, 'geometry_sha256': carried, 'delta_F_Ry': dF, 'max_abs_dF_Ry_bohr': dmax, 'n_components': n}


def _transitions(cell, route, segs, parsed):
    """v8 (Codex v7 item 2): every settings change between consecutive pw.x segments is a pure label split (no epoch)
    or one registered transition with its exact state, segment, route and trigger (f9_common.registered_transition);
    otherwise not derivable. The conditional A36 rescue needs a FAILED [scf] segment that ended before the cutoff,
    its bestvalid geometry and its section-3 reset record."""
    starts, splits, used = [], [], set()
    cutoff = F.registered_dates(None)['cutoff']
    for j in range(1, len(segs)):
        a, b = segs[j - 1], segs[j]
        if a['settings_sha256'] == b['settings_sha256']:
            continue
        if a['epoch_key'] == b['epoch_key']:
            splits.append(b['segment'])
            continue
        # v13/v14 (Codex v12, v13): the registered segment is a SCIENTIFIC position: k in attempt 1; after an authorized
        # rescue, the last pw.x position + 1, advancing only with pw.x segments (guard-only starts do not move it)
        i, ref, trig, rescue, changed = F.registered_transition(cell, route, b['position'], 1,
                                                                F.settings_block(parsed[j - 1][0]),
                                                                F.settings_block(parsed[j][0]), used)
        if trig == 'failed_scf_before_cutoff':
            end = F.parse_utc(a['end_utc'])
            if a['d24_status'] != 'FAILED' or a['d24_category'] != 'scf' or end is None or end > cutoff:
                raise F.DeriveError('conditional_rescue_without_a_preceding_scf_failure')
            if not a['bestvalid_geometry_sha256'] or b['start_geometry_sha256'] != a['bestvalid_geometry_sha256']:
                raise F.DeriveError('conditional_rescue_not_from_the_best_valid_geometry')
            if b['continuation'] != 'section3_reset':
                raise F.DeriveError('conditional_rescue_without_its_reset_record')
        used.add(i)
        b['rescue_start'] = rescue
        starts.append({'segment': b['segment'], 'amendment': ref, 'changed_keys': changed, 'rescue': rescue})
    return starts, splits


def _no_revival(segs, guard=()):
    """v9/v12 (Codex v8 item 3; v11 case 2): after a rescue start, an SCF failure is terminal for the route (A35/A36 'one
    attempt'). Every administrative boundary - a section-3 reset or rescue on a pw.x segment OR on a guard-only first
    execution of a new attempt - is checked in execution order: none may follow such a failure, and a rescue record's
    restated terminal-failure status must equal the derived one. No ordinary pw.x continuation may follow a D-24
    FAILED [scf] after the rescue start either (the registered prohibition on resuming)."""
    first = next((i for i, s in enumerate(segs) if s['rescue_start']), None)

    def failed(x, strict=False):
        d24 = x['d24_status'] == 'FAILED' and x['d24_category'] == 'scf'
        return d24 if strict else (x['scf_failures'] or d24)

    def term(j, strict=False):
        return first is not None and first < j and any(failed(x, strict) for x in segs[first:j])

    def boundary(rec_kind, rescue_record, j):
        if rec_kind not in ('section3_reset', 'section3_rescue', 'd24_transition_reset'):
            return False
        t = term(j)
        if t:
            raise F.DeriveError('transition_after_a_terminal_rescue_failure')
        if rescue_record is not None and rescue_record['terminal_failure'] != t:
            raise F.DeriveError('rescue_terminal_failure_status_differs')
        return True
    for j in range(len(segs) + 1):
        for g in guard:
            if g.get('_after_pw') == j:
                boundary(g.get('continuation'), g.get('rescue_record'), j)
        if j < len(segs):
            s = segs[j]
            if not boundary(s['continuation'], s['rescue_record'], j) and term(j, strict=True):
                raise F.DeriveError('continuation_after_a_terminal_rescue_failure')
    for g in guard:
        g.pop('_after_pw', None)


def derive_relaxation_lineage(params, paths):
    cell, route = params.get('cell'), params.get('route')
    if route not in F.ROUTES:
        raise F.DeriveError('route_unknown')
    segs, parsed, guard, run, _ = _segments(paths, _tz(paths), cell)
    if params.get('run') is not None and params['run'] != run:
        raise F.DeriveError('lineage_run_differs_from_the_archive_identity')
    if any(s['bfgs_converged'] for s in segs[:-1]):
        raise F.DeriveError('segment_after_bfgs_convergence')
    starts, splits = _transitions(cell, route, segs, parsed)
    _no_revival(segs, guard)
    last_inp, last_q = parsed[-1]
    conv = bool(last_q['bfgs_converged'] and last_q['final_geometry_sha256'])
    last_eval = None
    for (inp, q), s in zip(reversed(parsed), reversed(segs)):
        if q['evaluations']:
            e = q['evaluations'][-1]
            last_eval = {'segment': s['segment'], 'index': e['index'], 'geometry_sha256': e['geometry_sha256']}
            break
    if conv and (last_eval is None or last_eval['segment'] != segs[-1]['segment'] or
                 last_eval['geometry_sha256'] != last_q['final_geometry_sha256']):
        raise F.DeriveError('final_geometry_is_not_the_last_scf_geometry')
    geoms = {e['geometry_sha256'] for _, q in parsed for e in q['evaluations']}
    required = F.required_gate_boundaries(cell, route, segs)
    gates = [_gate(b, segs, parsed) for b in required]
    diagnostics = [_gate(b, segs, parsed) for b in F.diagnostic_boundaries(cell, route, segs)]
    ep = F.epochs(segs)
    last_names = {s['segment'] for s in ep[-1]}
    residual = None
    if conv:
        ev = last_q['evaluations']
        residual = {'max_force_component_Ry_bohr': F.max_force_component(ev[-1]['forces']),
                    'energy_change_Ry': (ev[-1]['F_Ry'] - ev[-2]['F_Ry']) if len(ev) >= 2 else None}
    return {'cell': cell, 'route': route, 'run': run, 'nat': last_inp['nat'], 'segments': segs,
            'guard_only_attempts': guard, 'epoch_starts': starts, 'label_splits': splits,
            'epochs': [[s['segment'] for s in e] for e in ep],
            'smearing_history': [{'segment': s['segment'], 'smearing': s['smearing'], 'degauss_Ry': s['degauss_Ry']}
                                 for s in segs],
            'relaxation_settings_sha256': ep[-1][-1]['settings_sha256'],
            'start_geometry_sha256': segs[0]['start_geometry_sha256'],
            'final_geometry_sha256': last_q['final_geometry_sha256'] if conv else None,
            'bfgs_converged': conv, 'bfgs_converged_utc': segs[-1]['end_utc'] if conv else None,
            'timing_source': segs[-1]['timing_source'] if conv else None,
            'registered_ionic_thresholds': all(
                s['ionic_thresholds']['forc_conv_thr'] == F.REGISTERED_FORC_CONV_THR and
                s['ionic_thresholds']['etot_conv_thr'] == F.REGISTERED_ETOT_CONV_THR for s in ep[-1]),
            'final_residual': residual,
            'terminal_scf_failures': [s['segment'] for s in segs if s['segment'] in last_names and s['scf_failures']],
            'historical_scf_failures': [s['segment'] for s in segs
                                        if s['segment'] not in last_names and s['scf_failures']],
            'n_ionic_steps': max(0, len(geoms) - 1), 'required_gates': required, 'gates': gates,
            'diagnostic_comparisons': diagnostics,
            'last_evaluation': last_eval, 'has_parent': bool(paths.get('parent'))}


def _last_relaxation_evaluation(lineage_path):
    lin = load_record(lineage_path, 'relaxation_lineage')
    lp = resolve(lin['sources'], os.path.dirname(os.path.abspath(lineage_path)))
    seg = lp['segments'][-1]
    _, k = F.segment_index(seg.get('segment'))       # the segment's own index (= its position in a verified lineage)
    if k is None:
        raise F.DeriveError('segments_not_contiguous_from_0')
    b = _bind_segment(seg, k, _tz(lp))
    if b['kind'] == 'guard_only':
        raise F.DeriveError('lineage_last_segment_has_no_scf')
    inp = F.read_pw_input(seg['relax_in'])
    q = F.read_qe_output(seg['relax_out'], inp)
    if not q['evaluations']:
        raise F.DeriveError('lineage_last_segment_has_no_scf')
    return lin, seg, q['evaluations'][-1]


def derive_qualification_scf(params, paths):
    lin, seg, last = _last_relaxation_evaluation(paths['lineage'])
    if params.get('cell') != lin['derived'].get('cell'):
        raise F.DeriveError('qualification_cell_differs_from_lineage')
    if not paths.get('export_manifest'):
        raise F.DeriveError('qualification_input_provenance_missing')
    # v7 (Codex v6 review item 3, same hole): the returned archive is identified with this cluster, and its scf.out
    # was written inside that cluster's execution window
    man = _identity_manifest(paths['export_manifest'], 'qualification')
    cl = params.get('cluster')
    if cl is None or not paths.get('joblog'):
        raise F.DeriveError('qualification_job_identity_missing')
    arcs = [a for a in paths.get('archives') or []
            if F._listed(man, a) and (man['identity'].get(F._basename(a)) or (None,))[0] == int(cl)]
    if len(arcs) != 1:
        raise F.DeriveError('qualification_archive_not_identified_with_this_job')
    arc = arcs[0]
    if F.archive_member_sha256(arc, SCF_INPUT) != F.sha256_file(paths['scf_in']):
        raise F.DeriveError('scf_in_not_bound_to_the_historical_export')
    if F.archive_member_sha256(arc, SCF_OUTPUT) != F.sha256_file(paths['scf_out']):
        raise F.DeriveError('scf_out_not_bound_to_the_historical_export')
    F.check_members_in_window(arc, [SCF_OUTPUT], F.job_window(paths['joblog'], cl, _tz(paths)), 'qualification')
    qin = F.read_pw_input(paths['scf_in'])
    qq = F.read_qe_output(paths['scf_out'], qin)
    geom = F.input_geometry_hash(qin)
    conv = qq['scf_ok'] >= 1 and qq['scf_fail'] == 0 and len(qq['evaluations']) == 1
    out = {'cell': params['cell'], 'run': man['run'], 'geometry_sha256': geom, 'settings_sha256': F.settings_sha256(qin),
           'fresh_start': F.start_mode(qin) == 'fresh', 'scf_converged': conv,
           'compared_with': {'segment': seg['segment'], 'index': last['index'],
                             'geometry_sha256': last['geometry_sha256']},
           'delta_F_Ry': None, 'max_abs_dF_Ry_bohr': None, 'n_components': None, 'comparison_error': None}
    if not conv:
        out['comparison_error'] = 'qualification_scf_not_converged'
    elif last['geometry_sha256'] != geom:
        out['comparison_error'] = 'relaxation_last_scf_not_at_this_geometry'
    else:
        dF, dmax, n = F.compare_evaluations(last, qq['evaluations'][0])
        out.update({'delta_F_Ry': dF, 'max_abs_dF_Ry_bohr': dmax, 'n_components': n})
    out['completed_utc'] = F.fmt_utc(F.terminated_utc(paths['joblog'], params.get('cluster'), _tz(paths)))
    out['timing_source'] = 'htcondor_job_log'
    return out


def _certify_output(path):
    co = load_json(path)
    rf, g, pp = co.get('run_files'), co.get('geometry_sha256'), co.get('pseudopotentials')
    if not isinstance(rf, dict) or not isinstance(g, str) or not isinstance(pp, dict):
        raise F.DeriveError('certify_output_malformed')
    return bound(rf), g, pp


def _bound_run_input(paths, pre, input_key, what):
    """v5 (Codex 20:44Z items 2 and 4).
      * The certified run consumed its D-24 lineage file (rc7 binds lineage_<job>.dat as a run file): the supplied
        lineage file must be that certified file (sha256 in the certify run_files).
      * The lineage file records the sha256 of scf.in AS pw.x READ IT ('sha256 <h> scf.in as-run ...'): the selected
        input must have exactly that sha256. Any other exported .in (e.g. an unused fresh sibling) is refused.
      * Historical provenance: every certified run file and the input itself are the files of the run's D-24 export
        (listed in exp/MANIFEST, or members recomputed from a listed archive such as final_small.tar.gz).
      Missing pieces are a provenance gap: the record cannot be derived (A14 gaps stay unresolved)."""
    keys = {k: paths.get(pre + k) for k in ('lineage_file', 'certify_output', 'export_manifest')}
    if paths.get(input_key) is None or None in keys.values():
        raise F.DeriveError(f'{what}_input_provenance_missing')
    rf, g, pp = _certify_output(keys['certify_output'])
    lin_name = F._basename(keys['lineage_file'])
    if rf.get(lin_name) != F.sha256_file(keys['lineage_file']):
        raise F.DeriveError(f'{what}_lineage_is_not_a_certified_run_file')
    asrun, prerun_same = F.asrun_scf_input(keys['lineage_file'])
    if F.sha256_file(paths[input_key]) != asrun:
        raise F.DeriveError(f'{what}_input_is_not_the_asrun_scf_input')
    man = F.read_export_manifest(keys['export_manifest'])
    # v7 (Codex ruling): the in-job exp/MANIFEST or, when it never reached EOS, export_manifest_final.dat
    if man['format'] not in ('d24', 'd24_final') or man['cluster'] is None or man['written_utc'] is None:
        raise F.DeriveError(f'{what}_export_manifest_is_not_the_in_job_d24_manifest')
    archives = paths.get(pre + 'archives')
    binding = F.bind_run_files(man, archives, rf)
    F.bind_exported_file(man, archives, paths[input_key], SCF_INPUT, f'{what}_input')
    inp = F.read_pw_input(paths[input_key])
    if F.input_geometry_hash(inp) != g:
        raise F.DeriveError(f'{what}_input_geometry_differs_from_certify')
    prov = {'asrun_scf_input_sha256': asrun, 'asrun_identical_to_prerun_apart_from_max_seconds': prerun_same,
            'export_format': man['format'], 'export_run': man['run'], 'export_cluster': man['cluster'],
            'export_written_utc': F.fmt_utc(man['written_utc']), 'export_eos_dest': man.get('eos_dest'),
            'run_file_binding': binding}
    return inp, rf, g, pp, prov


def derive_final_run(params, paths):
    inp, rf, g, pp, prov = _bound_run_input(paths, '', 'final_in', 'final')
    s = F.settings_block(inp)
    return {'cell': params.get('cell'), 'run_files': rf, 'geometry_sha256': g, 'settings': s,
            'settings_sha256': F.canonical_sha256(s), 'template_key': F.final_template_key(s), 'upf_sha256': pp,
            'smearing': F.family(inp['fields'].get('system.smearing')),
            'degauss_Ry': inp['fields'].get('system.degauss'), 'start_mode': F.start_mode(inp), 'provenance': prov}


def derive_c3_companion_run(params, paths):
    """v5 (Codex item 3): the start mode of BOTH endpoints is derived from their as-run inputs."""
    r, rrf, rg, _, rprov = _bound_run_input(paths, 'ref_', 'ref_in', 'reference')
    c, crf, cg, _, cprov = _bound_run_input(paths, 'comp_', 'comp_in', 'companion')
    rs, cs = F.settings_block(r), F.settings_block(c)
    changed = sorted(k for k in set(rs) | set(cs) if rs.get(k) != cs.get(k))
    if rg != cg:
        changed.append('geometry')
    return {'cell': params.get('cell'), 'degauss_Ry': c['fields'].get('system.degauss'),
            'smearing': F.family(c['fields'].get('system.smearing')), 'geometry_sha256': cg, 'run_files': crf,
            'reference_run_files': rrf, 'reference_geometry_sha256': rg,
            'reference_degauss_Ry': r['fields'].get('system.degauss'),
            'start_mode': F.start_mode(c), 'reference_start_mode': F.start_mode(r),
            'diff_gate': {'changed_physical_keys': changed,
                          'status': 'PASS' if changed == ['system.degauss'] else 'FAIL'},
            'reference_provenance': rprov, 'companion_provenance': cprov}


def derive_c4_polish(params, paths):
    pc = load_json(paths['parent_certificate'])
    if pc.get('schema') != F.CERT_SCHEMA:
        raise F.DeriveError('parent_is_not_a_certificate')
    pl = load_record(paths['polish_lineage'], 'relaxation_lineage')['derived']
    load_record(paths['qualification'], 'qualification_scf')
    zero = pl.get('final_geometry_sha256') is not None and pl['final_geometry_sha256'] == pl['start_geometry_sha256']
    reuse = None
    if zero:
        if not paths.get('reused_final'):
            raise F.DeriveError('zero_step_polish_without_reused_final')
        fr = load_record(paths['reused_final'], 'final_run')['derived']
        reuse = {'run_files': fr['run_files'], 'final_settings_sha256': fr['settings_sha256'],
                 'upf_sha256': fr['upf_sha256'], 'degauss_Ry': fr['degauss_Ry'], 'smearing': fr['smearing']}
    elif paths.get('reused_final'):
        raise F.DeriveError('reused_final_without_zero_step')
    return {'cell': params.get('cell'), 'parent_cell': pc.get('cell'),
            'parent_geometry_sha256': pc.get('geometry_sha256'),
            'polish_start_geometry_sha256': pl.get('start_geometry_sha256'),
            'polish_final_geometry_sha256': pl.get('final_geometry_sha256'), 'zero_step': zero,
            'zero_step_reuse': reuse}


def _extension(paths):
    return load_record(paths['extension'], 'cern_extension')['derived'] if paths.get('extension') else None


def derive_a15_provisional(params, paths):
    """v4 item 5: the A31(f) selection is DERIVED from bound relaxation_lineage status records (primary required,
    backup optional) at the extension-aware cutoff: s1 if converged by the cutoff, else the backup if converged,
    else the role is unresolved. Nothing is copied from parameters."""
    cutoff = F.registered_dates(_extension(paths))['cutoff']
    a = load_json(paths['audit_report'])
    ins = (a.get('provenance') or {}).get('inputs') or []
    pairs = sorted({(e.get('cell'), round(float(e.get('degauss_Ry')), 9)) for e in ins
                    if isinstance(e, dict) and F.finite(e.get('degauss_Ry'))}, key=str)
    roles_src = paths.get('roles') or {}
    roles, selection = {}, {}
    for role, (prim_cell, back_cell) in A15_ROLE_CELLS.items():
        src = roles_src.get(role) or {}
        if not src.get('primary'):
            raise F.DeriveError('role_primary_status_record_missing')
        stat = {}
        for which, want in (('primary', prim_cell), ('backup', back_cell)):
            if not src.get(which):
                stat[which] = None
                continue
            if want is None:
                raise F.DeriveError('role_has_no_registered_backup')
            d = load_record(src[which], 'relaxation_lineage')['derived']
            if d.get('cell') != want:
                raise F.DeriveError('role_status_record_for_another_cell')
            ok, why = F.converged_at_cutoff(d, cutoff)
            stat[which] = {'cell': want, 'converged_at_cutoff': ok, 'reasons': why}
        if stat['primary']['converged_at_cutoff']:
            roles[role] = prim_cell
        elif stat['backup'] is not None and stat['backup']['converged_at_cutoff']:
            roles[role] = back_cell
        else:
            roles[role] = None
        selection[role] = {'primary': stat['primary'], 'backup': stat['backup'],
                           'selected': roles[role], 'basis': 'A31(f) relaxation status at the cutoff'}
    return {'roles': roles, 'selection': selection, 'cutoff_utc': F.fmt_utc(cutoff),
            'audit_kind': a.get('kind'), 'audit_code_sha256': (a.get('provenance') or {}).get('code_sha256'),
            'audit_sealed': F.verify_seal(a), 'audit_inputs': [list(p) for p in pairs], 'audit_n_inputs': len(ins),
            'widths_Ry': sorted({p[1] for p in pairs}),
            'provisional_width_candidate_Ry': a.get('provisional_width_candidate_Ry'), 'status': A15_STATUS}


class _Ambiguous(F.DeriveError):
    """An attempt's evidence names a run that the frozen plan gives to another slot (ambiguous ownership)."""

    def __init__(self, code, other):
        super().__init__(code)
        self.other = other


def _plan(path):
    """v7 (Codex v6 review item 1): the frozen F10 plan names the export root ($EXPORT_EOS, steps_final.sh.D24:28) and
    the run names (IWOJob '<name>_final' without the suffix, :58-62) of every slot. A run owned by two slots is an
    ambiguous plan and blocks the whole inventory."""
    plan = load_json(path)
    root, slots = plan.get('export_root'), plan.get('slots')
    if plan.get('schema') != PLAN_SCHEMA or not isinstance(slots, list) or not isinstance(root, str) or \
            not root.startswith('/') or root.endswith('/') or '..' in root.split('/'):
        raise F.DeriveError('plan_malformed')
    pslots, owner = {}, {}
    for s in slots:
        if not isinstance(s, dict) or s.get('slot') in pslots or not isinstance(s.get('runs'), list) or not s['runs']:
            raise F.DeriveError('plan_malformed')
        for r in s['runs']:
            if not isinstance(r, str) or not RUN_NAME.match(r):
                raise F.DeriveError('plan_malformed')
            if r in owner:
                raise F.DeriveError('plan_run_owned_by_two_slots')
            owner[r] = s.get('slot')
        pslots[s.get('slot')] = s
    return root, pslots, owner


def _owned(run, ps, owner, code):
    if run in ps['runs']:
        return
    if run in owner:
        raise _Ambiguous('attempt_evidence_names_a_run_of_another_slot', owner[run])
    raise F.DeriveError(code)


def export_destination(root, run, cluster):
    """$EXPORT_EOS/<name>/final_<ClusterId> (steps_final.sh.D24:65 export_dest)."""
    return f'{root}/{run}/final_{int(cluster)}'


def _actual_run(a, joblog, tz):
    """v8 (Codex v7 item 1): the run the cluster actually was, from the scheduler's record of that job (condor_history
    -l: ClusterId, IWOJob '<name>_final', QDate), whose submission time must match the slot user log's 000 event."""
    if not a.get('job_history'):
        raise F.DeriveError('attempt_job_history_missing')
    h = F.read_job_history(a['job_history'])
    cl = int(a['cluster'])
    if h['cluster'] != cl:
        raise F.DeriveError('attempt_job_history_is_for_another_cluster')
    subs = [t for c, t in F.job_events(joblog, cl, tz) if c == '000']
    if not subs or abs((h['qdate'] - min(subs)).total_seconds()) > F.ARCHIVE_CLOCK_TOLERANCE_S:
        raise F.DeriveError('attempt_job_history_differs_from_the_user_log')
    return h['run']


def _attempt_inventory(a, joblog, tz, ps, root, owner, actual):
    """v6 (Codex 2026-10-13 blocking 1): the attempt's bound artifact inventory (f9_common.read_attempt_inventory),
    verified against the attempt: same cluster, the job's own export directory final_<cluster>, captured at or after
    the job's terminal event. None when no inventory is bound.
    v7 (Codex v6 review item 1): the listed run is one of the slot's frozen runs and the location is EXACTLY
    <export_root>/<run>/final_<cluster>; a basename match is not enough."""
    if not a.get('artifact_inventory'):
        return None
    inv = F.read_attempt_inventory(a['artifact_inventory'])
    cl = int(a['cluster'])
    if inv['cluster'] != cl:
        raise F.DeriveError('attempt_inventory_is_for_another_cluster')
    if inv['location_name'] != f'final_{cl}':
        raise F.DeriveError('attempt_inventory_location_is_not_this_jobs_export_directory')
    _owned(inv['run'], ps, owner, 'attempt_inventory_run_is_not_this_slots_run')
    if inv['run'] != actual:                                                  # v8 (Codex v7 item 1)
        raise F.DeriveError('attempt_inventory_run_is_not_the_jobs_actual_run')
    if inv['location'].rstrip('/') != export_destination(root, inv['run'], cl):
        raise F.DeriveError('attempt_inventory_destination_is_not_this_runs_export_directory')
    end = F.terminal_utc(joblog, cl, tz)
    if end is None or inv['captured_utc'] < end:
        raise F.DeriveError('attempt_inventory_captured_before_the_job_ended')
    inv['summary'] = {'sha256': F.sha256_file(a['artifact_inventory']), 'run': inv['run'],
                      'location_state': inv['state'], 'n_files': len(inv['files']),
                      'n_exported_files': len(inv['exported']), 'captured_utc': F.fmt_utc(inv['captured_utc'])}
    return inv


def _resolve_attempt(a, ss, ps, root, owner, reports, tz):
    """One attempt -> (record, matched report or None); DeriveError leaves the attempt (and its slot) UNRESOLVED."""
    cl = int(a['cluster'])
    actual = _actual_run(a, ss['joblog'], tz)                                  # v8 (Codex v7 item 1)
    _owned(actual, ps, owner, 'attempt_actual_run_is_not_this_slots_run')
    dispo = F.disposition(ss['joblog'], cl, tz)
    if not a.get('certify_output'):
        # v5 (Codex 20:44Z item 1): a completed job without its output, or an unfinished one, is an unexplained gap.
        if dispo is None:
            raise F.DeriveError('attempt_not_finished_no_terminal_event')
        if dispo == 'normal_exit_0':
            raise F.DeriveError('attempt_completed_normally_but_output_missing')
        # v6 (blocking 1): a failure event alone does not establish that no usable export exists.
        inv = _attempt_inventory(a, ss['joblog'], tz, ps, root, owner, actual)
        if inv is None:
            raise F.DeriveError('attempt_failed_without_artifact_inventory')
        if inv['exported']:
            raise F.DeriveError('attempt_inventory_lists_an_export_without_its_c3_report')
        return {'cluster': cl, 'result': 'no_output', 'run': actual, 'disposition': dispo,
                'artifact_inventory': inv['summary']}, None
    # any usable comparison counts whatever the exit status (Codex ruling)
    if not a.get('export_manifest'):
        raise F.DeriveError('attempt_export_provenance_missing')
    rf, g, _ = _certify_output(a['certify_output'])
    aman = F.read_export_manifest(a['export_manifest'])
    if aman['format'] not in ('d24', 'd24_final') or aman['cluster'] != cl or aman['written_utc'] is None:
        raise F.DeriveError('attempt_export_is_not_this_jobs_in_job_manifest')
    _owned(aman['run'], ps, owner, 'attempt_export_run_is_not_this_slots_run')         # v7 item 1
    if aman['run'] != actual:                                                           # v8 item 1
        raise F.DeriveError('attempt_export_run_is_not_the_jobs_actual_run')
    if aman.get('eos_dest') != export_destination(root, aman['run'], cl):
        raise F.DeriveError('attempt_export_destination_is_not_this_runs_export_directory')
    inv = _attempt_inventory(a, ss['joblog'], tz, ps, root, owner, actual)   # optional here; must agree if bound
    if inv is not None and (not inv['exported'] or inv['run'] != aman['run']):
        raise F.DeriveError('attempt_inventory_contradicts_its_export')
    end = F.terminal_utc(ss['joblog'], cl, tz)                            # v6: 005 or 009
    if end is not None and aman['written_utc'] > end:
        raise F.DeriveError('attempt_export_manifest_written_after_the_job_ended')
    F.bind_run_files(aman, a.get('archives'), rf)
    hits = [r for r in reports if bound(r['oth'].get('run_files')) == rf and
            r['ref'].get('cell') == ps.get('cell') and r['ref'].get('geometry_sha256') == ps.get('geometry_sha256')
            and r['oth'].get('geometry_sha256') == ps.get('geometry_sha256') and
            F.finite(r['oth'].get('degauss_Ry')) and abs(r['oth']['degauss_Ry'] - ps.get('width_Ry')) < 1e-9]
    if len(hits) != 1:
        raise F.DeriveError('attempt_without_exactly_one_result')
    return {'cluster': cl, 'result': 'report', 'report_sha256': hits[0]['sha256'], 'run': aman['run'],
            'run_files_sha256': F.canonical_sha256(rf), 'disposition': dispo,
            'artifact_inventory': inv['summary'] if inv is not None else None}, hits[0]


def derive_readout_manifest(params, paths):
    """v4 item 4: the complete C3 inventory: the frozen F10 plan lists every comparison slot; each slot has ONE
    HTCondor user log, and every cluster submitted to it must be accounted for; every bound report must belong to an
    attempt. v6: a failed attempt is 'no_output' only with a verified artifact inventory showing no export.
    v7 (Codex v6 review item 1 and the blocking-scope ruling, prospective):
      * every attempt is retained explicitly with result 'report', 'no_output' or 'unresolved' (+ reason);
      * an ordinary unresolved attempt makes only its own slot (frozen cell / geometry / width) UNRESOLVED;
      * ambiguous ownership (evidence naming another slot's run) makes both slots UNRESOLVED;
      * a corrupted global inventory (plan, slot set, malformed or unowned report) is not derivable at all."""
    root, pslots, owner = _plan(paths['plan'])
    tz = _tz(paths)
    src_slots = {s.get('slot'): s for s in paths.get('slots') or []}
    if set(src_slots) != set(pslots):
        raise F.DeriveError('slots_differ_from_frozen_plan')
    reports = []
    for p in paths.get('c3_reports') or []:
        r = load_json(p)
        if r.get('kind') != 'C3':
            raise F.DeriveError('inventory_entry_is_not_a_c3_report')
        ins = (r.get('provenance') or {}).get('inputs') or []
        if len(ins) < 2 or not all(isinstance(e, dict) for e in ins[:2]):
            raise F.DeriveError('c3_report_without_input_roles')
        reports.append({'path': p, 'sha256': F.sha256_file(p), 'ref': ins[0], 'oth': ins[1], 'used': False})
    reasons = {sid: set() for sid in pslots}
    recs_by = {}
    for sid in sorted(pslots):
        ps, ss = pslots[sid], src_slots[sid]
        atts, recs = ss.get('attempts') or [], []
        try:
            if not ss.get('joblog'):
                raise F.DeriveError('slot_without_user_log')
            submitted = F.submitted_clusters(ss['joblog'], tz)
        except F.DeriveError as e:
            reasons[sid].add(str(e))
            recs_by[sid] = [{'cluster': int(a['cluster']), 'result': 'unresolved', 'reason': str(e)} for a in atts]
            continue
        listed = [int(a['cluster']) for a in atts]
        if sorted(listed) != submitted:
            reasons[sid].add('slot_attempts_differ_from_user_log')
            recs += [{'cluster': c, 'result': 'unresolved', 'reason': 'attempt_missing_from_the_inventory'}
                     for c in sorted(set(submitted) - set(listed))]
            recs += [{'cluster': c, 'result': 'unresolved', 'reason': 'attempt_not_in_the_slot_user_log'}
                     for c in sorted(set(listed) - set(submitted))]
        for a in sorted(atts, key=lambda x: int(x['cluster'])):
            if int(a['cluster']) not in submitted:
                continue
            try:
                rec, hit = _resolve_attempt(a, ss, ps, root, owner, reports, tz)
            except _Ambiguous as e:
                reasons[sid].add(str(e))
                reasons[e.other].add(str(e))
                rec, hit = {'cluster': int(a['cluster']), 'result': 'unresolved', 'reason': str(e)}, None
            except F.DeriveError as e:
                reasons[sid].add(str(e))
                rec, hit = {'cluster': int(a['cluster']), 'result': 'unresolved', 'reason': str(e)}, None
            if hit is not None:
                hit['used'] = True
            recs.append(rec)
        recs_by[sid] = sorted(recs, key=lambda x: x['cluster'])
    for r in reports:
        if r['used']:
            continue
        own = [sid for sid, ps in pslots.items() if r['ref'].get('cell') == ps.get('cell') and
               r['ref'].get('geometry_sha256') == ps.get('geometry_sha256') and
               F.finite(r['oth'].get('degauss_Ry')) and abs(r['oth']['degauss_Ry'] - ps.get('width_Ry')) < 1e-9]
        if not own:
            raise F.DeriveError('c3_report_not_in_the_attempt_inventory')
        for sid in own:
            reasons[sid].add('c3_report_not_assigned_to_an_attempt')
    out = [{'slot': sid, 'cell': pslots[sid].get('cell'), 'geometry_sha256': pslots[sid].get('geometry_sha256'),
            'width_Ry': pslots[sid].get('width_Ry'), 'runs': list(pslots[sid]['runs']),
            'status': 'unresolved' if reasons[sid] else 'resolved', 'reasons': sorted(reasons[sid]),
            'attempts': recs_by[sid]} for sid in sorted(pslots)]
    return {'plan_sha256': F.sha256_file(paths['plan']), 'export_root': root, 'slots': out,
            'n_c3_reports': len(reports)}


def derive_cutoff_selection(params, paths):
    cutoff = F.registered_dates(_extension(paths))['cutoff']
    tz = _tz(paths)
    segs, parsed, _, _, srcs = _segments(paths, tz, params.get('cell'))   # v8: sources aligned with the pw.x segments
    # (guard-only entries are not used by the selection; their internal ordering key stays local to _segments' caller)
    last = F.epochs(segs)[-1]
    names = [s['segment'] for s in segs]
    C, over = [], []

    def row(seg, e):
        return {'segment': seg, 'index': e['index'], 'F_Ry': e['F_Ry'],
                'max_component_Ry_bohr': F.max_force_component(e['forces']), 'geometry_sha256': e['geometry_sha256']}
    for s in last:
        i = names.index(s['segment'])
        inp, q = parsed[i]
        src = srcs[i]
        end = F.parse_utc(s['end_utc']) if s['end_utc'] else None
        if end is not None and end <= cutoff and s['timing_source'] == 'htcondor_job_log':
            C += [row(s['segment'], e) for e in q['evaluations']]
            continue
        n_ok = 0
        if src.get('snapshot_out') and src.get('snapshot_meta') and src.get('export_manifest'):
            meta = load_json(src['snapshot_meta'])
            if meta.get('snapshot_sha256') != F.sha256_file(src['snapshot_out']) or \
                    meta.get('relax_in_sha256') != F.sha256_file(src['relax_in']):
                raise F.DeriveError('snapshot_meta_does_not_pin_these_files')
            t = F.parse_utc(meta.get('transfer_completed_utc'))
            if t is not None and t <= cutoff:
                snap = F.read_qe_output(src['snapshot_out'], inp)['evaluations']
                C += [row(s['segment'], e) for e in snap]
                n_ok = len(snap)
        elif end is not None and end <= cutoff:          # a snapshot-only segment completed before the cutoff
            C += [row(s['segment'], e) for e in q['evaluations']]
            continue
        over += [row(s['segment'], e) for e in q['evaluations'][n_ok:]]
    order = {n: k for k, n in enumerate(names)}
    C.sort(key=lambda r: (order[r['segment']], r['index']))
    seen = {}
    for r in C:
        seen[r['geometry_sha256']] = r
    merged = [r for r in C if seen[r['geometry_sha256']] is r]
    g_star = None
    if C:                       # v11 (Codex v10 case 3): minimum and tie rules over ALL eligible evaluations, then dedup
        fmin = min(r['F_Ry'] for r in C)
        t1 = [r for r in C if r['F_Ry'] - fmin <= F.GATE_DF_RY]
        mmin = min(r['max_component_Ry_bohr'] for r in t1)
        t2 = [r for r in t1 if r['max_component_Ry_bohr'] - mmin <= 1e-6]
        g_star = max(t2, key=lambda r: (order[r['segment']], r['index']))
    return {'cell': params.get('cell'), 'cutoff_utc': F.fmt_utc(cutoff), 'epoch': [s['segment'] for s in last],
            'C': merged, 'C_all_eligible': C, 'overhang': over, 'g_star': g_star,
            'g_star_geometry_sha256': g_star['geometry_sha256'] if g_star else None,
            'L': merged[-1] if merged else None, 'g0': merged[0] if merged else None}


def derive_cern_extension(params, paths):
    end, logged = params.get('confirmed_end_date'), params.get('logged_utc')
    if F.parse_utc(logged) is None:
        raise F.DeriveError('logged_utc_malformed')
    try:
        d_end = dt.date.fromisoformat(end)
    except (TypeError, ValueError):
        raise F.DeriveError('confirmed_end_date_malformed')
    conf = F.sha256_file(paths['confirmation'])
    with open(paths['work_chat_entry'], encoding='utf-8', errors='replace') as f:
        text = f.read()
    if conf not in text:
        raise F.DeriveError('work_chat_entry_lacks_the_confirmation_sha256')
    head = '## ' + logged[:16] + 'Z'
    if not any(line.startswith(head) for line in text.splitlines()):
        raise F.DeriveError('work_chat_entry_heading_differs_from_logged_utc')
    return {'confirmed_end_date': end, 'logged_utc': logged, 'confirmation_sha256': conf,
            'delta_days': max(0, (d_end - dt.date.fromisoformat(F.ACCESS_END_DATE)).days)}


DERIVE = {t: globals()['derive_' + t] for t in TYPES}


def derive(rtype, params, paths):
    if rtype not in DERIVE:
        raise F.DeriveError('record_type_unknown')
    return DERIVE[rtype](params or {}, paths)


def build_record(rtype, params, sources, out_path):
    """Write one record. sources: the same structure with absolute or cwd-relative paths."""
    out_path = os.path.abspath(out_path)
    base = os.path.dirname(out_path)
    refs = to_refs(sources, base)
    derived = derive(rtype, params, resolve(refs, base))
    rec = {'schema': F.RECORD_SCHEMA, 'type': rtype, 'params': params, 'sources': refs, 'derived': derived,
           'writer': VERSION, 'writer_sha256': writer_fingerprint()}
    json.dumps(rec, allow_nan=False)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description='Blind F9 evidence-record writers (D-42 draft v4).')
    ap.add_argument('type', choices=TYPES)
    ap.add_argument('--spec', required=True, help='JSON {"params": {...}, "sources": {...}} (paths relative to it)')
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    spec = load_json(a.spec)
    sdir = os.path.dirname(os.path.abspath(a.spec))

    def absify(v, k=None):
        if isinstance(v, dict):
            return {kk: absify(vv, kk) for kk, vv in v.items()}
        if isinstance(v, list):
            return [absify(x, k) for x in v]
        if isinstance(v, str) and (k in FILE_KEYS or k in FILE_LIST_KEYS):
            return v if os.path.isabs(v) else os.path.join(sdir, v)
        return v
    try:
        build_record(a.type, spec.get('params') or {}, absify(spec.get('sources') or {}), a.out)
    except F.SightAbort as e:
        print(f'SIGHT_ABORT: {e}')
        return 2
    except F.DeriveError as e:
        print(f'NOT WRITTEN: {e}')
        return 1
    print(f'wrote {os.path.basename(a.out)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
