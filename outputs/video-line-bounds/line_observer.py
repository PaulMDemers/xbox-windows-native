"""Pair real LineTo arguments and returns within bounded user-draw markers."""
import struct
from desktop_observer import DesktopObserver
class LineObserver(DesktopObserver):
 def __init__(self,env,marker,rva):
  self.e=env;self.marker=marker;self.rva=rva;self.active=False
  self.entries={};self.pending=[];self.returns=set();self.base=None
  self.rows=[];self.stages=[]
  env['r']['line_calls']=self.rows;env['r']['line_stages']=self.stages
 def handle(self,regs,owner):
  e=self.e;a=regs['EIP'];g=e['g']
  if a==self.marker:
   assert owner==e['r']['probe_entry']['owner']
   args=list(struct.unpack('<2I',g.read(regs['ESP']+4,8)));index,phase=args
   assert (index,phase)==divmod(len(self.stages),2) and index<18 and not self.pending
   e['pin']('probe.exe',self.rva)
   if phase==0:
    assert not self.active;self.base=self.module()['base'];symbols=e['coff_symbols'](e['pes']['xwnown.dll'])
    self.entries={self.base+symbols['XwnLineTo']:'XwnLineTo'}
    for address in self.entries:self.arm(address)
    self.active=True
   else:assert self.active
   self.stages.append(dict(args=args,owner=owner,registers=regs,stop_index=len(e['r']['stop_sequence'])-1,call_count=len(self.rows),pending=len(self.pending),module=self.module(),ownership=self.ownership()))
   if phase==1:
    self.active=False
    for address in self.entries:self.disarm(address)
    assert not self.returns
   e['save']();self.advance(a,len(self.stages)<36);return True
  if not self.active or a not in set(self.entries)|self.returns:return False
  self.module()
  if a in self.entries:
   assert len(self.rows)<64
   raw=g.read(regs['ESP'],40);args=list(struct.unpack('<10I',raw))
   ret,surface,clip,brush,x1,y1,x2,y2,bounds,mix=args
   row=dict(index=len(self.rows),sample=self.stages[-1]['args'][0],name='XwnLineTo',owner=owner,entry_registers=regs,entry_stop_index=len(e['r']['stop_sequence'])-1,args=args,raw_stack=raw.hex(),module=self.module())
   self.rows.append(row);e['save']();e['pin']('xwnown.dll',a-self.base)
   row['bounds_raw']=g.read(bounds,16).hex() if bounds else None
   row['bounds']=list(struct.unpack('<4i',bytes.fromhex(row['bounds_raw']))) if bounds else None
   row['clip_raw']=g.read(clip,24).hex() if clip else None
   row['surface_raw']=g.read(surface,52).hex()
   row['ownership']=self.ownership()
   m=next(v for v in e['modules'](None) if v['base']<=ret<v['base']+v['size'])
   assert m['name'] in ['win32k.sys','xwnown.dll'];e['pin'](m['name'],ret-m['base']);row['return_module']=m
   self.pending.append(row);self.returns.add(ret);self.arm(ret)
   e['save']();self.advance(a);return True
  matches=[v for v in self.pending if v['args'][0]==a and v['owner']['thread']==owner['thread'] and regs['ESP']==v['entry_registers']['ESP']+40]
  if not matches:
   foreign=e['r'].setdefault('line_foreign_return_hits',[]);assert len(foreign)<64
   foreign.append(dict(owner=owner,registers=regs));e['save']();self.advance(a);return True
  assert len(matches)==1
  row=matches[0];assert row is [v for v in self.pending if v['owner']['thread']==owner['thread']][-1]
  row['return']=dict(owner=owner,registers=regs,stop_index=len(e['r']['stop_sequence'])-1)
  self.pending.remove(row);remains=any(v['args'][0]==a for v in self.pending)
  if not remains:self.returns.remove(a)
  e['save']();self.advance(a,remains or a in self.entries);return True
