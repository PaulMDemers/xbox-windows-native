"""Bounded new three-stage protocol. No retries of accepted mutating requests."""
import hashlib,json,re,time
def numbers(s):return {k:int(v) for k,v in re.findall(r'(?<![\w])(\w+)=(\d+)',s)}
def qpath(tree):
 stack=[];found=[]
 for line in tree.splitlines():
  m=re.match(r'^(\s*)/([^ ]*) \(([^)]+)\)',line)
  if not m:continue
  level=len(m[1]);name=m[2]
  while stack and stack[-1][0]>=level:stack.pop()
  if name:stack.append((level,name))
  if m[3]=='nv2a':found.append('/'+'/'.join(n for _,n in stack))
 assert len(found)==1;return found[0]
class Backend:
 def __init__(self,cmd,out,root,result,save):
  self.cmd=cmd;self.out=out;self.root=root;self.r=result;self.save=save
  self.path=None;self.closed=False;self.reopened=False;self.completed=False
  self.candidate=out.name.startswith('candidate');self.groups=[]
 def get(self,prop):return self.cmd('qom-get '+self.path+' '+prop)
 def set(self,prop,value):
  reply=self.cmd('qom-set -j '+self.path+' '+prop+' '+json.dumps(value));assert 'Error' not in reply;return reply
 def wait(self,prop,states,seconds):
  end=time.monotonic()+seconds
  while True:
   s=self.get(prop);n=numbers(s)
   if n['state'] in states:return s
   assert time.monotonic()<end,(prop,s);time.sleep(.03)
 def pages(self,kind,count,epoch):
  assert 0<count<=704
  folder=self.out/(kind+'-pages');folder.mkdir(exist_ok=False);manifest=[]
  prop='xwn-ui265-page' if kind=='ui' else 'xwn-ledger265-page'
  prefix='' if kind=='ui' else f'stage281,{epoch},'
  end=time.monotonic()+120
  for i in range(count):
   assert time.monotonic()<end
   self.set(prop,prefix+str(i));s=self.get(prop);v=numbers(s)
   assert v['epoch']==epoch and v['page']==i and v['pages']==count
   p=folder/(str(i).zfill(4)+'.txt');p.write_bytes(s.encode());manifest.append(dict(file=p.relative_to(self.out).as_posix(),sha256=hashlib.sha256(s.encode()).hexdigest()))
   self.r[kind+'_pages']=list(manifest);self.save()
  self.set(prop,prefix+'0');assert self.get(prop).encode()==(self.out/manifest[0]['file']).read_bytes()
 def capture_stages(self,text,stages):
  n=numbers(text)
  for stage in stages:
   if n.get(f's{stage}_pages'):self.pages(f'stage{stage}',n[f's{stage}_pages'],stage)
 def begin(self):
  from proof import load_pages,initial_snapshots
  import checks
  self.path=qpath(self.cmd('info qom-tree'));self.r['nv2a_path']=self.path
  assert numbers(self.get('xwn-ledger265-report'))['state']==0
  self.closed=True;self.r['frontend_close_requested']=True;self.save()
  reply=self.cmd('qom-set '+self.path+' xwn-frontend246-close true');assert 'Error' not in reply
  s=self.wait('xwn-frontend246-report',[2,3],8);v=numbers(s);self.r['frontend_initial']=s;self.save()
  assert v['state']==2 and all(v[n]==0 for n in ['loan','bql','error'])
  ui=self.get('xwn-ui265-report');v=numbers(ui);self.r['ui_report']=ui;self.save()
  assert v['ready']==v['epoch']==1 and v['error']==v['overflow']==0
  self.pages('ui',v['pages'],1);self.ui=load_pages(self.out,self.r,'ui',1,8192)
  self.allocations=self.r['checkpoints'][-1]['state_header'][10:14]
  self.r['attested_allocations282']=self.allocations
  self.r['initial_request_may_be_accepted']=True;self.save()
  self.set('xwn-ledger265',('candidate281,' if self.candidate else 'control281,')+','.join(map(str,self.allocations)))
  s=self.wait('xwn-ledger265-report',[3,6],25);self.r['initial_report']=s;self.save()
  self.capture_stages(s,[1,2]);checks.report(s,self.candidate)
  self.groups=[load_pages(self.out,self.r,f'stage{i}',i,180000) for i in [1,2]]
  result=checks.initial(s,self.groups,self.ui,self.allocations,self.candidate)
  self.r['initial_proof282']=result;self.save()
  self.r['initial_snapshot_proof282']=initial_snapshots(self.root,self.r,result,self.candidate);self.save()
  assert self.get('xwn-ledger265-report')==s
 def end(self):
  from proof import load_pages,resumed
  import checks
  self.r['terminal_request_may_be_accepted']=True;self.save();self.set('xwn-ledger265','finish281')
  s=self.wait('xwn-ledger265-report',[5,6],15);self.r['terminal_report']=s;self.save()
  self.capture_stages(s,[3]);checks.report(s,self.candidate,True)
  self.groups.append(load_pages(self.out,self.r,'stage3',3,180000))
  self.r['terminal_proof282']=checks.final(self.r['initial_report'],s,self.groups,self.ui,self.allocations,self.candidate);self.save()
  assert (self.root/'watch/terminal273.bin').is_file() and self.get('xwn-ledger265-report')==s
  self.r['reuse_before_resume282']=resumed(self.root,self.r,self.r['initial_proof282'],self.r['terminal_proof282'],self.candidate);self.save()
  self.completed=True;self.r['owner_boundaries_completed']=True;self.save()
 def cleanup(self):
  if self.closed and not self.reopened:
   reply=self.cmd('qom-set '+self.path+' xwn-frontend246-close false');assert 'Error' not in reply
   s=self.wait('xwn-frontend246-report',[5],8);self.r['frontend_reopened_report']=s;self.reopened=True;self.save()
