"""Reconstruct exact predecessor sources/payload and exercise independent decoder."""
import hashlib,json,struct
from pathlib import Path
from marker_decode import success
K=Path(__file__).resolve().parent;B=Path('C:/xwn466/build001');P=Path('E:/xwn462/build001')
out=K/'source-review002.json';assert not out.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
b=json.loads((K/'build001.json').read_text());assert b['status']=='compiled'
r=dict(passed=False,physical_access=False,emulator_run=False)
def local(s):return Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
try:
 for kit in [K.parent/'entry-marker465/host001.json',K/'host001.json',K/'stub-host001.json']:
  h=json.loads(kit.read_text());assert h['status']=='passed'
  for p,v in h['files'].items():assert sha(local(p).read_bytes())==v['sha256'],p
 for p,v in b['files'].items():assert sha(local(p).read_bytes())==v['sha256'],p
 helper=(K.parent/'entry-marker465/marker.S').read_text().replace('.section .note.GNU-stack,"",@progbits','')
 source=(B/'xbeboot.S').read_text()
 tail='\n.balign 4\nbefore_marker_record:\n    .long 0x354b524d,1,96,1,0xff\n    .zero 76\n'+helper+'\n'
 assert source.count(tail)==1;source=source.replace(tail,'')
 hook='''diag_handoff:
    mov dword ptr [diag_reason], 12
    push offset before_marker_record
    call marker_guarded
    add esp, 4
    mov eax, [before_marker_record+20]
    cmp eax, 1
    jne diag_reboot
diag_marker_ready:
    popad'''
 assert source.count(hook)==1;source=source.replace(hook,'diag_handoff:\n    popad')
 source=source.replace(f'.long {hex(b["payload_bytes"])}','.long 0x4663c').replace('466','462')
 # The original size token contains the new namespace digits; restore explicitly.
 source=source.replace('.long 0x4623c','.long 0x4663c')
 assert source==(P/'xbeboot.S').read_text(),'source reconstruction'
 x=(B/'default.xbe').read_bytes();original=Path('E:/xwn374/build001/default.xbe').read_bytes()
 old=Path('E:/xwn374/build001/image-crom.bin').read_bytes();payload=(B/'payload.bin').read_bytes();stub=(B/'stub.bin').read_bytes()
 assert sha(x)==b['sha256'] and len(payload)==b['payload_bytes']
 repaired=bytearray(payload[:len(old)]);assert repaired[0xf0]==0xe9
 assert 0x26000f5+struct.unpack_from('<i',repaired,0xf1)[0]==0x2680000
 repaired[0xf0:0xf5]=bytes.fromhex('bc00008002');assert bytes(repaired)==old
 assert payload[len(old):0x80000]==bytes(0x80000-len(old)) and payload[0x80000:]==stub
 assert stub[:5]==bytes.fromhex('bc00008002')
 ready=b['stub_symbols']['after_stack_ready']-0x2680000
 assert stub[ready]==0xe9 and 0x2680000+ready+5+struct.unpack_from('<i',stub,ready+1)[0]==0x26000f5
 assert x[0x3000:0x3000+len(payload)]==payload and x[0x3000+len(payload):]==original[0x3000+len(old):]
 header=bytearray(x[:4096]);allowed=list(range(0x10c,0x110))+list(range(0x350,0x354))+list(range(0x358,0x35c))+list(range(0x36c,0x380))
 for i in allowed:header[i]=original[i]
 assert bytes(header)==original[:4096]
 assert x[0x36c:0x380]==hashlib.sha1(struct.pack('<I',len(x)-4096)+x[4096:]).digest()
 s=b['wrapper_symbols'];assert s['gdt_48_base']+4-s['blentry']==224 and s['ptr_newloc']-s['blentry']==74 and s['newloc']-s['blentry']==80
 accepted=[];rejected=0
 for p in sorted(Path('C:/xwn465/host001').glob('case*.bin'))+sorted(Path('C:/xwn466/stub-host001').glob('stub*.bin'))+sorted(Path('C:/xwn466/host001').glob('marker*.bin')):
  data=p.read_bytes();v=struct.unpack('<24I',data)
  if v[5]==1 and v[22]==1:
   success(data,v[3]);accepted.append(str(p))
  else:
   try:success(data,v[3])
   except ValueError:rejected+=1
   else:raise AssertionError(('accepted non-success',str(p)))
 base=Path(accepted[0]).read_bytes();v=list(struct.unpack('<24I',base));negatives=0
 invalid=[0,2,95,3,0,5,1,1,0,4097,0xffffffff,0xffffffff,0,0xffffffff,0x800,0x20,0,0,2,99,99,0,0,1]
 for i,bad in enumerate(invalid):
  w=v.copy();w[i]=bad
  try:success(struct.pack('<24I',*w),1)
  except ValueError:negatives+=1
  else:raise AssertionError(('accepted invalid field',i))
 for n in range(96):
  try:success(base[:n],1)
  except ValueError:negatives+=1
  else:raise AssertionError('accepted truncation')
 r.update(passed=True,source_reconstructed=True,payload_reconstructed=True,header_change_scope_exact=True,
          original_loader_layout_unchanged=True,private_build_files=len(b['files']),host_success_records=len(accepted),
          host_failure_or_unexecuted_records_rejected=rejected,independent_negative_cases=negatives,
          decoder_sha256=sha((K/'marker_decode.py').read_bytes()),review_sha256=sha(Path(__file__).read_bytes()))
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
