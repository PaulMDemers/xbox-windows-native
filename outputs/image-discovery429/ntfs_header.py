# SPDX-License-Identifier: MIT
"""Validate the narrow 512-byte-sector NTFS image geometry, not MFT integrity."""
import struct
from reader import require
def validate(boot,backup,byte_length,absolute_start,serial):
    require(type(boot) is bytes and len(boot)==512 and type(backup) is bytes and backup==boot,'primary/backup boot sector')
    require(boot[3:11]==b'NTFS    ' and boot[510:]==b'\x55\xaa','NTFS/signature')
    sector=struct.unpack_from('<H',boot,11)[0];spc=boot[13]
    require(sector==512 and spc in (1,2,4,8,16,32,64,128),'NTFS sector/cluster')
    require(byte_length%512==0 and absolute_start%512==0 and 0<absolute_start//512<=0xffffffff,'NTFS projection bounds')
    total,mft,mirror=struct.unpack_from('<QQQ',boot,40)
    require(total==byte_length//512-1,'NTFS data sector count excludes backup')
    require(struct.unpack_from('<I',boot,28)[0]==absolute_start//512,'HiddenSectors mismatch')
    require(0<mft<total//spc and 0<mirror<total//spc and mft!=mirror,'MFT clusters')
    sizes=[]
    for at in (64,68):
        n=struct.unpack_from('<b',boot,at)[0]
        require(n in (1,2,4,8,16,32,64) or -16<=n<=-9,'record encoding')
        size=(1<<-n) if n<0 else n*sector*spc
        require(512<=size<=65536 and size&(size-1)==0,'record size');sizes.append(size)
    require(struct.unpack_from('<Q',boot,72)[0]==serial and serial!=0,'NTFS serial')
    return dict(sector=sector,sectors_per_cluster=spc,data_sectors=total,backup_sector=total,
                mft_lcn=mft,mirror_lcn=mirror,record_bytes=sizes[0],index_bytes=sizes[1],hidden_sectors=absolute_start//512)
