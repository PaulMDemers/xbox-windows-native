"""Pin actual NT5 providers and verify every experimental import; no runtime claim."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--build',required=True);args=ap.parse_args()
    k=Path(__file__).resolve().parent
    dest=k/(args.build+'-review.json');assert not dest.exists()
    providers=k/'artifacts/providers001'; manifest=json.loads((k/'providers001.json').read_text())
    for row in manifest['files'].values():assert sha(providers/row['output'])==row['sha256']
    aliases={'hal.dll':'halxboxnt5.dll'}
    build=json.loads((k/(args.build+'-build.json')).read_text())
    for row in build['sources']:assert sha(k/row['name'])==row['sha256']
    result={'scope':__doc__,'files':[],'providers':{},'passed':True}
    for row in build['files']:
        p=k/'artifacts'/args.build/row['name'];assert sha(p)==row['sha256']
        if p.suffix not in ('.sys','.exe'):continue
        pe=pefile.PE(str(p)); imports=[]
        for descriptor in pe.DIRECTORY_ENTRY_IMPORT:
            dll=descriptor.dll.decode().lower(); provider=providers/aliases.get(dll,dll)
            actual=pefile.PE(str(provider)); exports={v.name.decode() for v in actual.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
            result['providers'][dll]={'path':str(provider),'sha256':sha(provider),'exports':len(exports)}
            for item in descriptor.imports:
                name=item.name.decode() if item.name else '#'+str(item.ordinal)
                found=name in exports;imports.append({'dll':dll,'name':name,'available':found})
                result['passed'] &= found
        version=[pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion]
        image={'name':p.name,'sha256':sha(p),'machine':pe.FILE_HEADER.Machine,'subsystem':pe.OPTIONAL_HEADER.Subsystem,'version':version,'imports':imports,
               'relocations':bool(pe.OPTIONAL_HEADER.DATA_DIRECTORY[5].VirtualAddress),
               'sections':[{'name':s.Name.rstrip(b'\0').decode(),'flags':hex(s.Characteristics)} for s in pe.sections]}
        if hasattr(pe,'VS_FIXEDFILEINFO'):
            v=pe.VS_FIXEDFILEINFO[0];image['file_version']=[v.FileVersionMS>>16,v.FileVersionMS&65535,v.FileVersionLS>>16,v.FileVersionLS&65535]
        result['passed'] &= pe.FILE_HEADER.Machine==0x14c and version==[5,0]
        result['files'].append(image)
    for row in result['providers'].values():
        pe=pefile.PE(row['path'])
        if hasattr(pe,'VS_FIXEDFILEINFO'):
            v=pe.VS_FIXEDFILEINFO[0];row['file_version']=[v.FileVersionMS>>16,v.FileVersionMS&65535,v.FileVersionLS>>16,v.FileVersionLS&65535]
    dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    assert result['passed']
if __name__=='__main__':main()
