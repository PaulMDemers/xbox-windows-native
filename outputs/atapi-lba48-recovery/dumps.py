"""Bounded cold enumeration of saved dump files, using the existing FATX reader."""
import struct
def dump_files(reader):
    paths=[]
    try:
        at=1
        for part in ['winnt','minidump']:
            entry=reader.directory(at)['entries'][part][2]
            assert entry[1]&16
            at=struct.unpack_from('<I',entry,44)[0]
        entries=reader.directory(at)['entries']
        assert len(entries)<256
        paths.extend('winnt/minidump/'+name for name,(_,_,e) in entries.items()
                     if not e[1]&16 and name.endswith('.dmp'))
    except KeyError:
        pass
    try:reader.read('winnt/memory.dmp');paths.append('winnt/memory.dmp')
    except KeyError:pass
    return {path:reader.read(path) for path in paths}
def cookie(data):
    return len(data)==65536 and data[:8]==b'PAGEDUMP' and struct.unpack_from('<5I',data,40)==(0xe058d103,0x44554d50,0x103,0x10000,1)
