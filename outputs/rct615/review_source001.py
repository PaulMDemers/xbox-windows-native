"""Reuse the cached-scene/cold review and replace trace gates with cost gates."""
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K.parent/'rct612/review001.py').read_text()
assert not (K/'review001.py').exists()
for prefix in ['rct','xwn','run','verify']:s=s.replace(prefix+'612',prefix+'615')
s=s.replace('from analyze_trace001 import analyze','from cost_oracle import analyze')
s=s.replace(",'park_phase_requested=1','park_phase_ack_wait=0','park_phase_acknowledged=1'",'')
s=s.replace(" and run.count('park_phase_requested=1')==1",'')
start=s.index(" game=Path('C:/xwn566")
end=s.index('except BaseException',start)
s=s[:start]+''' cost=(logs/'cost.txt').read_text()
 host=json.loads(Path('C:/xwn615/pc001/phase1/serial-host.json').read_text())
 result=analyze(cost,host)
 (K/'serial-host001.json').write_text(json.dumps(host,indent=2)+'\\n')
 (K/'raw-counter-logs001.json').write_text(json.dumps(dict(cost=cost,runner=run),indent=2)+'\\n')
 (K/'cost-review001.json').write_text(json.dumps(result,indent=2)+'\\n')
 states=[]
 import re
 for tag in ['cost-before','cost-after']:
  match=re.search(r'input_state='+tag+r' tick=(\\d+) valid=1 pid=(\\d+) foreground=1 foreground_pid=(\\d+) foreground_class=RollerCoaster Tycoon rect_read=1 origin_read=1 cursor_read=1 client=(\\d+),(\\d+),640,480 cursor=(\\d+),(\\d+) display=1024,768',run)
  assert match,tag
  values=list(map(int,match.groups()));assert values[1]==values[2]
  assert values[5]==values[3]+5 and values[6]==values[4]+5
  states.append(values)
 assert states[0][1:]==states[1][1:] and states[0][0]<=host['rows'][2]['tick']<=host['rows'][3]['tick']<=states[1][0]
 r.update(passed=True,cost=result,window_states=states)
''' + s[end:]
s=s.replace("print('606 independent saved scene, phase trace and cold cleanup passed; visual inspection pending')",
            "print('615 saved scene, process costs and cold cleanup passed; visual inspection pending')")
(K/'review001.py').write_text(s,encoding='utf-8',newline='\n')
