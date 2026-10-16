"""Exhaustive finite-state refusal checks for the rollback planner; no FTP."""
import itertools
import json
from pathlib import Path
from activate import restore_plan
accepted=refused=0
for active,old,new,used in itertools.product([None,'base','candidate','unknown'],repeat=4):
    known=active in (None,'base','candidate') and old in (None,'base') and new in (None,'candidate') and used in (None,'candidate')
    expected=known and (active=='base' or (old=='base' and (active is None or used is None)))
    try:plan=restore_plan(active,old,new,used,'base','candidate')
    except ValueError:
        assert not expected;(refused:=refused+1);continue
    assert expected
    state=dict(active=active,old=old,new=new,used=used)
    for source,target in plan:
        assert state[source] is not None and state[target] is None
        state[target]=state[source];state[source]=None
    assert state['active']=='base'
    accepted+=1
out=Path(__file__).with_name('restore-tests001.json')
with out.open('x') as f:json.dump(dict(passed=True,states=256,accepted=accepted,refused=refused,scope='Pure recovery planner, FTP/rename operations not mocked or exercised'),f,indent=2);f.write('\n')
print(accepted,refused)
