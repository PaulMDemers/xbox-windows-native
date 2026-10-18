"""Separate fixture oracle; no output-derived pixel or CPU expectations."""
import struct
from decode import decode
def review(raw,symbols):
 assert raw[:4]==b'T490';p=4;success=0;refusals=0;seen=set()
 # CALL ends are pinned labels exported immediately after each actual CALL.
 returns=[symbols['context490_pre_return'],symbols['context490_post_return']]
 for target in range(2):
  assert raw[p:p+1]==b'S';p+=1
  assert struct.unpack_from('<I',raw,p)[0]==target;p+=4
  packet=raw[p:p+400];p+=400
  before=raw[p:p+36];after=raw[p+36:p+72];p+=72
  assert before==after
  frame=struct.unpack('<9I',before);address=frame[3]-32
  assert frame[:3]==(0x55555555,0x44444444,0x66666666)
  assert frame[4:8]==(0x22222222,symbols['fixture_success'],0x33333333,0x11111111)
  assert frame[8]==(0x682 if target else 0x282)
  d=decode(packet,witness_address=symbols['witness_record'],frame_address=address,return_eips=returns)
  for i,r in enumerate(d['records']):
   assert r['cr0']==0x80000011 and r['cr4']==0x10
   assert r['cr2']==(0x12345000 if i==0 else 0x6789a000)
   assert r['cr3']==(0x1000000 if i==0 else 0x1002000)
   assert r['selectors']==[8,16,16,16,16,16,0,0]
   assert r['gdtr']==[23,symbols['fixture_gdt']] and r['idtr']==[0,0]
  success+=1
  for mode in range(1,19):
   assert raw[p:p+1]==b'R';m,t,reason,step,n=struct.unpack_from('<5I',raw,p+1);p+=21
   op=0 if mode<=6 else 1 if mode<=12 else 2 if mode<=16 else 3
   assert (m,t,reason,step)==(mode,target,(22 if target else 13)+op,target*4+op+1)
   expected=0 if not target or mode<=7 else 399 if mode==11 else 400
   assert n==expected
   seen.add((m,t));refusals+=1
 for mode in range(19,27):
  assert raw[p:p+1]==b'R';m,t,reason,step,n=struct.unpack_from('<5I',raw,p+1);p+=21
  assert (m,t)==(mode,1)
  assert reason==(mode-2 if mode<=21 else 20 if mode<=23 else 21)
  assert (step,n)==((8,400) if mode<=21 else (0,0) if mode<=23 else (4,0))
  seen.add((m,t));refusals+=1
 assert raw[p:]==b'P'+struct.pack('<I',46) and len(seen)==44
 return dict(passed=True,cases=46,successful_context_pairs=success,refusals=refusals,actual_privileged_capture=True,original_handoff_frames_exact=True,kernel_IO='MODELED',physical_context=False,original_refusal_cleanup_tested=False)
