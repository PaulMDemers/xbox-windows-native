"""Unique standalone nxdk compilation, pinned inputs and read-only SDK preflight."""
import datetime,hashlib,json,re,shutil,struct,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;a=sys.argv[1];assert re.fullmatch(r'\d{3}',a)
out=Path('E:/xwn271')/('build'+a);report=k/('build'+a+'.json')
assert not out.exists() and not report.exists()
assert shutil.disk_usage('C:/').free-64*1024**2>=20*1024**3,'Projected20GiB guard'
out.mkdir(parents=True);(out/'input').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
for p in (k/'native').iterdir():
    if p.is_file():shutil.copy2(p,out/p.name);shutil.copy2(p,out/'input'/p.name)
for name in ['build.py','Build.ps1']:shutil.copy2(k/name,out/'input'/name)
sdk=Path('C:/nxdk');pins=json.loads((k.parent/'lifetime-accounting270/fixture-review.json').read_text())
for name,v in pins['pins'].items():assert sha((sdk/name).read_bytes())==v['sha256'],name
def sdkpins():
    paths=list(sdk.rglob('*.lib'))+[sdk/n for n in pins['pins']]
    paths+=list((sdk/'bin').glob('nxdk-*'))
    for n in ['tools/cg/win/cgc.exe','tools/vp20compiler/vp20compiler.exe','tools/fp20compiler/fp20compiler.exe','tools/cxbe/cxbe.exe','tools/extract-xiso/build/extract-xiso.exe']:
        p=sdk/n;assert p.exists(),p;paths.append(p)
    return {str(p.relative_to(sdk)):sha(p.read_bytes()) for p in paths if p.is_file()}
before=sdkpins()
closure={}
dependency_lead=Path('E:/xwn271/build004/main.c.d')
assert dependency_lead.exists()
for name in sorted(set(re.findall(r'C:/nxdk/[^\s:]+',dependency_lead.read_text()))):
    p=Path(name);assert p.is_file(),name
    relative=p.relative_to(sdk);data=p.read_bytes();closure[str(relative)]=sha(data)
    dest=out/'sdk-inputs'/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
for name in before:
    p=sdk/name;dest=out/'sdk-inputs'/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copy2(p,dest)
r=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),attempt=a,path=str(out),
    sdk_head=pins['head'],sdk_before=before,guest_prepared=False,guest_launched=False,physical_access=False,
    sdk_header_closure_before=closure,closure_lead=str(dependency_lead),
    projected_c_free=shutil.disk_usage('C:/').free-64*1024**2,source={p.name:sha(p.read_bytes()) for p in (out/'input').iterdir()})
def make(command,name,timeout):
    p=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File','C:/Homebrew/Invoke-Console.ps1','-Console','xbox','-WorkingDirectory',str(out),'-Command',command],capture_output=True,timeout=timeout)
    data=p.stdout+p.stderr;(out/name).write_bytes(data);(k/('build'+a+'-'+name)).write_bytes(data)
    return p.returncode,data.decode(errors='replace')
try:
    rc,plan=make('make -n V=1','plan.log',90);r['preflight_exit']=rc;assert rc==0,plan[-2000:]
    # No shared library/tool compilation, recursion, install or shared output.
    assert not re.search(r'\[ (?:LIB|AS|BUILD|CXX)\s+\]',plan),plan[-2000:]
    commands=[line.strip() for line in plan.splitlines() if line.strip().startswith(('nxdk-cc ','nxdk-link ','/c/nxdk/','make '))]
    assert sum(line.startswith('nxdk-cc ') for line in commands)==1
    for line in commands:
        assert not line.startswith('make '),line
        if line.startswith('nxdk-cc '):
            assert "-o '/e/xwn271/build"+a+"/main.obj'" in line,line
        if line.startswith('/c/nxdk/'):
            assert any(tool in line for tool in ['/cg/win/cgc ','/vp20compiler/vp20compiler ','/fp20compiler/fp20compiler ','/cxbe/cxbe ','/extract-xiso/build/extract-xiso ']),line
    r['preflight_commands']=commands;r['preflight_passed']=True
    rc,log=make('make -j4 V=1','compile.log',180);r['compile_exit']=rc
    assert rc==0,log[-2500:]
    warnings=[line for line in log.splitlines() if re.search(r'\bwarning:',line,re.I)]
    expected=[f'warning: line {20+i}, column 20: MOV   o[TEX{i}], v[8]; (Vertex attribute register v[8] (TEX0) will be mapped to hardware register v[9])' for i in range(4)]
    expected+=['lld: warning: .edata=.rdata: already merged into .edataxb']
    assert sorted(warnings)==sorted(expected),warnings
    r['reviewed_warnings']=warnings
    pe=(out/'main.exe').read_bytes();peoff=struct.unpack_from('<I',pe,60)[0]
    assert pe[peoff:peoff+4]==b'PE\0\0' and struct.unpack_from('<H',pe,peoff+24)[0]==0x10b
    assert struct.unpack_from('<II',pe,peoff+24+96)==(0,0)
    r['warning_meaning']='Four pinned vp20compiler TEX0 mappings to hardware attribute9 match native setup; SDK nxdk-link explicitly redirects .edata to .edataxb, final PE export directory is0/0. No warning suppression.'
    r['pe_export_directory']=[0,0]
    for n in ['main.exe','main.map','bin/default.xbe','owned-texture271.iso','vs.inl','ps.inl','flat.inl','main.c.d']:
        p=out/n;assert p.exists(),n
    actual=set(re.findall(r'C:/nxdk/[^\s:]+',(out/'main.c.d').read_text()))
    assert actual=={str(sdk/n).replace('\\','/') for n in closure}
    assert all(sha((sdk/n).read_bytes())==v for n,v in closure.items())
    r['header_closure_unchanged']=True
    r['outputs']={str(p.relative_to(out)):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in out.rglob('*') if p.is_file() and 'input' not in p.parts and 'sdk-inputs' not in p.parts}
    r['compiled']=True
except Exception as e:
    r['failure']=repr(e);r['compiled']=False
finally:
    r['sdk_after']=sdkpins();r['sdk_unchanged']=r['sdk_after']==before
    r['closed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    report.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:v for n,v in r.items() if n not in ['source','sdk_before','sdk_after','outputs','preflight_commands']},indent=2))
assert r['compiled'] and r['sdk_unchanged']
