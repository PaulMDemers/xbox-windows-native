"""New observer: a nonresident display PE header is unknown, not invented."""
from pathlib import Path
import json,shutil
p=Path(__file__).resolve().parent;k=p.parent/'video-ram-scanout3'
t=json.loads((p/'candidate001/trace.json').read_text());assert t['error']=="AssertionError('E14')" and t['guest_resumed'] and not t['armed_breakpoints_remaining'] and t['kernel_discovery']
k.mkdir(exist_ok=False)
for n in ['display','tests']:shutil.copytree(p/n,k/n)
for n in ['0108-ram-primary.patch','patch-review.json','build-report.json','source-verification.json','host-tests.json','tests-body.c','probe.c','pe-review.json','discover_kernel.py','discovery-replay.json']:
 shutil.copyfile(p/n,k/n)
(k/'candidate001/artifacts').mkdir(parents=True);(k/'artifacts').mkdir()
for n in ['candidate001/artifacts/xwnram.dll','candidate001/build.json','artifacts/probe.exe']:shutil.copyfile(p/n,k/n)
for n in ['atomic_json.py','audit.py','configuration.py','cold-map.py','preflight.py','Run.ps1','supervise.py','record-closure.py','common.py','prepare.py','review.py','mark-diagnostic.py','verify.py','trace.py']:
 s=(p/n).read_text().replace('video-ram-scanout2','video-ram-scanout3').replace('nt5-vrscan2-','nt5-vrscan3-')
 if n=='trace.py':
  s=s.replace('g=None;stopped=False;armed=set();loaded=[];', 'g=None;stopped=False;armed=set();loaded=[];headers={};')
  needle=" assert g.read(base,2)==b'MZ';nt=u32(base+60);assert nt<4096 and u32(base+nt+8)==p.FILE_HEADER.TimeDateStamp"
  assert needle in s
  s=s.replace(needle,''' if name not in headers:
  try:
   assert g.read(base,2)==b'MZ';nt=u32(base+60);assert nt<4096 and u32(base+nt+8)==p.FILE_HEADER.TimeDateStamp
   headers[name]=dict(readable=True,base=base,timestamp=p.FILE_HEADER.TimeDateStamp)
  except AssertionError as exc:
   if name!='xwnram.dll' or str(exc)!='E14':raise
   headers[name]=dict(readable=False,base=base,reason='GDB E14 on header; identity instead requires loader base/size/name and exact relocated resident code. Cold PE hash retained.')
  r['module_header_observations']=headers
''')
  # Require all driver text to match, not merely five function prefixes.
  needle="   pin('ntoskrnl.exe',sites['modules']['ntoskrnl.exe']['exports']['KeBugCheckEx'])"
  assert needle in s
  s=s.replace(needle,"""   sec=next(s for s in pes['xwnram.dll'].sections if s.Name.rstrip(b'\\0')==b'.text')
   offset=0
   while offset<sec.Misc_VirtualSize:
    pin('xwnram.dll',sec.VirtualAddress+offset,min(48,sec.Misc_VirtualSize-offset));offset+=len(bytes.fromhex(r['pins'][-1]['raw']))
   r['display_text_identity']=dict(rva=sec.VirtualAddress,bytes=sec.Misc_VirtualSize,matched=True)
"""+needle)
 (k/n).write_text(s,newline='\n')
