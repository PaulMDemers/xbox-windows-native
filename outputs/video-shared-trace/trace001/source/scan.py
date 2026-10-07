"""Decode a closed private snapshot; no guest or console operations."""
import json,hashlib,struct
from pathlib import Path
from walk import *
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'trace001'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(out/'trace.json');assert r['status']=='desktop_snapshot_captured' and r['guest_resumed'] and not r['armed_breakpoints_remaining'] and 'error' not in r
raw=Path(r['private_memory']);assert sha(raw)==r['private_memory_sha256'];data=raw.read_bytes();assert len(data)==67108864
cr=r['control_registers'];assert cr['CR0']&0x80000000 and not cr['CR4']&0x20
cr3=cr['CR3'];base=r['kernel_base'];pubs=read(ws/'outputs/native-windows-nt5-kernel/kernel-publics.json')['symbols']
layouts=read(k/'process-layouts.json');f=layouts['_EPROCESS']['fields'];kf=layouts['_KPROCESS']['fields']
u32=lambda va:struct.unpack('<I',read_virtual(data,cr3,va,4))[0]
assert u32(0xc0300c00)&0xfffff000==cr3&0xfffff000
head=base+pubs['_PsActiveProcessHead']['rva'];link=u32(head);previous=head;seen=set();processes=[]
while link!=head:
 assert link not in seen and len(seen)<128;seen.add(link);assert u32(link+4)==previous
 process=link-f['ActiveProcessLinks']['offset'];directory=u32(process+f['Pcb']['offset']+kf['DirectoryTableBase']['offset']);assert directory&0xfffff000
 processes.append(dict(address=process,pid=u32(process+f['UniqueProcessId']['offset']),image=read_virtual(data,cr3,process+f['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii'),cr3=directory))
 previous=link;link=u32(link)
assert u32(head+4)==previous and any(p['address']==r['owner']['process'] and p['cr3']&0xfffff000==cr3&0xfffff000 for p in processes)
roots=sorted(set([cr3&0xfffff000]+[p['cr3']&0xfffff000 for p in processes]));directories=[]
for root in roots:
 d=scan_directory(data,root);d['ranges']=ranges(d['matches']);d['processes']=[p for p in processes if p['cr3']&0xfffff000==root]
 directories.append(d)
result=dict(passed=True,physical_access=False,ordinary_qualified=False,source_sha256=sha(Path(__file__)),walker_sha256=sha(k/'walk.py'),snapshot_sha256=sha(raw),trace_sha256=sha(out/'trace.json'),processes=processes,directories=directories,limits='Point-in-time present mappings of linked active process roots and current root. No TLB, inactive/exited process, future alias, pagefile-resident table, PFN ownership or current PAT/MTRR audit. GPU aperture and reserved RAM are distinct physical address ranges; hardware equivalence comes from platform contract, not page translation alone.')
p=k/'alias-scan.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(processes=len(processes),directories=len(directories),ranges=[dict(root=d['root'],ranges=d['ranges']) for d in directories]),indent=2))
