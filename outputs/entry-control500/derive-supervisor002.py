from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'supervise002.py';assert not p.exists()
b=(K/'supervise.py').read_bytes()
b=b.replace(b'import datetime,json,os,subprocess,sys',b'import datetime,importlib.util,json,os,subprocess,sys')
anchor=b"LOG=Path('C:/xwn500/supervisor001')"
replacement=b"s=importlib.util.spec_from_file_location('atomic500',W/'outputs/surface-bridge260/atomic_json.py')\natomic=importlib.util.module_from_spec(s);s.loader.exec_module(atomic)\nLOG=Path('C:/xwn500/supervisor002')"
assert b.count(anchor)==1;b=b.replace(anchor,replacement)
anchor=b"tmp=out.with_suffix('.tmp');tmp.write_bytes((json.dumps(r,indent=2)+'\\n').encode());tmp.replace(out)"
assert b.count(anchor)==1;b=b.replace(anchor,b'atomic.write_json(out,r)')
p.write_bytes(b)
p=K/'supervisor-host002.py';assert not p.exists()
b=(K/'supervisor-host001.py').read_bytes().replace(b'supervisor-host001',b'supervisor-host002').replace(b"K/'supervise.py'",b"K/'supervise002.py'")
p.write_bytes(b)
