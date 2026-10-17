"""Prepare a distinct physical RGB32 probe kit; no console access."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'presentation442'
for name in ('physical.py','observe002.py','review001.py','closeout001.py'):
 s=(old/name).read_text(encoding='utf-8').replace('presentation442','key-xbox448').replace('xwn442','xwn448').replace('run442','run448').replace("'442'","'448'").replace('442 staged','448 staged').replace('442 collected','448 collected')
 if name=='physical.py':
  s=s.replace("K.parent/'presentation440/runtime-review001.json'","K.parent/'key-depth447/runtime-review001.json'").replace("pc['all_allowed_cases_passed']","pc['all_semantics_passed']")
  s=s.replace("K.parent/'presentation440/independent001.json'","K.parent/'key-depth447/independent001.json'")
 elif name=='review001.py':
  s=s.replace('import graphics_present as g','import graphics_keyprobe as g').replace('present.exe','keyprobe.exe').replace('4f1abf4417620aee9c8343962042cc48cbd6c6abc37215a457acd08c2e310132','0fcbc34e3d18339aa0f4a7bfe1d2e8852846a697469e7a591d97456863b3649c')
  s=s.replace("('r03d','default'),('r03s','hel')","('keyd','default'),('keys','hel')").replace('row=dict(name=name,process_exit=int(code),fields=f)','row=dict(name=name,backend=backend,process_exit=int(code),fields=f)')
  s=s.replace("g.validate((root/(name+'.txt')).read_bytes(),{k:(root/(name+'-'+k+'.bin')).read_bytes() for k in ('source','before','after')},backend,int(code))","g.validate((root/(name+'.txt')).read_bytes(),(root/(name+'-source.bin')).read_bytes(),(root/(name+'-dest.bin')).read_bytes(),backend,int(code))")
  s=s.replace("all('review' in row for row in r['rows'])","all(row.get('review',{}).get('semantics_passed') is True for row in r['rows'])")
 elif name=='closeout001.py':
  s=s.replace('scoped_presentation_passed','scoped_keyprobe_passed').replace("get('exact_bytes',0)","get('captured_bytes',0)").replace('GDI readback not human visual/scanout qualification','Raw system-memory readback, not human visual/scanout qualification')
 (K/name).write_text(s,encoding='utf-8',newline='\n')
s=(K.parent/'key-semantics446/runner.c').read_text(encoding='utf-8')
s=s.replace('Owned NT5 fixture only','Owned physical Xbox Windows fixture only').replace('xwn446','xwn448').replace('number("schema",446)','number("schema",448)').replace('A:\\\\KEYPROBE.EXE','C:\\\\xwn448-kit\\\\keyprobe.exe')
(K/'runner.c').write_text(s,encoding='utf-8',newline='\n')
for name in ('build001.py','binary-review001.py'):
 s=(K.parent/'key-semantics446'/name).read_text(encoding='utf-8').replace('key-semantics446-runner-build001','key-xbox448-runner-build001').replace('run446','run448')
 (K/name).write_text(s,encoding='utf-8',newline='\n')
print('Distinct physical kit created; no stage/launch.')
