import json
from pathlib import Path
from activation_analysis import analyze
rows=[('START201',[1,1,120000]),('ACTIVATE_OWNER313',[10,100,1]),('ACTIVATE_INTENT313',[10,20,1]),('FG_ACTIVATE_BEFORE313',[30,40,31]),('GUI_ACTIVATE_BEFORE313_OWNER',[10,11,0]),('GUI_ACTIVATE_BEFORE313_ACTIVE',[0,0,0]),('GUI_ACTIVATE_BEFORE313_CAPTURE',[0,0,0]),('ACTIVATE_RESULT313',[10,20,1]),('FG_ACTIVATE_AFTER313',[10,20,11]),('GUI_ACTIVATE_AFTER313_OWNER',[10,11,0]),('GUI_ACTIVATE_AFTER313_ACTIVE',[0,20,21]),('GUI_ACTIVATE_AFTER313_CAPTURE',[0,0,0]),('CANCEL_ACTIVE_VERIFIED',[10,20,11]),('CANCEL_CLOSED_OWNER',[10,100,1]),('CANCEL_WINDOW_CLOSED',[10,20,0]),('IDLE201',[5000,1,8000])]
def encode(r):return ''.join(k+' '+' '.join(map(str,v))+'\r\n' for k,v in r).encode()
assert analyze(encode(rows))['passed']
rejected=0
for i in range(1,len(rows)-1):
    r=rows[:i]+rows[i+1:]
    try:analyze(encode(r))
    except AssertionError:rejected+=1
    else:raise AssertionError(('missing accepted',i))
for i,j,value in [(1,0,0),(1,1,0),(2,2,2),(3,1,20),(4,1,0),(5,0,2),(6,0,1),(7,2,2),(8,0,99),(8,2,99),(9,1,99),(10,0,16),(11,2,1),(12,2,99),(13,1,99),(14,1,99),(15,0,4999),(5,1,20),(5,1,99),(10,1,0)]:
    r=[(k,list(v)) for k,v in rows];r[i][1][j]=value
    try:analyze(encode(r))
    except AssertionError:rejected+=1
    else:raise AssertionError(('mutation accepted',i,j))
dest=Path(__file__).with_name('analysis-tests001.json');assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,negative_controls=rejected,interfaces='Synthetic log only; unchanged original Cancel/idle decoder required'),indent=2)+'\n');print('Rejected',rejected,'negative controls')
