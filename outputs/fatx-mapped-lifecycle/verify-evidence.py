"""Check source, raw buffer and cold evidence pins, keeping coverage failures."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002']
out=k/case;sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text())
t=read(out/'trace.json');a=read(out/'lifecycle-analysis.json')
source=out/'trace-source.py' if (out/'trace-source.py').exists() else k/'trace.py'
sites=out/'sites-source.json' if (out/'sites-source.json').exists() else k/'sites.json'
review=out/'review-sites-source.py' if (out/'review-sites-source.py').exists() else k/'review-sites.py'
assert sha(source.read_bytes())==t['source_sha256'] and sha(sites.read_bytes())==t['sites_sha256']
assert sha(review.read_bytes())==read(sites)['source_sha256']
assert sha((k/'atomic_json.py').read_bytes())==t['atomic_json_source_sha256']
assert sha((out/'trace.json').read_bytes())==a['trace_sha256']
assert t.get('guest_resumed') and not t['armed_breakpoints_remaining'] and not t['active_records_remaining']
assert not a['ordinary_qualified'] and not a['physical_access']
assert read(out/'setupapi-identity.json')['matched']
for name,digest in a['evidence_sha256'].items():assert sha((out/name).read_bytes())==digest
count=0
for row in t['records']:
    refs=[row[n] for n in ['first_string','second_string'] if n in row]
    refs.extend(e[n] for e in row['events'] for n in ['mapped_append','target_warning'] if n in e)
    for ref in refs:
        b=(out/'artifacts'/ref['file']).read_bytes();assert len(b)==ref['bytes'] and sha(b)==ref['sha256'];count+=1
assert count==a['buffers_verified']
for name in subprocess.check_output(['git','ls-files','--','outputs/fatx-mapped-lifecycle'],cwd=ws,text=True).splitlines():
    assert subprocess.check_output(['git','show',':'+name],cwd=ws)==(ws/name).read_bytes(),'Staged bytes differ: '+name
print(json.dumps(dict(case=case,buffers_verified=count,target_mapped_lifecycle_verified=a['target_mapped_lifecycle_verified'],cold_checks_passed=a['cold_checks_passed'])))
