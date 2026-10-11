"""Check actual NT5 exports, PE target and exact build/source provenance before guest launch."""
import hashlib,json,pathlib,sys
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
providers=repo/'outputs/audio-listen001/artifacts/providers001'
manifest=json.loads((repo/'outputs/audio-listen001/providers001.json').read_text())
assert manifest['passed']
tables={}
for name,row in manifest['files'].items():
 p=providers/name;assert sha(p)==row['sha256']
 pe=pefile.PE(str(p));tables[name.lower()]={}
 for s in pe.DIRECTORY_ENTRY_EXPORT.symbols:
  if s.name:tables[name.lower()][s.name.decode()]=s
  tables[name.lower()]['#'+str(s.ordinal)]=s
def resolve(module,name,depth=0):
 assert depth<8 and module in tables and name in tables[module],(module,name)
 s=tables[module][name];assert s.address
 if not s.forwarder:return
 m,n=s.forwarder.decode().rsplit('.',1);resolve(m.lower()+('' if m.lower().endswith('.dll') else '.dll'),n,depth+1)
p=k/'artifacts/build003/probe.exe';pe=pefile.PE(str(p))
assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.Magic==0x10b
assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
imports={}
for dll in pe.DIRECTORY_ENTRY_IMPORT:
 name=dll.dll.decode().lower();imports[name]=[]
 for s in dll.imports:
  n=s.name.decode() if s.name else '#'+str(s.ordinal);resolve(name,n);imports[name].append(n)
record={'passed':True,'binary_sha256':sha(p),'imports':imports,'provider_sha256':{n:manifest['files'][n]['sha256'] for n in imports},'pe_machine':'i386','subsystem_version':'5.0','actual_builder_sha256':sha(k/'build003.py'),'link_libraries':['kernel32','user32','winmm'],'source_sha256':{n:sha(k/n) for n in ['probe.c','waveform.h','build003.py','Build003.ps1','test-waveform.c']},'build_record_note':'build001 pre-review and build002 host recording failure retained; final build003 has actual source/compiler and checked NT5 providers.'}
with (k/'helper-review001.json').open('x') as f:json.dump(record,f,indent=2)
print(json.dumps({'passed':True,'imported_libraries':list(imports),'binary_sha256':record['binary_sha256']}))
