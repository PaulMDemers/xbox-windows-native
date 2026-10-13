"""Independent little-endian decoder. No console, process, or memory access.

Intel 253668-021, sections 10.11/10.12 and table10-7. This reports sampled page
policy, not TLB contents, an alias audit, or authorization to change caching.
"""
import collections,json,struct,sys
from pathlib import Path
BYTES=66560
TYPES={0:'UC',1:'WC',4:'WT',5:'WP',6:'WB',7:'UC-'}
TABLE={0:{0:0,7:0,1:1,4:0,6:0,5:0},
       1:{0:0,7:1,1:1,4:0,6:1,5:0},
       4:{0:0,7:0,1:1,4:4,6:4,5:5},
       5:{0:0,7:1,1:1,4:4,6:5,5:5},
       6:{0:0,7:0,1:1,4:4,6:6,5:5}}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def q(words,i):return words[i]|words[i+1]<<32
def cpu(c):
 need(len(c)==80,'CPU size')
 need(c[0]&0x80000000 and not c[0]&0x60000000,'paging/cache global state unknown')
 need(not c[2]&0x20 and c[3]&3==0,'PAE or privilege')
 need(c[4]>=1 and c[5:8]==(0x756e6547,0x49656e69,0x6c65746e),'vendor')
 need(c[8]>>8&15==6 and c[8]>>4&15==8 and not c[8]&0x0fff0000,'CPU model')
 need(c[9]&0x11020==0x11020 and not c[9]&0x10000000,'features')
 need(1<=c[11]<=8 and c[11]==c[14]&255,'variable count')
 need(c[19] in (0,1) and 32<=c[20]<=36,'physical width')
 need((c[19]==0 and c[18]<0x80000008 and c[20]==36) or
      (c[19]==1 and c[18]>=0x80000008),'physical width provenance')
 need(not any(c[21:24]+c[78:80]),'reserved CPU')
 need(not any(c[24+4*c[11]:56]),'truncated/extra MTRRs')
 cap=q(c,14);default=q(c,16);pat=q(c,12)
 need(not cap&~0x5ff and not default&~0xcff and default&0x800,'disabled or reserved MTRRs')
 need(default&255 in TABLE,'default type')
 need(not default&0x400 or cap&0x100,'unsupported fixed range')
 need(cap&0x100 or not any(c[56:78]),'unexpected fixed data')
 pats=[pat>>(8*i)&255 for i in range(8)];need(all(x in TYPES for x in pats),'PAT encoding')
 mask=((1<<c[20])-1)&~4095;ranges=[]
 for i in range(c[11]):
  b=q(c,24+i*4);m=q(c,26+i*4)
  if not m&0x800:continue
  need(not b&~(mask|255) and not m&~(mask|0x800),'MTRR reserved bits')
  t=b&255;need(t in TABLE and (t!=1 or cap&0x400),'MTRR type')
  start=b&mask;size=((~m)&mask)+4096
  need(size&(size-1)==0 and start%size==0,'noncontiguous or unaligned MTRR')
  need(start+size<=1<<c[20],'MTRR wrap')
  ranges.append((start,start+size,t))
 fixed=[]
 if cap&0x100 and default&0x400:
  for i in range(11):
   values=[q(c,56+i*2)>>(8*j)&255 for j in range(8)]
   need(all(t in TABLE for t in values),'fixed MTRR type');fixed.extend(values)
 def memory_type(pa):
  if pa<0x100000 and default&0x400:
   if pa<0x80000:at=pa//0x10000
   elif pa<0xc0000:at=8+(pa-0x80000)//0x4000
   else:at=24+(pa-0xc0000)//0x1000
   return fixed[at]
  hits={t for lo,hi,t in ranges if lo<=pa<hi}
  if not hits:return default&255
  if 0 in hits:return 0
  if hits=={4,6}:return 4
  need(len(hits)==1,'undefined overlapping MTRRs');return hits.pop()
 return pats,memory_type,ranges
def decode(data,warm=False):
 need(len(data)==BYTES,'packet length');w=struct.unpack('<16640I',data)
 need(w[:3]==(0x4d57584e,357 if warm else 354,BYTES),'packet identity')
 need(w[3]==0,'collector refused: '+str(w[3]))
 need(w[15]==4096 and 0<w[14]<=4096,'row capacity')
 need(all(w[i]>=0x80000000 for i in (4,6,7,8)) and w[5]!=0,'owner/base/opaque HSURF')
 need(640<=w[9]<=1920 and 480<=w[10]<=1080 and w[11]==w[9]*4 and w[12]==32 and w[13]==w[11]*w[10],'geometry')
 need(all(w[i]+w[13]<=0xffffffff for i in (7,8)),'range wrap')
 need(w[7]+w[13]<=w[8] or w[8]+w[13]<=w[7],'virtual overlap')
 before=w[16:96];after=w[96:176];need(before==after,'CPU changed')
 need(w[176]&1 and not w[176]&0x80 and (w[176]^before[1])&0xfffff000==0,'self map')
 need((w[176]^w[177])&~0x60==0,'self map changed')
 if warm:
  need(w[178]==0 and w[179]==0 and w[180]==w[13]//4 and w[181]==1 and not any(w[182:256]),'warm preflight/exception/reserved')
 else:need(not any(w[178:256]),'exception/reserved header')
 need(not any(w[256+w[14]*4:]),'unused output')
 pats,resolve,ranges=cpu(before);expected=[]
 for role in (0,1):
  base=w[7+role];expected.extend((role,va) for va in range(base&~4095,(base+w[13]-1&~4095)+4096,4096))
 need(len(expected)==w[14],'incomplete ranges');rows=[];physical=[set(),set()]
 for i,(role,va) in enumerate(expected):
  r=w[256+i*4:260+i*4];need(r[:2]==(role,va),'row order/coverage')
  pde,pte=r[2:];need(pde&1 and not pde&0x84 and pte&7==3,'unsupported translation')
  pa=pte&~4095;index=((pte>>7)&1)*4+((pte>>4)&1)*2+((pte>>3)&1)
  mt=resolve(pa);pt=pats[index];et=TABLE[mt][pt];physical[role].add(pa)
  rows.append(dict(role=role,virtual=va,physical=pa,pde=pde,pte=pte,pat_index=index,pat=TYPES[pt],mtrr=TYPES[mt],effective=TYPES[et]))
 need(not physical[0]&physical[1],'RAM/scanout physical alias')
 return dict(passed=True,scope='Sampled stable current translations and cache-register reads; no atomicity/TLB/complete-alias guarantee',
             owner=w[4],shadow=w[7],scanout=w[8],bytes=w[13],cpu_signature=before[8],cr0=before[0],cr3=before[1],cr4=before[2],
             variable_ranges=ranges,counts={name:dict(collections.Counter(r['effective'] for r in rows if r['role']==role)) for role,name in enumerate(('shadow','scanout'))},
             rows=rows,physical_qualified=False,cache_change_authorized=False)
if __name__=='__main__':
 try:r=decode(Path(sys.argv[1]).read_bytes())
 except ValueError as e:r=dict(passed=False,error=str(e),cache_change_authorized=False)
 print(json.dumps(r,indent=2));sys.exit(0 if r['passed'] else 1)
