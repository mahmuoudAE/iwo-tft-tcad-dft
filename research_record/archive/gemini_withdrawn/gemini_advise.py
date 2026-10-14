#!/usr/bin/env python3
"""Gemini as blind theoretical critic for the IWO project: the Gemini counterpart of tools/codex_advise.sh.

usage (WSL):
  python3 tools/gemini_advise.py --test                      list the models the key can use + one-word ping
                                                             (no research data are sent)
  python3 tools/gemini_advise.py --set-model models/<name>   choose the model used for reviews
  python3 tools/gemini_advise.py "<topic>" <brief.md> [file ...]
                                                             send a brief plus attached text files
  python3 tools/gemini_advise.py --bundle "<topic>" <brief.md> [file ...]
                                                             manual route (Google AI Pro plan, no API): write one
                                                             file to upload or paste into the Gemini app
  python3 tools/gemini_advise.py --ingest <reply.md>         log a reply copied back from the Gemini app

Key: ~/.config/iwo/gemini_key (written by tools/set_gemini_key.sh, which the user runs) or $GEMINI_API_KEY.
     The key is never printed or logged, and is scrubbed from error messages.
Data: research files are sent only if ~/.config/iwo/gemini_billing_confirmed exists (paid tier: Google does not
     use prompts or responses to improve its products; the free tier may).
Memory: the API is stateless, so the conversation is kept in codex/work_chat/gemini/history.json and resent each
     call. Attached file contents are not stored in the history; only name, size and sha256 are.
Blindness: files from the Codex work chat or Codex reviews are refused, so Gemini never sees Codex's or Claude's
     verdicts on the question.
Log: codex/work_chat/GEMINI_REVIEW_LOG.md (topic, model, attachments with sha256, reply, sources,
     "Claude decision _pending_"), the same pattern as CODEX_WORK_CHAT.md.
"""
import datetime
import fcntl
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GDIR = ROOT / 'codex' / 'work_chat' / 'gemini'
LOG = ROOT / 'codex' / 'work_chat' / 'GEMINI_REVIEW_LOG.md'
BRIEF = GDIR / 'GEMINI_BRIEF.md'
HIST = GDIR / 'history.json'
MODEL_FILE = GDIR / 'model.txt'
CFG = Path.home() / '.config' / 'iwo'
API = 'https://generativelanguage.googleapis.com/v1beta'
DENY = ('CODEX_WORK_CHAT', 'codex_', 'GEMINI_REVIEW_LOG', 'independent_reviews', 'history.json')
MAX_ATTACH = 600_000    # bytes of attached text per call (cost control)


def _key():
    k = os.environ.get('GEMINI_API_KEY', '').strip()
    if not k and (CFG / 'gemini_key').exists():
        k = (CFG / 'gemini_key').read_text().strip()
    if not k:
        sys.exit('No Gemini key found. The user runs tools/set_gemini_key.sh first.')
    return k


def _call(method, path, body=None, timeout=1200):
    k = _key()
    req = urllib.request.Request(API + path, method=method,
                                 headers={'x-goog-api-key': k, 'Content-Type': 'application/json'},
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors='replace')[:800].replace(k, '<key>')
        raise RuntimeError(f'HTTP {e.code}: {msg}') from None
    except urllib.error.URLError as e:
        raise RuntimeError(f'network error: {str(e.reason).replace(k, "<key>")}') from None


def list_models():
    out, tok = [], ''
    while True:
        r = _call('GET', '/models?pageSize=200' + (f'&pageToken={tok}' if tok else ''))
        out += r.get('models', [])
        tok = r.get('nextPageToken')
        if not tok:
            return [m for m in out if 'generateContent' in m.get('supportedGenerationMethods', [])]


