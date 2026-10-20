"""Close the failed display-layout experiment; preserve valid trace separately."""
import datetime,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn598/pc001/cold1-002')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
from Registry import Registry
from parse_trace001 import parse
read=lambda n:json.loads((K/n).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
s=read('ntfs-phase1.json');a=read('ntfs-cold1-002.json');b=read('build001.json');manifest=json.loads((P/'manifest.json').read_text())
assert s['closed'] and s['exit_code']==0 and not s['deadline'] and a['complete']
assert not any(s.get(n) for n in ['host_quit','host_terminate','host_kill','space_stop'])
assert a['audit_unchanged'] and a['source_unchanged'] and a['normal_shutdown_delta']==1
assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in a['hives'])
for row in b['rows']:assert manifest['xwn598-kit/'+Path(row['path']).name]['sha256']==row['sha256']
logs=P/'files/xwn598';run=(logs/'runner.txt').read_text()
for line in ['pc_display_change=4294967294','initial_width=640','initial_height=480','input_sequence_submitted=0','game_exit=0','registry_restored=1','restart_requested=1']:assert line in run
assert 'forced_terminate=' not in run and not list(logs.glob('*.bmp'))
copy=(P/'files/xwn598-kit/copy-verified.txt').read_text();assert 'verified=1' in copy and 'files=502' in copy
reg=Registry.Registry(str(P/'files/WINNT/system32/config/software'))
try:reg.open('Fish Technology Group')
except Registry.RegistryKeyNotFoundException:pass
else:raise AssertionError('Temporary game registry subtree remained')
pe=pefile.PE('C:/xwn566/transfer002/game/RCT.EXE')
parsed=parse((logs/'trace.txt').read_text(),pe.OPTIONAL_HEADER.ImageBase,pe.OPTIONAL_HEADER.SizeOfImage)
parsed['private_log_sha256']=sha(logs/'trace.txt');(K/'trace-review001.json').write_text(json.dumps(parsed,indent=2)+'\n')
assets=read('asset-integrity001.json');changes=[]
for name,row in assets.items():
 observed=manifest['xwn598-kit/'+name.lower()]
 if observed['sha256']!=row['sha256']:changes.append(dict(name=name,before=row['sha256'],after=observed['sha256'],bytes=observed['bytes']))
(K/'asset-changes001.json').write_text(json.dumps(changes,indent=2)+'\n')
r=dict(closed=True,passed=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),failure='DISP_CHANGE_BADMODE(-2) from requested800x600x32; helper ignored result and strict visible-client guard later refused input.',
 trace_entry_discovery_passed=True,total_requests=parsed['total_entry_requests'],main_image_requests=parsed['main_image_requests'],other_caller_requests=parsed['other_caller_requests'],
 park_observation=False,registry_restored=True,normal_shutdown_delta=1,protected_binary_audit_passed=True,physical_access=False,
 screen_race='One screen request encountered already-closed process ownership guard after normal exit; no input or runtime reopening.',
 misleading_field='runner game_exit reports debugger exit; trace END independently reports child exit0.',
 next='Fresh599 native Display control panel1024x768 with fail-closed helper preflight; no reopening598.',
 pins={str(p):sha(p) for p in K.iterdir() if p.is_file()},new_system_events=a['new_system_events'])
out.write_text(json.dumps(r,indent=2)+'\n');print('598 CLOSED failure: display setup; trace',parsed['total_entry_requests'],'requests; normal cleanup passed')
