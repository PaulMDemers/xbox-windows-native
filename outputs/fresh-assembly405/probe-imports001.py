import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'work/python-packages'));import pefile
r=json.loads((K/'probe-build001.json').read_text());p=Path(r['artifact']['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['artifact']['sha256']
root=Path('/mnt/c/xwn405/extract004/files/WINNT/system32');files={p.name.lower():p for p in root.iterdir() if p.is_file()};pe=pefile.PE(str(p));rows=[]
assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.MajorSubsystemVersion==5
for library in pe.DIRECTORY_ENTRY_IMPORT:
    name=library.dll.decode().lower();dll=pefile.PE(str(files[name]));exports={v.name.decode():v for v in dll.DIRECTORY_ENTRY_EXPORT.symbols if v.name}
    for item in library.imports:
        assert item.name;symbol=item.name.decode();assert symbol in exports,(name,symbol)
        rows.append(dict(library=name,symbol=symbol,forwarder=exports[symbol].forwarder.decode() if exports[symbol].forwarder else None))
    dll.close()
pe.close();(K/'probe-imports001.json').write_text(json.dumps(dict(passed=True,imports=rows,scope='Actual fresh404 NT5 exports; no runtime claim'),indent=2)+'\n');print('NT5 imports verified',len(rows))
