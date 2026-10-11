"""Read back a caller window with complete leading/trailing relocation overlap."""
import ast,datetime,hashlib,json,socket,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'veto001'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=read(out/'run.json');trace=read(out/'trace.json');plan=read(k/'preflight001.json')
assert not run['closed'] and 'finished_utc' in trace and trace['guest_resumed'] and trace['breakpoints_remaining']==0
assert 'tcp:127.0.0.1:4895' in run['argv']
assert sha(k/'trace.py')==plan['sources']['trace.py']
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
provider=plan['providers']['hidclass.sys'];assert sha(Path(provider['path']))==provider['sha256']
pe=pefile.PE(provider['path']);base=0xf8f10000;K=plan['kernel_base_expected']
tree=ast.parse((k/'trace.py').read_text())
nodes=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in ('Remote','monitor')]
assert len(nodes)==2
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(k/'trace.py'),'exec'))
dest=out/'loaded-site-review001.json';assert not dest.exists()
r=dict(scope=__doc__,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=run['pid'],provider_sha256=provider['sha256'],source_sha256=sha(Path(__file__)),memory_writes=False,register_writes=False,breakpoints_used=False,regions=[])
g=None
try:
    monitor('stop');g=Remote();g.ask('qSupported');g.ask('?')
    u=lambda a:struct.unpack('<I',g.read(a,4))[0]
    assert g.read(base,2)==b'MZ';nt=u(base+60)
    assert u(base+nt+8)==pe.FILE_HEADER.TimeDateStamp and u(base+nt+0x50)==pe.OPTIONAL_HEADER.SizeOfImage
    for rva,n in ((0x4209,16),(0x4213,6),(0x4235,6)):
        start=rva-4;wide=bytearray(pe.get_data(start,n+8));old=bytearray(pe.get_data(rva,n));relocs=[]
        for block in pe.DIRECTORY_ENTRY_BASERELOC:
            for e in block.entries:
                if e.type!=3 or not (e.rva<rva+n and e.rva+4>rva):continue
                offset=e.rva-start;relocs.append(e.rva)
                struct.pack_into('<I',wide,offset,(struct.unpack_from('<I',wide,offset)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
                if rva<=e.rva and e.rva+4<=rva+n:
                    at=e.rva-rva;struct.pack_into('<I',old,at,(struct.unpack_from('<I',old,at)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
        expected=bytes(wide[4:4+n]);actual=g.read(base+rva,n);assert actual==expected
        r['regions'].append(dict(rva=rva,size=n,raw=pe.get_data(rva,n).hex(),actual=actual.hex(),correct_expected=expected.hex(),old_expected=old.hex(),old_matched=actual==old,overlapping_highlow_rvas=relocs))
    assert not r['regions'][0]['old_matched']
    r['IoSetDeviceInterfaceState_iat']=u(base+0x3618);assert r['IoSetDeviceInterfaceState_iat']==K+0xa381a
    r['passed']=True
except Exception as e:r.update(passed=False,error=repr(e));raise
finally:
    if g:g.s.close()
    r['resume_response']=monitor('cont');r['status_response']=monitor('info status');r['guest_resumed']='VM status: running' in r['status_response']
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n')
print('Loaded caller bytes match with overlapping relocations; IAT targets the observed kernel API; guest resumed')
