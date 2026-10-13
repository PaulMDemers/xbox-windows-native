"""Pure x86 observation decoders; no guest writes or qualification policy."""
import struct
def surface(raw,address):
    assert len(raw)==52 and 0<address<=0xffffffff
    v=struct.unpack('<12I2H',raw)
    return dict(address=address,raw=raw.hex(),dhsurf=v[0],hsurf=v[1],dhpdev=v[2],hdev=v[3],width=v[4],height=v[5],cjBits=v[6],pvBits=v[7],pvScan0=v[8],stride=struct.unpack_from('<i',raw,36)[0],uniq=v[10],format=v[11],type=v[12],flags=v[13])
def paired(call,address,stack,thread,process):
    return (call['return_address']==address and call['expected_return_sp']==stack
            and call['thread']==thread and call['process']==process and not call['returned'])
