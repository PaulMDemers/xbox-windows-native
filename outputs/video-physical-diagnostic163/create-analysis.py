"""Preserve verifier failure and apply the already-qualified current-boot trace contract."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k/'verify-diagnostic.py';new=k/'verify-current-boot.py'
assert not new.exists() and not (k/'verifier-failure.json').exists()
s=old.read_text(encoding='utf-8')
a='assert n<=count<=254 and dropped==d==0 and before[32:32+n*16]==after[32:32+n*16]'
b="assert 1<=count<=254 and dropped==d==0\nassert struct.unpack_from('<I',after,32)[0]==1\nassert not any(struct.unpack_from('<I',before,32+i*16)[0] in [0x30,0x31,0x32] for i in range(n))"
assert s.count(a)==1;s=s.replace(a,b).replace('range(n,count)','range(count)')
s=s.replace('new_trace_records=len(delta)','current_boot_trace_records=len(delta),trace_restarts_per_boot=True')
s=s.replace('save(dest,r);print',"r['trace_reset_source_sha256']=sha(k.parent/'video-trace-reuse/0093-video-reuse-existing-trace.patch')\nr['prior_failed_verifier_sha256']=sha(k/'verify-diagnostic.py')\nsave(dest,r);print")
new.write_text(s,encoding='utf-8')
(k/'verifier-failure.json').write_text(json.dumps(dict(failed_verifier_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),
    error='Incorrect assertion that reusable trace appends prior-boot records',before_records=43,after_records=44,dropped=0,
    qualified_source_contract='0093 trace reuse resets the in-memory records for each boot',guest_relaunched=False,cold_collection_repeated=False,
    correction='New verifier analyzes current boot, requires shared event absent before, retains all other strict gates',
    analysis_creation_shell_failure='Earlier inline Python command rejected by PowerShell parser before execution; no file changed'),indent=2)+'\n',encoding='utf-8')
print('Failed verifier preserved; new current-boot analysis created')
