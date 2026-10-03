"""Static packaging gate for this pinned i386 FreeLoader/Cromwell chain."""
import argparse,hashlib,json,pathlib,struct

def validate(data):
    if not 0x900 <= len(data) <= 0x80000:
        raise ValueError('FreeLoader must fit Cromwell\'s 512 KiB staging limit')
    header=None
    for offset in range(0,min(8192,len(data))-31,4):
        words=struct.unpack_from('<8I',data,offset)
        if words[0]==0x1badb002 and sum(words[:3])&0xffffffff==0:
            header=(offset,words);break
    if header is None: raise ValueError('No valid aligned Multiboot v1 address header in first 8 KiB')
    offset,(_,flags,_,address,load,end,bss,entry)=header
    if flags!=0x10003: raise ValueError('Unexpected Multiboot flags for pinned chain')
    if load!=0x200000 or address-load!=offset: raise ValueError('Unexpected staging address/header mapping')
    loaded_end=end or load+len(data)
    if not load<=entry<loaded_end: raise ValueError('Entry is outside initialized image')
    if loaded_end!=load+len(data) or (bss and bss<loaded_end): raise ValueError('Unsupported image/BSS extent')
    if max(loaded_end,bss)>=0x03c00000: raise ValueError('Staged image reaches reserved framebuffer')
    pe_base=0x800
    if data[pe_base:pe_base+2]!=b'MZ': raise ValueError('Expected PE image at offset 0x800')
    pe=pe_base+struct.unpack_from('<I',data,pe_base+0x3c)[0]
    if pe+84>len(data) or data[pe:pe+4]!=b'PE\0\0': raise ValueError('Invalid PE header')
    if struct.unpack_from('<H',data,pe+4)[0]!=0x14c: raise ValueError('Expected i386 PE')
    if struct.unpack_from('<H',data,pe+24)[0]!=0x10b: raise ValueError('Expected PE32')
    size=struct.unpack_from('<I',data,pe+24+56)[0]
    if size==0 or 0x10000+size>0xa0000: raise ValueError('Relocated image does not fit low-memory window')
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'multiboot_header_offset':offset,
        'staging_address':hex(load),'entry_address':hex(entry),'relocated_pe_end':hex(0x10000+size),
        'scope':'Packaging constraints only; does not prove runtime memory safety or a working boot.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('freeldr',type=pathlib.Path)
    args=parser.parse_args()
    try: print(json.dumps(validate(args.freeldr.read_bytes()),indent=2))
    except (ValueError,struct.error) as error: parser.exit(1,str(error)+'\n')
