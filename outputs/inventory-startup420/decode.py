"""Independent bounded decoder; an incomplete trace never qualifies completion."""
import json
import struct
import sys
from pathlib import Path

def decode(data):
    if len(data) > 65536 or len(data) % 32:
        raise ValueError('Trace size or partial record')
    rows = []
    for i in range(len(data) // 32):
        row = struct.unpack_from('<8I', data, i * 32)
        check = 0
        for value in row[:7]: check ^= value
        if row[0] != 0x58573420 or row[1] != i or row[6] or row[7] != check:
            raise ValueError('Invalid record identity/sequence/checksum')
        if row[2] not in {0, 1, 2, 3, 4, 5, 6, 7, 20, 21, 30, 31, 32, 33} or row[3] > 1:
            raise ValueError('Unknown stage/phase')
        rows.append(dict(stage=row[2], phase=row[3], arg=row[4], result=row[5]))
    if not rows or rows[0] != dict(stage=0, phase=1, arg=0, result=0):
        raise ValueError('Missing application entry')
    calls = []
    pending = None
    terminal = False
    for row in rows[1:]:
        if terminal: raise ValueError('Data after reboot request')
        if row['stage'] == 33:
            if pending or row['phase'] != 0 or row['arg'] or row['result']:
                raise ValueError('Invalid/error terminal')
            terminal = True
        elif row['phase'] == 0:
            if pending: raise ValueError('Nested uncompleted operation')
            pending = row
        else:
            if not pending or row['stage'] != pending['stage']:
                raise ValueError('Unpaired completion')
            if row['stage'] != 7 and row['arg'] != pending['arg']:
                raise ValueError('Changed call argument')
            calls.append(row)
            pending = None
    complete = False
    if terminal:
        at = 0
        def take(stage):
            nonlocal at
            if at >= len(calls) or calls[at]['stage'] != stage:
                raise ValueError('Missing/reordered required operation')
            row = calls[at]; at += 1
            return row
        for stage in range(1, 7):
            row = take(stage)
            if stage in (1, 6) and row['result'] != 1: raise ValueError('E unavailable')
            if stage == 2 and row['result']: raise ValueError('Memory query failed')
        modes = 0
        while True:
            row = take(7); modes += 1
            if row['result'] == 0: break
            if row['result'] != 1 or modes >= 128: raise ValueError('Invalid modes')
        for slot in [(bus << 8) | device | (function << 5)
                     for bus in range(2) for device in range(32) for function in range(8)]:
            row = take(20)
            if row['arg'] != slot: raise ValueError('Missing/reordered PCI slot')
            if row['result'] & 0xffff not in (0, 65535):
                row = take(21)
                if row['arg'] != slot: raise ValueError('PCI class slot mismatch')
        if take(30)['result']: raise ValueError('Report save failed')
        if take(31)['result'] != 1: raise ValueError('Display setup failed')
        take(32)
        if at != len(calls): raise ValueError('Extra calls')
        complete = True
    return dict(records=len(rows), complete=complete, terminal_reboot_request=terminal,
                last_record=rows[-1], pending_call=pending, calls=calls)

if __name__ == '__main__':
    print(json.dumps(decode(Path(sys.argv[1]).read_bytes()), indent=2))
