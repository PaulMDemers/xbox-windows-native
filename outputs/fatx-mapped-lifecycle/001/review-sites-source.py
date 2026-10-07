from pathlib import Path
import hashlib,json,sys
ws=Path.cwd();k=ws/'outputs/fatx-mapped-lifecycle'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile,capstone
p=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/setupapi.dll')
raw=p.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='1d0a6e9d062a51e71eaae93d776746823834f5c518096d340f2b332fc059a23d'
pe=pefile.PE(data=raw);base=pe.OPTIONAL_HEADER.ImageBase;assert base==0x77880000
imports={v.address:(v.name or b'').decode() for d in pe.DIRECTORY_ENTRY_IMPORT for v in d.imports}
dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);bounds={}
for lo,hi in [(0x77893cb5,0x77893d76),(0x77893da6,0x77893ef8),(0x77893f87,0x77894270)]:
    for i in dis.disasm(pe.get_data(lo-base,hi-lo),lo):bounds[i.address]=i
definitions=[('outer_entry',0x77893f87,None),('mapping_call',0x77893e69,'CreateFileMappingW'),('mapping_return',0x77893e6f,None),('view_call',0x77893e7f,'MapViewOfFile'),('view_return',0x77893e85,None),('helper_return',0x77894020,None),('seek_call',0x778940e2,'SetFilePointer'),('seek_return',0x778940e8,None),('cleanup_call',0x77894121,None),('unmap_call',0x77893ce8,'UnmapViewOfFile'),('unmap_return',0x77893cee,None),('close_mapping_call',0x77893d05,'CloseHandle'),('close_mapping_return',0x77893d0b,None),('eof_call',0x77893d28,'SetEndOfFile'),('eof_return',0x77893d2e,None),('close_file_call',0x77893d50,'CloseHandle'),('close_file_return',0x77893d56,None),('outer_return',0x77894129,None)]
sites=[]
for name,address,api in definitions:
    i=bounds[address];data=bytes(i.bytes)
    if api:assert data[:2]==b'\xff\x15' and imports[int.from_bytes(data[2:6],'little')]==api
    sites.append(dict(name=name,address=address,bytes=data.hex(),instruction=i.mnemonic+' '+i.op_str,api=api))
out=k/'sites.json';assert not out.exists()
out.write_text(json.dumps(dict(scope='Static candidate mapped-append lifecycle; runtime use remains unproven',source_sha256=sha(Path(__file__).read_bytes()),setupapi_sha256=sha(raw),base=base,timestamp=pe.FILE_HEADER.TimeDateStamp,sites=sites),indent=2)+'\n')
print('Reviewed18 candidate boundaries against pinned original SetupAPI')
