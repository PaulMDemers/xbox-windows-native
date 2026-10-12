"""Native pair imports, exports, checksum, flags and complete warning comparison."""
import collections,hashlib,json,pathlib,re,sys
K=pathlib.Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=K/'binary-review003.json';assert not dest.exists()
b=read(K/'build003.json');s=read(K/'source-review003.json');assert b['status']=='compiled' and read(K/'host001.json')['passed']
assert b['patch_sha256']==s['patch_sha256']==sha(K/'0119-hd-surface-bounds003.patch')
for n,h in s['source_files'].items():assert hashlib.sha256((K/'display'/n).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==h
provider=W/'outputs/video-physical-rehearsal160/artifacts/F/winnt/system32/win32k.sys'
available={v.name for v in pefile.PE(str(provider)).DIRECTORY_ENTRY_EXPORT.symbols if v.name}
cases={};warnings=[]
for case in ['control001','candidate001']:
 p=pathlib.Path('D:/xwn303/build003')/case/'xwnown.dll';assert sha(p)==b['cases'][case]['sha256']
 pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Subsystem==1
 assert pe.OPTIONAL_HEADER.CheckSum==pe.generate_checksum()
 imports={}
 for e in pe.DIRECTORY_ENTRY_IMPORT:
  assert e.dll.lower()==b'win32k.sys' and all(v.name in available for v in e.imports)
  imports[e.dll.decode()]=[v.name.decode() for v in e.imports]
 exports={v.name.decode():v.ordinal for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
 log=(p.parent.parent/(case+'.log')).read_text()
 assert not re.search(r'clock skew|modification time .*future|error:',log,re.I)
 w=[re.sub(r'/home/paul/xbox-windows-native/build/[^/]+/source','SOURCE',v) for v in log.splitlines() if 'warning:' in v.lower()]
 warnings.append(collections.Counter(w))
 cases[case]=dict(sha256=sha(p),bytes=p.stat().st_size,imports=imports,exports=exports,definitions=b['cases'][case]['definitions'],warnings=w,
  metadata_diagnostics=[v for v in log.splitlines() if 'fatal:' in v])
a,c=[cases[n] for n in ['control001','candidate001']]
assert a['imports']==c['imports'] and a['exports']==c['exports'] and warnings[0]==warnings[1]
defs=[dict(v['definitions']) for v in [a,c]]
assert defs[0].pop('XWN_HD_SURFACE_BOUNDS')=='OFF' and defs[1].pop('XWN_HD_SURFACE_BOUNDS')=='ON' and defs[0]==defs[1]
old=read(W/'outputs/video-text-clip205/build-review.json')['cases']['candidate001'];assert old['imports']==a['imports']
r=dict(passed=True,source_tree=b['source_tree'],cases=cases,only_definition_difference='XWN_HD_SURFACE_BOUNDS',new_imports=False,
 warning_messages_matched=True,warning_count=len(a['warnings']),host_sha256=sha(K/'host001.json'),source_review_sha256=sha(K/'source-review003.json'),
 physical_access=False,guest_launch=False,limits='Bounds and matched static binaries only. CMake version discovery reports absent HEAD in both tree-only reconstructions; compilation succeeds. No 1080i timing or runtime allocation qualification.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Native bounds pair reviewed',r['warning_count'],'matched warnings')
