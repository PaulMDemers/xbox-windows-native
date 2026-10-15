import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha
build=json.loads((K/'probe-build004.json').read_text());seed=json.loads((K/'assembly004.json').read_text())
disk=Path(seed['fixture_path_linux']);assert sha(disk)==seed['fixture_sha256']
m.fatx.PARTITIONS['E']=(5633024*512,10000048*512);rows=[]
with ColdIO(disk) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'));exports={}
    def symbols(name):
        if name not in exports:
            b=wr.read('winnt/system32/'+name);pe=pefile.PE(data=b)
            exports[name]=({v.name.decode():v.forwarder for v in pe.DIRECTORY_ENTRY_EXPORT.symbols if v.name},m.sha(b));pe.close()
        return exports[name]
    for row in build:
        p=Path(row['path']);assert sha(p)==row['sha256'];pe=pefile.PE(str(p));assert pe.FILE_HEADER.Machine==0x14c
        for library in pe.DIRECTORY_ENTRY_IMPORT:
            name=library.dll.decode().lower();syms,digest=symbols(name)
            for v in library.imports:
                assert v.name;symbol=v.name.decode();assert symbol in syms,(name,symbol)
                rows.append(dict(artifact=row['name'],library=name,library_sha256=digest,symbol=symbol))
        pe.close()
    for name,symbol in [('newdev.dll','UpdateDriverForPlugAndPlayDevicesA'),('cfgmgr32.dll','CM_Get_DevNode_Status')]:
        syms,digest=symbols(name);assert symbol in syms;rows.append(dict(dynamic=True,library=name,library_sha256=digest,symbol=symbol))
(K/'probe-imports004.json').write_text(json.dumps(dict(passed=True,actual_fresh_image_exports=rows),indent=2)+'\n');print('Install witness imports verified',len(rows))
