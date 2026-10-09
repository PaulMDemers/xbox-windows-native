"""Offline, one-shot verification of the observed cross-thread token close.

This records a diagnostic result, not ordinary or physical qualification.
The frozen general verifier independently checks every resident pin and call pair.
"""
import hashlib
import json
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
out = k / 'candidate001'
dest = out / 'token-race-verification.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
t = read(out / 'trace.json')
v = read(out / 'trace-verification.json')
c = read(out / 'closure.json')
assert c['closed'] and v['diagnostic_capture_complete']
events = {e['index']: e for e in t['events']}
pairs = {p['entry']: p for p in v['creation_pairs'] + v['native_api_pairs']}
outer = events[189]
token = outer['arguments'][0]
assert token == 1880 and 'DEV_01B4' in outer['command_line']
assert outer['function'] == 'CreateProcessAsUserW'
assert outer['owner']['image'] == 'services.exe'
pre, user, kernel, inner, post = [events[i] for i in [190, 199, 200, 192, 210]]
assert pre['arguments'][:2] == [token, 12] and pairs[190]['result'] == 0
assert pairs[190]['returned'] == 191 and pairs[190]['output_prefix'] == '00000000'
assert user['function'] == 'NtClose' and kernel['function'] == '_NtClose@4'
for e in [user, kernel]:
    assert e['arguments'] == [token] and e['cross_thread_token_close'] is True
    assert e['owner']['process'] == outer['owner']['process']
    assert e['owner']['pid'] == outer['owner']['pid'] == 208
    assert e['owner']['thread'] != outer['owner']['thread']
    assert e['outer_scope']['entry'] == outer['index']
    assert e['outer_scope']['token_handle'] == token
    assert pairs[e['index']]['result'] == 0
assert user['owner']['thread'] == kernel['owner']['thread']
assert pairs[200]['returned'] == 201 and pairs[199]['returned'] == 202
assert 189 < 190 < 191 < 192 < 199 < 200 < 201 < 202 < 209 < 210 < 211 < 220
assert pre['tick_count'] == 6621 < user['tick_count'] == kernel['tick_count'] == 6624
assert pairs[192]['returned'] == 209 and pairs[192]['result'] == 1
assert pairs[192]['process_information'] == [1904, 1892, 732, 936]
assert post['arguments'][:2] == [token, 8]
assert post['owner']['thread'] == pre['owner']['thread'] == outer['owner']['thread']
assert pairs[210]['result'] == 0xc0000008 and pairs[210]['returned'] == 211
assert events[211]['tick_count'] == 6631
assert pairs[189]['returned'] == 220 and pairs[189]['result'] == 0
assert pairs[189]['last_error'] == 6
assert not any(e.get('kind') == 'native_api' and e['function'] in ['NtClose', '_NtClose@4']
               and e['arguments'] == [token] and e['owner']['thread'] == outer['owner']['thread']
               for e in t['events'] if 189 < e['index'] < 220)

# Attribute only the immediate, resident-pinned user wrapper. No higher frame
# was captured; an EBP value by itself cannot name the closing cleanup routine.
pin = t['pins'][user['caller_identity']['pin']]
assert pin['module']['name'] == 'kernel32.dll' and pin['rva'] == 32496
assert pin['address'] == user['caller']
meta = read(k / 'sites.json')['binaries']['kernel32.dll']
file = ws / meta['path']
assert sha(file) == pin['source_sha256'] == meta['sha256']
sys.path.insert(0, str(ws / 'work/python-packages'))
import pefile
pe = pefile.PE(str(file))
close_export = next(e for e in pe.DIRECTORY_ENTRY_EXPORT.symbols if e.name == b'CloseHandle')
assert close_export.address == 32417
assert pe.get_data(pin['rva'], len(bytes.fromhex(pin['raw']))).hex() == pin['raw']
exports_after = [e.address for e in pe.DIRECTORY_ENTRY_EXPORT.symbols
                 if e.address > close_export.address and not e.forwarder]
assert pin['rva'] < min(exports_after)

r = dict(
    passed=True, debugger=True, ordinary_qualified=False, physical_qualified=False,
    sources={p.name: sha(p) for p in [Path(__file__), out/'trace.json', out/'trace-verification.json', out/'closure.json']},
    outer_entry=189, token_handle=token, process=outer['owner']['process'], pid=208,
    installer_thread=outer['owner']['thread'], closing_thread=user['owner']['thread'],
    valid_query=[190,191], user_close=[199,202], kernel_close=[200,201],
    inner_creation=[192,209], invalid_query=[210,211], outer_failure=[189,220],
    immediate_user_close_caller=dict(module='kernel32.dll', export='CloseHandle',
        export_rva=close_export.address, return_rva=pin['rva'], resident_pin=user['caller_identity']['pin'],
        binary_sha256=sha(file)),
    observed='Same-process other thread successfully closes the supplied token during inner creation; the installer then queries that handle and receives STATUS_INVALID_HANDLE, followed by outer FALSE/LastError6.',
    limits=['No higher closing-thread call stack or token object identity captured.',
            'Owner EPROCESS comparison does not establish arbitrary APC attached-process contexts.',
            'Debugger scheduling may expose or change race timing; this is not ordinary validation.',
            'No popup in this run does not fix the popup captured in other runs.',
            'No evidence here of graphics, FATX, or physical storage corruption.'])
dest.write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')
print(json.dumps(r))
