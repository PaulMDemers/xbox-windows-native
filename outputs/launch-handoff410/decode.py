"""Decode bounded preparation evidence; never infer successful paging/handoff."""
import struct


def decode(data):
    if len(data) != 144:
        raise ValueError('Incomplete or oversized report')
    r = struct.unpack('<36I', data)
    if r[:4] != (0x30313458, 1, 128, 0x41000101) or r[32:] != (0x454e4f44, 1, 0x41000101, 128):
        raise ValueError('Header/trailer identity')
    phase = r[5]
    if phase not in (1, 2, 3, 5, 6, 7) or r[12] != 288316 or r[15] or any(r[30:32]):
        raise ValueError('Phase/payload/create/reserved')
    if (r[16], r[18], r[19], r[20]) != (1024, 80, 74, 224) or r[17] != 70310:
        raise ValueError('Pinned compiled layout')
    if phase == 1:
        if any(r[6:10]) or r[10] != 0xeeeeeeee or r[13] or r[14]:
            raise ValueError('First allocation refusal')
    else:
        if r[6] != (r[7] | 0x80000000) or r[7] % 4096 or not 0x200000 <= r[7] <= 0x1f00000:
            raise ValueError('Payload allocation range/identity')
        if bool(r[13] & 0x400) != (phase == 5):
            raise ValueError('Copy direction')
        if phase in (2, 5):
            if r[8] or r[9] or r[10] != 0xeeeeeeee or r[14]:
                raise ValueError('Unexpected loader state')
        else:
            if not r[8] or r[8] % 4096 or not 0x1000000 <= r[14] <= 0x2000000 or r[14] % 4096:
                raise ValueError('Loader allocation')
            if phase == 3 and not r[10] & 0x80000000:
                raise ValueError('Missing virtual failure')
            if phase in (6, 7) and r[10] != 0:
                raise ValueError('Virtual allocation status')
    if phase == 7:
        expected = 1 if r[11] != 4096 else 2 if r[9] != r[14] else 3 if r[8] != r[9]+0x80000000 else 0
        if not expected or r[29] != expected or any(r[21:29]):
            raise ValueError('Refusal reason/order')
    elif phase != 6:
        if any(r[21:30]):
            raise ValueError('Unexpected post-copy evidence')
    else:
        if r[11] != 4096 or r[9] != r[14] or r[8] != r[9]+0x80000000 or r[29]:
            raise ValueError('Unmet mapping precondition')
        if r[21] % 4096 or not 0 < r[21] < 0x4000000 or r[27] != 1:
            raise ValueError('Queried physical mapping/precondition marker')
        if any(v not in (0, 1) for v in r[24:27]):
            raise ValueError('Invalid comparison boolean')
        if (r[26] and r[22] != r[9]+r[18]) or (r[25] and r[23] != r[9]+r[18]):
            raise ValueError('Comparison/target contradiction')
    passed = phase == 6 and r[24:27] == (1, 1, 1) and not r[28] & 0x400
    return dict(record_complete=True, phase=phase, preparation_verified=passed,
                kernel_virtual=r[6], kernel_physical=r[7], loader_virtual=r[8],
                loader_physical=r[14], virtual_alias=r[9], alias_backing_physical=r[21],
                low_jump_target=r[22], high_jump_target=r[23],
                payload_exact=bool(r[24]), high_loader_exact=bool(r[25]), low_loader_exact=bool(r[26]),
                loader_copy_bytes=r[16], critical_span_bytes=r[20], refusal_reason=r[29],
                paging_transition_executed=False, windows_started=False,
                historical_failure_cause_established=False)
