import hashlib,json
from pathlib import Path
from primary_analysis import analyze
K=Path(__file__).resolve().parent;dest=K/'parser001.json';assert not dest.exists();checks=0
def require(v):
 global checks
 checks+=1;assert v
def fixture(mode):
 lines=[]
 for id in range(15):
  for phase in [0,1]:
   d=[0x50435758,351,128,mode]+[0]*28
   # Modeled actual350 shape:8 eligible nonempty +3 ineligible output +2 saves.
   if phase:
    d[4]=130;d[5]=80;d[6 if mode else 8]=80;d[8]+=50
    d[12]=20675640;d[9]=d[12] if mode else 0
   lines.append(f'PRIMARY351_PACKET {id} {phase} 1')
   lines.extend(f'PRIMARY351_{"AFTER" if phase else "BEFORE"} {id} {i} {v}' for i,v in enumerate(d))
  lines.append(f'LARGE_TIMING {id} 10 750')
 return lines
for mode in [0,1]:
 lines=fixture(mode);text='\n'.join(lines);require(analyze(text,mode)['passed'])
 for i,line in enumerate(lines):
  damaged=lines.copy();parts=line.split();parts[-1]='4294967296';damaged[i]=' '.join(parts)
  require(not analyze('\n'.join(damaged),mode)['passed'])
 for tag,index,value in [('AFTER',1,348),('AFTER',11,1),('AFTER',14,1),('AFTER',15,1),('AFTER',12,0),('AFTER',12,20675639),('AFTER',5,79),('AFTER',4,129)]:
  # OFF byte totals may legitimately vary: only malformed/global impossible cases must fail.
  if not mode and (index==12 and value!=0 or index==5):continue
  bad=text.replace(f'PRIMARY351_{tag} 2 {index} '+('351' if index==1 else str({11:0,14:0,15:0,12:20675640,5:80,4:130}[index])),f'PRIMARY351_{tag} 2 {index} {value}')
  require(bad!=text);require(not analyze(bad,mode)['passed'])
 require(not analyze(text,1-mode)['passed']);require(not analyze(text+'\n'+lines[-1],mode)['passed'])
 require(not analyze('\n'.join(lines[:-1]),mode)['passed'])
 # Explicit64-bit carry: lowword decreases while full total increases, no wrap.
 carry=text
 for id in range(15):
  for phase in [0,1]:
   vals={4:1000000+phase*130,5:600000+phase*80,6:(600000+phase*80 if mode else 0),8:(400000+phase*50 if mode else 1000000+phase*130),12:0xfffffff0 if not phase else (0xfffffff0+20675640)&0xffffffff,13:phase}
   if mode:vals.update({9:vals[12],10:phase})
   for index,value in vals.items():
    prefix=f'PRIMARY351_{"AFTER" if phase else "BEFORE"} {id} {index} '
    carry='\n'.join(prefix+str(value) if row.startswith(prefix) else row for row in carry.splitlines())
 require(analyze(carry,mode)['passed'])
dest.write_text(json.dumps(dict(passed=True,checks=checks,scope='Synthetic351 schema/counters/eligibility/overflow/transport;6036 ineligible output bytes accepted only via exact eligible denominator, no percentage threshold',parser_sha256=hashlib.sha256((K/'primary_analysis.py').read_bytes()).hexdigest()),indent=2)+'\n');print(checks,'passed')
