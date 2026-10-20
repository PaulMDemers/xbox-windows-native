"""Single cold readback review of game request discovery, before visual review."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn599/pc001/cold1-002')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
from Registry import Registry
from parse_trace001 import parse
read=lambda n:json.loads((K/n).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'review001.json';assert not out.exists()
r=dict(passed=False,physical_access=False)
try:
 s=read('ntfs-phase1.json');a=read('ntfs-cold1-002.json');b=read('build001.json');manifest=json.loads((P/'manifest.json').read_text())
 assert s['closed'] and s['exit_code']==0 and not s['deadline'] and a['complete']
 assert not any(s.get(n) for n in ['host_quit','host_terminate','host_kill','space_stop'])
 assert a['audit_unchanged'] and a['source_unchanged'] and a['normal_shutdown_delta']==1
 assert all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in a['hives'])
 for row in b['rows']:assert manifest['xwn599-kit/'+Path(row['path']).name]['sha256']==row['sha256']
 logs=P/'files/xwn599';run=(logs/'runner.txt').read_text()
 for line in ['display_preflight_passed=1','initial_width=1024','initial_height=768','input_sequence_submitted=1','game_exit=0','registry_restored=1','restart_requested=1']:assert line in run,line
 assert 'forced_terminate=' not in run and 'display_preflight_failed' not in run
 copy=(P/'files/xwn599-kit/copy-verified.txt').read_text();assert 'verified=1' in copy and 'files=502' in copy
 reg=Registry.Registry(str(P/'files/WINNT/system32/config/software'))
 try:reg.open('Fish Technology Group')
 except Registry.RegistryKeyNotFoundException:pass
 else:raise AssertionError('Temporary game registry subtree remained')
 pe=pefile.PE('C:/xwn566/transfer002/game/RCT.EXE')
 parsed=parse((logs/'trace.txt').read_text(),pe.OPTIONAL_HEADER.ImageBase,pe.OPTIONAL_HEADER.SizeOfImage)
 parsed['private_log_sha256']=sha(logs/'trace.txt');(K/'trace-review001.json').write_text(json.dumps(parsed,indent=2)+'\n')
 assets=read('asset-integrity001.json');changes=[]
 for name,row in assets.items():
  observed=manifest['xwn599-kit/'+name.lower()]
  if observed['sha256']!=row['sha256']:changes.append(dict(name=name,before=row['sha256'],after=observed['sha256'],bytes=observed['bytes']))
 (K/'asset-changes001.json').write_text(json.dumps(changes,indent=2)+'\n')
 assert {x['name'] for x in changes}<={'game/Data/CSS0.DAT','game/Data/Game.cfg'}
 captures=[]
 for i,name in enumerate(['title','scenarios','objective','window-options','park-api-observation']):
  p=logs/('%02d-%s.bmp'%(i,name));data=p.read_bytes()
  assert len(data)==1228854 and data[:2]==b'BM'
  assert struct.unpack_from('<I',data,10)[0]==54 and struct.unpack_from('<IiiHHII',data,14)==(40,640,-480,1,32,0,1228800)
  assert 'capture='+name+' index='+str(i)+' success=1' in run
  captures.append(dict(name=p.name,bytes=len(data),sha256=sha(p),private_path=str(p)))
 r.update(passed=True,normal_shutdown_delta=1,registry_restored=True,protected_binary_audit_passed=True,
          total_requests=parsed['total_entry_requests'],main_image_requests=parsed['main_image_requests'],other_caller_requests=parsed['other_caller_requests'],captures=captures,
          new_system_events=a['new_system_events'],limits='Game helper/cold checks; visual review still required. API requests only, no successful resolution return, invocation, overhead, FPS or acceleration result.')
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('599 cold trace/capture/cleanup checks passed; visual review pending')