def generate(model, contents, system=None, search=True):
    body = {'contents': contents}
    if system:
        body['system_instruction'] = {'parts': [{'text': system}]}
    if search:
        body['tools'] = [{'google_search': {}}]
    last = None
    for think in ({'thinkingLevel': 'high'}, {'thinkingBudget': -1}, None):   # strongest reasoning the model accepts
        b = dict(body)
        if think:
            b['generationConfig'] = {'thinkingConfig': think}
        try:
            return _call('POST', f'/{model}:generateContent', b), think
        except RuntimeError as e:
            last = e
            if 'HTTP 400' in str(e):
                continue
            raise
    raise last


def reply_text(r):
    c = (r.get('candidates') or [{}])[0]
    parts = (c.get('content') or {}).get('parts', [])
    text = '\n'.join(p.get('text', '') for p in parts if not p.get('thought'))
    src = []
    for ch in (c.get('groundingMetadata') or {}).get('groundingChunks', []):
        w = ch.get('web') or {}
        if w.get('uri'):
            src.append(f"- [{w.get('title') or w['uri']}]({w['uri']})")
    return text.strip(), src, c.get('finishReason', '')


def model_name():
    if MODEL_FILE.exists() and MODEL_FILE.read_text().strip():
        return MODEL_FILE.read_text().strip()
    sys.exit('No model chosen yet: run --test, then --set-model models/<name>.')


def test():
    ms = list_models()
    print(f'{len(ms)} models support generateContent:')
    for m in ms:
        print(f"  {m['name']:<48} in {m.get('inputTokenLimit', '?'):>8}  out {m.get('outputTokenLimit', '?'):>7}"
              f"  thinking={m.get('thinking', '?')}  {m.get('displayName', '')}")
    name = MODEL_FILE.read_text().strip() if MODEL_FILE.exists() else ''
    target = name or ms[0]['name']
    r, think = generate(target, [{'role': 'user', 'parts': [{'text': 'Reply with the single word OK.'}]}], search=False)
    print(f'ping {target} (thinking config {think}): {reply_text(r)[0][:40]!r}')
    print('billing confirmed:', (CFG / 'gemini_billing_confirmed').exists())


