"""Owned QMP relative pointer event journal for the visible Welcome window."""
import importlib,json,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/home/paul/xbox-windows-native/d3d-texture477-pc001')
sys.path.insert(0,str(K.parent/'clean-media404'));Qmp=importlib.import_module('pc-run001').Qmp
s=json.loads((K/'ntfs-phase1.json').read_text());assert not s['closed']
assert b'xwn-d3d-texture477-pc-phase1\0' in Path(f"/proc/{s['pid']}/cmdline").read_bytes()
command=sys.argv[1];assert command in ('mouse_move 105 69','mouse_button 1','mouse_button 0')
with Qmp(P/'phase1/qmp.sock') as q:r=q.call('human-monitor-command',{'command-line':command})
(P/'phase1'/f'mouse003-{time.time_ns()}.json').write_text(json.dumps(dict(command=command,result=r)))
