"""Pure non-PAE physical-snapshot translation and bounded resident alias walk."""
import hashlib,struct
TARGETS=[('reserved_ram',0x03c00000,0x04000000),('gpu_aperture',0xf3c00000,0xf4000000)]
def word(data,at):
 assert 0<=at<=len(data)-4,('physical read outside captured RAM',at)
 return struct.unpack_from('<I',data,at)[0]
def table(data,at):
 assert at%4096==0 and 0<=at<=len(data)-4096,('page table outside captured RAM',at)
 return struct.unpack_from('<1024I',data,at)
def physical(data,cr3,va):
 assert 0<=va<=0xffffffff
 pde=table(data,cr3&0xfffff000)[va>>22];assert pde&1,('absent PDE',va)
 if pde&128:
  assert not pde&0x003fe000,'PSE36 unsupported'
  return (pde&0xffc00000)+(va&0x3fffff)
 pte=table(data,pde&0xfffff000)[(va>>12)&1023];assert pte&1,('absent PTE',va)
 return (pte&0xfffff000)+(va&4095)
def read_virtual(data,cr3,va,n):
 assert 0<=n<=65536 and va+n<=0x100000000
 result=bytearray()
 while n:
  pa=physical(data,cr3,va);length=min(n,4096-(va&4095))
  assert pa+length<=len(data),'virtual read outside captured RAM'
  result.extend(data[pa:pa+length]);va+=length;n-=length
 return bytes(result)
def scan_directory(data,cr3):
 root=cr3&0xfffff000;directory=table(data,root);records=[];tables=[];present=large=0
 def intersect(va,pa,size,pde,pte,pde_at,pte_at):
  for kind,start,end in TARGETS:
   lo=max(start,pa);hi=min(end,pa+size)
   if lo>=hi:continue
   bits=pde if pte is None else pte
   records.append(dict(kind=kind,virtual=va+lo-pa,physical=lo,length=hi-lo,
    page_bytes=size,pde=pde,pte=pte,pde_physical=pde_at,pte_physical=pte_at,
    pcd=bool(bits&16),pwt=bool(bits&8),pat=bool(bits&(4096 if pte is None else 128)),
    user=bool(pde&4 and (pte is None or pte&4))))
 for i,pde in enumerate(directory):
  if not pde&1:continue
  present+=1;va=i<<22;pde_at=root+i*4
  if pde&128:
   assert not pde&0x003fe000,'PSE36 unsupported'
   large+=1;intersect(va,pde&0xffc00000,0x400000,pde,None,pde_at,None)
  else:
   base=pde&0xfffff000;pt=table(data,base)
   tables.append(dict(pde_index=i,physical=base,sha256=hashlib.sha256(data[base:base+4096]).hexdigest(),present_ptes=sum(bool(p&1) for p in pt)))
   for j,pte in enumerate(pt):
    if pte&1:intersect(va+j*4096,pte&0xfffff000,4096,pde,pte,pde_at,base+j*4)
 return dict(cr3=cr3,root=root,present_pdes=present,large_pdes=large,page_tables=tables,matches=records,
  directory_sha256=hashlib.sha256(data[root:root+4096]).hexdigest(),pdes_examined=1024,ptes_examined=len(tables)*1024)
def ranges(records):
 result=[]
 for r in records:
  flags=(r['kind'],r['page_bytes'],r['pcd'],r['pwt'],r['pat'],r['user'])
  if result and result[-1]['flags']==flags and result[-1]['virtual']+result[-1]['length']==r['virtual'] and result[-1]['physical']+result[-1]['length']==r['physical']:
   result[-1]['length']+=r['length'];result[-1]['entries']+=1
  else:result.append(dict(flags=flags,virtual=r['virtual'],physical=r['physical'],length=r['length'],entries=1))
 return result
