"""Synthetic complete checkpoint layouts: actual attestation code, no guest."""
import copy,hashlib,json,struct,sys
from pathlib import Path
from attest import Attestor
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'attestation-review001.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
plan=json.loads((k/'attestation-inputs001.json').read_text());pes={n:pefile.PE(str(ws/v['path'])) for n,v in plan['modules'].items()}
segments={};physical={};checks=0
def add(a,size):segments[a]=bytearray(size)
def put(a,data):
 for begin,b in segments.items():
  if begin<=a and a+len(data)<=begin+len(b):b[a-begin:a-begin+len(data)]=data;return
 raise AssertionError(hex(a))
def word(a,value):put(a,struct.pack('<I',value))
def read(a,n):
 assert not (0xa2000000<=a<0xa2004000),'Attestor read dirty arena'
 for begin,b in segments.items():
  if begin<=a and a+n<=begin+len(b):return bytes(b[a-begin:a-begin+n])
 raise AssertionError(('unmapped synthetic',hex(a),n))
def pread(a,n):return physical[a][:n]
def off(t,n):return plan['structures'][t]['fields'][n]['offset']
bases={'ntoskrnl.exe':plan['kernel_base_lead'],'probe.exe':0x16000000,'pattern.sys':0xfe660000}
for name,base in bases.items():
 pe=pes[name];buf=bytearray(pe.get_memory_mapped_image());buf.extend(bytes(pe.OPTIONAL_HEADER.SizeOfImage-len(buf)))
 for block in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]):
  for e in block.entries:
   if e.type==3:struct.pack_into('<I',buf,e.rva,(struct.unpack_from('<I',buf,e.rva)[0]+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 segments[base]=buf
for a in [0x81000000,0x81010000,0x81020000,0x81021000,0x81022000,0x81023000,0x81024000,0x81025000,0x81026000,0x81030000,0x81031000,0x81032000,0xffdff000,0x120000]:add(a,4096)
process=0x81000000;thread=0x81010000;table=0x81020000;header=0x81024000;owner=header+off('_OBJECT_HEADER','Body');dev=0x81025000;driver=0x81026000
word(0xffdff124,thread);word(thread+plan['thread_owner_offset'],process)
word(process+off('_EPROCESS','UniqueProcessId'),404);word(process+off('_EPROCESS','SectionBaseAddress'),bases['probe.exe'])
put(process+off('_EPROCESS','ImageFileName'),b'probe.exe\0');word(process+off('_KPROCESS','DirectoryTableBase'),0x1000)
word(process+off('_EPROCESS','ObjectTable'),table);word(table+off('_HANDLE_TABLE','UniqueProcessId'),404);word(table+off('_HANDLE_TABLE','QuotaProcess'),process)
word(table+off('_HANDLE_TABLE','Table'),0x81021000);word(0x81021000,0x81022000);word(0x81022000,0x81023000)
entry=0x81023000+65*8;word(entry,(header&0x7fffffff)|3);word(entry+4,0x120116)
word(header+off('_OBJECT_HEADER','PointerCount'),2);word(header+off('_OBJECT_HEADER','HandleCount'),1)
put(owner,struct.pack('<HH',5,plan['structures']['_FILE_OBJECT']['size']));word(owner+off('_FILE_OBJECT','DeviceObject'),dev)
word(dev+off('_DEVICE_OBJECT','DriverObject'),driver);word(driver+off('_DRIVER_OBJECT','DriverStart'),bases['pattern.sys'])
word(driver+off('_DRIVER_OBJECT','DriverSize'),plan['modules']['pattern.sys']['image_size'])
head=bases['ntoskrnl.exe']+plan['module_list_rva'];nodes=[0x81030000,0x81031000]
word(head,nodes[0]);word(head+4,nodes[-1])
for i,name in enumerate(['ntoskrnl.exe','pattern.sys']):
 node=nodes[i];word(node,nodes[i+1] if i==0 else head);word(node+4,head if i==0 else nodes[i-1])
 word(node+off('_LDR_DATA_TABLE_ENTRY','DllBase'),bases[name]);word(node+off('_LDR_DATA_TABLE_ENTRY','SizeOfImage'),plan['modules'][name]['image_size'])
 text=name.encode('utf-16le');at=0x81032000+i*256;put(at,text)
 put(node+off('_LDR_DATA_TABLE_ENTRY','BaseDllName'),struct.pack('<HHI',len(text),len(text)+2,at))
virtual=0xa2000000;pa=0x200000
physical[0x1000+(virtual>>22)*4]=struct.pack('<I',0x3003)
for i in range(4):physical[0x3000+(((virtual>>12)&1023)+i)*4]=struct.pack('<I',pa+4096*i+3)
arena=bases['pattern.sys']+plan['arena_rva'];reply=bases['probe.exe']+plan['reply_rva'];esp=0x120000
def stage(n):
 reads,writes=[(0,0),(1,0),(2,0),(3,1),(4,1)][n-1]
 put(arena,struct.pack('<8I',owner,virtual,1,pa,0,reads,writes,1))
 put(reply,struct.pack('<8I',258,0,1,pa,16384,0,reads,writes))
 call=next(v for v in plan['callsites'] if v['stage']==n)
 put(esp,struct.pack('<4I',bases['probe.exe']+call['rva']+5,n,reply,0x104))
def run(n):return Attestor(plan,pes,read,pread).checkpoint(n,dict(esp=esp,eip=bases['probe.exe']+plan['checkpoint_rva']),0x1000,0)
for n in range(1,6):
 stage(n);r=run(n);assert r['passed'] and r['pages']==[pa+4096*i for i in range(4)] and not r['dirty_arena_read'];checks+=1
stage(1)
negative={
 'wrong_owner':(arena,owner+8),'wrong_generation':(arena+8,2),'closed':(arena+16,1),
 'wrong_reads':(arena+20,1),'wrong_writes':(arena+24,1),'wrong_attempt':(arena+28,2),
 'no_write_access':(entry+4,0x120114),'wrong_handle_object':(entry,0x01024083),
 'wrong_process':(table+off('_HANDLE_TABLE','QuotaProcess'),process+4),
 'wrong_pid':(table+off('_HANDLE_TABLE','UniqueProcessId'),405),
 'wrong_dtb':(process+off('_KPROCESS','DirectoryTableBase'),0x2000),
 'wrong_base':(process+off('_EPROCESS','SectionBaseAddress'),0x17000000),
 'wrong_driver':(driver+off('_DRIVER_OBJECT','DriverStart'),0xfe670000),
 'wrong_caller':(esp,0x16000000),'wrong_reply':(esp+8,reply+4),'wrong_stage':(esp+4,2),
 'corrupt_resident_probe':(0x16001000,0),'corrupt_resident_driver':(0xfe661000,0),
 'module_cycle':(nodes[0],nodes[0]),'wrong_reply_status':(reply+4,1),
}
for name,(at,value) in negative.items():
 old=read(at,4);word(at,value)
 try:run(1)
 except AssertionError:checks+=1
 else:raise AssertionError(('accepted negative',name))
 finally:put(at,old)
at=0x3000+(((virtual>>12)&1023)+3)*4;old=physical[at];physical[at]=struct.pack('<I',pa+5*4096+3)
try:run(1)
except AssertionError:checks+=1
else:raise AssertionError('Noncontiguous fourth page accepted')
finally:physical[at]=old
r=dict(passed=True,checks=checks,guest_observed=False,physical_access=False,synthetic_only=True,
 inputs={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['attest.py','test-live-attestor.py','attestation-inputs001.json']},
 actual_probe_handle_access='GENERIC_WRITE / FILE_WRITE_DATA required; FILE_READ_DATA is not required',
 scope='All five complete synthetic runtime layouts and21 mutations using actual pinned PE bytes/relocations. No live process observed and no renderer invoked.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('260 complete synthetic attestation',checks,'checks PASS')
