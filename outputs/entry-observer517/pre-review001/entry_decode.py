"""MIT. Independent early-entry transport decoder, not a boot qualifier."""
import struct

def decode(data):
    if len(data) != 112:
        raise ValueError('incomplete or oversized entry receipt')
    w = struct.unpack('<28I', data)
    if data[:4] != b'E498' or w[1:4] != (1,96,0x49800101):
        raise ValueError('entry schema/cookie')
    if any(w[19:24]) or not w[4] & 2 or any(x > 0xffff for x in w[13:19]):
        raise ValueError('reserved/flags/selector fields')
    h = 2166176261
    for b in data[:96]:
        h = ((h ^ b) * 16777619) & 0xffffffff
    if data[96:100] != b'DONE' or w[25:] != (h,0x49800101,96):
        raise ValueError('entry trailer/checksum')
    return dict(entry_witness=True, xbe_entry_proof_requires_actual_provenance=True,
                flags=w[4], registers=dict(zip(('edi','esi','ebp','esp','ebx','edx','ecx','eax'),w[5:13])),
                selectors=dict(zip(('cs','ds','es','ss','fs','gs'),w[13:19])),
                final_flush_or_close_proved=False, preparation_proved=False,
                windows_boot_proved=False, graphics_qualified=False)
