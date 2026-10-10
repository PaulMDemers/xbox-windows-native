"""Bounded non-stopping HMP reads of the owned ordinary219 guest's layout."""
import datetime,hashlib,json,re,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['control001','candidate001']
out=k/('emu-'+case);dest=out/'live-layout.json';assert not dest.exists()
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/blayout219-runs/nt5-blayout219-'+case)
sys.path.insert(0,str(ws/'outputs/native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
review=read(k/'build-review.json');binary=k/'artifacts/build001'/case/'xboxbvid.dll'
assert sha(binary)==review['binaries'][case]['sha256']
kernel=ws/'outputs/video-upload-runtime211/artifacts/F/winnt/system32/ntoskrnl.exe';pe=pefile.PE(str(kernel))
pub=read(ws/'outputs/native-windows-nt5-kernel/kernel-publics.json')['symbols']
K=read(ws/'outputs/fatx-cache-buffer/sites.json')['kernel_base_expected']
r=dict(scope=__doc__,source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),kernel_sha256=sha(kernel),
    physical_access=False,debugger_memory_mutated=False,cpu_stopped=False,read_only_monitor_observation=True,
    attempts=[],passed=False,complete=False)
def save():
    p=dest.with_suffix('.tmp');p.write_text(json.dumps(r,indent=2)+'\n');p.replace(dest)
def words(address,count):
    text=command(4594,'x /%dwx 0x%x'%(count,address));values=[]
    for line in text.replace('\r','').splitlines():
        match=re.match(r'^(?:0x)?[0-9a-fA-F]+:\s+((?:0x[0-9a-fA-F]{8}\s*)+)',line)
        if match:values+=list(map(lambda v:int(v,16),re.findall(r'0x([0-9a-fA-F]{8})',match.group(1))))
    assert len(values)==count,(address,count,text[-500:]);return values
deadline=time.monotonic()+360
while time.monotonic()<deadline:
    if (run/'cleanup.json').exists():r['reason']='Guest closed before live layout observed';break
    if not (run/'instance.json').exists():time.sleep(2);continue
    lock=None
    try:
        lock=acquire_monitor_lock(4594)
        assert 'VM status: running' in command(4594,'info status')
        header=words(K,256);data=struct.pack('<256I',*header);assert data[:2]==b'MZ'
        off=struct.unpack_from('<I',data,60)[0];assert data[off:off+4]==b'PE\0\0'
        assert struct.unpack_from('<I',data,off+8)[0]==pe.FILE_HEADER.TimeDateStamp
        head=K+pub['_PsLoadedModuleList']['rva'];link=words(head,1)[0];seen=set();found=None
        while link!=head:
            assert link not in seen and len(seen)<128;seen.add(link);row=words(link,14)
            length=row[11]&65535;maximum=row[11]>>16;pointer=row[12]
            assert length<=maximum and length<=512 and not length%2
            n=(length+3)//4;blob=struct.pack('<%dI'%n,*words(pointer,n))[:length] if n else b''
            name=blob.decode('utf-16le')
            if name.lower()=='bootvid.dll':found=dict(base=row[6],bytes=row[8],name=name);break
            link=row[0]
        assert found,'Bootvid module not yet listed'
        B=found['base'];disk=pefile.PE(str(binary));h=struct.pack('<256I',*words(B,256));offset=struct.unpack_from('<I',h,60)[0]
        assert h[:2]==b'MZ' and h[offset:offset+4]==b'PE\0\0' and struct.unpack_from('<I',h,offset+8)[0]==disk.FILE_HEADER.TimeDateStamp
        symbols=review['binaries'][case]['symbols'];reset=symbols['_ResetDisplay']['rva']
        disk.relocate_image(B);expected_code=disk.get_data(reset,64)
        resident_code=struct.pack('<16I',*words(B+reset,16));assert resident_code==expected_code
        r['resident_reset_pin']=dict(rva=reset,bytes=64,sha256=hashlib.sha256(resident_code).hexdigest(),matched_relocated_disk=True)
        cells={n:words(B+v['rva'],1)[0] for n,v in symbols.items() if v['kind'].lower()=='b'}
        cells2={n:words(B+v['rva'],1)[0] for n,v in symbols.items() if v['kind'].lower()=='b'};assert cells==cells2
        frame=cells['_FrameBufferStart'];back=cells['_BackBuffer'];assert frame and back
        hidden=back-frame;expected=0x39dd00 if case=='candidate001' else 0x3b2d00;assert hidden==expected
        if case=='candidate001':assert cells['_BootWritableBytes']==0x3eb000
        assert 'VM status: running' in command(4594,'info status')
        r.update(passed=True,complete=True,module=found,cells=cells,hidden_offset=hidden,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        break
    except Exception as exc:r['attempts'].append(dict(error=repr(exc),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));save()
    finally:
        if lock:lock.close()
    time.sleep(5)
r.update(closed=True,closed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    limits='Live immutable layout values read twice with CPU running and actual module/header identities. No breakpoint, stop, seed/guard mutation or GPU access. Does not prove all runtime writes preserved the tail or qualify GPU ownership.')
save();print(json.dumps({n:r[n] for n in ['passed','complete','closed','cpu_stopped']}))
