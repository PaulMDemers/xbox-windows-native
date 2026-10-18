"""Independent fixed transport decoder. Receipt fields are not future completion."""
import struct
def decode(data,stage=2):
 if len(data)!=48:raise ValueError('receipt length')
 v=struct.unpack('<12I',data)
 if data[:4]!=b'X528' or v[1:5]!=(1,48,528,stage) or stage not in (1,2):raise ValueError('header/stage')
 if v[5]!=1 or v[6]!=0 or not 0<v[7]<=65535 or v[8]>65535:raise ValueError('kernel fields')
 if v[9]!=stage-1 or v[10]!=0:raise ValueError('flags/reserved')
 h=2166136261
 for b in data[:44]:h=((h^b)*16777619)&0xffffffff
 if v[11]!=h:raise ValueError('checksum')
 return dict(stage=stage,kernel=list(v[5:9]),runtime_entry=True,
             begin_write_flush_close_readback_proved=stage==2,
             own_final_close_proved=False,firmware_return_proved=False,windows_boot_proved=False)
