"""Read an NT5 VK's declared bytes without string/type reinterpretation."""
import struct

def stored_value(data, vk_offset):
    if vk_offset < 0 or vk_offset + 20 > len(data) or data[vk_offset:vk_offset+2] != b'vk':
        raise ValueError('Invalid VK bounds/signature')
    length, offset, typ = struct.unpack_from('<III', data, vk_offset + 4)
    if length & 0x80000000:
        length &= 0x7fffffff
        if length > 4:
            raise ValueError('Oversized inline data')
        return typ, data[vk_offset+8:vk_offset+8+length]
    if length == 0:
        return typ, b''
    cell = 4096 + offset
    if cell < 4096 or cell + 4 > len(data):
        raise ValueError('Data cell outside hive')
    size = struct.unpack_from('<i', data, cell)[0]
    if size >= 0 or cell - size > len(data) or length > -size - 4:
        raise ValueError('Unallocated/short data cell; segmented data unsupported')
    return typ, data[cell+4:cell+4+length]
