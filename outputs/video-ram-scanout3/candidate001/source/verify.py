"""Recheck raw physical bytes, resident pins, bounded teardown and cold gates."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
dest=k/'verification.json';assert not dest.exists();trace=read(out/'trace.json');audit=read(out/'audit.json');closure=read(out/'closure.json')
for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
assert sha(Path(closure['private_disk']))==closure['private_disk_sha256']
for n,h in trace['dependencies'].items():
 p=Path(n);p=p if p.is_absolute() else ws/p;assert sha(p)==h
paths={'probe.exe':k/'artifacts/probe.exe','xwnram.dll':out/'artifacts/xwnram.dll','ntoskrnl.exe':Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe')}
for pin in trace['pins']:
 p=pefile.PE(str(paths[pin['module']]));raw=bytes.fromhex(pin['raw']);assert p.get_data(pin['rva'],len(raw))==raw
 expected=bytearray(raw)
 for off in pin['relocations']:struct.pack_into('<I',expected,off,(struct.unpack_from('<I',expected,off)[0]+pin['base']-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 assert bytes(expected)==bytes.fromhex(pin['resident']) and sha(paths[pin['module']])==pin['sha256']
expected_order=[(phase,size,kind) for size in [0,2] for kind in [1,3] for phase in [0,1,2]]
events=[]
for index,e in enumerate(trace['events']):
 assert tuple(e['args'][:3])==expected_order[index]
 p=out/'artifacts'/e['raw'];assert sha(p)==e['sha256'];data=p.read_bytes();assert len(data)==2359296
 phase,size,kind,cx,cy=e['args'];delta=16 if kind==3 and phase else 0;w,h=[(64,64),(768,384)][size//2];x,y=cx+delta,cy+delta
 assert e['rectangle']==[x,y,w,h] and e['physical_address']==0x3c00000 and e['pitch']==4096
 bad=0
 for yy in range(h):
  for xx in range(w):
   b=(xx*17+yy*19)&255;green=(yy*11+xx*3)&255;red=(xx*13+yy*7)&255
   at=(y+yy)*4096+(x+xx)*4;bad+=data[at:at+3]!=bytes([b,green,red])
 assert bad==e['mismatches'];events.append(dict(index=index,pixels=w*h,mismatches=bad,sha256=sha(p)))
before=read(out/'before-pagefile-map.json');after=read(out/'after-pagefile-map.json');pagefile=all(before[n]==after[n] for n in ['file_size','clusters','first_cluster','requested_65536','whole_file'])
v=(out/'artifacts/video-trace.bin').read_bytes();count,dropped=struct.unpack_from('<II',v,16);assert count<=254
shared=[list(struct.unpack_from('<4I',v,32+i*16)) for i in range(count) if struct.unpack_from('<I',v,32+i*16)[0] in [0x30,0x31,0x32]]
mapped=any(e==[0x30,0,0xfced6000,0x03c00000] for e in shared) and all(e[1]==0 for e in shared)
pins={v['module'] for v in trace['pins']};teardown=trace.get('guest_resumed') is True and trace.get('armed_breakpoints_remaining')==[] and not trace.get('resume_error')
pe=pefile.PE(str(paths['xwnram.dll']));sec=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.text')
covered=set()
for pin in trace['pins']:
 if pin['module']=='xwnram.dll':covered.update(range(pin['rva'],pin['rva']+len(bytes.fromhex(pin['raw']))))
full_text=all(rva in covered for rva in range(sec.VirtualAddress,sec.VirtualAddress+sec.Misc_VirtualSize))
passed=trace['status']=='twelve_physical_snapshots_match' and len(events)==12 and not any(e['mismatches'] for e in events) and pins==set(paths) and full_text and teardown and audit['strict_qualification_passed'] and read(out/'after-configuration.json')['expected_configuration'] and pagefile and mapped and dropped==0
r=dict(passed=bool(passed),strict_diagnostic_passed=bool(passed),ordinary_qualified=False,physical_qualified=False,events=events,pixels=sum(e['pixels'] for e in events),runtime_pins=len(trace['pins']),teardown_passed=teardown,pagefile_unchanged=pagefile,shared_events=shared,trace_records=count,dropped=dropped,cold_qualification=audit['strict_qualification_passed'],
 pins={n:sha(out/n) for n in ['trace.json','audit.json','closure.json','preflight.json','allocation.json','after-configuration.json','before-pagefile-map.json','after-pagefile-map.json']},verifier_sha256=sha(Path(__file__)),limits='Twelve physical-buffer checkpoints for initialization/DIB copy/overlap; not complete DDI, cursor exclusion, mode/crash or hardware/performance qualification.')
r['full_display_text_matched']=full_text;r['display_text_bytes']=sec.Misc_VirtualSize;r['module_header_observations']=trace.get('module_header_observations',{})
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','pixels','runtime_pins','teardown_passed','cold_qualification','full_display_text_matched']},indent=2))
