"""Fail closed on remaining PE binding gaps; layout assertions run at build."""
import argparse,hashlib,json,pathlib,sys
r=pathlib.Path(__file__).resolve().parents[2];out=r/'outputs/native-windows-nt5-debug'
sys.path.insert(0,str(r/'work/python-packages'))
import pefile
p=argparse.ArgumentParser();p.add_argument('--require-compatible',action='store_true');p.add_argument('--kernel',type=pathlib.Path,default=r/'work/media-inspection/EN_WIN2000_PRO_SP4/ntoskrnl.exe');p.add_argument('--report',default='binary-audit.json');a=p.parse_args()
records={}
for n,f in {'ntoskrnl.exe':a.kernel,
            'hal.dll':out/'artifacts/halxboxnt5.dll','bootvid.dll':out/'artifacts/xboxbvid.dll'}.items():
    pe=pefile.PE(str(f));records[n]={
        'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
        'native_version':[pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion],
        'imports':{d.dll.decode().lower():[s.name.decode() if s.name else '#'+str(s.ordinal) for s in d.imports] for d in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])},
        'exports':{s.name.decode():{'rva':hex(s.address),'forwarder':s.forwarder.decode() if s.forwarder else None} for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}}
checks=[]
for n,rec in records.items():
    for lib,names in rec['imports'].items():
        missing=sorted(set(names)-records.get(lib,{}).get('exports',{}).keys())
        checks.append({'source':n,'target':lib,'count':len(names),'missing':missing})
    for name,s in rec['exports'].items():
        if s['forwarder']:
            lib,sym=s['forwarder'].rsplit('.',1);lib+='.exe' if lib.lower()=='ntoskrnl' else '.dll'
            checks.append({'source':n,'export':name,'forwarder':s['forwarder'],'resolved':sym in records.get(lib,{}).get('exports',{})})
report={'runtime_approved':False,'scope':'Name binding only; not kernel runtime approval. Selected timer/interrupt paths and field offsets are tested separately. Full scheduler, interrupt delivery, loader and hardware initialization remain unvalidated.','checks':checks,'records':records}
(out/a.report).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(checks,indent=2))
if a.require_compatible and any(c.get('missing') or c.get('resolved') is False for c in checks):raise SystemExit('Gate failed: do not deploy this HAL as a Windows replacement')
