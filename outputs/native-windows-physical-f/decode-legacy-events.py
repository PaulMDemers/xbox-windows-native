"""Recover validated EVENTLOGRECORDs from local legacy EVT files; no execution.

This is a record scan, including potentially stale records outside the active
ring. It does not render message DLLs or claim every record belongs to this boot.
Layout: https://learn.microsoft.com/windows/win32/api/winnt/ns-winnt-eventlogrecord
"""
import pathlib,struct,json,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('input',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
data=a.input.read_bytes();records=[]
def string(b,at,limit):
 start=at
 while at+2<=limit:
  if b[at:at+2]==b'\0\0':return b[start:at].decode('utf-16le'),at+2
  at+=2
 raise ValueError('Unterminated record string')
for off in range(0,len(data)-60,4):
 if data[off+4:off+8]!=b'LfLe':continue
 n=struct.unpack_from('<I',data,off)[0]
 if n<60 or n%4 or off+n>len(data) or struct.unpack_from('<I',data,off+n-4)[0]!=n:continue
 b=data[off:off+n]
 length,magic,number,generated,written,event,kind,count,category,flags,closing,strings,sidlen,sidoff,datalen,dataoff=struct.unpack_from('<6I4H6I',b)
 if count>1024 or strings>n-4 or dataoff+datalen>n-4 or sidoff+sidlen>n-4:continue
 try:
  source,at=string(b,56,n-4);computer,at=string(b,at,n-4);values=[];at=strings
  for _ in range(count):value,at=string(b,at,n-4);values.append(value)
 except (ValueError,UnicodeError):continue
 records.append({'offset':off,'record':number,'generated_unix':generated,'written_unix':written,'event_id_hex':f'{event:08x}','event_id':event&65535,'type':kind,'source':source,'computer':computer,'strings':values,'data_hex':b[dataoff:dataoff+datalen].hex()})
r={'scope':__doc__,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'records':sorted(records,key=lambda x:x['record'])}
a.output.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r['records'][-35:],indent=2))
