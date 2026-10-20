from dib_oracle import decode_header,validate_headers
"""Independent trace structure, graphics ABI, output and arithmetic checks."""
from collections import Counter,defaultdict
NARGS={1:1,2:2,3:9,4:6,5:3,6:1,7:3,8:4,9:1,10:2,11:13,12:0,13:6,14:2,15:1}

def parse(text):
 lines=text.splitlines();assert lines and lines[-1].startswith('END ')
 stacks=defaultdict(list);calls={};bp={};modules={};caps=[];objects={};words={};outputs={};ends=[];totals=[];args={};dibs={}
 for line in lines:
  p=line.split();kind=p[0];v=[int(x,16) for x in p[1:]] if kind not in ['LOAD','PROC','ORD'] else []
  if kind=='MODULE':
   base,size,stamp=v;assert base and size and base+size<=0x100000000 and base not in modules
   modules[base]=dict(size=size,stamp=stamp,active=True)
  elif kind=='BP':
   index,address,api,owner=v;assert index==len(bp) and address not in bp and owner in modules
   assert modules[owner]['active'] and owner<=address<owner+modules[owner]['size'] and api in {0,*NARGS}
   bp[address]=(api,owner)
  elif kind=='UNLOAD':
   base,_,_=v;assert modules[base]['active'] and not any(o==base for a,o in bp.values());modules[base]['active']=False
  elif kind=='CALL':
   ident,tid,api,ret,sp,a,b,target=v;assert ident==len(calls)+1 and api in NARGS and bp[target][0]==api
   assert tid and sp and bp[ret][0]==0 and api not in [c[0] for c in caps]
   rsp=sp+4+(0 if api in [14,15] else NARGS[api]*4);assert rsp<=0xffffffff
   if stacks[tid]:assert rsp<=calls[stacks[tid][-1]]['sp']
   calls[ident]=dict(tid=tid,api=api,ret=ret,sp=sp,return_sp=rsp,a=a,b=b,target=target)
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
   ident,phase,address,n,*values=v;assert n==len(values) and n<=36 and ident in calls and (ident,phase) not in words
   words[ident,phase]=(address,values)
  elif kind=='CAP':
   api,count,address=v;assert api>=3 and count==32 and bp[address][0]==api and api not in [c[0] for c in caps]
   assert sum(c['api']==api for c in calls.values())==32;caps.append(tuple(v))
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
 assert len(ends)==1 and ends[0]==[0,len(calls),0] and totals==[[len(calls),len(calls),len(bp)]]
 assert calls and all('result' in c for c in calls.values()) and not any(stacks.values()) and len(args)==len(calls)
 for ident,c in calls.items():
  api=c['api'];value=c['result']
  if api in [4,11,15]:assert ident in dibs
  if api in [4,5,8]:assert ident in outputs
  if api==4 and value:assert outputs[ident]
  if api in [5,8] and not value&0x80000000:
   assert ident in objects and (ident,2) in words
   obj,vt,n=objects[ident];addr,table=words[ident,2];assert addr==vt and len(table)==n
   expected={2:6,20:7,6:8} if api==5 else {2:9,22:10,5:13}
   for slot,method in expected.items():assert bp[table[slot]][0]==method
  if api==8:
   address,desc=words[ident,0];assert address==args[ident][1] and len(desc)==27 and desc[0]==108
  if api==10 and not value&0x80000000:
   address,desc=words[ident,1];assert address==args[ident][1] and len(desc)==27 and desc[0]==108
 return dict(calls=calls,args=args,bp=bp,modules=modules,caps=caps,objects=objects,words=words,outputs=outputs,dibs=dibs)

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
 assert all(c['result']!=0 for _,c in groups[3][1:]) and [c[0] for c in r['caps']]==[3]
 for i,c in groups[3]:
  assert args[i][1:5]==[0,0,8,8] and args[i][6:]==[0,0,0xcc0020]
 assert len(groups[4])==3 and [bool(c['result']) for _,c in groups[4]]==[False,True,True]
 assert r['outputs'][groups[4][0][0]]==0
 assert len(groups[11])==1 and groups[11][0][1]['result']==8
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
 return dict(passed=True,header_records=len(r['dibs']),header_statuses=[d['status'] for d in r['dibs'].values()],total_pairs=len(calls),main_call_counts={str(a):len(v) for a,v in groups.items()},
  probe_invocations=20,bitblt_recorded=32,bitblt_sample_limit=32,bitblt_failed=1,
  stretch_returned_scanlines=8,dd_create_failed_hresult=groups[5][0][1]['result'],
  returned_surface_width=got[3],returned_surface_height=got[2],returned_surface_caps=got[26],
  returned_surface_bpp=got[21],modules=len(r['modules']),breakpoint_sites=len(r['bp']),
  scope='Original NT5 GDI/DirectDraw control only. Trace limited to32 entries per graphics API. Not game FPS or Xbox acceleration.')
