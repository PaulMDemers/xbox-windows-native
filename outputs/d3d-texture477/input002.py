"""Explicit short key holds prevent overlapping modifier releases in owned QMP UI."""
import argparse,importlib,json,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/d3d-texture477-pc001')
sys.path.insert(0,str(K.parent/'clean-media404'));Qmp=importlib.import_module('pc-run001').Qmp
p=argparse.ArgumentParser();p.add_argument('--key');p.add_argument('--text');a=p.parse_args()
assert bool(a.key)!=bool(a.text)
state=json.loads((K/'ntfs-phase1.json').read_text());assert not state['closed']
assert b'xwn-d3d-texture477-pc-phase1\0' in Path(f"/proc/{state['pid']}/cmdline").read_bytes()
keys=[a.key] if a.key else [{'\\':'backslash',':':'shift-semicolon','.':'dot',' ':'spc','-':'minus','/':'slash'}.get(c,c) for c in a.text]
out=P/'phase1'/f'input002-{time.time_ns()}.json';r=dict(key=a.key,text=a.text,hold_ms=20,spacing_ms=200,sent=False)
out.write_text(json.dumps(r))
with Qmp(P/'phase1/qmp.sock') as q:
    for key in keys:q.call('human-monitor-command',{'command-line':'sendkey '+key+' 20'});time.sleep(.2)
r['sent']=True;out.write_text(json.dumps(r))
