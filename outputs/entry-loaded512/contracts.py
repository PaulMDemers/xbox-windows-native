"""Exact499 call-site/argument contract; interfaces do not claim actual execution."""
import struct
def plan(xbe,s):
 start=s['entry498_gate'];end=s['entry498_fail'];code=xbe[start-0x10000:end-0x10000]
 def indirect(name):
  needle=b'\xff\x15'+struct.pack('<I',s[name]);assert code.count(needle)==1
  return start+code.index(needle)+6
 writes=[]
 for i in range(len(code)-5):
  if code[i]==0xe8 and (start+i+5+struct.unpack_from('<i',code,i+1)[0])==s['entry498_write']:writes.append(start+i+5)
 assert len(writes)==2
 return [('create','DiagNtCreateFile',190,9,indirect('DiagNtCreateFile')),
 ('body','DiagNtWriteFile',236,8,writes[0]),('flush1','DiagNtFlushBuffersFile',198,2,indirect('DiagNtFlushBuffersFile')),
 ('trailer','DiagNtWriteFile',236,8,writes[1]),('flush2','DiagNtFlushBuffersFile',198,2,indirect('DiagNtFlushBuffersFile')),
 ('close','DiagNtClose',187,1,indirect('DiagNtClose'))]
def arguments(row,words,s,handle):
 label,_,_,count,ret=row;assert len(words)==count+1 and words[0]==ret
 a=list(words[1:]);io=s['entry498_iosb']
 if label=='create':expected=[s['entry498_handle'],0x40100000,s['entry498_object'],io,0,0x80,0,2,0x62]
 elif label in ('body','trailer'):
  assert 0<handle<=0xffffffff
  expected=[handle,0,0,0,io,s['entry498_record'] if label=='body' else s['entry498_trailer'],96 if label=='body' else 16,0]
 elif label.startswith('flush'):expected=[handle,io];assert handle>0
 else:expected=[handle];assert handle>0
 assert a==expected
 return True
def returned(row,before,after,iosb,handle):
 label,_,_,count,_=row
 assert after['EAX']==0 and after['ESP']==before['ESP']+4*(count+1)
 if label=='create':assert handle>0 and iosb==[0,2]
 elif label in ('body','trailer'):assert iosb==[0,96 if label=='body' else 16]
 elif label.startswith('flush'):assert iosb[0]==0
 return True
