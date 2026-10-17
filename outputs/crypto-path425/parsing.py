"""Bounded x86 native file arguments; filenames only, never file payloads."""
import struct
def user_span(p,n):
    assert isinstance(p,int) and 0x10000<=p<0x80000000 and 0<=n<=4096
    assert p+n<=0x80000000
def words(read,p,n):
    user_span(p,n*4);b=read(p,n*4);assert len(b)==n*4
    return list(struct.unpack('<'+'I'*n,b))
def object_name(read,p):
    v=words(read,p,6);assert v[0]==24
    if v[2]:user_span(v[2],8)
    length,maximum,buffer=struct.unpack('<HHI',read(v[2],8)) if v[2] else (0,0,0)
    assert length%2==0 and length<=maximum<=4096 and length<=2048
    if length:
        user_span(v[2],8);user_span(buffer,length)
        data=b''.join(read(buffer+i,min(256,length-i)) for i in range(0,length,256))
        assert len(data)==length
        name=data.decode('utf-16le',errors='strict');assert '\0' not in name
    else:name=''
    return {'attributes_address':p,'attributes':v[3],'root_handle':v[1],
            'name_bytes':length,'name':name,'absolute_name_observed':v[1]==0 and name.startswith('\\'),
            'root_handle_resolution':'not attempted; relative roots remain unknown'}
def pair_key(thread,process,stack,api):
    assert 0x80000000<=thread<=0xfffffffc and 0x80000000<=process<=0xfffffffc
    user_span(stack,4);assert api in ['NtCreateFile','NtOpenFile','NtQueryAttributesFile','NtQueryFullAttributesFile']
    return thread,process,stack,api
