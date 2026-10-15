"""Pin actual native probe imports and event message text from owned installed files."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
r=json.loads((K/'assembly003.json').read_text());disk=Path(r['fixture_path_linux']);assert sha(disk)==r['fixture_sha256']
build=json.loads((K/'probe-build002.json').read_text())[0];exe=Path(build['path']);assert sha(exe)==build['sha256']
imports=[];messages=[];m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with ColdIO(disk) as io:
    w=m.Writer(io,m.fatx.open_partition(io,disk,'E'));pe=pefile.PE(str(exe))
    for lib in pe.DIRECTORY_ENTRY_IMPORT:
        name=lib.dll.decode();b=w.read('WINNT/system32/'+name);p=pefile.PE(data=b)
        exports={s.name for s in p.DIRECTORY_ENTRY_EXPORT.symbols}
        for sym in lib.imports:assert sym.name in exports;imports.append(dict(library=name,symbol=sym.name.decode(),library_sha256=m.sha(b)))
        p.close()
    pe.close()
    for path,targets in [('IoLogMsg.dll',[0x80050001,0xc0040031]),('drivers/kbdhid.sys',[0x80050001]),('drivers/ftdisk.sys',[0xc0040031]),('umpnpmgr.dll',[0x80000100,0x100])]:
        data=w.read('WINNT/system32/'+path);p=pefile.PE(data=data)
        for kind in getattr(p,'DIRECTORY_ENTRY_RESOURCE',type('R',(),{'entries':[]})()).entries:
            if kind.id!=11:continue
            for entry in kind.directory.entries:
                for language in entry.directory.entries:
                    d=language.data.struct;b=p.get_data(d.OffsetToData,d.Size);blocks=struct.unpack_from('<I',b)[0]
                    for i in range(blocks):
                        low,high,offset=struct.unpack_from('<III',b,4+i*12)
                        for ident in range(low,high+1):
                            length,flags=struct.unpack_from('<HH',b,offset);assert length>=4 and offset+length<=len(b)
                            if ident in targets:messages.append(dict(file=path,sha256=m.sha(data),event_hex=f'{ident:08x}',language=language.id,message=b[offset+4:offset+length].decode('utf-16le' if flags&1 else 'cp1252').rstrip('\0')))
                            offset+=length
        p.close()
out=dict(probe_sha256=sha(exe),imports=imports,event_messages=messages,scope='Exact installed module resource meaning, not attribution of the runtime producer')
with (K/'review-imports001.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(dict(imports=len(imports),messages=messages)))
