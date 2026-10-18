"""Read-only two-stop trampoline observer; transport is supplied by caller."""
import struct

FIELDS = ('EAX','EBX','ECX','EDX','ESI','EDI','EBP','ESP','EFL','CR0','CR3','CR4')
ENTRY, TARGET, GUARD = 0x11100, 0x94aff, 0x11105

def checked_state(row, address):
    if not isinstance(row, dict) or not isinstance(row.get('registers'), dict):
        raise ValueError('missing register record')
    r = row['registers']
    for name in FIELDS + ('EIP',):
        if type(r.get(name)) is not int or not 0 <= r[name] <= 0xffffffff:
            raise ValueError('missing or invalid '+name)
    if r['EIP'] != address:
        raise ValueError('wrong stop')
    return r

def verify_stub(header, stub, image):
    if len(header) != 4096 or len(stub) != 5 or len(image) != 545088:
        raise ValueError('capture length')
    if struct.unpack_from('<I', header, 0x128)[0] != ENTRY:
        raise ValueError('loaded entry')
    if stub[0] != 0xe9 or ENTRY + 5 + struct.unpack_from('<i', stub, 1)[0] != TARGET:
        raise ValueError('opcode or target')
    if stub != image[0x1100:0x1105] or struct.unpack_from('<I', image, 0x128)[0] ^ 0xa8fc57ab != ENTRY:
        raise ValueError('pinned image mismatch')

def observe_trampoline(low, image, capture, advance, bp):
    """Caller owns cleanup for all breakpoints, including failure paths."""
    before = checked_state(low, ENTRY)
    header = capture(0x10000, 4096, 'trampoline-loaded-header')
    stub = capture(ENTRY, 5, 'trampoline-five-bytes')
    verify_stub(header, stub, image)
    bp(GUARD, True)
    after_row = advance(TARGET, 'early-entry')
    after = checked_state(after_row, TARGET)
    for name in FIELDS:
        if before[name] != after[name]:
            raise ValueError('jump changed '+name)
    return after_row, dict(entry=ENTRY, target=TARGET, guard=GUARD,
                          stub_hex=stub.hex(), compared_fields=list(FIELDS),
                          before=dict(before), after=dict(after), passed=True)
