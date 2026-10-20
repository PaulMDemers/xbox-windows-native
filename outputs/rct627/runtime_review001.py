"""Validate private runtime bytes and a narrowly bounded original-control unwind.
No stack-word scanning, proprietary byte publication or general unwinder claim.
"""
import hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import pefile,capstone
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'runtime-review001.json';assert not out.exists()
assert read(K/'review001.json')['passed']
P=Path('C:/xwn627/pc001/cold1-002')
log=P/'files/xwn627/sampler.txt';manifest=read(P/'manifest.json')
files={}
for row in read(K.parent/'rct621/seed-symbols001.json')['files']:
    p=Path(row['path'].replace('/mnt/c/','C:/'))
    assert sha(p)==row['sha256']==manifest['winnt/system32/'+row['name']]['sha256']
    files[row['name']]=p
files['kernel32.dll']=P/'files/WINNT/system32/kernel32.dll'
files['subject.exe']=P/'files/xwn627-kit/subject.exe'
for name,p in files.items():
    n=('xwn627-kit/' if name=='subject.exe' else 'winnt/system32/')+name
    assert sha(p)==manifest[n]['sha256']
mods={};samples={};captures={};images={};counts=Counter();returns=Counter()
for line in log.read_text().splitlines():
    v=line.split();tag=v[0]
    if tag=='MODULE':mods.setdefault(int(v[1]),[]).append((int(v[2],16),int(v[3],16),' '.join(v[4:]).lower().split('\\')[-1]))
    elif tag=='SAMPLE':samples[int(v[1]),int(v[2])]=v
    elif tag in ('CODE','STACK'):
        assert len(v)==6
        key=(int(v[1]),int(v[2]),tag);assert key not in captures
        address=int(v[3],16);ok=int(v[4]);assert ok in (0,1)
        data=bytes.fromhex(v[5]) if ok else b''
        assert (len(data)==(32 if tag=='CODE' else 64)) if ok else v[5]=='-'
        captures[key]=(address,ok,data)
assert len(captures)==2*len(samples)
dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
subject=pefile.PE(str(files['subject.exe']))
calls={}
for sec in subject.sections:
    if sec.Name.rstrip(b'\0')==b'.text':
        for i in dis.disasm(sec.get_data(),subject.OPTIONAL_HEADER.ImageBase+sec.VirtualAddress):
            if i.mnemonic=='call':calls[i.address+i.size]=(i.address,i.op_str)
# Supported instruction boundaries and stack offsets in exact pinned WINMM.
offsets={r:0 for r in (0x7bbc,0x7bc3,0x7bc9,0x7bce,0x7bd4,0x7bda,0x7bdc,0x7be2,0x7bf6,0x7bfc)}
offsets.update({0x7be4:4,0x7be9:8,0x7bef:8,0x7bf0:12,0x7bf1:16,0x7bfd:20,0x7bfe:24,0x7bff:28,0x7c40:28,0x7c41:24,0x7c42:20})
offsets.update({r:32 for r in (0x7c00,0x7c02,0x7c06,0x7c08,0x7c0e,0x7c12,0x7c14,0x7c1a,0x7c1c,0x7c22,0x7c26,0x7c2a,0x7c2c,0x7c2e,0x7c30,0x7c34,0x7c36,0x7c38,0x7c39,0x7c3f)})
winmm=pefile.PE(str(files['winmm.dll']))
boundaries={i.address for i in dis.disasm(winmm.get_data(0x7bbc,0x89),0x7bbc)}
assert set(offsets)<=boundaries
for key,v in samples.items():
    ip=int(v[4],16);sp=int(v[5],16)
    code=captures[key+('CODE',)];stack=captures[key+('STACK',)]
    assert code[0]==ip and stack[0]==sp
    owners=[(b,s,n) for b,s,n in mods[key[0]] if b<=ip<b+s];assert len(owners)==1
    base,size,name=owners[0]
    counts['code_read_success' if code[1] else 'code_read_failure']+=1
    counts['stack_read_success' if stack[1] else 'stack_read_failure']+=1
    if not code[1]:continue
    assert name in files,name
    if (name,base) not in images:
        pe=pefile.PE(str(files[name]));images[name,base]=pe.get_memory_mapped_image(ImageBase=base)
    assert code[2]==images[name,base][ip-base:ip-base+32],(key,name,hex(ip-base))
    counts['exact_code_matches']+=1
    if name!='winmm.dll' or ip-base not in offsets or not stack[1]:continue
    offset=offsets[ip-base]
    if ip-base>=0x7bfd:
        assert struct.unpack_from('<I',stack[2],offset-20)[0]==base+0x7bf6
    ret=struct.unpack_from('<I',stack[2],offset)[0]
    sb=[b for b,s,n in mods[key[0]] if n=='subject.exe'];assert len(sb)==1
    diskret=ret-sb[0]+subject.OPTIONAL_HEADER.ImageBase
    assert diskret in calls,(key,hex(ret))
    returns[key[0],diskret-subject.OPTIONAL_HEADER.ImageBase]+=1
    counts['fixed_winmm_unwind_to_original_call_boundary']+=1
assert counts['code_read_success']>=100 and counts['stack_read_success']>=100
assert counts['fixed_winmm_unwind_to_original_call_boundary']>=10
r=dict(passed=True,private_log_sha256=sha(log),snapshots=len(samples),counts=dict(counts),
       original_return_sites=[dict(case=c,return_rva=hex(rv),observations=n) for (c,rv),n in sorted(returns.items())],
       source_sha256=sha(Path(__file__)),binary_pins={n:sha(p) for n,p in files.items()},
       scope='Exact runtime instruction comparison and fixed-version WINMM stack-layout control leading to original subject call boundaries. Not a general unwinder, retail caller proof, sample-time fractions, FPS or Xbox measurement.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
