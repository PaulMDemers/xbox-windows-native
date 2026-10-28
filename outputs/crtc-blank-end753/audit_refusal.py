"""Audit753 clock refusal locally; no recollection or physical access."""
from pathlib import Path
import json,hashlib,datetime,subprocess
K=Path(__file__).resolve().parent;P=Path('C:/xwn753');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
c=read(K/'collection001.json');assert c['completed'] and c['unrelated_directory_entries_unchanged']
rows=sorted(c['reports'].items());assert [v['data']['phase'] for n,v in rows]==['start','clock_reference_refused']
for n,v in rows:assert sha(P/'collection001'/n)==v['sha256'] and read(P/'collection001'/n)==v['data']
for n,h in read(K/'sources001.json').items():assert sha(K/n)==h
for n,v in read(K/'build001.json')['files'].items():assert sha(P/'build001'/n)==v['sha256']
assert rows[-1][1]['data']['kernel_qpc_frequency']==3375000
s=(K/'main.c').read_text();assert 'if(frequency!=3375300)' in s
assert s.index('if(frequency!=3375300)')<s.index('BOOL applied=XVideoSetMode(')<s.index('probe753(&result)')
d=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dr','/mnt/c/xwn753/build001/main.obj'],text=True)
a=d.index('__imp__KeQueryPerformanceFrequency');snippet=d[a-150:a+1450];assert '$0x3380c4,%eax' in snippet and int('3380c4',16)==3375300
assert read(K/'dashboard001.json')['reachable'] and not read(K/'audit001.json')['passed']
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'outcome':'CLOSED clock-reference refusal; no CR03 test executed','reported_frequency_low32':3375000,'erroneous_comparison_constant':3375300,'intended_constant':3375000,'cause':'prepare.py broad namespace replacement changed decimal3375000; source comparison repeated same replacement and missed it','object_disassembly_excerpt':snippet,'audit001_failure_retained':True,'exact_sources_build_stage_collection':True,'before_video_mode_or_probe':True,'normal_windows_shutdown':False,'native_or_CR03_proof':False,'hook':False,'dashboard_authenticated':True,'physical_access':False}
p=K/'refusal-audit001.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','outcome','reported_frequency_low32','erroneous_comparison_constant']}))
