"""Bounded entry/return pairing during the real supported desktop API intervals only."""
import struct

FUNCTIONS={
 'DrvAssertMode':(2,True),'DrvEnableSurface':(1,True),
 'DrvDisableSurface':(1,True),'DrvEnablePDEV':(11,True),
 'DrvCompletePDEV':(2,True),'DrvDisablePDEV':(1,True),
 'XwnRegisterPrimary':(1,False),'XwnUnregisterPrimary':(1,False),
 'XwnOwnershipDisable':(0,True),
}

class DesktopObserver:
 def __init__(self,env,marker,rva):
  self.e=env;self.marker=marker;self.rva=rva;self.active=False
  self.entries={};self.pending=[];self.returns=set();self.base=None
  self.rows=[];self.stages=[]
  env['r']['desktop_calls']=self.rows;env['r']['desktop_stages']=self.stages
 def arm(self,a):
  if a not in self.e['armed']:self.e['g'].bp(a);self.e['armed'].add(a)
 def disarm(self,a):
  if a in self.e['armed']:self.e['g'].bp(a,False);self.e['armed'].remove(a)
 def advance(self,a,rearm=True):
  self.disarm(a);assert self.e['step_observed']().startswith(('T','S'))
  if rearm:self.arm(a)
  self.e['g'].send('c')
 def snapshot(self,p):
  if not p:return None
  assert 0x80000000<=p<=0xffffffe0
  raw=self.e['g'].read(p,28)
  return dict(address=p,raw=raw.hex(),fields=dict(zip(['driver','hdev','primary','shadow_surface','shadow_object','shadow_bits','active'],struct.unpack('<7I',raw))))
 def module(self):
  rows=self.e['modules'](None);m=next(v for v in rows if v['name']=='xwnown.dll')
  # A different base requires a new observer design, never an invisible coverage waiver.
  assert self.base is None or m['base']==self.base,('display module relocated inside interval',m,self.base)
  return m
 def ownership(self):
  e=self.e;symbols=e['coff_symbols'](e['pes']['xwnown.dll']);m=self.module();address=m['base']+symbols['XwnOwners'];raw=e['g'].read(address,384);slots=[]
  for index in range(32):
   owner,surface,device=struct.unpack_from('<3I',raw,index*12)
   if owner or surface or device:
    assert owner and surface and device
    slots.append(dict(index=index,owner=owner,surface=surface,device=device,pdev=self.snapshot(owner)))
  return dict(address=address,raw=raw.hex(),slots=slots)
 def handle(self,regs,owner):
  e=self.e;a=regs['EIP'];g=e['g']
  if a==self.marker:
   assert owner==e['r']['probe_entry']['owner'];args=list(struct.unpack('<4I',g.read(regs['ESP']+4,16)));round,phase,desktop,result=args
   assert (round,phase)==divmod(len(self.stages),5) and round<3 and result==int(phase!=0) and (desktop!=0 if phase else desktop==0) and not self.pending
   e['pin']('probe.exe',self.rva)
   if phase==0:
    assert not self.active;self.base=self.module()['base'];symbols=e['coff_symbols'](e['pes']['xwnown.dll'])
    for name in FUNCTIONS:self.entries[self.base+symbols[name]]=name;self.arm(self.base+symbols[name])
    self.active=True
   else:assert self.active
   self.stages.append(dict(args=args,owner=owner,registers=regs,stop_index=len(e['r']['stop_sequence'])-1,call_count=len(self.rows),pending=len(self.pending),module=self.module(),ownership=self.ownership()))
   if phase==4:
    self.active=False
    for address in self.entries:self.disarm(address)
    assert not self.returns
   e['save']();self.advance(a,len(self.stages)<15);return True
  if not self.active or a not in set(self.entries)|self.returns:return False
  self.module()
  if a in self.entries:
   name=self.entries[a];argc,stdcall=FUNCTIONS[name]
   assert len(self.rows)<64
   args=list(struct.unpack('<'+'I'*(argc+1),g.read(regs['ESP'],4*(argc+1))))
   row=dict(index=len(self.rows),name=name,owner=owner,entry_registers=regs,entry_stop_index=len(e['r']['stop_sequence'])-1,args=args,argc=argc,stdcall=stdcall,module=self.module())
   self.rows.append(row);e['save']()
   e['pin']('xwnown.dll',a-self.base)
   ret=args[0];m=next(v for v in e['modules'](None) if v['base']<=ret<v['base']+v['size'])
   assert m['name'] in ['win32k.sys','xwnown.dll'],m
   e['pin'](m['name'],ret-m['base'])
   row['return_module']=m
   if name not in ['DrvEnablePDEV','XwnOwnershipDisable']:row['before']=self.snapshot(args[1])
   self.pending.append(row);self.returns.add(ret);self.arm(ret)
   e['save']();self.advance(a);return True
  matches=[v for v in self.pending if v['args'][0]==a and v['owner']['thread']==owner['thread'] and regs['ESP']==v['entry_registers']['ESP']+4+(4*v['argc'] if v['stdcall'] else 0)]
  if not matches:
   foreign=e['r'].setdefault('desktop_foreign_return_hits',[]);assert len(foreign)<64
   foreign.append(dict(owner=owner,registers=regs));e['save']();self.advance(a);return True
  assert len(matches)==1
  row=matches[0];assert row is [v for v in self.pending if v['owner']['thread']==owner['thread']][-1]
  row['return']=dict(owner=owner,registers=regs,stop_index=len(e['r']['stop_sequence'])-1)
  if row['name'] not in ['DrvDisablePDEV','XwnOwnershipDisable']:
   row['after']=self.snapshot(regs['EAX'] if row['name']=='DrvEnablePDEV' else row['args'][1])
  self.pending.remove(row)
  remains=any(v['args'][0]==a for v in self.pending)
  if not remains:self.returns.remove(a)
  e['save']();self.advance(a,remains or a in self.entries);return True
