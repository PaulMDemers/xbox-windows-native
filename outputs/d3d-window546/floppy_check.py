"""Independent strict FAT12 test-floppy decoder, no writes or guest access."""
import hashlib,struct


def validate(raw,wanted):
    if len(raw)!=1474560 or raw[510:512]!=b'\x55\xaa':raise ValueError('Floppy length/signature')
    bps,spc,res,nfat,nroot,total,media,spf,spt,heads,hidden,large=struct.unpack_from('<HBHBHHBHHHII',raw,11)
    if (bps,spc,res,nfat,nroot,total,media,spf,spt,heads,hidden,large)!=(512,1,1,2,224,2880,0xf0,9,18,2,0,0):raise ValueError('Geometry')
    fat=raw[512:512+4608]
    if fat!=raw[512+4608:512+9216] or fat[:3]!=b'\xf0\xff\xff':raise ValueError('FAT copies')
    def next_cluster(c):
        n=int.from_bytes(fat[c+c//2:c+c//2+2],'little')
        return (n>>4 if c&1 else n)&0xfff
    entries={};used=set()
    for at in range(19*512,33*512,32):
        e=raw[at:at+32]
        if e[0]==0:
            if any(raw[at:33*512]):raise ValueError('Hidden directory entries')
            break
        if e[11]!=32 or e[0]==0xe5:raise ValueError('Unexpected entry')
        name=e[:8].decode('ascii').rstrip()+'.'+e[8:11].decode('ascii').rstrip()
        if name not in wanted or name in entries:raise ValueError('Unexpected file')
        c=struct.unpack_from('<H',e,26)[0];size=struct.unpack_from('<I',e,28)[0]
        if size!=len(wanted[name]) or size==0:raise ValueError('File size')
        data=bytearray()
        for _ in range((size+511)//512):
            if not 2<=c<2849 or c in used:raise ValueError('Crosslink/range/cycle')
            used.add(c);start=(33+c-2)*512;data+=raw[start:start+512];c=next_cluster(c)
        if not 0xff8<=c<=0xfff or data[:size]!=wanted[name] or any(data[size:]):raise ValueError('Chain/content/padding')
        entries[name]=dict(bytes=size,sha256=hashlib.sha256(data[:size]).hexdigest())
    if set(entries)!=set(wanted):raise ValueError('Missing files')
    for c in range(2,2849):
        if c not in used and next_cluster(c):raise ValueError('Orphan cluster')
    return dict(passed=True,bytes=len(raw),files=entries,allocated_clusters=len(used))
