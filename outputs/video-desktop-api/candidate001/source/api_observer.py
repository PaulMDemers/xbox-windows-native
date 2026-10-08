"""Real owned user32 desktop API entry/return pairs; no guest mutations."""
import re,struct
FUNCTIONS={'OpenDesktopA':4,'CloseDesktop':1}
class ApiObserver:
 def __init__(self,e):self.e=e;self.entries={};self.pending=[];self.rows=[];e['r']['api_calls']=self.rows
 def arm(self,a):
  if a not in self.e['armed']:self.e['g'].bp(a);self.e['armed'].add(a)
 def advance(self,a,rearm=True):
  e=self.e;e['g'].bp(a,False);e['armed'].remove(a);assert e['step_observed']().startswith(('T','S'))
  if rearm:self.arm(a)
  e['g'].send('c')
 def install(self):
  e=self.e;p=e['pes']['user32.dll'];base=next(m['base'] for m in e['loaded'] if m['name']=='user32.dll')
  self.rvas={s.name.decode():s.address for s in p.DIRECTORY_ENTRY_EXPORT.symbols if s.name and not s.forwarder}
  for name in FUNCTIONS:self.entries[base+self.rvas[name]]=name;self.arm(base+self.rvas[name])
  p=e['pes']['kernel32.dll'];self.error_rva=next(s.address for s in p.DIRECTORY_ENTRY_EXPORT.symbols if s.name==b'GetLastError')
  # Actual NT5 instructions load TEB via fs:[18], then TEB.LastErrorValue at34.
  assert p.get_data(self.error_rva,10)==bytes.fromhex('64a1180000008b4034c3')
 def teb(self):
  e=self.e;text=e['command'](4594,'info registers');m=re.search(r'FS\s*=([0-9a-fA-F]+)\s+([0-9a-fA-F]+)',text);assert m
  base=int(m[2],16);assert 0x10000<=base<0x80000000
  raw=e['g'].read(base,64);assert struct.unpack_from('<I',raw,0x18)[0]==base
  e['pin']('kernel32.dll',self.error_rva,10)
  return dict(base=base,raw_first64=raw.hex(),last_error=struct.unpack_from('<I',raw,0x34)[0],segment_registers=text)
 def handle(self,regs,owner):
  e=self.e;g=e['g'];a=regs['EIP'];returns={r['args'][0] for r in self.pending}
  if a not in self.entries and a not in returns:return False
  if a in self.entries:
   name=self.entries[a];argc=FUNCTIONS[name];args=list(struct.unpack('<'+'I'*(argc+1),g.read(regs['ESP'],4*(argc+1))))
   probe=e['pes']['probe.exe'];base=probe.OPTIONAL_HEADER.ImageBase
   if owner!=e['r']['probe_entry']['owner'] or not base<=args[0]<base+probe.OPTIONAL_HEADER.SizeOfImage:
    rows=e['r'].setdefault('api_foreign_entries',[]);assert len(rows)<128;rows.append(dict(name=name,owner=owner,registers=regs,args=args));e['save']();self.advance(a);return True
   assert len(self.rows)<40
   e['pin']('user32.dll',self.rvas[name]);e['pin']('probe.exe',args[0]-base)
   row=dict(index=len(self.rows),name=name,argc=argc,args=args,owner=owner,entry_registers=regs,entry_stop=len(e['r']['stop_sequence'])-1,stage_count=len(e['r']['desktop_stages']),teb_before=self.teb())
   if name=='OpenDesktopA':
    b=bytearray()
    for i in range(64):
     c=g.read(args[1]+i,1)
     if c==b'\0':break
     b+=c
    else:raise AssertionError('Unbounded desktop name')
    row['desktop_name']=b.decode('ascii');assert row['desktop_name'].startswith('XwnDesktop126_')
   self.rows.append(row);self.pending.append(row);self.arm(args[0]);e['save']();self.advance(a);return True
  matches=[r for r in self.pending if r['args'][0]==a and owner['thread']==r['owner']['thread'] and regs['ESP']==r['entry_registers']['ESP']+4+4*r['argc']]
  if not matches:
   rows=e['r'].setdefault('api_foreign_returns',[]);assert len(rows)<64;rows.append(dict(owner=owner,registers=regs));e['save']();self.advance(a);return True
  assert len(matches)==1;row=matches[0];assert row is self.pending[-1]
  e['pin']('probe.exe',a-e['pes']['probe.exe'].OPTIONAL_HEADER.ImageBase)
  row['return']=dict(owner=owner,registers=regs,stop=len(e['r']['stop_sequence'])-1,teb=self.teb());self.pending.remove(row);e['save']();self.advance(a,any(r['args'][0]==a for r in self.pending) or a in self.entries);return True
