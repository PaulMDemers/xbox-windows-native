"""MIT. Preserve the refused display prerequisite; no successful scene claim."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
s=read(K/'ntfs-phase1.json');c=read(K/'ntfs-cold1-002.json');q=read(K/'preflight001.json')
assert s['closed'] and s['exit_code']==0 and not s['deadline'] and not any(s.get(n) for n in ('host_quit','host_kill','host_terminate'))
assert c['complete'] and c['normal_shutdown_delta']==1 and c['source_unchanged'] and c['audit_unchanged']
p=Path(c['private_path'])/'files/xwn546';raw=(p/'runner.txt').read_bytes();fields=dict(line.split('=',1) for line in raw.decode().splitlines())
assert fields['mode.test']=='4294967294' and fields['completed_cases']=='0' and fields['restart_request']=='1'
assert set(x.name for x in p.iterdir())=={'d3d.exe','runner.txt'}
archive=Path('/mnt/c/xwn546/frozen001');assert not archive.exists();archive.mkdir();rows=[]
for i,(name,h) in enumerate(q['files'].items()):
 src=Path(name);assert sha(src)==h;dest=archive/f'{i:03d}-{src.name}';dest.write_bytes(src.read_bytes());assert sha(dest)==h;rows.append(dict(original=name,path=str(dest),sha256=h))
(K/'pc001-runner.txt').write_bytes(raw)
r=dict(closed=True,scene_qualified=False,physical_launched=False,failed_prerequisite='Cirrus desktop32 CDS_TEST refused DISP_CHANGE_BADMODE(-2)',runner=fields,normal_restart=True,all_owned_processes_closed=True,frozen_inputs=rows,cold_audit_sha256=sha(K/'ntfs-cold1-002.json'),source_sha256=sha(Path(__file__)))
(K/'final-failed001.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('546 closed: no scene ran; input pins archived; normal restart.')
