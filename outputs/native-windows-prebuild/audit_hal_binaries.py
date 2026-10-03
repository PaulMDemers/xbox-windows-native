"""Audit actual built Xbox HAL/boot-video imports against supplied Windows 2000."""
import argparse,hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'work/python-packages'))
import pefile
out=root/'outputs/native-windows-stage2'
parser=argparse.ArgumentParser();parser.add_argument('--flavor',choices=['debug','free'],default='debug');parser.add_argument('--require-compatible',action='store_true');args=parser.parse_args()
folder='hal-audit' if args.flavor=='debug' else 'hal-free-audit'
def inspect(path):
    pe=pefile.PE(str(path))
    exports={s.name.decode():{'rva':hex(s.address),'forwarder':s.forwarder.decode() if s.forwarder else None} for s in getattr(getattr(pe,'DIRECTORY_ENTRY_EXPORT',None),'symbols',[]) if s.name}
    imports={d.dll.decode().lower():[s.name.decode() if s.name else '#'+str(s.ordinal) for s in d.imports] for d in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[])}
    return {'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'machine':hex(pe.FILE_HEADER.Machine),'image_base':hex(pe.OPTIONAL_HEADER.ImageBase),'entry_rva':hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint),'image_size':pe.OPTIONAL_HEADER.SizeOfImage,'imports':imports,'exports':exports}
records={name:inspect(path) for name,path in {
    'ntoskrnl.exe':root/'work/media-inspection/EN_WIN2000_PRO_SP4/ntoskrnl.exe',
    'halxbox.dll':out/'artifacts'/folder/'halxbox.dll',
    'xboxbvid.dll':out/'artifacts'/folder/'xboxbvid.dll',
}.items()}
checks=[]
aliases={'hal.dll':'halxbox.dll','bootvid.dll':'xboxbvid.dll','ntoskrnl.exe':'ntoskrnl.exe'}
for source,record in records.items():
    for module,names in record['imports'].items():
        target=aliases.get(module)
        checks.append({'source':source,'target_import_name':module,'candidate':target,'count':len(names),'missing':sorted(set(names)-records[target]['exports'].keys()) if target else names})
    for name,export in record['exports'].items():
        if not export['forwarder']:continue
        module,symbol=export['forwarder'].rsplit('.',1)
        target=aliases.get(module.lower()+'.exe') or aliases.get(module.lower()+'.dll')
        checks.append({'source':source,'export':name,'forwarder':export['forwarder'],'candidate':target,'resolved':bool(target and symbol in records[target]['exports'])})
kernel=pefile.PE(records['ntoskrnl.exe']['file'])
scalars={}
for name in ('NtBuildNumber','HalDispatchTable','HalPrivateDispatchTable'):
    item=records['ntoskrnl.exe']['exports'].get(name)
    if item:scalars[name]=hex(kernel.get_dword_at_rva(int(item['rva'],16)))
report={'scope':'Actual PE import/export/forwarder name audit only; no ABI or runtime compatibility claim.', 'flavor':args.flavor,'kernel_export_initial_dwords':scalars,'records':records,'checks':checks}
(out/('hal-binary-audit.json' if args.flavor=='debug' else 'hal-free-binary-audit.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(scalars,indent=2))
print(json.dumps(checks,indent=2))
if args.require_compatible and any(c.get('missing') or c.get('resolved') is False for c in checks):
    raise SystemExit('Import/export gate failed; candidate is not ready for a Windows kernel test.')
