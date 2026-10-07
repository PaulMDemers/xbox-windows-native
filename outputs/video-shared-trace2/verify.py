"""Validate paired runtime calls, complete resident text and present framebuffer aliases."""
import hashlib,json,struct,sys
from pathlib import Path
from walk import read_virtual,physical
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'trace002'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');a=read(out/'audit.json');s=read(k/'alias-scan.json');sites=read(k/'sites.json')
assert t['status']=='desktop_snapshot_captured' and t['guest_resumed'] and not t['armed_breakpoints_remaining'] and not t.get('error')
assert a['strict_qualification_passed'] and a['debugger'] and not a['ordinary_qualified']
assert s['passed'] and s['trace_sha256']==sha(out/'trace.json') and s['walker_sha256']==sha(k/'walk.py')
raw=Path(t['private_memory']);assert sha(raw)==s['snapshot_sha256']==t['private_memory_sha256'];data=raw.read_bytes();cr3=t['control_registers']['CR3']
for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
for pin in t['runtime_pins']:
 mod=sites['modules'][pin['module']];assert sha(Path(mod['path']))==mod['sha256'];p=pefile.PE(mod['path']);b=bytearray(p.get_data(pin['rva'],len(bytes.fromhex(pin['raw']))));assert b.hex()==pin['raw']
 for off in pin['relocations']:struct.pack_into('<I',b,off,(struct.unpack_from('<I',b,off)[0]+pin['base']-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 assert b.hex()==pin['resident'] and read_virtual(data,cr3,pin['address'],len(b))==b
for name in ['bootvid.dll','xboxvnt5.sys']:
 p=pefile.PE(sites['modules'][name]['path']);sec=next(v for v in p.sections if v.Name.rstrip(b'\0')==b'.text');covered=set()
 for pin in t['runtime_pins']:
  if pin['module']==name:covered.update(range(pin['rva'],pin['rva']+len(bytes.fromhex(pin['raw']))))
 assert set(range(sec.VirtualAddress,sec.VirtualAddress+sec.Misc_VirtualSize))<=covered
calls=t['calls'];rets={v['call_id']:v for v in t['returns']};assert len(calls)==len(rets)
for c in calls:
 v=rets[c['id']];assert (v['thread'],v['esp'],v['eip'],v['caller'])==(c['thread'],c['esp']+4+4*c['argc'],c['return_address'],c['caller'])
def one(name):
 rows=[v for v in calls if v['name']==name];assert len(rows)==1,(name,len(rows));return rows[0]
pub=one('XwnFbPublish');acq=one('XwnFbAcquire');check=one('InbvCheckDisplayOwnership');mapping=one('MmMapIoSpace')
assert not any(v['name']=='MmMapVideoDisplay' for v in calls)
view=t['published_view'];g=t['provider_globals']
assert view==pub['view']==rets[acq['id']]['view']
assert rets[pub['id']]['value']&255==1 and rets[acq['id']]['value']==0 and rets[check['id']]['value']&255==0
assert mapping['args']==[0x03c00000,0,0x400000,0] and rets[mapping['id']]['value']==view[2]==g['_FrameBufferStart']
assert pub['id']<acq['id']<check['id'] and any(pub['id']<v['id']<acq['id'] for v in calls if v['name']=='InbvNotifyDisplayOwnershipLost')
assert view[:2]==[44,1] and view[3:]==[0x03c00000,0x400000,1024*576*4,1024,576,4096,3878144,0]
assert g['_Ready']==1 and g['_References']==1 and g['_Owner']==acq['args'][0]
assert physical(data,cr3,g['_FrameBufferStart'])==0x03c00000 and physical(data,cr3,g['_BackBuffer'])==0x03c00000+view[9]
rows=[]
for d in s['directories']:
 assert len(d['ranges'])==1 and len(d['matches'])==1024
 region=d['ranges'][0];assert region['virtual']==view[2] and region['physical']==0x03c00000 and region['length']==0x400000
 assert all(v['page_bytes']==4096 and v['pcd'] and v['pwt'] and not v['pat'] and not v['user'] for v in d['matches'])
 rows.append({n:d[n] for n in ['root','pdes_examined','ptes_examined','ranges','processes','directory_sha256']})
before,after=[read(out/(phase+'-pagefile-map.json')) for phase in ['before','after']];assert before['clusters']==after['clusters'] and before['whole_file']==after['whole_file']
assert all(read(out/(phase+'-configuration.json'))['expected_configuration'] for phase in ['before','after'])
r=dict(passed=True,physical_access=False,ordinary_qualified=False,calls=[dict(id=v['id'],name=v['name'],return_value=rets[v['id']]['value']) for v in calls],runtime_pins=len(t['runtime_pins']),stops=t['stops'],published_view=view,provider_globals=g,process_count=len(s['processes']),directory_count=len(rows),directories=rows,evidence={n:sha(k/n) for n in ['sites.json','trace002/trace.json','trace002/audit.json','trace002/closure.json','alias-scan.json']},limits='Current linked active roots and current root, present mappings only. No TLB, MSR, inactive/future process or generic PnP lifetime proof; requested cache type0 and PCD/PWT1/PAT0 retained. No performance/physical qualification.')
dest=k/'verification.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','runtime_pins','stops','process_count','directory_count','calls']},indent=2))
