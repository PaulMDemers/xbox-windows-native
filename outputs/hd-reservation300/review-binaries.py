"""Review compiled reservation pair before any guest deployment."""
import collections,hashlib,importlib.util,json,pathlib,re,struct,sys
K=pathlib.Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
s=importlib.util.spec_from_file_location('elf293',W/'outputs/launcher-relocation293/review.py');mod=importlib.util.module_from_spec(s);s.loader.exec_module(mod)
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=read(K/'build001.json');assert build['status']=='compiled'
assert read(K/'host001.json')['passed']
dest=K/'binary-review001.json';assert not dest.exists()
r=dict(passed=False,scope='Static binary/ABI/layout review only',cases={})
warnings=[];exports=[];imports=[]
archive=pathlib.Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
for case in ['control001','candidate001']:
 p=pathlib.Path('E:/xwn300/build001')/case
 for n,v in build['cases'][case]['files'].items():assert sha(p/n)==v['sha256']
 b,sections,symbols=mod.elf(p/'image-crom.elf');assert sections['.text']['va']==0x02600000
 end=max(v['va']+v['size'] for v in sections.values() if v['flags']&2)
 assert end==symbols['BSS_END']['va'] and 0x02800000-end>=262144
 text=b[sections['.text']['offset']:sections['.text']['offset']+sections['.text']['size']]
 assert b'\xbc'+struct.pack('<I',0x02800000) in text
 bb,_,_=mod.elf(p/'xbeboot.elf')
 assert b'\xbf'+struct.pack('<I',0x02600000)+b'\xb9\x00\x00\x10\x00\xf3\xa4\xfa\xea'+struct.pack('<I',0x02600000)+b'\x08\x00' in bb
 physical=0x03c00000 if case=='control001' else 0x03700000
 size=0x400000 if case=='control001' else 0x900000
 assert struct.pack('<I',physical|0xf0000000) in text and struct.pack('<I',size) in text
 log=(p.parent/(case+'.log')).read_text();assert not re.search(r'clock skew|modification time .* future|error:',log,re.I)
 w=[re.sub(r'(cromwell-)?(?:control001|candidate001)',lambda m:'cromwell-CASE' if m.group(1) else 'CASE',v) for v in log.splitlines() if re.search('warning:',v,re.I)]
 warnings.append(collections.Counter(w))
 pes={n:pefile.PE(str(p/n)) for n in ['xboxvnt5.sys','xboxbvid.dll','rosload.exe']}
 ex={v.name.decode():v.ordinal for v in pes['xboxbvid.dll'].DIRECTORY_ENTRY_EXPORT.symbols};exports.append(ex)
 assert {'XwnFbAcquire','XwnFbRelease','XwnFbReleaseOwner'}<=ex.keys()
 imp={}
 for n in ['xboxvnt5.sys','xboxbvid.dll']:
  pe=pes[n];assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Subsystem==1
  assert pe.OPTIONAL_HEADER.CheckSum==pe.generate_checksum()
  imp[n]={}
  for entry in pe.DIRECTORY_ENTRY_IMPORT:
   dll=entry.dll.decode().lower();names=[v.name.decode() for v in entry.imports];imp[n][dll]=names
   if dll=='bootvid.dll':target=pes['xboxbvid.dll']
   else:
    match=next(q for base in [archive,archive/'drivers'] for q in base.iterdir() if q.name.lower()==dll)
    target=pefile.PE(str(match))
   available={v.name.decode() for v in target.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
   assert set(names)<=available,(n,dll)
  t=next(s.get_data() for s in pe.sections if s.Name.rstrip(b'\0')==b'.text')
  assert struct.pack('<I',size) in t,(n,'reservation immediate missing')
 imports.append(imp)
 assert not {'VideoPortMapMemory','VideoPortUnmapMemory'} & set(imp['xboxvnt5.sys']['videoprt.sys'])
 r['cases'][case]=dict(bss_end=end,stack_headroom=0x02800000-end,physical=physical,reserved=size,files=build['cases'][case]['files'],provider_exports=ex,imports=imp,warning_count=len(w),definitions=build['cases'][case]['definitions'])
assert warnings[0]==warnings[1] and exports[0]==exports[1] and imports[0]==imports[1]
r.update(passed=True,matched_warning_messages=True,new_warning_messages=[],native_shared_abi_size=44,candidate_abi_version=2,control_abi_version=1,bootvid_tail_bytes=316160,geometry_timing_changed=False,hardware_deployed=False,guest_qualified=False,limits='Immediate/layout/export checks do not prove runtime reservations or aliases. Software display remains limited to visible images <=4MiB; this phase keeps low-resolution timing.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','matched_warning_messages','guest_qualified']}))
