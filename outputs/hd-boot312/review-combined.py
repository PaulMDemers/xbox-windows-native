"""Supplement the frozen audit: require clean events across BOTH audio and video, never waive strict errors."""
import hashlib
import json,sys
from pathlib import Path

k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ('control001','candidate001');out=k/case
dest=out/'combined-review.json';assert not dest.exists()
a=json.loads((out/'audit.json').read_text())
p=out/'artifacts/attempt.log';lines=p.read_text().splitlines()
def ft(line,label):
    parts=line.split();assert len(parts)==3 and parts[0]==label
    lo,hi=map(int,parts[1:]);assert 0<=lo<=0xffffffff and 0<=hi<=0xffffffff
    return (hi<<32)|lo
checkpoints=[(i,ft(v,'CHECKPOINT_TIME')) for i,v in enumerate(lines) if v.startswith('CHECKPOINT_TIME ')]
ends=[(i,ft(v,'MEASUREMENT_END_TIME')) for i,v in enumerate(lines) if v.startswith('MEASUREMENT_END_TIME ')]
assert len(checkpoints)==2 and len(ends)==1
first,start=checkpoints[0];last,end=ends[0]
tags=['AUDIO_STATE_JOIN 0','AUDIO_STATE_EXIT 0','AUDIO_PROBE_JOIN 0','AUDIO_PROBE_EXIT 0']
indices=[]
for tag in tags:
    assert lines.count(tag)==1;indices.append(lines.index(tag))
assert first<indices[0] and indices==list(range(indices[0],indices[0]+4)) and indices[-1]<last
assert lines[indices[-1]+1].startswith('MEASUREMENT_START_TIME ')
assert 0<start<end
interval=[start//10000000-11644473600,end//10000000-11644473600]
inside=[v for group in a['new_events'].values() for v in group
        if v['type'] in [1,2] and interval[0]-1<=v['generated_unix']<=interval[1]+1]
passed=a['scoped_combined_passed'] and not inside
r=dict(scoped_combined_passed=passed,strict_qualification_passed=passed and a['strict_events_passed'],
       audio_and_video_interval_unix=interval,interval_warning_errors=inside,
       strict_warning_errors=a['warnings_errors'],physical_qualified=False,release_qualified=False,
       source_review='PCI chat identified original frozen audit window omitted audio. This additional gate supersedes its combined verdict.',
       original_audit_sha256=hashlib.sha256((out/'audit.json').read_bytes()).hexdigest(),
       attempt_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
       limits='No event exception inside combined interval. Whole-boot Ftdisk49 remains strict failure.')
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
