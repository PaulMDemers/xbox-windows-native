"""Prove both compiled idle helpers differ only in identical imported addresses."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k.parents[1]/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text());review=read(k/'nvnet-review.json');rows=[];normalized=[]
for case in ['control001','candidate001']:
    rec=review[case];p=k/'artifacts'/rec['name'];assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'];pe=pefile.PE(str(p))
    start=int(rec['functions']['_NvNetIdleTransmitter']['rva'],16);size=sum(len(bytes.fromhex(v['bytes'])) for v in rec['disassembly']['_NvNetIdleTransmitter']);raw=bytearray(pe.get_data(start,size))
    imports={v.address:(d.dll.decode().lower(),v.name.decode()) for d in pe.DIRECTORY_ENTRY_IMPORT for v in d.imports};rel=[]
    for block in pe.DIRECTORY_ENTRY_BASERELOC:
        for e in block.entries:
            if e.type==3 and start<=e.rva<start+size:
                off=e.rva-start;assert off+4<=size;target=struct.unpack_from('<I',raw,off)[0];assert target in imports
                rel.append(dict(offset=off,target=list(imports[target])));struct.pack_into('<I',raw,off,0)
    normalized.append(bytes(raw));rows.append(dict(case=case,bytes=size,relocations=rel,normalized_sha256=hashlib.sha256(raw).hexdigest()))
assert normalized[0]==normalized[1] and rows[0]['relocations']==rows[1]['relocations']
r=dict(passed=True,scope=__doc__,rows=rows,limits='Checks the entire176-byte compiled helper. Entry placement changes; no instruction change beyond identical import-address relocations. Runtime callback completion is separate.')
(k/'helper-equivalence.json').write_text(json.dumps(r,indent=2)+'\n');print('176-byte helper instruction stream identical after resolving imported addresses')
