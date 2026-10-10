"""Independent closed225 raw code/state review; observation never grants ownership."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'trace001';dest=k/'evidence-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
iv=read(k/'inventory002.json');trace=read(out/'trace.json');audit=read(out/'audit.json');host=read(out/'host-state.json')
assert host['closed'] and read(out/'closure.json')['closed'] and trace['closed']
assert trace.get('guest_resumed') and not trace['remaining_breakpoints'] and not trace.get('breakpoint_cleanup_errors')
assert trace['debugger_memory_writes'] is False and not trace['gpu_ownership_qualified']
for name,h in read(k/'emulator-frozen.json').items():assert sha(ws/name)==h,name
assert trace['passed'] and audit['handoff_scope_passed'] and not audit['ordinary_qualified']
raw=(ws/iv['binaries']['image-crom.bin']['path']).read_bytes();loader=(ws/iv['binaries']['freeldr.sys']['path']).read_bytes()
labels=list(iv['sites']);assert [v['label'] for v in trace['events']]==labels and len(trace['pins'])==5
for row in trace['pins']:
 a=row['address'];expected=(loader[a-0x200000:a-0x200000+64] if row['label']=='freeldr_entry' else raw[a-0x03a00000:a-0x03a00000+64])
 assert bytes.fromhex(row['hex'])==expected and hashlib.sha256(expected).hexdigest()==row['sha256']
states=[];raw_bytes=0
for v in trace['events']:
 assert v['registers']['EIP']==iv['sites'][v['label']] and v['gpu_register_reads']==26
 assert not v['cpu']['CR0']&0x80000000
 blobs={}
 for row in v['artifacts']:
  p=ws/row['path'];data=p.read_bytes();assert len(data)==row['bytes'] and sha(p)==row['sha256'];blobs[row['address']]=data;raw_bytes+=len(data)
 assert set(blobs)=={0xfd710000,0x03feb000} and len(blobs[0xfd710000])==0x5000 and len(blobs[0x03feb000])==0x15000
 gpu=v['gpu_registers']
 ht=gpu['NV_PFIFO_RAMHT'];base=((ht&0x1f0)>>4)<<12;size=1<<(((ht&0x30000)>>16)+12)
 captured=base>=0x10000 and base+size<=0x15000
 entries=[]
 if captured:
  data=blobs[0xfd710000][base-0x10000:base-0x10000+size]
  for at in range(0,len(data),8):
   handle,context=struct.unpack_from('<II',data,at)
   if context&0x80000000:
    instance=(context&0xffff)<<4
    entry=dict(slot=at//8,handle=handle,context=context,channel=(context>>24)&31,engine=(context>>16)&3,instance=instance,descriptor_captured=0x10000<=instance<=0x15000-16)
    if entry['descriptor_captured']:entry['descriptor_words']=list(struct.unpack_from('<4I',blobs[0xfd710000],instance-0x10000))
    entries.append(entry)
 state=dict(label=v['label'],pfifo_channel=gpu['NV_PFIFO_CACHE1_PUSH1']&31,pgraph_channel=(gpu['NV_PGRAPH_CTX_USER']>>24)&31,current_context_valid=bool(gpu['NV_PGRAPH_CTX_CONTROL']&0x10000),hardware_switch_enabled=bool(gpu['NV_PGRAPH_DEBUG_3']&4),ramht=dict(raw=ht,base=base,bytes=size,fully_captured=captured,valid_entries=entries),ramfc_raw=gpu['NV_PFIFO_RAMFC'],ramro_raw=gpu['NV_PFIFO_RAMRO'],ramin_sha256=hashlib.sha256(blobs[0xfd710000]).hexdigest(),tail_sha256=hashlib.sha256(blobs[0x03feb000]).hexdigest())
 states.append(state)
changes=[]
for a,b in zip(trace['events'],trace['events'][1:]):
 delta=[dict(name=n,before=a['gpu_registers'][n],after=b['gpu_registers'][n]) for n in a['gpu_registers'] if a['gpu_registers'][n]!=b['gpu_registers'][n]]
 changes.append(dict(before=a['label'],after=b['label'],register_delta=delta,ramin_changed=states[a['index']]['ramin_sha256']!=states[b['index']]['ramin_sha256'],tail_changed=states[a['index']]['tail_sha256']!=states[b['index']]['tail_sha256']))
assert trace['events'][0]['uploaded_loader_pin']['sha256']==iv['binaries']['freeldr.sys']['sha256']
assert trace['events'][3]['copied_loader_sha256']==iv['binaries']['freeldr.sys']['sha256']
assert trace['events'][3]['multiboot_info']==trace['events'][4]['multiboot_info']
for v in trace['events'][2:]:assert not v['registers']['EFL']&0x200
r=dict(passed=True,scope=__doc__,source_sha256=sha(Path(__file__)),trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'),inventory_sha256=sha(k/'inventory002.json'),raw_bytes_verified=raw_bytes,actual_code_pins=5,gpu_register_reads=130,states=states,transitions=changes,debugger=True,ordinary_qualified=False,physical_qualified=False,gpu_ownership_qualified=False,limits='Bounded captured RAMHT decode is existing firmware state, never an allocator grant. RAMFC/RAMRO structure/unsampled instance ranges and backend references remain unresolved. CPU off/empty registers do not establish full GPU drain; source census does not enumerate every possible consumer.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('225 independent handoff evidence verified',raw_bytes,'raw bytes')
