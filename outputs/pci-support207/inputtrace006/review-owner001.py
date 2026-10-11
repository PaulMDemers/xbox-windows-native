"""Resolve retained input file handles in the captured NT5 CSRSS handle table."""
import hashlib,json,re,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=k/'veto001';readjson=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=readjson(k/'preflight001.json');capture=readjson(case/'memory-capture001.json');trace=readjson(case/'trace.json');layout=readjson(k/'owner-layouts001.json');L=layout['structures']
assert layout['pdb_sha256']=='29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
dump=case/'artifacts/runtime/memory001.bin';assert sha(dump)==capture['dump_sha256'];data=dump.read_bytes()
regs=next(x['reply'] for x in capture['commands'] if x['command']=='info registers');cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',regs)[1],16)
assert int(re.search(r'CR4=([0-9a-fA-F]+)',regs)[1],16)&0x20==0
def phys32(a):return struct.unpack_from('<I',data,a)[0]
def pa(va):
    pde=phys32((cr3&0xfffff000)+4*(va>>22));assert pde&1,('nonresident PDE',hex(va))
    if pde&128:return (pde&0xffc00000)+(va&0x3fffff)
    pte=phys32((pde&0xfffff000)+4*((va>>12)&1023));assert pte&1,('nonresident PTE',hex(va))
    return (pte&0xfffff000)+(va&4095)
def mem(va,size):
    result=b''
    while size:
        at=pa(va);n=min(size,4096-(va&4095));assert at+n<=len(data);result+=data[at:at+n];va+=n;size-=n
    return result
def u32(a):return struct.unpack('<I',mem(a,4))[0]
def off(t,n):return L[t]['fields'][n]['offset']
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile,capstone
provider=plan['providers']['ntoskrnl.exe'];assert sha(Path(provider['path']))==provider['sha256'];pe=pefile.PE(provider['path']);cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
code=[]
for rva,n in ((0x8f87c,0x49),(0x8eaa4,0x68),(0x8eb0c,0x42),(0x4e702,0x65)):
    raw=pe.get_data(rva,n);code.append(dict(rva=rva,raw=raw.hex(),disassembly=[dict(rva=x.address,mnemonic=x.mnemonic,operands=x.op_str) for x in cs.disasm(raw,rva)]))
assert pe.get_data(0x4e704,3)==bytes.fromhex('83e2f8')
assert pe.get_data(0x8eabd,5)==bytes.fromhex('0d00000080')
assert pe.get_data(0x8eb35,6)==bytes.fromhex('81e7ffffff7f')
prior=[x for x in trace['calls'] if x.get('enable')==1 and x.get('status')==0 and x['identity']['image']=='csrss.exe'];assert len(prior)==2
process=prior[0]['identity']['process'];assert all(x['identity']['process']==process for x in prior)
assert u32(process+off('_EPROCESS','UniqueProcessId'))==160 and mem(process+off('_EPROCESS','ImageFileName'),16).split(b'\0')[0]==b'csrss.exe'
table=u32(process+off('_EPROCESS','ObjectTable'));table_raw=mem(table,L['_HANDLE_TABLE']['size']);tf={n:struct.unpack_from('<I',table_raw,off('_HANDLE_TABLE',n))[0] for n in ('HandleCount','Table','QuotaProcess','UniqueProcessId','NextIndexNeedingPool')}
assert tf['UniqueProcessId']==160 and tf['QuotaProcess']==process
targets={x['file_after']['address']:x for x in prior};matches=[];allocated=0;entries=0
top=struct.unpack('<256I',mem(tf['Table'],1024))
for high,middle in enumerate(top):
    if not middle:continue
    for mid,leaf in enumerate(struct.unpack('<256I',mem(middle,1024))):
        if not leaf:continue
        allocated+=1;assert allocated<=1024
        for low,(obj,access) in enumerate(struct.iter_unpack('<II',mem(leaf,2048))):
            if not obj:continue
            entries+=1
            # Exact NT5 lock/unlock and object-reference code above establishes
            # sign-bit locking, low-three attribute bits and Body offset24.
            header=(obj|0x80000000)&0xfffffff8;body=header+off('_OBJECT_HEADER','Body')
            if body not in targets:continue
            old=targets[body];file_raw=mem(body,L['_FILE_OBJECT']['size']);typ,size=struct.unpack_from('<HH',file_raw)
            assert typ==5 and size==112
            fields={n:u32(body+off('_FILE_OBJECT',n)) for n in ('DeviceObject','FsContext','FsContext2','Flags')}
            assert all(fields[n]==old['file_after'][n] for n in ('DeviceObject','FsContext','FsContext2'))
            counts={n:u32(header+off('_OBJECT_HEADER',n)) for n in ('PointerCount','HandleCount','Type')};assert counts['PointerCount']>=counts['HandleCount']>=1
            matches.append(dict(call_id=old['id'],owner_process=process,owner_pid=160,owner_image='csrss.exe',table=table,entry=leaf+low*8,entry_raw=mem(leaf+low*8,8).hex(),handle=(high<<18)|(mid<<10)|(low<<2),file_object=body,object_header=header,header_raw=mem(header,24).hex(),object_counts=counts,granted_access=access,file_fields=fields))
assert entries==tf['HandleCount'],(entries,tf)
assert {m['file_object'] for m in matches}==set(targets)
r=dict(scope=__doc__,review_passed=True,physical_access=False,ordinary_qualified=False,post_failure_owner_proven=True,owner_at_exact_failure_instant_proven=False,sole_owner_proven=False,root_cause_proven=False,memory_snapshot_utc=capture['started_utc'],cr3=cr3,kernel_sha256=provider['sha256'],dependencies={str(p):sha(p) for p in (k/'owner-layouts001.json',case/'memory-capture001.json',case/'trace.json',Path(__file__))},table_address=table,table_raw=table_raw.hex(),table_fields=tf,allocated_leaves=allocated,nonzero_entries=entries,matches=matches,lookup_and_pointer_semantics=code,limits='This paused post-failure snapshot proves CSRSS has handles to both earlier successful input file objects. It does not prove sole ownership, continuity at the exact failure instant, or the HID internal condition that rejects a second CREATE. No handle-table or guest memory mutation.')
dest=k/'owner-review001.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(table=tf,matches=matches),indent=2))
