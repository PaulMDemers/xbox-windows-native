"""Classify traced virtual-disk writes against native-kernel execution evidence."""
import pathlib,argparse,re,json,gzip
k=pathlib.Path(__file__).resolve().parent;root=k.parents[1]
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args();assert re.fullmatch('nt5-extended-f-[0-9]+',a.run)
run=root/'work/runs'/a.run;assert (run/'cleanup.json').exists()
states=[json.loads(p.read_text()) for p in sorted(run.glob('state-*.json'))]
state=next(s for s in states if s.get('kernel_base'));kernel=next(m for m in state['modules'] if m['name']=='ntoskrnl.exe')
base=int(kernel['base'],0);end=base+kernel['size'];mark=json.loads((run/'disk-trace-prelaunch.json').read_text())['traceBytesBeforeLaunch']
nt_seen=False;first_nt=None;ip=0;records=[];before=0;outside=[];high=[];count=0
trace=run/'cpu-trace.log'
with (trace.open('rb') if trace.exists() else gzip.open(trace.with_suffix('.log.gz'),'rb')) as f:
 while line:=f.readline():
  position=f.tell();m=re.search(rb' IP=[0-9a-fA-F]+:([0-9a-fA-F]+)',line)
  if m:
   ip=int(m[1],16)
   if base<=ip<end and not nt_seen:nt_seen=True;first_nt=position
  m=re.search(rb'blk_co_pwritev blk (\S+) bs (\S+) offset (\d+) bytes (\d+)',line)
  if not m:continue
  offset,size=map(int,m.groups()[2:]);record={'offset':offset,'bytes':size,'last_interrupt_ip':hex(ip),'trace_position':position}
  if not nt_seen:
   before+=1
   if position>mark:records.append(record)
   continue
  count+=1
  if offset<8004132864 or offset+size>250059350016:outside.append(record)
  if offset>=2**28*512:high.append(record)
r={'run':a.run,'scope':'Observed blk_co_pwritev events after first native-kernel interrupt IP; not a hardware guarantee',
   'first_native_kernel_trace_position':first_nt,'writes_before_native_kernel_observed':before,
   'postlaunch_pre_kernel_writes':records,'writes_after_native_kernel_observed':count,
   'outside_f_after_native_kernel_observed':outside,'high_lba_writes':high,
   'all_observed_native_writes_within_f':nt_seen and count>0 and not outside}
(k/(a.run+'-write-trace.json')).write_text(json.dumps(r,indent=2)+'\n')
print({key:r[key] for key in ['run','writes_before_native_kernel_observed','writes_after_native_kernel_observed','all_observed_native_writes_within_f']});print('High-LBA writes:',len(high),'postlaunch pre-kernel writes:',records)
