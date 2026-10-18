"""New context lifecycle extension; older refusal requirements remain intact."""
import struct
from witness_decode import decode_refusal as old_refusal,marker_success
def decode_refusal(data):
 def need(v,msg):
  if not v:raise ValueError(msg)
 need(len(data)==192,'refusal length')
 q=struct.unpack('<48I',data);reason=q[4]
 if reason<=19:
  r=old_refusal(data)
  if reason>=17:r['handle_role']='context: post-context-close original comparison'
  return r
 need(q[:4]==(0x30393452,2,192,0x49000101) and q[44:]==(0x454e4f44,2,0x49000101,192),'identity')
 need(20<=reason<=25 and q[19]==0,'context reason/reserved')
 need(q[10:16]==(6,1,1,1,1,1) and not q[16]&1024 and q[17]==0,'eligible original frame')
 need(q[9]==(2 if reason<=21 else 1 if reason==25 else 0),'close state')
 need(not(q[9] or not q[8]) or q[18]==0xeeeeeeee,'no repeat cleanup close')
 need(reason==22 or q[8]!=0,'missing owner handle')
 if reason==22:need(q[5]!=0 or q[6]!=0 or q[7]!=2 or not q[8],'create did not refuse')
 if reason==23:need(q[5]!=0 or q[6]!=0 or q[7]!=400,'write did not refuse')
 if reason==24:need(q[5]!=0 or q[6]!=0,'flush did not refuse')
 if reason==25:need(q[5]!=0 and q[6]==0,'close did not refuse')
 marker_success(data[80:176])
 return dict(record_complete=True,deliberate_wrapper_refusal=True,reason=reason,
             handle_role='primary' if reason==20 else 'witness' if reason==21 else 'context',
             return_status=q[5],iosb_status=q[6],iosb_information=q[7],close_state=q[9],cleanup_status=q[18],
             fallback_flush_close_proved=False,paging_transition_proved=False)
