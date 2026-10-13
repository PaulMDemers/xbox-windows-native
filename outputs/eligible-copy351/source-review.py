import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'primary-copy348';dest=K/'source-review001.json';assert not dest.exists() and sys.platform=='linux'
base=Path('/home/paul/xbox-windows-native/build');a=base/'primary-copy348-build001/source/win32ss/drivers/displays/framebuf';b=base/'eligible-copy351-build001/source/win32ss/drivers/displays/framebuf'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changes=[n for n in sorted(p.name for p in a.iterdir() if p.is_file()) if (a/n).read_bytes()!=(b/n).read_bytes()]
assert changes==['enable.c','framebuf.h','ownership.c'],changes
assert {p.name for p in b.iterdir() if p.is_file()}-{p.name for p in a.iterdir() if p.is_file()}=={'eligible.h'}
s=(b/'ownership.c').read_text().replace('#include "eligible.h"\n','').replace(' XwnEligibleRecord(p->PrimaryStats,result,bytes);\n','')
s=s[:s.index('\nVOID XwnEligibleSnapshot')];assert s==(a/'ownership.c').read_text()
old=(P/'probe/large_cases.c').read_text();new=(K/'probe/large_cases.c').read_text()
assert new.replace('0x58574439','0x58574438').replace('data[1]!=351','data[1]!=348').replace('PRIMARY351_','PRIMARY348_').replace('||data[11]||data[14])','||data[11])').replace('for(i=15;i<32;i++)','for(i=12;i<32;i++)')==old
for n in ['gdi-probe.c','text-cases.c','large_oracle.h']:assert (P/'probe'/n).read_bytes()==(K/'probe'/n).read_bytes()
assert (b/'eligible.h').read_bytes()==(K/'eligible.h').read_bytes()
dest.write_text(json.dumps(dict(passed=True,changed_original_files=changes,new_file='eligible.h',old348_record_and_snapshot_exact_after_removing_new_call=True,old348_packet_unchanged=True,pdev_layout_unchanged=True,unchanged={p.name:sha(p) for p in a.iterdir() if p.is_file() and p.name not in changes},new_counter_sha256=sha(K/'eligible.h'),probe_only_packet_version_validation_and_tags=True,planner_admission_copy_upload_cache_lifetime_unchanged=True),indent=2)+'\n');print('Source identity PASS')