def send(topic, brief_path, files):
    if not (CFG / 'gemini_billing_confirmed').exists():
        sys.exit('Billing not confirmed (tools/set_gemini_key.sh): research data are not sent on the free tier.')
    for f in files:
        if any(d in Path(f).name or d in str(f) for d in DENY):
            sys.exit(f'Refused to attach {f}: Gemini reviews are blind to Codex/Claude review threads.')
    model = model_name()
    GDIR.mkdir(parents=True, exist_ok=True)
    lock = open(GDIR / '.lock', 'w')
    fcntl.flock(lock, fcntl.LOCK_EX)
    brief = Path(brief_path).read_text(encoding='utf-8', errors='replace')
    att, meta, total = [], [], 0
    for f in files:
        b = Path(f).read_bytes()
        total += len(b)
        if total > MAX_ATTACH:
            sys.exit(f'Attachments exceed {MAX_ATTACH} bytes; trim the file list.')
        sha = hashlib.sha256(b).hexdigest()
        att.append(f'\n\n=== FILE: {f} (sha256 {sha[:12]}) ===\n' + b.decode('utf-8', errors='replace'))
        meta.append(f'`{f}` ({len(b)} bytes, sha256 {sha[:12]}…)')
    hist = json.loads(HIST.read_text()) if HIST.exists() else []
    user_full = f'# {topic}\n\n{brief}' + ''.join(att)
    user_hist = f'# {topic}\n\n{brief}' + (('\n\n[attached, content omitted from history: ' + '; '.join(meta) + ']') if meta else '')
    contents = hist + [{'role': 'user', 'parts': [{'text': user_full}]}]
    system = BRIEF.read_text(encoding='utf-8') if BRIEF.exists() else None
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    r, think = generate(model, contents, system=system, search=True)
    text, src, fin = reply_text(r)
    hist += [{'role': 'user', 'parts': [{'text': user_hist}]}, {'role': 'model', 'parts': [{'text': text}]}]
    HIST.write_text(json.dumps(hist, indent=1), encoding='utf-8')
    with open(LOG, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(f'\n\n## {ts}: Claude to Gemini: {topic} ({model}, thinking {think})\n\n### Brief\n\n{brief}\n\n')
        if meta:
            fh.write('**Attached:** ' + '; '.join(meta) + '\n\n')
        fh.write(f'### Gemini reply (finish: {fin})\n\n{text}\n\n')
        if src:
            fh.write('**Search sources returned by the API:**\n' + '\n'.join(src) + '\n\n')
        fh.write('### Claude decision\n\n_pending_\n')
    print(text)
    if src:
        print('\nSources:\n' + '\n'.join(src))


def _attachments(files, cap):
    for f in files:
        if any(d in Path(f).name or d in str(f) for d in DENY):
            sys.exit(f'Refused to attach {f}: Gemini reviews are blind to Codex/Claude review threads.')
    att, meta, total = [], [], 0
    for f in files:
        b = Path(f).read_bytes()
        total += len(b)
        if total > cap:
            sys.exit(f'Attachments exceed {cap} bytes; trim the file list.')
        sha = hashlib.sha256(b).hexdigest()
        att.append(f'\n\n=== FILE: {Path(f).name} (sha256 {sha[:12]}) ===\n' + b.decode('utf-8', errors='replace'))
        meta.append(f'`{f}` ({len(b)} bytes, sha256 {sha[:12]}…)')
    return att, meta


def bundle(topic, brief_path, files):
    """Manual route (Google AI Pro plan, no API): one self-contained file to upload or paste into the Gemini app."""
    att, meta = _attachments(files, 1_500_000)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%MZ')
    out = GDIR / 'outbox' / f'{ts}_{"".join(c if c.isalnum() else "_" for c in topic)[:40]}.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    role = BRIEF.read_text(encoding='utf-8') if BRIEF.exists() else ''
    brief = Path(brief_path).read_text(encoding='utf-8', errors='replace')
    out.write_text(f'{role}\n\n---\n\n# {topic}\n\n{brief}' + ''.join(att), encoding='utf-8', newline='\n')
    (GDIR / 'outbox' / 'LATEST').write_text(f'{out.name}\n{topic}\n' + '\n'.join(meta) + '\n', encoding='utf-8')
    print(f'{out}  ({out.stat().st_size} bytes)')


def ingest(reply_path, model='Gemini app (manual, Google AI Pro)'):
    """Log a reply the user copied from the Gemini app, against the latest bundle."""
    latest = (GDIR / 'outbox' / 'LATEST').read_text(encoding='utf-8').splitlines()
    name, topic, meta = latest[0], latest[1], latest[2:]
    text = Path(reply_path).read_text(encoding='utf-8', errors='replace').strip()
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    with open(LOG, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(f'\n\n## {ts}: Claude to Gemini: {topic} ({model})\n\n**Bundle:** `codex/work_chat/gemini/outbox/{name}`\n\n')
        if meta:
            fh.write('**Attached:** ' + '; '.join(meta) + '\n\n')
        fh.write(f'### Gemini reply (pasted by the user)\n\n{text}\n\n### Claude decision\n\n_pending_\n')
    print('logged reply to', LOG)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == '--bundle' and len(a) >= 3:
        bundle(a[1], a[2], a[3:])
    elif a[0] == '--ingest' and len(a) == 2:
        ingest(a[1])
    elif a[0] == '--test':
        test()
    elif a[0] == '--set-model' and len(a) == 2:
        GDIR.mkdir(parents=True, exist_ok=True)
        MODEL_FILE.write_text(a[1].strip() + '\n')
        print('model set:', a[1])
    elif len(a) >= 2:
        send(a[0], a[1], a[2:])
    else:
        sys.exit(__doc__)
