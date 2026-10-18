"""Independent semantic decoder of the unchanged465 first-marker state machine."""
import struct
def decode_marker(data,reason,result):
 if len(data)!=96:raise ValueError('marker length')
 r=struct.unpack('<24I',data)
 def need(ok,why):
  if not ok:raise ValueError(why)
 need(r[:5]==(0x354b524d,1,96,1,0xff),'marker identity')
 if reason!=12:
  need(r[5:]==(0,)*19,'marker executed before eligibility')
  return dict(executed=False)
 need(r[5]==result and result in (3,4,5,6,7),'failed result')
 need(r[22:]==(1,0),'terminal/reserved')
 complete,mask,tx=r[6],r[7],r[18]
 need(tx in (0,1) and complete==tx,'completed/current transaction')
 started=1 if mask==1 else 2 if mask==3 else 0 if mask==0 else -1
 need(started in (tx,tx+1),'started mask')
 in_completion=started==tx+1
 need(0<=r[9]<=4096 and all(x<=0xffff for x in (r[8],*r[14:18])),'poll/status bounds')
 need(r[20]<=started and r[19]==4*started+r[20],'writes/acks')
 need(r[20]==sum(r[14+i]==0x10 for i in range(started)),'actual acknowledged idle values')
 for i in range(tx):need(r[16+i]==0x10 and r[14+i] in (0,0x10),'completed prior transaction')
 if started:need(all(r[14+i] in (0,0x10) for i in range(started)),'configured on nonidle state')
 if tx==0:need(r[15]==0 and r[17]==0,'future transaction status')
 if not in_completion:need(r[16+tx]==0,'unstarted completion')
 if r[9]:
  expected=r[(16 if in_completion else 14)+tx]
  transition=result in (6,7) and expected==0 and ((in_completion and r[8]==r[14+tx]) or (not in_completion and tx==1 and r[8]==r[16]))
  need(r[8]==expected or transition,'last status identity')
 else:need(r[8]==0 and started==0,'status without poll')
 start=r[10]+(r[11]<<32);end=r[12]+(r[13]<<32)
 if result in (3,4):
  need(r[9]==4096 and r[21]==r[9]+2,'poll budget termination')
  need(in_completion==(result==4),'poll budget phase')
 elif result==5:
  need(r[9]>0 and r[8]&~0x810 and r[21]==r[9]+1,'unrecognized status refusal')
 else:need(r[21]==r[9]+2,'clock termination')
 if result==6:need(end>=start+64000000,'deadline result')
 elif result==7:need(end<start,'reverse clock result')
 else:need(start<=end<start+64000000,'bounded timestamp')
 return dict(executed=True,result=result,completed=complete,started_mask=mask,transaction=tx,
  phase='completion' if in_completion else 'idle',last_status=r[8],last_status_hex=hex(r[8]),
  idle_status=list(r[14:16]),completion_status=list(r[16:18]),polls=r[9],tsc_start=start,
  tsc_end=end,io_writes=r[19],acknowledgments=r[20],tsc_reads=r[21],done=True,
  hardware_model_or_physical_origin='requires external evidence')
