"""Compare existing process page tables in the post-failure physical snapshot."""
import hashlib,json,re,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash001'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sys.path.insert(0,str(k.parent/'video-shared-trace2'));from walk import read_virtual,table,physical
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');meta=read(out/'failure-residency.json');raw=Path(meta['private_memory']);assert sha(raw)==meta['private_memory_sha256'];ram=raw.read_bytes()
cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',meta['registers'])[1],16);K=t['kernel_base']
info=read(k/'modules.json')['xwnown.dll'];pe=pefile.PE(info['path']);assert sha(Path(info['path']))==info['sha256']
base=next(v['base'] for v in t['module_list'] if v['name'].lower()=='xwnown.dll');sec=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.text');va=base+sec.VirtualAddress
expected=bytearray(pe.get_data(sec.VirtualAddress,sec.Misc_VirtualSize))
for b in pe.DIRECTORY_ENTRY_BASERELOC:
 for e in b.entries:
  if e.type==3 and sec.VirtualAddress<=e.rva<sec.VirtualAddress+len(expected):
   off=e.rva-sec.VirtualAddress;struct.pack_into('<I',expected,off,(struct.unpack_from('<I',expected,off)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
rv=lambda a,n:read_virtual(ram,cr3,a,n)
u32=lambda a:struct.unpack('<I',rv(a,4))[0]
layoutpath=k.parent/'native-windows-nt5-kernel/process-layouts.json';publicpath=k.parent/'native-windows-nt5-kernel/kernel-publics.json'
L=read(layoutpath);E=L['_EPROCESS']['fields'];P=L['_KPROCESS']['fields'];head=K+read(publicpath)['symbols']['_PsActiveProcessHead']['rva'];q=u32(head);seen=set();rows=[]
while q!=head:
 assert q and q not in seen and len(seen)<128;seen.add(q);ep=q-E['ActiveProcessLinks']['offset']
 row=dict(process=ep,pid=u32(ep+E['UniqueProcessId']['offset']),name=rv(ep+E['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace'),cr3=u32(ep+E['Pcb']['offset']+P['DirectoryTableBase']['offset']))
 row['pde']=table(ram,row['cr3']&~4095)[va>>22]
 try:
  data=read_virtual(ram,row['cr3'],va,len(expected));row['text_matches']=data==expected;row['text_sha256']=hashlib.sha256(data).hexdigest();row['first_text_physical']=physical(ram,row['cr3'],va)
  owner=base+info['symbols']['XwnOwners'];row['ownership_raw']=read_virtual(ram,row['cr3'],owner,384).hex()
 except AssertionError as exc:row['read_error']=repr(exc)
 rows.append(row);q=u32(q)
r=dict(physical_access=False,scope=__doc__,current_cr3=cr3,display_base=base,text_virtual=va,expected_bytes=len(expected),processes=rows,
 snapshot_sha256=sha(raw),dependencies={str(p.relative_to(ws)):sha(p) for p in [layoutpath,publicpath,k/'modules.json',Path(__file__),k.parent/'video-shared-trace2/walk.py']},
 limits='Read-only physical snapshot after failed observer resumed; cannot replace missing before-crash observations or qualify this attempt.')
dest=out/'residency-analysis.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps([{n:v for n,v in row.items() if n!='ownership_raw'} for row in rows],indent=2))
