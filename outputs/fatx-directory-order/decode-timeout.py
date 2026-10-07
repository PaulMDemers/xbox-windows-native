"""Offline-only analysis of the retained post-timeout snapshot. No monitor access."""
import hashlib,json,pathlib,re,struct,sys
k=pathlib.Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['001','002']
caseout=k/case;out=k.parent/'native-windows-nt5-kernel'
snapshot=caseout/'timeout-memory.json'
if len(sys.argv)>2:
 assert len(sys.argv)==5 and sys.argv[2]=='--snapshot' and sys.argv[4]=='--replay-only'
 snapshot=pathlib.Path(sys.argv[3]).resolve();assert snapshot.name=='timeout-memory.json'
meta=json.loads(snapshot.read_text());raw=snapshot.parent/'artifacts/timeout.ram'
data=raw.read_bytes();assert len(data)==67108864 and hashlib.sha256(data).hexdigest()==meta['raw_sha256']
regs=meta['registers'];report={'scope':__doc__,'physical_access':False,'raw_sha256':meta['raw_sha256'],'snapshot_metadata':str(snapshot),'decoder_replay_only':len(sys.argv)>2}
# Process/module decoding derived from capture-threads.py SHA256 b11ca4dc119a1698c406f380d6800121c61b4f1d95e4597ecb2dd7434cde1aed
cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',regs)[1],16)
def phys32(a):return struct.unpack_from('<I',data,a)[0]
def pa(va):
 pde=phys32((cr3&0xfffff000)+4*(va>>22));assert pde&1
 if pde&128:return (pde&0xffc00000)+(va&0x3fffff)
 pte=phys32((pde&0xfffff000)+4*((va>>12)&1023));assert pte&1
 return (pte&0xfffff000)+(va&4095)
def read(va,size):
 result=b''
 while size:
  at=pa(va);n=min(size,4096-(va&4095));assert at+n<=len(data)
  result+=data[at:at+n];va+=n;size-=n
 return result
def u32(a):return struct.unpack('<I',read(a,4))[0]
candidates=[]
for pos in range(0,len(data)-4096,4096):
 if data[pos:pos+2]!=b'MZ':continue
 offset=phys32(pos+60)
 if offset>4096 or data[pos+offset:pos+offset+4]!=b'PE\0\0':continue
 if phys32(pos+offset+8)==0x4b7a1bd5:candidates.append(pos)
pubs=json.loads((out/'kernel-publics.json').read_text())['symbols'];valid=[]
for page in range(0x80000,0xc0000):
 va=page*4096
 try:
  if pa(va) not in candidates:continue
  node=u32(va+pubs['_PsLoadedModuleList']['rva'])
  if u32(node+24)==va:valid.append(va)
 except (AssertionError,struct.error):pass
assert len(valid)==1,('kernel mapping candidates',valid)
base=valid[0];report['kernel_base']=hex(base)
modules=[];head=base+pubs['_PsLoadedModuleList']['rva'];link=u32(head);seen=set()
while link!=head and link not in seen and len(seen)<256:
 seen.add(link);module_base,entry,size=struct.unpack('<III',read(link+24,12))
 length,maximum,buffer=struct.unpack('<HHI',read(link+44,8));assert length<=maximum and length<1024
 modules.append({'name':read(buffer,length).decode('utf-16le') if length else '', 'base':hex(module_base),'entry':hex(entry),'size':size})
 link=u32(link)
assert link==head;report['modules']=modules
if '_KiBugCheckData' in pubs:
 report['bugcheck_data']=[hex(v) for v in struct.unpack('<5I',read(base+pubs['_KiBugCheckData']['rva'],20))]
