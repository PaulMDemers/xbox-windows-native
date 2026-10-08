"""Bounded LOG-backend windows; trace off before debugger memory observations."""
import hashlib,re,time
EVENTS=('nv2a_pgraph_surface_cpu_read','nv2a_pgraph_surface_cpu_write')
PATTERN=re.compile(rb'^(nv2a_pgraph_surface_cpu_(read|write)) 0x([0-9a-fA-F]+)\+0x([0-9a-fA-F]+)$')
MAX_SEGMENT=4*1024*1024
MAX_TOTAL=16*1024*1024
MAX_RECORDS=65536

def decode(data):
 assert len(data)<=MAX_SEGMENT
 rows=[]
 for line in data.splitlines():
  if b'nv2a_pgraph_surface_cpu_' not in line:continue
  m=PATTERN.fullmatch(line);assert m,line
  base,offset=int(m[3],16),int(m[4],16);assert 0<=base+offset<64*1024*1024
  rows.append((m[2].decode(),base,offset))
  assert len(rows)<=MAX_RECORDS
 return rows

class Windows:
 def __init__(self,command,run,out,report):
  self.command=command;self.path=run/'cpu-trace.log';self.out=out;self.report=report
  self.active=None;self.total=0;self.records=0
  self.directory=out/'artifacts/surface-windows';self.directory.mkdir(parents=True,exist_ok=False)
  report['surface']=dict(backend='log',events=list(EVENTS),windows=[],state_checks=[],max_segment_bytes=MAX_SEGMENT,max_total_bytes=MAX_TOTAL,max_records=MAX_RECORDS)
 def state(self,on):
  replies=[];failures=[]
  for event in EVENTS:
   try:
    reply=self.command(4594,'trace-event '+event+(' on' if on else ' off'))
    info=self.command(4594,'info trace-events '+event)
    assert re.search(re.escape(event)+r' : state '+str(int(on))+r'\b',info),info
    replies.append(dict(event=event,toggle=reply,state=info))
   except Exception as exc:failures.append(dict(event=event,error=repr(exc)))
  self.report['surface']['state_checks'].append(dict(enabled=on,replies=replies))
  if failures:
   self.report['surface'].setdefault('state_errors',[]).extend(failures)
   raise RuntimeError(repr(failures))
 def prelaunch(self):
  # CPU is stopped. Prove actual HMP switches exist; no guest workload executed.
  self.state(False);self.state(True);self.state(False)
  self.report['surface']['prelaunch_state_verified']=True
 def begin(self,sample,after):
  assert self.active is None
  self.state(True)
  self.active=dict(sample=sample,after_stop=after,start_offset=self.path.stat().st_size,start_monotonic=time.monotonic())
 def check_bound(self):
  if self.active:
   size=self.path.stat().st_size-self.active['start_offset']
   assert size<=MAX_SEGMENT and self.total+size<=MAX_TOTAL,'Trace byte bound exceeded'
   assert time.monotonic()-self.active['start_monotonic']<=30,'Upload window exceeded 30 seconds'
 def end(self):
  if self.active is None:return
  self.state(False)
  row=self.active;self.active=None
  end=self.path.stat().st_size;size=end-row['start_offset']
  assert 0<=size<=MAX_SEGMENT and self.total+size<=MAX_TOTAL,'Trace byte bound exceeded'
  with self.path.open('rb') as f:f.seek(row['start_offset']);data=f.read(size)
  assert len(data)==size
  events=decode(data);self.total+=size;self.records+=len(events);assert self.records<=MAX_RECORDS
  name='%02d.log'%len(self.report['surface']['windows']);(self.directory/name).write_bytes(data)
  row.update(end_offset=end,bytes=size,records=len(events),sha256=hashlib.sha256(data).hexdigest(),artifact=name,duration_seconds=time.monotonic()-row.pop('start_monotonic'))
  self.report['surface']['windows'].append(row)
 def close(self):
  try:self.end()
  finally:self.state(False)
  self.report['surface'].update(events_disabled=True,total_bytes=self.total,total_records=self.records)
