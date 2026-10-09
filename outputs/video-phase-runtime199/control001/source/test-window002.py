"""Synthetic host-only adversaries; no guest result or physical permission."""
import copy, hashlib, json
from pathlib import Path
from window_analysis import window
k=Path(__file__).resolve().parent;dest=k/'window-tests002.json';assert not dest.exists()
def make(mode):
    lines=[['WINDOW_CASE_pass',1,40,0],['WINDOW_ROUNDS_paints_ms',40,40,1000]]
    for phase in range(2):
        s=[0]*32;s[0:2]=[0x53525758,112];s[20]=1
        p=[0]*32;p[:7]=[0x544d5758,113,128,mode,1125000,0,128];p[9]=22;p[26]=256
        if phase:
            s[2:5]=[40,40,40];s[16]=80;s[17]=80*131072
            for i,c in enumerate([40,40,80,80]):p[14+3*i]=c;p[15+3*i]=c*mode
            p[26]+=480*mode
        lines += [['WINDOW_STATS_CALL',phase,1,0],['WINDOW_PROFILE_CALL',phase,1,0]]
        lines += [['WINDOW_STATS_index_value',phase,i,v] for i,v in enumerate(s)]
        lines += [['WINDOW_PROFILE_index_value',phase,i,v] for i,v in enumerate(p)]
    return lines
def render(rows):return '\n'.join(' '.join(map(str,r)) for r in rows)
checks=0
for mode in range(2):
    rows=make(mode);assert window(render(rows),mode)['passed'];checks+=1
    def reject(q):
        global checks
        assert not window(render(q),mode)['passed'];checks+=1
    reject(rows[:-1]);reject(rows+[rows[-1]]);reject(rows+[['MISMATCH_WINDOW_round_index',3,8,0]])
    reject([r for r in rows if r[0]!='WINDOW_CASE_pass']);reject([r for r in rows if r[0]!='WINDOW_STATS_CALL'])
    for label,phase,index,value in [
        ('WINDOW_PROFILE_index_value',0,3,1-mode),('WINDOW_PROFILE_index_value',0,4,0),
        ('WINDOW_PROFILE_index_value',0,5,0x80000000),('WINDOW_PROFILE_index_value',0,6,127),
        ('WINDOW_PROFILE_index_value',1,11,1),('WINDOW_PROFILE_index_value',1,12,1),
        ('WINDOW_PROFILE_index_value',1,26,1),('WINDOW_PROFILE_index_value',1,27,1),
        ('WINDOW_PROFILE_index_value',1,14,39),('WINDOW_STATS_index_value',1,4,39),
        ('WINDOW_STATS_index_value',1,16,79),('WINDOW_STATS_index_value',1,17,0),
        ('WINDOW_STATS_index_value',1,19,1),('WINDOW_STATS_index_value',1,21,1),
        ('WINDOW_STATS_index_value',1,2,0xffffffff)]:
        q=copy.deepcopy(rows)
        next(r for r in q if r[:3]==[label,phase,index])[3]=value;reject(q)
    q=copy.deepcopy(rows)
    for index in [2,14]:
        next(r for r in q if r[:3]==['WINDOW_STATS_index_value',1,index])[3]=0
    reject(q)
    for index,value in [(1,39),(2,39),(3,0),(3,180000)]:
        q=copy.deepcopy(rows);next(r for r in q if r[0]=='WINDOW_ROUNDS_paints_ms')[index]=value;reject(q)
dest.write_text(json.dumps(dict(passed=True,checks=checks,host_synthetic_only=True,guest_launch=False,physical_access=False,pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [k/'window_analysis.py',Path(__file__)]}),indent=2)+'\n')
print(checks,'window packet adversary checks')
