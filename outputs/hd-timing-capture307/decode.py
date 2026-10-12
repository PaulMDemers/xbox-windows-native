"""Independent exact transport checks; raw timing values are observations, not specifications."""
import importlib.util,json,re,struct
from pathlib import Path
old=Path(__file__).resolve().parent.parent/'hd-physical292/decode.py'
spec=importlib.util.spec_from_file_location('original292decoder',old);legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
CR=[0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x15,0x16,0x17,0x18,0x19,0x1a,0x25,0x28,0x2d,0x39]
MM=[0x600804,0x680508,0x680600]
def decode(data,kernel=None):
 lines=data.decode('ascii').splitlines();assert all(lines)
 base=[x for x in lines if x.split()[0] in ['XWN_HD307','SETTINGS','SET','MODE','FP','COMPLETE']]
 legacy_result=legacy.decode(('\r\n'.join(base).replace('XWN_HD307','XWN_HD292')+'\r\n').encode())
 def fields(line,names):
  parts=line.split()[1:];assert len(parts)==len(names)
  pairs=[p.split('=') for p in parts];assert [a for a,b in pairs]==names
  assert all(re.fullmatch('[0-9a-f]+',b) for a,b in pairs);return dict(pairs)
 ks=[x for x in lines if x.startswith('KERNEL ')];assert len(ks)==1
 q=fields(ks[0],['base','bytes','avset','avoption','smbwrite','smbread','pages','valid','saved'])
 b=int(q['base'],16);size=int(q['bytes']);pages=int(q['pages'])
 assert 0x80010000<=b<0x80400000 and 4096<=size<=0x200000 and pages==(size+4095)//4096
 assert all(b<=int(q[n],16)<b+size for n in ['avset','avoption','smbwrite','smbread']) and q['saved']=='1'
 pp=[x for x in lines if x.startswith('KPAGE ')];assert len(pp)==pages
 validity=[]
 for i,p in enumerate(pp):
  f=fields(p,['offset','valid']);assert int(f['offset'],16)==i*4096 and f['valid'] in ['0','1'];validity.append(int(f['valid']))
 assert sum(validity)==int(q['valid']) and validity[0]
 assert lines.index(pp[-1])<lines.index(ks[0])<next(i for i,x in enumerate(lines) if x.startswith('SET '))
 rows=[]
 for stage in range(1,4):
  group=[x for x in lines if x.startswith(('TIMING stage='+str(stage)+' ','CRTC stage='+str(stage)+' ','MMIO stage='+str(stage)+' '))]
  assert len(group)==1+len(CR)+len(MM)
  t=fields(group[0],['stage','index_before','index_after','flags_before','flags_after']);assert t['stage']==str(stage)
  assert 0<=int(t['index_before'])<256 and t['index_before']==t['index_after'] and not ((int(t['flags_before'],16)^int(t['flags_after'],16))&0x200)
  cr=[];mm=[]
  for line,index in zip(group[1:24],CR):
   f=fields(line,['stage','index','value']);assert line.startswith('CRTC ') and int(f['index'],16)==index and int(f['stage'])==stage and 0<=int(f['value'],16)<256;cr.append(int(f['value'],16))
  for line,offset in zip(group[24:],MM):
   f=fields(line,['stage','offset','value']);assert line.startswith('MMIO ') and int(f['offset'],16)==offset and int(f['stage'])==stage and 0<=int(f['value'],16)<=0xffffffff;mm.append(int(f['value'],16))
  rows.append(dict(stage=stage,crtc=dict(zip(map(hex,CR),cr)),mmio=dict(zip(map(hex,MM),mm)),selector_restored=True,interrupt_flag_restored=True))
 assert len(lines)==57+pages+1+3*27
 assert lines[-1].startswith('COMPLETE ')
 if kernel is not None:
  assert len(kernel)==size and kernel[:2]==b'MZ';pe=struct.unpack_from('<I',kernel,0x3c)[0]
  assert pe<=0xe00 and kernel[pe:pe+4]==b'PE\0\0' and struct.unpack_from('<I',kernel,pe+80)[0]==size
  for i,valid in enumerate(validity):
   if not valid:assert not any(kernel[i*4096:min((i+1)*4096,size)])
 return dict(passed=True,pixels=legacy_result,kernel=q,kernel_page_validity=validity,timings=rows,encoder_access=False,windows_hd_qualified=False)
