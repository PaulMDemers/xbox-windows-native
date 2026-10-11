"""Explain baseline code differences without equating relocated data to a rebuild proof."""
import hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
k=Path(__file__).resolve().parent
paths=[k.parent/'artifacts/providers001/halxboxnt5.dll',k/'artifacts/build001/native/artifacts/halxboxnt5.dll']
pes=[pefile.PE(str(p)) for p in paths];result={'scope':__doc__,'inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'sections':[]}
for name in (b'.text',b'.data',b'INIT'):
    sections=[next(s for s in pe.sections if s.Name.rstrip(b'\0')==name) for pe in pes]
    chunks=[s.get_data()[:s.Misc_VirtualSize] for s in sections]
    coverage=[]
    for pe,s in zip(pes,sections):
        coverage.append({e.rva-s.VirtualAddress+i for block in pe.DIRECTORY_ENTRY_BASERELOC for e in block.entries if e.type==3 and s.VirtualAddress<=e.rva<s.VirtualAddress+s.Misc_VirtualSize for i in range(4)})
    different=[i for i,(a,b) in enumerate(zip(*chunks)) if a!=b]
    other=[i for i in different if i not in coverage[0] or i not in coverage[1]]
    result['sections'].append(dict(name=name.decode(),sizes=[len(v) for v in chunks],differing_bytes=len(different),differences_outside_matching_relocation_fields=len(other),first_nonrelocation_offsets=[hex(i) for i in other[:32]],same_relocation_offsets=coverage[0]==coverage[1]))
result['source_path_strings']=[]
for pe in pes:
    s=next(s for s in pe.sections if s.Name.rstrip(b'\0')==b'.rdata')
    strings=[v.decode('ascii',errors='replace') for v in re.findall(rb'[ -~]{12,}',s.get_data()) if b'/home/paul/' in v or b'/mnt/e/' in v]
    result['source_path_strings'].append(strings)
result['limits']='Relocation-only code differences do not prove semantic equivalence of the referenced data. This records evidence for review, not byte-identical or runtime qualification.'
dest=k/'baseline-comparison001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sections':result['sections'],'path_string_counts':[len(v) for v in result['source_path_strings']]},indent=2))
