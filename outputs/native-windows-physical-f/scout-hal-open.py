"""Exploratory debugger observation, not production validation."""
import sys,pathlib,struct,json
k=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(k.parent/'native-windows-physical-bootvideo'))
from debug_remote import Remote
r=Remote(4595);r.s.settimeout(50);r.ask('?');r.bp(0x15e70);r.send('c');events=[]
try:
 for i in range(40):
  r.recv();g=r.regs()
  if g['eip']!=0x15e70:r.send('c');continue
  args=struct.unpack('<4I',r.read(g['esp'],16));path=r.read(args[1],200).split(b'\0')[0].decode('ascii',errors='replace');events.append({'path':path,'registers':g});print(ascii(path),flush=True)
  if 'halxboxnt5' in path.lower():
   r.bp(0x15e70,False);r.bp(0x163d0);r.send('c');r.recv();g=r.regs();ret=struct.unpack('<I',r.read(g['esp'],4))[0];r.bp(0x163d0,False);r.bp(ret);r.send('c');r.recv();g=r.regs();events[-1]['ArcOpen_status']=g['eax'];r.bp(ret,False);print('ArcOpen',g,flush=True);r.send('c');break
  r.bp(0x15e70,False);r.ask('s');r.bp(0x15e70);r.send('c')
finally:
 (k/'hal-open-scout.json').write_text(json.dumps({'scope':'Exploratory breakpoint observation','events':events},indent=2)+'\n');r.s.close()
