"""Independent replay of retained real stack/IOSB/entry evidence; no live guest."""
import copy,hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'actual-review001.json';assert not out.exists()
t=json.loads((K/'emu001/trace.json').read_text());b=json.loads((K.parent/'entry-trampoline510/build001.json').read_text());s=b['wrapper_symbols']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reads={v['label']:v for v in t['reads']}
for v in t['reads']:assert sha(Path(v['private_file']))==v['sha256']
def raw(label):return Path(reads[label]['private_file']).read_bytes()
handlers=next(p for p in t['checkpoints'] if p['label']=='early-entry')['handlers']
expected=[('create','DiagNtCreateFile',190,0x94963),('body','DiagNtWriteFile',236,0x949b9),('flush1','DiagNtFlushBuffersFile',198,0x94aa7),('trailer','DiagNtWriteFile',236,0x94a1c),('flush2','DiagNtFlushBuffersFile',198,0x94aa7),('close','DiagNtClose',187,0x94abe)]
def verify(rows):
 assert len(rows)==6
 handle=rows[0]['handle_after'];assert 0<handle<=0xffffffff
 for row,(label,thunk,ordinal,ret) in zip(rows,expected):
  assert row['label']==label and row['ordinal']==ordinal
  before=row['before'];after=row['after']
  assert before['EIP']==handlers[thunk] and after['EIP']==ret and after['EAX']==0
  assert row['handle_before']==(0 if label=='create' else handle) and row['handle_after']==handle
  if label=='create':args=[s['entry498_handle'],0x40100000,s['entry498_object'],s['entry498_iosb'],0,128,0,2,98];iosb=[0,2]
  elif label in ('body','trailer'):args=[handle,0,0,0,s['entry498_iosb'],s['entry498_record']+(96 if label=='trailer' else 0),16 if label=='trailer' else 96,0];iosb=[0,args[-2]]
  elif label.startswith('flush'):args=[handle,s['entry498_iosb']];iosb=[0,0]
  else:args=[handle];iosb=[0,0]
  assert row['stack']==[ret]+args and after['ESP']==before['ESP']+4*(len(args)+1) and row['iosb']==iosb
 return True
