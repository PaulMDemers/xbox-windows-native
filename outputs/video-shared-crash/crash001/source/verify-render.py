"""Verify retained shared pointer and resident crash renderer independently of screen appearance."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash001'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'video-shared-trace2'));from walk import read_virtual,physical
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');a=read(out/'audit.json');v=read(k/'verification.json');d=read(k/'payload-verification.json')
assert v['dump_write_qualified'] and d['passed'] and a['integrity_passed']
assert t['status']=='dump_return_observed' and t['guest_resumed'] and not t['armed_breakpoints_remaining']
assert t['boot_before']==t['boot_after'];g=t['boot_after']['globals'];view=t['boot_after']['published']
assert g['_Ready']==1 and g['_References']==1 and g['_Owner']!=0 and g['_FrameBufferStart']==view[2]
assert view[:2]==[44,1] and view[3:]==[0x03c00000,0x400000,1024*576*4,1024,576,4096,3878144,0]
render=[e for e in t['events'] if e['kind']=='bootvid_render_entry'];assert render
assert any(e['function']=='VidDisplayString' for e in render)
assert all(e['state']==t['boot_before'] for e in render)
raw=Path(t['private_memory']);assert sha(raw)==t['private_memory_sha256'];ram=raw.read_bytes();assert len(ram)==67108864
cr=t['control_registers'];assert cr['CR0']&0x80000000 and not cr['CR4']&0x20
assert physical(ram,cr['CR3'],view[2])==view[3]
info=read(k/'video-sites.json')['modules']['bootvid.dll'];p=pefile.PE(info['path']);assert sha(Path(info['path']))==info['sha256']
base=next(v['base'] for v in t['module_list'] if v['name'].lower()=='bootvid.dll');sec=next(v for v in p.sections if v.Name.rstrip(b'\0')==b'.text')
code=bytearray(p.get_data(sec.VirtualAddress,sec.Misc_VirtualSize))
for block in p.DIRECTORY_ENTRY_BASERELOC:
 for e in block.entries:
  if e.type==3 and sec.VirtualAddress<=e.rva<sec.VirtualAddress+len(code):
   offset=e.rva-sec.VirtualAddress;assert offset+4<=len(code);struct.pack_into('<I',code,offset,(struct.unpack_from('<I',code,offset)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
assert read_virtual(ram,cr['CR3'],base+sec.VirtualAddress,len(code))==code
for n,value in g.items():assert struct.unpack('<I',read_virtual(ram,cr['CR3'],base+info['symbols'][n],4))[0]==value
assert list(struct.unpack('<11I',read_virtual(ram,cr['CR3'],base+info['symbols']['_Published'],44)))==view
assert read_virtual(ram,cr['CR3'],view[2],65536)==ram[0x3c00000:0x3c10000]
assert (out/'artifacts/crash.png').exists() and read(out/'launch.json')['capture_exit']==0
r=dict(passed=True,physical_access=False,ordinary_qualified=False,recovery_qualified=False,shared_framebuffer_retained=True,pointer=hex(view[2]),references=g['_References'],observed_render_functions=[e['function'] for e in render],bootvid_sha256=info['sha256'],resident_text_bytes=len(code),resident_text_sha256=hashlib.sha256(code).hexdigest(),crash_screen_sha256=sha(out/'artifacts/crash.png'),framebuffer_at_dump_return_sha256=hashlib.sha256(ram[0x3c00000:0x4000000]).hexdigest(),dump_payload_bytes=d['total_payload_bytes'],evidence={n:sha(k/n) for n in ['verification.json','payload-verification.json','crash001/trace.json','crash001/audit.json','crash001/closure.json']},limits='One controlled crash after desktop acquired the mapping. Does not cover arbitrary crash timing, provider-lock interruption, PnP remove, WC/cache transitions, physical hardware or recovery of this new crash disk. Screen appearance requires separate visual review.')
dest=k/'render-verification.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
