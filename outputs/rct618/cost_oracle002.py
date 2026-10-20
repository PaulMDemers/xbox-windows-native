"""Actual retail process costs plus timestamped capped-recorder activity."""
from counter_oracle import costs
from alignment_oracle002 import alignment
from trace_oracle import parse
from analyze_trace001 import analyze as graphics

def analyze(log,host,trace,base,size):
 windows={};plain=[]
 for line in log.splitlines():
  if line.startswith('WINDOW '):
   case,*v=map(int,line.split()[1:]);assert case==1 and not windows and len(v)==3
   windows[case]=v
  else:plain.append(line)
 assert len(windows)==1
 result,rows,ids,_=costs('\n'.join(plain),host)
 extra=[];plain=[]
 for line in trace.splitlines():
  if line.startswith('COST_'):
   p=line.split();assert len(p)==4;extra.append((p[0],[int(x,16) for x in p[1:]]))
  else:plain.append(line)
 text='\n'.join(plain);parsed=parse(text)
 timing=alignment(parsed,extra,ids[1],rows[1,'SUBJECT_START'][0]['tick'],
                  rows[1,'SUBJECT_END'][0]['tick'],windows[1])
 evidence=graphics(text,base,size)
 assert evidence['rct_stretch_per_phase']==[32,32]
 assert all(c['result']==768 for c in parsed['calls'].values() if c['api']==11)
 return dict(passed=True,cases=result,timing=timing,graphics=evidence,
  scope='Single paused PC saved-scene interval under finite32-pair-per-phase debugger recording. Entry breakpoints remain active. No FPS or Xbox acceleration claim.')
