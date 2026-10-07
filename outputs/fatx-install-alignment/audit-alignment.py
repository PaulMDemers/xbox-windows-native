"""Check actual installer warning position and exact bytes after owned shutdown."""
import importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002']
out=k/case;assert not (out/'alignment.json').exists()
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'));from coldio import ColdIO
f=json.loads((k/('fixture-'+case+'.json')).read_text());a=f['alignment']
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
assert m.filehash(base)==f['fixture_sha256']
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
with ColdIO(base) as io:before=m.Writer(io,m.fatx.open_partition(io,base,'F')).read('winnt/setupapi.log')
after=(out/'artifacts/after-setupapi.log').read_bytes()
assert m.sha(before)==a['before_sha256']
assert m.sha(before[:a['original_bytes']])==a['original_sha256'] and m.sha(before[a['original_bytes']:])==a['padding_sha256']
marker=b'An unsigned or incorrectly signed driver (c:\\xwninf99\\xwnvideo.inf) was installed'
control=(k.parent/'fatx-first-install-0101/001/artifacts/after-setupapi.log').read_bytes();assert m.sha(control)==a['control_sha256']
expected=control[a['control_warning_offset']:].split(b'\r\n',1)[0]+b'\r\n'
copy=b'Copying file c:\\xwninf99\\xboxvnt5.sys to C:\\WINNT\\system32\\DRIVERS\\xboxvnt5.sys.\r\n'
positions=[];at=len(before)
while True:
 at=after.find(marker,at)
 if at<0:break
 positions.append(dict(offset=at,mod512=at%512,mod4096=at%4096,line_exact=after[at:at+len(expected)]==expected,after_copy=after[:at].endswith(copy)));at+=len(marker)
target=a['target_offset'];matched=[p for p in positions if p['after_copy']]
prefix=after.startswith(before)
r=dict(case=case,physical_access=False,warning_positions=positions,desired_offset=target,actual_after_copy_offsets=[p['offset'] for p in matched],
 actual_alignment_verified=len(matched)==1 and matched[0]['offset']==target,
 target_warning_intact=after[target:target+len(expected)]==expected,
 prefix_preserved=prefix,original_prefix_preserved=after[:a['original_bytes']]==before[:a['original_bytes']],
 target_first111_exact=after[target:target+111]==expected[:111],target_first111_sha256=m.sha(after[target:target+111]),expected_warning_bytes=len(expected),
 new_bytes=len(after)-len(before),new_non_ascii_offsets=[i for i in range(len(before),len(after)) if after[i]>127],
 before_sha256=m.sha(before),after_sha256=m.sha(after),
 limits='Actual log offset verified separately from integrity; a missed offset is not itself a storage failure. Emulator path and UI timing differ from physical run; no cause established.')
(out/'alignment.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
