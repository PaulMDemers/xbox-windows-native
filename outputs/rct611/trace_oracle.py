from dib_oracle import decode_header,validate_headers
"""Independent trace structure, graphics ABI, output and arithmetic checks."""
from collections import Counter,defaultdict
NARGS={1:1,2:2,3:9,4:6,5:3,6:1,7:3,8:4,9:1,10:2,11:13,12:0,13:6,14:2,15:1,16:1}

def parse(text):
 lines=text.splitlines();assert lines and lines[-1].startswith('END ')
 stacks=defaultdict(list);calls={};bp={};modules={};caps=[];objects={};words={};outputs={};ends=[];totals=[];args={};dibs={};phase=0;phase_rows=[];pending_rows=[];phase_ends=[];cap_phases=[]
 generations={};bp_rows={};owners=set();codes={};retired=[];quiescent=None;pending_module=None;pending_bp=None;bp_stage=0
 for line in lines:
  p=line.split();kind=p[0];v=[int(x,16) for x in p[1:]] if kind not in ['LOAD','PROC','ORD'] else []
  if pending_module is not None:assert kind=='LIFETIME'
  if pending_bp is not None:assert kind==('BPOWNER' if bp_stage==0 else 'BPCODE')
  if quiescent is not None:assert kind in ['RETIRE','UNLOAD']
  if kind=='MODULE':
   base,size,stamp=v;assert base and size and base+size<=0xffffffff
   assert all(not m['active'] or base>=b+m['size'] or b>=base+size for b,m in modules.items())
   modules[base]=dict(size=size,stamp=stamp,active=True)
   pending_module=base
  elif kind=='LIFETIME':
   base,gen,size=v;assert base==pending_module and gen==len(generations)+1 and size==modules[base]['size']
   modules[base]['generation']=gen;generations[gen]=dict(base=base,size=size,active=True);pending_module=None
  elif kind=='BP':
   index,address,api,owner=v;assert index==len(bp_rows) and address not in bp and owner in modules
   assert modules[owner]['active'] and owner<=address<owner+modules[owner]['size'] and api in {0,*NARGS}
   bp[address]=(api,owner)
   bp_rows[index]=dict(address=address,api=api,owner=owner,generation=modules[owner]['generation'],retired=False)
   pending_bp=index;bp_stage=0
  elif kind=='BPOWNER':
   index,gen,reserved=v;assert index==pending_bp and gen==bp_rows[index]['generation'] and reserved==0 and index not in owners
   owners.add(index);bp_stage=1
  elif kind=='BPCODE':
   index,gen,byte=v;assert index==pending_bp and gen==bp_rows[index]['generation'] and 0<=byte<=255 and byte!=0xcc and index not in codes
   codes[index]=byte;pending_bp=None
  elif kind=='QUIESCENT':
   base,gen,reserved=v;assert quiescent is None and reserved==0 and modules[base]['active'] and modules[base]['generation']==gen
   assert not any(stacks.values());quiescent=(base,gen)
   assert all(r['api']==0 for r in bp_rows.values() if not r['retired'] and r['generation']==gen)
  elif kind=='RETIRE':
   index,gen,address=v;assert quiescent is not None and gen==quiescent[1]
   r=bp_rows[index];assert not r['retired'] and (r['generation'],r['address'],r['api'])==(gen,address,0)
   assert not any(stacks.values());r['retired']=True;del bp[address];retired.append(index)
  elif kind=='UNLOAD':
   base,a,b=v;gen=modules[base]['generation']
   assert a==b==0 and quiescent==(base,gen) and modules[base]['active'] and not any(o==base for api,o in bp.values())
   modules[base]['active']=False;generations[gen]['active']=False;quiescent=None
  elif kind=='CALL':
   ident,tid,api,ret,sp,a,b,target=v;assert ident==len(calls)+1 and api in NARGS and bp[target][0]==api
   assert tid and sp and bp[ret][0]==0 and (phase if api==11 else 0,api) not in [(cp,c[0]) for cp,c in zip(cap_phases,caps)]
   rsp=sp+4+(0 if api in [14,15,16] else NARGS[api]*4);assert rsp<=0xffffffff
   if stacks[tid]:assert rsp<=calls[stacks[tid][-1]]['sp']
   calls[ident]=dict(tid=tid,api=api,ret=ret,sp=sp,return_sp=rsp,a=a,b=b,target=target,phase=phase,generation=modules[bp[ret][1]]['generation'])
   stacks[tid].append(ident)
  elif kind=='ARGS':
   ident,count,*values=v;assert ident in calls and ident not in args
   c=calls[ident];assert count==len(values)==NARGS[c['api']]
   assert (values[0] if values else 0)==c['a'] and (values[1] if len(values)>1 else 0)==c['b']
   args[ident]=values
  elif kind=='RETURN':
   ident,tid,api,ret,sp,value=v;assert stacks[tid] and stacks[tid][-1]==ident and ident in args
   c=calls[ident];assert 'result' not in c and (tid,api,ret,sp)==(c['tid'],c['api'],c['ret'],c['return_sp'])
   c['result']=value;stacks[tid].pop()
  elif kind=='DIB':
   ident,address,status,count,stride,extent,*raw=v
   assert ident in calls and ident not in dibs and 'result' not in calls[ident]
   api=calls[ident]['api'];assert api in [4,11,15] and ident in args
   assert address==args[ident][{4:1,11:10,15:0}[api]]
   assert count==len(raw) and count in [0,1,10]
   expected=decode_header(address,raw,status)
   assert (status,stride,extent)==expected
   dibs[ident]=dict(address=address,status=status,raw=raw,stride=stride,extent=extent)
  elif kind=='OUTPUT_ABSENT':
   ident,api,address=v;assert ident in calls and ident not in outputs and api==calls[ident]['api']==4
   assert 'result' in calls[ident] and address==args[ident][3]==0
   outputs[ident]=None
  elif kind=='OUTPUT':
   ident,api,address,value=v;assert ident not in outputs and ident in calls
   c=calls[ident];assert c['api']==api and 'result' in c and api in [4,5,8]
   assert address==args[ident][{4:3,5:1,8:2}[api]] and address
   outputs[ident]=value
  elif kind=='OBJECT':
   ident,obj,vt,n=v;assert ident not in objects and outputs[ident]==obj and obj and vt
   assert calls[ident]['api'] in [5,8] and calls[ident]['result']&0x80000000==0
   assert n==({5:23,8:36}[calls[ident]['api']]);objects[ident]=(obj,vt,n)
  elif kind=='WORDS':
   ident,word_phase,address,n,*values=v;assert n==len(values) and n<=36 and ident in calls and (ident,word_phase) not in words
   words[ident,word_phase]=(address,values)
  elif kind=='CAP':
   api,count,address=v;assert api>=3 and count==32 and bp[address][0]==api and (phase if api==11 else 0,api) not in [(cp,c[0]) for cp,c in zip(cap_phases,caps)]
   assert sum(c['api']==api and (api!=11 or c['phase']==phase) for c in calls.values())==32
   caps.append(tuple(v));cap_phases.append(phase if api==11 else 0)
  elif kind=='PHASE_PENDING':
   old,pending,seen=v;assert phase==old==0 and not pending_rows
   assert pending==sum(len(x) for x in stacks.values()) and pending>0
   assert seen==sum(c['api']==11 for c in calls.values())
   pending_rows.append(v)
  elif kind=='PHASE':
   new,seen,skipped=v;assert phase==0 and new==1 and not phase_rows and not any(stacks.values())
   assert seen==sum(c['api']==11 for c in calls.values()) and seen<=32
   phase=1;phase_rows.append(v)
  elif kind=='PHASE_END':
   assert not any(stacks.values()) and v[0]==phase;phase_ends.append(v)
  elif kind=='STALE':
   tid,address,sp=v;assert bp[address][0]==0 and not any(calls[i]['ret']==address for i in stacks[tid])
  elif kind=='TOTAL':totals.append(v)
  elif kind=='END':ends.append(v)
  elif kind in ['LOAD','PROC','ORD']:
   assert len(p)==5
   int(p[1],16);int(p[2],16);int(p[3],16)
   if kind=='ORD':int(p[4],16)
   else:bytes.fromhex(p[4]).decode('ascii')
  else:assert kind in ['ARM','IMAGE','THREAD','DLL'],line
 assert pending_module is None and pending_bp is None and quiescent is None and len(owners)==len(codes)==len(bp_rows)
 assert len(ends)==1 and ends[0]==[0,len(calls),0] and totals==[[len(calls),len(calls),len(bp_rows)]]
 assert calls and all('result' in c for c in calls.values()) and not any(stacks.values()) and len(args)==len(calls)
 for ident,c in calls.items():
  api=c['api'];value=c['result']
  if api in [4,11,15]:assert ident in dibs
  if api in [4,5,8]:assert ident in outputs
  if api==4 and value and args[ident][3]:assert outputs[ident]
  if api in [5,8] and not value&0x80000000:
   assert ident in objects and (ident,2) in words
   obj,vt,n=objects[ident];addr,table=words[ident,2];assert addr==vt and len(table)==n
   expected={2:6,20:7,6:8} if api==5 else {2:9,22:10,5:13}
   for slot,method in expected.items():assert bp[table[slot]][0]==method
  if api==8:
   address,desc=words[ident,0];assert address==args[ident][1] and len(desc)==27 and desc[0]==108
  if api==10 and not value&0x80000000:
   address,desc=words[ident,1];assert address==args[ident][1] and len(desc)==27 and desc[0]==108
 assert len(phase_ends)==1
 return dict(calls=calls,args=args,bp=bp,modules=modules,caps=caps,objects=objects,words=words,outputs=outputs,dibs=dibs,phase_rows=phase_rows,pending_rows=pending_rows,phase_ends=phase_ends,cap_phases=cap_phases,generations=generations,bp_rows=bp_rows,codes=codes,retired=retired)

