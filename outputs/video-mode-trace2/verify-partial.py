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
paths={'kernel32.dll':Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/kernel32.dll'),'probe.exe':k/'artifacts/probe.exe','xwnown.dll':out/'artifacts/xwnown.dll','ntoskrnl.exe':Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/ntoskrnl.exe')}
for pin in trace['pins']:
 p=pefile.PE(str(paths[pin['module']]));raw=bytes.fromhex(pin['raw']);assert p.get_data(pin['rva'],len(raw))==raw
 expected=bytearray(raw)
 for off in pin['relocations']:struct.pack_into('<I',expected,off,(struct.unpack_from('<I',expected,off)[0]+pin['base']-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 assert bytes(expected)==bytes.fromhex(pin['resident']) and sha(paths[pin['module']])==pin['sha256']
from protocol import fnv
events=[]
for index,e in enumerate(trace['events']):
 assert e['args'][0]==index
 p=out/'artifacts'/e['raw'];assert sha(p)==e['sha256'];data=p.read_bytes();assert len(data)==2359296
 _,reference,x,y,w,h,stride,digest=e['args'];assert (w,h,stride)==(384,256,1536)
 assert 0<=x<x+w<=1024 and 0<=y<y+h<=576
 assert not(x<=1000<x+w and y<=550<y+h)
 ref=out/'artifacts'/e['reference_raw'];cold=out/'artifacts'/('ref%02d.rgb'%index)
 assert sha(ref)==e['reference_sha256']==sha(cold)
 expected=ref.read_bytes();assert len(expected)==393216 and fnv(expected)==digest
 assert e['rectangle']==[x,y,w,h] and e['physical_address']==0x3c00000 and e['pitch']==4096
 bad=0
 for yy in range(h):
  for xx in range(w):
   at=(y+yy)*4096+(x+xx)*4;want=yy*stride+xx*4
   bad+=data[at:at+3]!=expected[want:want+3]
 assert bad==e['mismatches'];events.append(dict(index=index,pixels=w*h,mismatches=bad,sha256=sha(p),reference_sha256=sha(ref)))
cursor_events=[]
for ordinal,e in enumerate(trace['cursor_events']):
 index,phase,reference,cx,cy,shape,digest,shown=e['args']
 assert (index,phase)==divmod(ordinal,3) and e['owner']==trace['probe_entry']['owner']
 if index<len(trace['events']):assert e['owner']==trace['events'][index]['owner']
 assert (cx,cy)==([80,0,380,170][index%4],[70,0,250,140][index%4])
 assert shape==(1-index%2 if phase==2 else index%2) and shown==int(phase!=1)
 hx,hy=([7,11] if shape==0 else [15,3]);assert e['position']==[cx,cy] and e['hotspot']==[hx,hy]
 raw=out/'artifacts'/e['raw'];ref=out/'artifacts'/e['reference_raw'];cold=out/'artifacts'/('ref%02d.rgb'%index)
 assert sha(raw)==e['sha256'] and sha(ref)==e['reference_sha256']==sha(cold)
 data=raw.read_bytes();expected=ref.read_bytes();assert len(data)==2359296 and len(expected)==393216 and fnv(expected)==digest
 bad=0;covered=0;changed=0
 for y in range(256):
  for x in range(384):
   want=int.from_bytes(expected[(y*384+x)*4:(y*384+x)*4+3],'little');bg=want;dx=x-cx+hx;dy=y-cy+hy
   if shown and 0<=dx<32 and 0<=dy<32:
    covered+=1
    if (dx//8+shape)%3:want=(((dx*7+shape*71)%256)<<16)|(((dy*9+shape*43)%256)<<8)|((dx*3+dy*5+shape*101)%256)
    changed+=want!=bg
   got=int.from_bytes(data[y*4096+x*4:y*4096+x*4+3],'little');bad+=got!=want
 assert (bad,covered,changed)==(e['mismatches'],e['cursor_pixels'],e['changed_by_cursor'])
 assert changed>0 if shown else changed==covered==0
 cursor_events.append(dict(index=index,phase=phase,pixels=98304,mismatches=bad,cursor_pixels=covered,changed_by_cursor=changed,sha256=sha(raw),reference_sha256=sha(ref)))
before=read(out/'before-pagefile-map.json');after=read(out/'after-pagefile-map.json');pagefile=all(before[n]==after[n] for n in ['file_size','clusters','first_cluster','requested_65536','whole_file'])
v=(out/'artifacts/video-trace.bin').read_bytes();count,dropped=struct.unpack_from('<II',v,16);assert count<=254
shared=[list(struct.unpack_from('<4I',v,32+i*16)) for i in range(count) if struct.unpack_from('<I',v,32+i*16)[0] in [0x30,0x31,0x32]]
mapped=any(e==[0x30,0,0xfced6000,0x03c00000] for e in shared) and all(e[1]==0 for e in shared)
pins={v['module'] for v in trace['pins']};teardown=trace.get('guest_resumed') is True and trace.get('armed_breakpoints_remaining')==[] and not trace.get('resume_error')
pe=pefile.PE(str(paths['xwnown.dll']));sec=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.text')
covered=set()
for pin in trace['pins']:
 if pin['module']=='xwnown.dll':covered.update(range(pin['rva'],pin['rva']+len(bytes.fromhex(pin['raw']))))
full_text=all(rva in covered for rva in range(sec.VirtualAddress,sec.VirtualAddress+sec.Misc_VirtualSize))
assert trace['status']=='capture_incomplete' and len(events)==0 and len(cursor_events)==3
passed=trace['status']=='104_color_cursor_snapshots_match' and len(cursor_events)==78 and not any(e['mismatches'] for e in cursor_events) and len(events)==26 and not any(e['mismatches'] for e in events) and pins==set(paths) and full_text and teardown and audit['strict_qualification_passed'] and read(out/'after-configuration.json')['expected_configuration'] and pagefile and mapped and dropped==0
r=dict(passed=bool(passed),strict_diagnostic_passed=bool(passed),ordinary_qualified=False,physical_qualified=False,events=events,cursor_events=cursor_events,pixels=sum(e['pixels'] for e in events+cursor_events),runtime_pins=len(trace['pins']),teardown_passed=teardown,pagefile_unchanged=pagefile,shared_events=shared,trace_records=count,dropped=dropped,cold_qualification=audit['strict_qualification_passed'],
 pins={n:sha(out/n) for n in ['trace.json','audit.json','closure.json','preflight.json','allocation.json','after-configuration.json','before-pagefile-map.json','after-pagefile-map.json']},verifier_sha256=sha(Path(__file__)),limits='104 raw framebuffer checkpoints cover two24bpp cursors, hiding, replacement and restored background; excludes alpha/animated cursors, ShowCursor counts, mode/crash or hardware/performance qualification.')
r['full_display_text_matched']=full_text;r['display_text_bytes']=sec.Misc_VirtualSize;r['module_header_observations']=trace.get('module_header_observations',{})
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','pixels','runtime_pins','teardown_passed','cold_qualification','full_display_text_matched']},indent=2))
