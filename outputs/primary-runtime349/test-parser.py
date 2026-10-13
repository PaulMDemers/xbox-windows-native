import hashlib,json
from pathlib import Path
from primary_analysis import analyze
K=Path(__file__).resolve().parent;dest=K/'parser001.json';assert not dest.exists()
checks=0
def require(x):
 global checks
 checks+=1;assert x
for mode in [0,1]:
 lines=[]
 for id in range(15):
  w,h=[(256,128),(640,360),(960,540)][id//5];amount=4*w*h*10
  for phase in [0,1]:
   data=[0x50435758,348,128,mode]+[0]*28
   if phase:data[4]=data[5]=10;data[6 if mode else 8]=10;data[9]=amount if mode else 0
   lines.append(f'PRIMARY348_PACKET {id} {phase} 1')
   for i,v in enumerate(data):lines.append(f'PRIMARY348_{"AFTER" if phase else "BEFORE"} {id} {i} {v}')
  lines.append(f'LARGE_TIMING {id} 10 750')
 text='\n'.join(lines);require(analyze(text,mode)['passed'])
 for i,line in enumerate(lines):
  damaged=lines.copy();parts=line.split();parts[-1]='4294967296';damaged[i]=' '.join(parts)
  require(not analyze('\n'.join(damaged),mode)['passed'])
 require(not analyze(text,1-mode)['passed']);require(not analyze(text+'\n'+lines[-1],mode)['passed'])
 require(not analyze('\n'.join(lines[:-1]),mode)['passed'])
dest.write_text(json.dumps(dict(passed=True,checks=checks,scope='Synthetic packet ordering/range/identity/coverage/transport controls; not guest evidence',parser_sha256=hashlib.sha256((K/'primary_analysis.py').read_bytes()).hexdigest()),indent=2)+'\n');print(checks,'parser checks passed')
