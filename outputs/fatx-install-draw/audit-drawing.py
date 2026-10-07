"""Audit GDI lifecycle and target-warning coverage without claiming exact syscall overlap."""
import json,re,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['001','002'];out=k/case;dest=out/'drawing-audit.json';assert not dest.exists()
f=json.loads((k/('fixture-'+case+'.json')).read_text());al=json.loads((out/'alignment.json').read_text())
lines=(out/'artifacts/drawing.log').read_text().splitlines()
start=re.fullmatch(r'DRAW_START (\d+) (\d+) (\d+) (\d+) (\d+)',lines[0]) if lines else None
end=re.fullmatch(r'DRAW_END (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)',lines[-1]) if lines else None
samples=[re.fullmatch(r'DRAW_SAMPLE (\d+) (\d+) (\d+) (\d+) (\d+)',line) for line in lines[1:-1]]
mode=1 if case=='002' else 0
valid=bool(start and end and len(samples)==5 and all(samples));coverage=False;r=dict(case=case,physical_access=False,mode=mode,raw_lines=lines)
if valid:
 st=list(map(int,start.groups()));en=list(map(int,end.groups()));rows=[list(map(int,v.groups())) for v in samples]
 r.update(start=st,end=en,samples=rows)
 valid=st[0]==en[0]==mode and st[4]==en[4]==en[5]==0 and st[2]==en[2] and f['alignment']['before_bytes']<=st[2]<=en[3]<0xffffffff
 prior_frames=st[3];prior_size=st[2]
 for i,row in enumerate(rows):
  index,elapsed,frames,size,error=row
  valid=valid and index==i and elapsed>=i*30000 and frames>=prior_frames and prior_size<=size<=en[3] and error==0
  prior_frames=frames;prior_size=size
 valid=valid and en[1]>=prior_frames
 if mode:
  valid=valid and st[3]>0 and all(rows[i+1][2]>rows[i][2] for i in range(4))
  coverage=bool(st[2]<=al['desired_offset'] and en[3]>al['desired_offset']+al['expected_warning_bytes'] and en[1]>st[3] and al['actual_alignment_verified'])
 else:valid=valid and st[3]==en[1]==0 and all(row[2]==0 for row in rows);coverage=True
r.update(protocol_passed=bool(valid),target_warning_coverage=bool(valid and coverage),hardware_qualified=False,limits='Positive mode1 coverage means API-completed drawing began before target bytes became visible in file size, continued across sampled growth, and stopped/joined before restart. It does not prove overlap of individual WriteFile/BitBlt syscalls or observe the original SetupAPI source buffer. Mode0 coverage gate is inapplicable and true by convention.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