def validate(text,base,size):
 r=parse(text);calls=r['calls'];args=r['args'];main={i:c for i,c in calls.items() if base<=c['ret']<base+size}
 groups=defaultdict(list)
 for i,c in main.items():groups[c['api']].append((i,c))
 # Recursive calls inside the original DLL do not have a main-image caller.
 probe=[c for c in calls.values() if c['api']==14];assert len(probe)==20
 assert len({c['tid'] for c in probe})==2
 for c in probe:
  d,s=c['a'],c['b'];assert d<=3 and c['result']==(((s+d)^0x601abcde)+d*(d+1)//2)&0xffffffff
 assert len(groups[3])==32 and groups[3][0][1]['result']==0
 assert all(c['result']!=0 for _,c in groups[3][1:]) and [c[0] for c in r['caps']]==[3,11,11] and r['cap_phases']==[0,0,1]
 for i,c in groups[3]:
  assert args[i][1:5]==[0,0,8,8] and args[i][6:]==[0,0,0xcc0020]
 assert len(groups[4])==8 and [bool(c['result']) for _,c in groups[4]]==[False,True,True,True,True,True,True,False]
 assert r['outputs'][groups[4][0][0]]==0
 assert all(r['outputs'][i] is None and args[i][3]==0 for i,c in groups[4][-3:])
 assert len(groups[11])==64 and all(c['result']==8 for _,c in groups[11])
 assert len(groups[5])==2
 assert groups[5][0][1]['result']&0x80000000 and r['outputs'][groups[5][0][0]]==0
 assert groups[5][1][1]['result']==0
 for api in [6,7,8,9,10,13]:assert len(groups[api])==1
 for api in [7,8,10,13]:assert groups[api][0][1]['result']==0
 dd=r['objects'][groups[5][1][0]][0];surface=r['objects'][groups[8][0][0]][0]
 for api in [6,7,8]:assert args[groups[api][0][0]][0]==dd
 for api in [9,10,13]:assert args[groups[api][0][0]][0]==surface
 got=r['words'][groups[10][0][0],1][1];assert got[2:4]==[8,8] and got[26]&0x800
 validate_headers(r)
 assert len(groups[16])==1 and groups[16][0][1]['result']==0x605face0
 assert r['phase_rows']==[[1,32,4]] and r['pending_rows']==[[0,1,32]] and r['phase_ends']==[[1,4,4]]
 assert [sum(c['phase']==p for _,c in groups[11]) for p in [0,1]]==[32,32]
 return dict(passed=True,phase_rows=r['phase_rows'],pending_rows=r['pending_rows'],phase_ends=r['phase_ends'],stretch_samples_per_phase=[32,32],header_records=len(r['dibs']),header_statuses=[d['status'] for d in r['dibs'].values()],total_pairs=len(calls),main_call_counts={str(a):len(v) for a,v in groups.items()},
  probe_invocations=20,bitblt_recorded=32,bitblt_sample_limit=32,bitblt_failed=1,
  stretch_returned_scanlines=8,dd_create_failed_hresult=groups[5][0][1]['result'],
  returned_surface_width=got[3],returned_surface_height=got[2],returned_surface_caps=got[26],
  returned_surface_bpp=got[21],modules=len(r['modules']),breakpoint_sites=len(r['bp']),
  lifetime=validate_lifetime610(r),scope='Original NT5 control only. Trace limited to32 entries per graphics API. Not game FPS or Xbox acceleration.')

def validate_lifetime610(r):
 gs=[(g,m) for g,m in r['generations'].items() if m['base']==0x62000000]
 assert len(gs)==3 and all(not m['active'] for g,m in gs)
 sites=[];code=[]
 for g,m in gs:
  rows=[(i,b) for i,b in r['bp_rows'].items() if b['generation']==g]
  assert len(rows)==1
  i,b=rows[0];assert b['retired'] and b['api']==0 and i in r['retired']
  calls=[c for c in r['calls'].values() if c['generation']==g]
  assert len(calls)==1 and calls[0]['api']==2 and calls[0]['ret']==b['address'] and calls[0]['result']
  sites.append(b['address']);code.append(r['codes'][i])
 assert len(set(sites))==1 and code==[0x90,0xf8,0x90]
 return dict(passed=True,generations=[g for g,m in gs],base=0x62000000,return_address=sites[0],original_bytes=code,retirements=3)
