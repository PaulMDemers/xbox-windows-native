import collections,hashlib,json,re,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=K/'binary-review001.json';assert not dest.exists();b=read(K/'build001.json');assert b['status']=='compiled'
provider=W/'outputs/video-physical-rehearsal160/artifacts/F/winnt/system32/win32k.sys';available={v.name for v in pefile.PE(str(provider)).DIRECTORY_ENTRY_EXPORT.symbols if v.name and not v.forwarder}
tool='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-';reports={};warnings=[]
for case in ['control001','candidate001']:
    p=Path('E:/xwn369/build001')/case/'xwnown.dll';assert sha(p)==b['cases'][case]['sha256'];pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Subsystem==1 and pe.OPTIONAL_HEADER.CheckSum==pe.generate_checksum()
    imports={}
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        assert entry.dll.lower()==b'win32k.sys' and all(v.name in available for v in entry.imports)
        imports[entry.dll.decode().lower()]=[v.name.decode() for v in entry.imports]
    linux='/mnt/e/xwn369/build001/'+case+'/xwnown.dll'
    nm=subprocess.check_output(['wsl','-d','Ubuntu','--',tool+'nm',linux],text=True,stderr=subprocess.DEVNULL);sites=[]
    for name in ['_XwnProfileStart','_XwnProfileEnd','_XwnProfileInit','_XwnProfileSnapshot','_XwnUploadBox','_XwnUploadInternal','_XwnBitBlt@44','_XwnCopyBits@24','_XwnStretchBlt@44','_XwnStretchBltROP@52']:
        match=re.search(r'^([0-9a-fA-F]+) [Tt] '+re.escape(name)+r'$',nm,re.M);assert match,name
        rva=int(match[1],16)-pe.OPTIONAL_HEADER.ImageBase;s=pe.get_section_by_rva(rva);assert s and s.Characteristics&0x08000000 and s.Characteristics&0x20000000
        sites.append(dict(name=name,rva=rva,section=s.Name.rstrip(b'\0').decode(),prefix=pe.get_data(rva,32).hex()))
    dis=subprocess.check_output(['wsl','-d','Ubuntu','--',tool+'objdump','-d','--disassemble=_XwnProfileStart',linux],text=True,stderr=subprocess.DEVNULL)
    (K/(case+'-clock.txt')).write_text(dis)
    clock=next(v.address for e in pe.DIRECTORY_ENTRY_IMPORT for v in e.imports if v.name==b'EngQueryPerformanceCounter')
    assert 'call' in dis and format(clock,'x') in dis
    log=(p.parent.parent/(case+'.log')).read_text();assert not re.search(r'clock skew|modification time .*future|error:',log,re.I)
    warning=[v for v in log.splitlines() if 'warning:' in v.lower()];warnings.append(collections.Counter(warning))
    reports[case]=dict(sha256=sha(p),imports=imports,resident_sites=sites,warnings=warning,definitions=b['cases'][case]['definitions'],clock_instructions_verified=True)
assert warnings[0]==warnings[1] and reports['control001']['imports']==reports['candidate001']['imports']
assert [k for k in reports['control001']['definitions'] if reports['control001']['definitions'][k]!=reports['candidate001']['definitions'][k]]==['XWN_STRETCH_BOUNDS']
dest.write_text(json.dumps(dict(passed=True,source_tree=b['source_tree'],cases=reports,provider_sha256=sha(provider),only_definition_difference='XWN_STRETCH_BOUNDS',runtime_qualified=False,physical_access=False),indent=2)+'\n');print('Matched imports/residency/actual clock code PASS')
