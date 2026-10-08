"""Observe real NT5 engine enumeration inside bounded, owned primary draws."""
import struct
from desktop_observer import DesktopObserver

class ClipObserver(DesktopObserver):
 def __init__(self,env,marker,rva):
  self.e=env;self.marker=marker;self.rva=rva;self.active=False
  self.entries={};self.pending=[];self.returns=set();self.base=None
  self.rows=[];self.stages=[]
  env['r']['clip_calls']=self.rows;env['r']['clip_stages']=self.stages
 def handle(self,regs,owner):
  e=self.e;a=regs['EIP'];g=e['g']
  if a==self.marker:
   assert owner==e['r']['probe_entry']['owner']
   args=list(struct.unpack('<2I',g.read(regs['ESP']+4,8)));index,phase=args
   assert (index,phase)==divmod(len(self.stages),2) and index<18 and not self.pending
   e['pin']('probe.exe',self.rva)
   if phase==0:
    assert not self.active;self.base=self.module()['base'];symbols=e['coff_symbols'](e['pes']['xwnown.dll'])
    wm=next(v for v in e['loaded'] if v['name']=='win32k.sys')
    self.entries={self.base+symbols['XwnBitBlt']:('XwnBitBlt',11,'xwnown.dll',self.base)}
    for name,argc in [('CLIPOBJ_cEnumStart',5),('CLIPOBJ_bEnum',3)]:
     rva=next(x.address for x in e['pes']['win32k.sys'].DIRECTORY_ENTRY_EXPORT.symbols if x.name==name.encode())
     self.entries[wm['base']+rva]=(name,argc,'win32k.sys',wm['base'])
    for address in self.entries:self.arm(address)
    self.active=True
   else:assert self.active
   self.stages.append(dict(args=args,owner=owner,registers=regs,stop_index=len(e['r']['stop_sequence'])-1,call_count=len(self.rows),pending=len(self.pending),module=self.module(),ownership=self.ownership(),entries={str(a):list(v) for a,v in self.entries.items()}))
   if phase==1:
    self.active=False
    for address in self.entries:self.disarm(address)
    assert not self.returns
   e['save']();self.advance(a,len(self.stages)<36);return True
  if not self.active or a not in set(self.entries)|self.returns:return False
  if a in self.entries:
   assert len(self.rows)<512
   name,argc,module,base=self.entries[a];raw=g.read(regs['ESP'],4*(argc+1));args=list(struct.unpack('<'+'I'*(argc+1),raw))
   row=dict(index=len(self.rows),sample=self.stages[-1]['args'][0],name=name,argc=argc,owner=owner,entry_registers=regs,entry_stop_index=len(e['r']['stop_sequence'])-1,args=args,raw_stack=raw.hex(),code_module=module,code_base=base)
   self.rows.append(row);e['save']();e['pin'](module,a-base)
   clip=args[4] if name=='XwnBitBlt' else args[1]
   row['clip_address']=clip;row['clip_raw']=g.read(clip,24).hex() if clip else None
   if name=='XwnBitBlt':
    row['surface_raw']=g.read(args[1],52).hex();row['destination_raw']=g.read(args[6],16).hex();row['ownership']=self.ownership()
   ret=args[0];m=next(v for v in e['modules'](None) if v['base']<=ret<v['base']+v['size'])
   assert m['name'] in ['win32k.sys','xwnown.dll'];e['pin'](m['name'],ret-m['base']);row['return_module']=m
   self.pending.append(row);self.returns.add(ret);self.arm(ret)
   e['save']();self.advance(a);return True
  matches=[v for v in self.pending if v['args'][0]==a and v['owner']['thread']==owner['thread'] and regs['ESP']==v['entry_registers']['ESP']+4*(v['argc']+1)]
  if not matches:
   foreign=e['r'].setdefault('clip_foreign_return_hits',[]);assert len(foreign)<64
   foreign.append(dict(owner=owner,registers=regs));e['save']();self.advance(a);return True
  assert len(matches)==1
  row=matches[0];assert row is [v for v in self.pending if v['owner']['thread']==owner['thread']][-1]
  row['return']=dict(owner=owner,registers=regs,stop_index=len(e['r']['stop_sequence'])-1)
  if row['name']=='CLIPOBJ_bEnum':
   size,ptr=row['args'][2:4];assert 4<=size<=65536
   count=e['u32'](ptr);assert count<=(size-4)//16 and count<=1024
   raw=g.read(ptr,4+count*16);row['enum_raw']=raw.hex()
   row['rectangles']=[list(struct.unpack_from('<4i',raw,4+i*16)) for i in range(count)]
  self.pending.remove(row);remains=any(v['args'][0]==a for v in self.pending)
  if not remains:self.returns.remove(a)
  e['save']();self.advance(a,remains or a in self.entries);return True
