"""Independent refusal-record decoder. Absence never proves successful handoff."""
import struct
from failure_marker import decode_marker
REASONS={1:'report create',2:'header write',3:'header flush',4:'trailer write',5:'trailer flush',6:'report close',7:'missing original snapshot',8:'ineligible original copies',9:'post-log payload mismatch',10:'post-log high loader mismatch',11:'post-log low loader mismatch',12:'bounded first marker refusal'}
def decode_refusal(data):
 if len(data)!=192:raise ValueError('Incomplete/oversized refusal')
 r=struct.unpack('<20I',data[:80])+struct.unpack('<4I',data[176:])
 if r[:4]!=(0x31383452,2,192,0x48100101) or r[20:]!=(0x454e4f44,2,0x48100101,192):raise ValueError('Refusal identity')
 reason=r[4]
 if reason not in REASONS or r[19] or r[10] not in (1,2,3,5,6,7):raise ValueError('Reason/phase/reserved')
 if any(v not in (0,1) for v in r[11:16]):raise ValueError('Noncanonical boolean')
 if r[9]!=(0 if reason<6 else 1 if reason==6 else 2):raise ValueError('Close state/order')
 if (r[9] or not r[8]) and r[18]!=0xeeeeeeee:raise ValueError('Unexpected cleanup close')
 if r[10]==6:
  if r[11]!=1 or r[17]:raise ValueError('Completed-copy state')
  eligible=int(r[13:16]==(1,1,1) and not r[16]&0x400)
  if r[12]!=eligible:raise ValueError('Eligibility contradiction')
 elif any(r[11:17]) or (r[10]==7 and r[17] not in (1,2,3)) or (r[10]!=7 and r[17]):raise ValueError('Early snapshot/mapping state')
 if reason==1 and r[5]==0 and r[6]==0 and r[7]==2 and r[8]:raise ValueError('Create did not refuse')
 if reason in (2,4) and r[5]==0 and r[6]==0 and r[7]==(160 if reason==2 else 16):raise ValueError('Write did not refuse')
 if reason in (3,5) and r[5]==0 and r[6]==0:raise ValueError('Flush did not refuse')
 if 2<=reason<=6 and not r[8]:raise ValueError('Missing primary handle')
 if reason==6 and (r[5]==0 or r[6]!=0):raise ValueError('Close refusal state')
 if 7<=reason<=11 and (r[5]!=0 or r[6]!=0 or not r[8]):raise ValueError('Post-close state')
 if reason==7 and r[11]!=0:raise ValueError('Snapshot exists')
 if reason==8 and (r[11]!=1 or r[12]!=0):raise ValueError('Eligibility did not refuse')
 if reason>=9 and (r[11:16]!=(1,1,1,1,1) or r[16]&0x400):raise ValueError('Invalid post-log mismatch state')
 if reason==12 and (r[5] not in (2,3,4,5,6,7) or r[6]!=0 or not r[8]):raise ValueError('Marker refusal state')
 marker=decode_marker(data[80:176], reason, r[5])
 return dict(marker=marker,record_complete=True,deliberate_wrapper_refusal=True,reason=reason,reason_name=REASONS[reason],
  primary_return_status=r[5],primary_iosb_status=r[6],primary_iosb_information=r[7],primary_handle=r[8],
  close_state=r[9],preparation_phase=r[10],snapshot_valid=r[11],eligible=r[12],initial_copy_checks=list(r[13:16]),
  saved_eflags=r[16],mapping_refusal_reason=r[17],cleanup_close_status=r[18],
  fallback_flush_close_proved=False,reboot_completed_proved=False,paging_transition_proved=False)
