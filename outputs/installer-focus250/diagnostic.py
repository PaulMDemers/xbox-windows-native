"""Bounded diagnostic grammar; projection never invents idle/cancel/completion rows."""
import hashlib
NUM={'WAIT_SAMPLE249','FG_WAIT249','GUI_WAIT249_OWNER','GUI_WAIT249_ACTIVE','GUI_WAIT249_CAPTURE','GUI_WAIT249_FAILED','WAIT_FG249','WAIT_WINDOW249','WAIT_TEXT249','WAIT_OWNER249','WAIT_CREATION249','WAIT_COMMAND_FAILED249','WAIT_OPEN_FAILED249','WAIT_END249'}
BLOB={'WAIT_TITLE249','WAIT_CLASS249','WAIT_COMMAND249'}
ALL=NUM|BLOB
def decode(raw):
 assert isinstance(raw,bytes) and len(raw)<=1048576 and raw.endswith(b'\r\n')
 lines=raw.decode('ascii').splitlines();samples=[];active=None;original=[]
 for line in lines:
  f=line.split(' ');label=f[0]
  if label not in ALL:
   assert not label.startswith(('WAIT_','FG_WAIT','GUI_WAIT')), 'Unknown diagnostic row'
   original.append(line);continue
  if label in NUM:
   assert len(f)==4 and all(v.isdecimal() for v in f[1:]);value=list(map(int,f[1:]));assert all(v<=0xffffffff for v in value)
  else:
   assert len(f)==4 and all(v.isdecimal() for v in f[1:3]);owner,n=map(int,f[1:3]);value=dict(owner=owner,bytes=n,text=bytes.fromhex(f[3]).decode('ascii'));assert len(bytes.fromhex(f[3]))==n and n<=512
  if label=='WAIT_SAMPLE249':
   assert active is None and value[0]<120000
   if samples:assert value[0]>=samples[-1]['begin'][0]+5000
   active=dict(begin=value,rows={});samples.append(active)
  assert active is not None and label not in active['rows'];active['rows'][label]=value
  if label=='WAIT_END249':
   assert value[0]>=active['begin'][0] and value[1:]==active['begin'][1:]
   rows=active['rows'];assert {'FG_WAIT249','WAIT_FG249','WAIT_WINDOW249','WAIT_TEXT249','WAIT_TITLE249','WAIT_CLASS249'}<=rows.keys()
   assert ('GUI_WAIT249_FAILED' in rows)^({'GUI_WAIT249_OWNER','GUI_WAIT249_ACTIVE','GUI_WAIT249_CAPTURE'}<=rows.keys())
   assert ('WAIT_OPEN_FAILED249' in rows)^({'WAIT_OWNER249','WAIT_CREATION249'}<=rows.keys())
   assert rows['WAIT_TITLE249']['owner']==rows['WAIT_CLASS249']['owner']==rows['WAIT_FG249'][1]
   stable=rows['FG_WAIT249']==rows['WAIT_FG249'];target=active['begin'][2]
   active['two_foreground_reads_agree']=stable
   active['foreground_differs_from_refused_window']=stable and rows['WAIT_FG249'][1]!=target
   active['target_gui_active_differs']=rows.get('GUI_WAIT249_ACTIVE',[0,target])[1]!=target
   active['target_capture_menu_move_present']=any(rows.get('GUI_WAIT249_CAPTURE',[]))
   active=None
 assert active is None,'Partial diagnostic snapshot retained as failure'
 return dict(raw_sha256=hashlib.sha256(raw).hexdigest(),samples=samples,sample_count=len(samples),foreground_refusal_observed=any(v['foreground_differs_from_refused_window'] for v in samples),limits='Sequential observations, not atomic GUI snapshots or proof of the foreground-change producer.'), ('\r\n'.join(original)+'\r\n').encode('ascii')
