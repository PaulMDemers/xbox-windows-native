"""Validate the complete348 extension before projecting to unchanged344 decoder."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'hd-phase344'))
from phase_analysis import analyze as original
from primary_analysis import analyze as primary
def analyze(log,mode):
    try:
        assert primary(log,mode)['passed']
        rows=[v.split() for v in log.splitlines()]
        for id in range(15):
            marker=['PRIMARY348_PACKET',str(id),'0','1'];positions=[i for i,v in enumerate(rows) if v==marker]
            assert len(positions)==1;start=positions[0]
            assert rows[start-1][:3]==['PHASE344_AFTER',str(id),'31']
            expected=[]
            for phase in [0,1]:
                expected.append(['PRIMARY348_PACKET',str(id),str(phase)])
                expected.extend([['PRIMARY348_AFTER' if phase else 'PRIMARY348_BEFORE',str(id),str(i)] for i in range(32)])
            assert [v[:3] for v in rows[start:start+66]]==expected
            assert rows[start+66][:2]==['LARGE_TIMING',str(id)]
        projected='\n'.join(' '.join(v) for v in rows if not v[0].startswith('PRIMARY348_'))
        r=original(projected,1);assert r['passed']
        r['limits']='Validated348 packets between contiguous344 packet and timing. Unchanged344 decoder receives projection ONLY after348 schema/placement/coverage checks. Both drivers profilingON; category1 is selected CopyBits body. Global/preemption/nested timing limitations remain.'
        return r
    except (AssertionError,ValueError,KeyError,IndexError,TypeError) as e:return {'passed':False,'error':type(e).__name__,'physical_qualified':False}