fields=json.loads((out/'process-layouts.json').read_text())['_EPROCESS']['fields']
head=base+pubs['_PsActiveProcessHead']['rva'];link=u32(head);seen=set();processes=[]
while link!=head and link not in seen and len(seen)<128:
 seen.add(link);process=link-fields['ActiveProcessLinks']['offset']
 processes.append({'eprocess':hex(process),'pid':u32(process+fields['UniqueProcessId']['offset']),'image':read(process+fields['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace')})
 threads=[];th=process+fields['ThreadListHead']['offset'];tl=u32(th);ts=set()
 while tl!=th and tl not in ts and len(ts)<200:
  ts.add(tl);t=tl-576;stack=u32(t+40);top=u32(t+24);words=[]
  try:
   for at in range(stack,min(top,stack+4096),4):
    value=u32(at)
    for mod in modules:
     mb=int(mod['base'],16)
     if mb<=value<mb+mod['size']:
      label=mod['name']+'+'+hex(value-mb)
      if mb==base:
       possible=[(value-mb-v['rva'],k) for k,v in pubs.items() if 0<=value-mb-v['rva']<4096]
       if possible:
        distance,name=min(possible);label=name+'+'+hex(distance)
      words.append({'stack':hex(at),'value':hex(value),'candidate':label})
  except (AssertionError,struct.error):pass
  threads.append({'thread':hex(t),'tid':u32(t+484),'state':read(t+45,1)[0],'wait_reason':read(t+87,1)[0],'stack':hex(stack),'initial_stack':hex(top),'stack_code_candidates':words})
  tl=u32(tl)
 processes[-1]['threads']=threads
 link=u32(link)
assert link==head;report['processes']=processes
fields=json.loads((out/'pnp-layouts.json').read_text())['_DEVICE_NODE']['fields']
def field(n,f):return u32(n+fields[f]['offset'])
def uni(n,f):
 length,maximum,buffer=struct.unpack('<HHI',read(n+fields[f]['offset'],8));assert length<=maximum and length<=2048
 return read(buffer,length).decode('utf-16le') if length else ''
pending=[u32(base+pubs['_IopRootDeviceNode']['rva'])];seen=set();nodes=[]
while pending and len(seen)<256:
 n=pending.pop()
 if not n or n in seen:continue
 seen.add(n);nodes.append({'InstancePath':uni(n,'InstancePath'),'ServiceName':uni(n,'ServiceName'),'Problem':field(n,'Problem'),'FailureStatus':hex(field(n,'FailureStatus'))})
 pending.extend([field(n,'Sibling'),field(n,'Child')])
report['pnp_tree']=nodes
report['tick_count']=u32(base+pubs['_KeTickCount']['rva'])
if '_MmNumberOfPhysicalPages' in pubs:report['physical_pages']=u32(base+pubs['_MmNumberOfPhysicalPages']['rva'])
report['status']='shell_running' if any(p['image'].lower()=='explorer.exe' for p in processes) else 'kernel_running'
if report.get('bugcheck_data',['0x0'])[0]!='0x0':report['status']='bugcheck_reported'
# Read user parameters through each process's own address space. Nonresident is unknown.
process_layout=json.loads((out/'process-layouts.json').read_text())
ef=process_layout['_EPROCESS']['fields'];kf=process_layout['_KPROCESS']['fields']
for process in processes:
 saved_cr3=cr3
 try:
  ep=int(process['eprocess'],16);peb=u32(ep+ef['Peb']['offset'])
  target_cr3=u32(ep+ef['Pcb']['offset']+kf['DirectoryTableBase']['offset'])
  assert 0x10000<=peb<0x80000000
  cr3=target_cr3
  params=u32(peb+0x10);assert 0x10000<=params<0x80000000
  flags=u32(params+8);length,maximum,buffer=struct.unpack('<HHI',read(params+0x40,8))
  assert length<=maximum and length<=4096 and length%2==0
  if not flags&1 and buffer:buffer+=params
  assert not length or 0x10000<=buffer<0x80000000-length
  process['command_line']=read(buffer,length).decode('utf-16le') if length else ''
  if 'xwnidle' in process['command_line'].lower() and process['image'].lower()=='concurrent.exe':
   # Never interpret another helper's globals at these addresses.
   symbols=json.loads((k/'probe-symbols.json').read_text())
   binary=(k/'artifacts/probe.exe').read_bytes()
   assert hashlib.sha256(binary).hexdigest()==symbols['probe_sha256']
   image_base=u32(peb+8);assert image_base==symbols['preferred_base']
   section=symbols['text']
   assert hashlib.sha256(read(image_base+section['rva'],section['raw_size'])).hexdigest()==section['sha256']
   process['diagnostic_counters']={name:list(struct.unpack('<5I',read(image_base+symbols['symbols'][name],20))) for name in ['_Completed','_Errors']}
   process['diagnostic_binary_sha256']=symbols['probe_sha256']
 except (AssertionError,struct.error,UnicodeError) as error:process['command_unknown']=type(error).__name__
 finally:cr3=saved_cr3
# Resolve wait-block object pointers against the kernel's registered ERESOURCE list.
# Inline exclusive ownership only; shared owner tables are not guessed.
layouts=json.loads((out/'thread-layouts.json').read_text())
waitoff=layouts['_KTHREAD']['fields']['WaitBlockList']['offset']
bf=layouts['_KWAIT_BLOCK']['fields'];resources=[]
resource_layout=json.loads((k/'kernel-resource-layouts.json').read_text())
assert resource_layout['pdb_sha256']==json.loads((out/'kernel-publics.json').read_text())['pdb_sha256']
rf=resource_layout['_ERESOURCE']['fields']
assert resource_layout['_ERESOURCE']['size']==56
assert all(rf[n]['offset']==v for n,v in {'OwnerTable':8,'ActiveCount':12,'Flag':14,'SharedWaiters':16,'ExclusiveWaiters':20,'OwnerThreads':24,'NumberOfSharedWaiters':44,'NumberOfExclusiveWaiters':46}.items())
head=base+pubs['_ExpSystemResourcesList']['rva'];link=u32(head);seen=set()
while link!=head and link not in seen and len(seen)<16384:
 seen.add(link);active,flags=struct.unpack('<hH',read(link+12,4));owners=[]
 for at in [24,32]:
  thread,count=struct.unpack('<Ii',read(link+at,8));owners.append({'thread':hex(thread),'count':count})
 shared,exclusive=struct.unpack('<HH',read(link+44,4))
 resources.append(dict(address=hex(link),active_count=active,flags=hex(flags),owner_table=hex(u32(link+8)),owners=owners,shared_object=hex(u32(link+16)),exclusive_object=hex(u32(link+20)),shared_waiters=shared,exclusive_waiters=exclusive))
 link=u32(link)
assert link==head;report['resource_count']=len(resources)
report['contended_resources']=[r for r in resources if r['shared_waiters'] or r['exclusive_waiters']]
waits=[]
for process in processes:
 for thread in process['threads']:
  if thread['state']!=5:continue
  t=int(thread['thread'],16);wb=u32(t+waitoff);visited=set()
  while wb and wb not in visited and len(visited)<16:
   visited.add(wb)
   try:
    obj=u32(wb+bf['Object']['offset']);owner=u32(wb+bf['Thread']['offset'])
    if owner!=t:break
    for resource in resources:
     if obj and hex(obj) in [resource['exclusive_object'],resource['shared_object']]:
      waits.append(dict(process=process['image'],thread=hex(t),tid=thread['tid'],object=hex(obj),resource=resource,wait_block=hex(wb)))
    wb=u32(wb+bf['NextWaitBlock']['offset'])
   except (AssertionError,struct.error):break
report['resource_waits']=waits
# Label filesystem resources using offsets compiled from the exact0098 source/flags.
layout=json.loads((k/'fatx-layouts.json').read_text());offset=layout['offsets']
fixture=json.loads((k/('fixture-'+case+'.json')).read_text())
assert fixture['fatx_sha256']==layout['driver_sha256']
fatx=next(m for m in modules if m['name'].lower()=='xwnfatx.sys')
global_data=u32(int(fatx['base'],16)+layout['global_pointer_rva'])
volume_head=global_data+offset['global_volume_list'];vl=u32(volume_head);volumes=set();labels={}
while vl!=volume_head and vl not in volumes and len(volumes)<64:
 volumes.add(vl);vcb=vl-offset['vcb_volume_link']
 for name in ['dir','fat']:labels[hex(vcb+offset['vcb_'+name+'_resource'])]=dict(kind=name,vcb=hex(vcb))
 fh=vcb+offset['vcb_fcb_list'];fl=u32(fh);fcbs=set()
 while fl!=fh and fl not in fcbs and len(fcbs)<65536:
  fcbs.add(fl);fcb=fl-offset['fcb_link']
  details=dict(vcb=hex(vcb),fcb=hex(fcb),flags=hex(u32(fcb+offset['fcb_flags'])),refcount=u32(fcb+offset['fcb_refcount']))
  try:
   length,maximum,buffer=struct.unpack('<HHI',read(fcb+offset['fcb_path'],8));assert length<=maximum and length<=2048 and length%2==0
   details['path']=read(buffer,length).decode('utf-16le') if length else ''
  except (AssertionError,struct.error,UnicodeError):details['path_unknown']=True
  for name in ['main','paging']:labels[hex(fcb+offset['fcb_'+name+'_resource'])]=dict(details,kind=name)
  fl=u32(fl)
 assert fl==fh,'FCB list incomplete'
 vl=u32(vl)
assert vl==volume_head,'Volume list incomplete'
thread_index={t['thread']:dict(process=p['image'],pid=p['pid'],tid=t['tid'],state=t['state'],wait_reason=t['wait_reason']) for p in processes for t in p['threads']}
for resource in resources:
 if resource['address'] in labels:resource['fatx']=labels[resource['address']]
 for owner in resource['owners']:
  if owner['count']>0:owner['active_thread']=thread_index.get(owner['thread'],'not_in_active_thread_list')
report['fatx_volume_count']=len(volumes)
report['fatx_resource_labels']=len(labels)
report['fatx_contended_resources']=[r for r in resources if 'fatx' in r and (r['shared_waiters'] or r['exclusive_waiters'])]

edges=[]
for wait in waits:
 r=wait['resource']
 if int(r['flags'],16)&128 and r['active_count']>0:
  owner=r['owners'][0]
  if owner['count']>0 and owner['thread']!='0x0':edges.append(dict(waiter=wait['thread'],owner=owner['thread'],resource=r['address']))
report['exclusive_wait_edges']=edges
cycles=[]
def visit(origin,current,path):
 for edge in edges:
  if edge['waiter']!=current:continue
  if edge['owner']==origin:cycles.append(path+[edge]);continue
  if edge['owner'] not in [e['waiter'] for e in path] and len(path)<16:visit(origin,edge['owner'],path+[edge])
for edge in edges:visit(edge['waiter'],edge['waiter'],[])
report['exclusive_cycles']=cycles
report['limits']='Stack entries are code candidates, not an unwind. Shared-owner tables and other synchronization types are not decoded. Empty exclusive_cycles does not exclude a deadlock.'
target=(k/'decoder-replay.json') if len(sys.argv)>2 else caseout/'timeout-analysis.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({n:report[n] for n in ['status','resource_count','exclusive_wait_edges','exclusive_cycles']},indent=2))