rows=t['actual_kernel_calls'];assert verify(rows)
for row in rows:
 label=row['label']
 assert list(struct.unpack('<'+'I'*(len(raw(label+'-stack'))//4),raw(label+'-stack')))==row['stack']
 assert list(struct.unpack('<2I',raw(label+'-iosb-after')))==row['iosb']
 assert struct.unpack('<I',raw(label+'-handle-after'))[0]==row['handle_after']
negatives=0
for i,row in enumerate(rows):
 for field in ('handle_before','handle_after','ordinal'):
  q=copy.deepcopy(rows);q[i][field]^=1
  try:verify(q)
  except AssertionError:negatives+=1
  else:raise AssertionError((i,field))
 for field in ('stack','iosb'):
  for index in range(len(row[field])):
   q=copy.deepcopy(rows);q[i][field][index]^=1
   try:verify(q)
   except AssertionError:negatives+=1
   else:raise AssertionError((i,field,index))
 for group,field in [('before','EIP'),('before','ESP'),('after','EIP'),('after','ESP'),('after','EAX')]:
  q=copy.deepcopy(rows);q[i][group][field]^=1
  try:verify(q)
  except AssertionError:negatives+=1
  else:raise AssertionError((i,group,field))
receipt=raw('entry-memory-receipt');from entry_decode import decode
assert decode(receipt)==t['entry_receipt']
receipt_negatives=0
for i in range(len(receipt)):
 q=bytearray(receipt);q[i]^=1
 try:decode(q)
 except ValueError:receipt_negatives+=1
 else:raise AssertionError(('receipt',i))
assert Path('C:/xwn513/cold001/entry.bin').read_bytes()==receipt
assert t['remaining_breakpoints']==[] and t['physical_mode_restored'] and not t.get('cleanup_error')
assert t['passed'] and t['original_start_not_executed'] and not t['windows_started']
mappings={}
for name,addresses in next(p for p in t['checkpoints'] if p['label']=='early-entry')['translations'].items():
 pde=struct.unpack('<I',raw(name+'-pde'))[0];pte=struct.unpack('<I',raw(name+'-pte'))[0] if name+'-pte' in reads else None
 mappings[name]=dict(**addresses,pde=pde,pte=pte,page_size=4194304 if pde&128 else 4096,pde_rw=bool(pde&2),pde_user=bool(pde&4),pde_pwt=bool(pde&8),pde_pcd=bool(pde&16),leaf_pwt=bool((pte if pte is not None else pde)&8),leaf_pcd=bool((pte if pte is not None else pde)&16))

# Separate independent indicator/kernel-return argument reconstruction.
ind=t['indicator_calls'];ir=ind['initial']+ind['terminal']
assert len(ir)==6
ispec=[('amber',50,[32,8,0,255],0x94c05),('manual',50,[32,7,0,1],0x94c05),('wait-amber',99,[0,0,0x95138],0x94c17),('green',50,[32,8,0,15],0x94c05),('wait-green',99,[0,0,0x95138],0x94c17),('automatic',50,[32,7,0,0],0x94c05)]
def verify_indicators(rows):
 assert len(rows)==6
 for row,(label,ordinal,args,ret) in zip(rows,ispec):
  name='Entry503HalWriteSMBusValue' if ordinal==50 else 'Entry503KeDelayExecutionThread'
  assert row['label']==label and row['ordinal']==ordinal and row['stack']==[ret]+args
  assert row['before']['EIP']==handlers[name] and row['after']['EIP']==ret
  assert row['after']['EAX']==0 and row['after']['ESP']==row['before']['ESP']+4*(len(args)+1)
  if ordinal==99:assert row['relative_interval_100ns']==-20000000
 return True
assert verify_indicators(ir)
for row in ir:
 label=row['label'];assert list(struct.unpack('<'+'I'*(len(raw(label+'-stack'))//4),raw(label+'-stack')))==row['stack']
 if row['ordinal']==99:assert struct.unpack('<q',raw(label+'-interval'))[0]==-20000000
indicator_negatives=0
for i,row in enumerate(ir):
 for j in range(len(row['stack'])):
  q=copy.deepcopy(ir);q[i]['stack'][j]^=1
  try:verify_indicators(q)
  except AssertionError:indicator_negatives+=1
  else:raise AssertionError(('indicator-stack',i,j))
 for group,field in [('before','EIP'),('before','ESP'),('after','EIP'),('after','ESP'),('after','EAX')]:
  q=copy.deepcopy(ir);q[i][group][field]^=1
  try:verify_indicators(q)
  except AssertionError:indicator_negatives+=1
  else:raise AssertionError(('indicator-register',i,group,field))
firm=ind['firmware'];assert firm['ordinal']==49 and firm['before']['EIP']==handlers['DiagHalReturnToFirmware']
assert firm['stack']==[0x94bf1,1] and struct.unpack('<2I',raw('firmware-stack'))==(0x94bf1,1)
assert struct.unpack('<6I',raw('terminal-indicator-status'))==(0,)*6
assert struct.unpack('<I',raw('terminal-indicator-state'))==(2,)
assert struct.unpack('<2I',raw('terminal-return-state'))==(1,1)
original=next(p for p in t['checkpoints'] if p['label']=='early-entry')['registers']
assert struct.unpack('<9I',raw('terminal-restored-registers'))==tuple(original[n] for n in ['EDI','ESI','EBP','ESP','EBX','EDX','ECX','EAX','EFL'])
assert t['dashboard_return_observed'] and t['dashboard_control']['passed']
assert t['dashboard_control']['receipt_size']==len(receipt)==112
assert t['dashboard_control']['live_receipt_bytes_verified'] is False
assert t['live_ftp_receipt_readback'] is False
assert t['checkpoints'][0]['registers']['EIP']==0x11100
assert not any(p['registers']['EIP']==0x11105 for p in t['checkpoints'])

r=dict(passed=True,actual_call_records=12,indicator_record_mutations_rejected=indicator_negatives,actual_firmware_entry=True,dashboard_return_observed=True,live_ftp_content_qualified=False,cold_content_verified=True,actual_record_mutations_rejected=negatives,actual_receipt_byte_mutations_rejected=receipt_negatives,private_captures_verified=len(t['reads']),cold_receipt_exact=True,mappings=mappings,physical_access=False,ordinary_boot_qualified=False)
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print({k:v for k,v in r.items() if k!='mappings'})
