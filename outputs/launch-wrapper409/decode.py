"""Independent parser: complete record is not proof of the historical failure cause."""
import struct

def decode(data):
    if len(data)!=80: raise ValueError('Incomplete or oversized report')
    r=struct.unpack('<20I',data)
    if r[:4]!=(0x39303458,1,64,0x40900101) or r[16:]!=(0x454e4f44,1,0x40900101,64):
        raise ValueError('Wrong version, cookie, size or completion trailer')
    phase=r[5]
    if phase not in (1,2,3,4,5) or r[12]!=288316 or r[15]!=0:
        raise ValueError('Unknown phase, payload or file creation result')
    if phase==1:
        if any(r[6:10]) or r[10]!=0xeeeeeeee or r[13] or r[14]:raise ValueError('Invalid first-allocation refusal')
    else:
        if r[6]!=(r[7]|0x80000000) or r[7]%4096 or not 0x200000<=r[7]<=0x1f00000:
            raise ValueError('Invalid payload allocation identity/range')
        if phase in (2,5):
            if r[8] or r[9] or r[10]!=0xeeeeeeee or r[14]:raise ValueError('Unexpected loader state')
        else:
            if r[8]!=(r[14]|0x80000000) or r[14]%4096 or not 0x1000000<=r[14]<=0x1fff000:
                raise ValueError('Invalid loader allocation identity/range')
            if phase==3 and not r[10]&0x80000000:raise ValueError('Missing virtual allocation failure')
            if phase==4 and (r[10]!=0 or r[9]!=r[14] or r[11]!=4096):
                raise ValueError('Invalid virtual allocation success')
        if bool(r[13]&0x400)!=(phase==5):raise ValueError('Direction flag/phase mismatch')
    return dict(record_complete=True,phase=phase,
                outcome={1:'payload_allocation_null',2:'loader_allocation_null',3:'virtual_allocation_failed',
                         4:'allocation_prefix_completed',5:'backward_copy_flag_observed'}[phase],
                entry_eflags=r[4],kernel_virtual=r[6],kernel_physical=r[7],loader_virtual=r[8],
                loader_physical=r[14],virtual_alias=r[9],virtual_status=r[10],virtual_size=r[11],
                copy_eflags=r[13],original_payload_bytes=r[12],
                windows_started=False,historical_failure_cause_established=False)
