"""Actual observer logic. Kernel effects and stop/read transports modeled in host tests."""
import struct
from kernel_calls import observe as observe_files

def plan(x,s):
 start=s['entry503_gate'];end=s['entry498_record'];code=x[start-0x10000:end-0x10000]
 def ret(name):
  needle=b'\xff\x15'+struct.pack('<I',s[name]);assert code.count(needle)==1
  return start+code.index(needle)+6
 led=ret('Entry503HalWriteSMBusValue');delay=ret('Entry503KeDelayExecutionThread');firmware=ret('DiagHalReturnToFirmware')
 def l(label,cmd,value):return (label,'Entry503HalWriteSMBusValue',50,[0x20,cmd,0,value],led)
 def d(label):return (label,'Entry503KeDelayExecutionThread',99,[0,0,s['entry503_interval']],delay)
 return [l('amber',8,255),l('manual',7,1),d('wait-amber')],[l('green',8,15),d('wait-green'),l('automatic',7,0)],firmware

def observe(b,s,calls):
 rows=[]
 for label,thunk,ordinal,args,ret in calls:
  before=b.stop(b.handlers[thunk],label+'-entry')
  stack=list(struct.unpack('<'+'I'*(len(args)+1),b.read(before['ESP'],4*(len(args)+1),label+'-stack')))
  row=dict(label=label,ordinal=ordinal,before=before,stack=stack)
  b.record(row);assert stack==[ret]+args
  if ordinal==99:
   interval=b.read(s['entry503_interval'],8,label+'-interval');assert struct.unpack('<q',interval)[0]==-20000000
   row['relative_interval_100ns']=-20000000
  after=b.stop(ret,label+'-return');row['after']=after;b.record(row)
  assert after['EAX']==0 and after['ESP']==before['ESP']+4*(len(args)+1)
  rows.append(row)
 return rows

def transaction(b,s,x,file_calls):
 pre,post,ret=plan(x,s)
 initial=observe(b,s,pre)
 gate=b.stop(s['entry498_gate'],'file-gate-entry');b.verify_entry(gate)
 files=observe_files(b,s,file_calls)
 complete=b.stop(s['entry503_complete'],'file-complete-before-indicator');b.verify_complete(complete)
 terminal=observe(b,s,post)
 firm=b.stop(b.handlers['DiagHalReturnToFirmware'],'firmware-return-entry')
 stack=list(struct.unpack('<2I',b.read(firm['ESP'],8,'firmware-stack')))
 row=dict(label='firmware',ordinal=49,before=firm,stack=stack);b.record(row)
 assert stack==[ret,1]
 b.verify_terminal()
 return dict(initial=initial,files=files,terminal=terminal,firmware=row)
