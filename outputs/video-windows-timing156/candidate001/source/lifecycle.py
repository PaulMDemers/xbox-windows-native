"""Sparse surface lifecycle tracing, bounded from emulator startup to final marker."""
import hashlib,re,time
EVENTS=tuple('nv2a_pgraph_surface_'+n for n in ('create_color','create_zeta','invalidated','evict_reason','evict_overlapping','upload','download'))
MAX_BYTES=16*1024*1024
MAX_EVENTS=65536
CREATE=re.compile(r'nv2a_pgraph_surface_create_(color|zeta)\s+Create: \[(COLOR|ZETA)\s+@ 0x([0-9a-fA-F]+) \((\d+)x(\d+)\)\] \(([^)]*)\) aa:(\d+), clip:x=(\d+),w=(\d+),y=(\d+),h=(\d+),p=(\d+)')
TRANSFER=re.compile(r'nv2a_pgraph_surface_(upload|download) \[(RAM->GPU|GPU->RAM)\] (\S+) \(([^)]*)\) surface @ 0x([0-9a-fA-F]+) \(w=(\d+),h=(\d+),p=(\d+),bpp=(\d+)\)')
INVALID=re.compile(r'nv2a_pgraph_surface_invalidated 0x([0-9a-fA-F]+)')
EVICT=re.compile(r'nv2a_pgraph_surface_evict_reason Evicting (.+) surface @ 0x([0-9a-fA-F]+)')
OVERLAP=re.compile(r'nv2a_pgraph_surface_evict_overlapping Evicting overlapping surface @ 0x([0-9a-fA-F]+) \((\d+)x(\d+),p=(\d+)\)')

def parse(data):
 assert len(data)<=MAX_BYTES
 rows=[];offset=0
 for raw in data.splitlines(keepends=True):
  line=raw.rstrip(b'\r\n').decode('ascii','replace');name=line.split(' ',1)[0]
  if name in EVENTS:
   r=dict(offset=offset,end_offset=offset+len(raw),event=name,raw=line)
   if m:=CREATE.fullmatch(line):
    r.update(kind='create',binding=m[1],base=int(m[3],16),width=int(m[4]),height=int(m[5]),layout=m[6],anti_aliasing=int(m[7]),clip_x=int(m[8]),clip_width=int(m[9]),clip_y=int(m[10]),clip_height=int(m[11]),pitch=int(m[12]))
   elif m:=TRANSFER.fullmatch(line):
    r.update(kind=m[1],binding=m[3],base=int(m[5],16),width=int(m[6]),height=int(m[7]),pitch=int(m[8]),bytes_per_pixel=int(m[9]),layout=m[4])
   elif m:=INVALID.fullmatch(line):r.update(kind='invalidated',base=int(m[1],16))
   elif m:=EVICT.fullmatch(line):r.update(kind='evict_reason',base=int(m[2],16),reason=m[1])
   elif m:=OVERLAP.fullmatch(line):r.update(kind='evict_overlapping',base=int(m[1],16),width=int(m[2]),height=int(m[3]),pitch=int(m[4]))
   else:raise AssertionError('Unparsed selected lifecycle event: '+line)
   if 'layout' in r:
    # Pinned surface.c uses "ln" for create, "lin" for transfer, "sz" for both.
    assert r['layout'] in ('ln','lin','sz')
    r['normalized_layout']='swizzled' if r['layout']=='sz' else 'linear'
   assert 0<=r['base']<64*1024*1024
   rows.append(r);assert len(rows)<=MAX_EVENTS
  offset+=len(raw)
 return rows

class Lifecycle:
 def __init__(self,command,run,out,report):
  self.command=command;self.path=run/'cpu-trace.log';self.out=out;self.report=report
  report['lifecycle']=dict(events=list(EVENTS),max_bytes=MAX_BYTES,max_events=MAX_EVENTS,states=[],markers=[])
 def check(self,expected,disable=False):
  errors=[];records=[]
  for name in EVENTS:
   try:
    toggle=self.command(4594,'trace-event '+name+' off') if disable else None
    response=self.command(4594,'info trace-events '+name)
    assert re.search(re.escape(name)+r' : state '+str(int(expected))+r'\b',response),response
    records.append(dict(event=name,toggle=toggle,response=response))
   except Exception as exc:errors.append(dict(event=name,error=repr(exc)))
  self.report['lifecycle']['states'].append(dict(expected=expected,disable=disable,records=records,errors=errors))
  assert not errors,errors
 def bound(self):assert self.path.stat().st_size<=MAX_BYTES,'Lifecycle log exceeded byte bound'
 def mark(self,name,**values):
  self.bound();self.report['lifecycle']['markers'].append(dict(name=name,offset=self.path.stat().st_size,**values))
 def prelaunch(self):
  self.check(True);self.mark('before_launch_armed')
 def close(self):
  self.check(False,disable=True);self.bound()
  data=self.path.read_bytes();events=parse(data)
  target=self.out/'artifacts/lifecycle.log';assert not target.exists();target.write_bytes(data)
  self.report['lifecycle'].update(events_disabled=True,bytes=len(data),event_count=len(events),sha256=hashlib.sha256(data).hexdigest(),events_observed=events)
