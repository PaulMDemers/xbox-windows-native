"""One ordered observation of real calls; backend is modeled only in host tests."""
import struct
from contracts import arguments,returned

def observe(b,s,calls):
    rows=[]
    for call in calls:
        label,thunk,ordinal,count,ret=call
        before=b.stop(b.handlers[thunk],label+'-entry')
        frame=list(struct.unpack('<'+'I'*(count+1),b.read(before['ESP'],4*(count+1),label+'-stack')))
        handle=struct.unpack('<I',b.read(s['entry498_handle'],4,label+'-handle-before'))[0]
        row=dict(label=label,ordinal=ordinal,before=before,stack=frame,handle_before=handle)
        b.record(row)
        arguments(call,frame,s,handle)
        if label=='create':
            obj=b.read(s['entry498_object'],12,'object')
            name=b.read(s['entry498_name'],8,'name')
            assert struct.unpack('<3I',obj)==(0,s['entry498_name'],0x40)
            length,maximum,pointer=struct.unpack('<HHI',name)
            expected=b'\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot510a\\entry.bin'
            assert (length,maximum,pointer)==(len(expected),len(expected)+1,s['entry498_path'])
            assert b.read(pointer,length+1,'path')==expected+b'\0'
        after=b.stop(ret,label+'-return')
        iosb=list(struct.unpack('<2I',b.read(s['entry498_iosb'],8,label+'-iosb-after')))
        handle=struct.unpack('<I',b.read(s['entry498_handle'],4,label+'-handle-after'))[0]
        row.update(after=after,iosb=iosb,handle_after=handle)
        b.record(row)
        returned(call,before,after,iosb,handle)
        rows.append(row)
    return rows
