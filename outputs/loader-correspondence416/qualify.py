"""Complete-byte correspondence and mutation checks; stage only reviewed artifacts."""
import collections
import hashlib
import json
import shutil
import sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'outputs/baseline-compare415'))
from compare import pe,pe_compare
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
r1=read(K/'build001.json');r2=read(K/'build002.json')
assert r1['status']==r2['status']=='compiled' and r2['generated_header_exact']
private=Path('/mnt/e/xwn416');assert not private.exists()
assert shutil.disk_usage('/mnt/e').free-16*1024**2>=20*1024**3
private.mkdir()
rows=[];checks=0
def accepted(a,b,base):
    try:return pe_compare(a,b,base)['timestamp_checksum_only']
    except (AssertionError,ValueError,IndexError):return False
for profile,artifact,relative,base,build in [
    ('hal','halxboxnt5.dll','loader/halxboxnt5.dll',0,r1['cases']['hal']),
    ('loader','freeldr.sys','freeldr.sys',2048,r2),
    ('loader','rosload.exe','rosload.exe',0,r2)]:
    source=Path(build['output'])/'artifacts'/artifact
    old=(Path('/mnt/e/xwn415/demo/Applications/XWNEBoot')/relative).read_bytes()
    new=source.read_bytes()
    assert sha(new)==next(x['sha256'] for x in build['result']['artifacts'] if x['file']==artifact)
    details=pe_compare(old,new,base);assert details['timestamp_checksum_only']
    layout=pe(new,base)
    allowed={i for o,n in layout['fields'].values() for i in range(o,o+n)}
    offsets={0,len(new)-1,base+60,base+64}
    for s in layout['sections']:
        if s['bytes']:offsets.update([s['raw'],s['raw']+s['bytes']//2,s['raw']+s['bytes']-1])
    for off in sorted(offsets-allowed):
        mutated=bytearray(new);mutated[off]^=1
        assert not accepted(old,mutated,base),(artifact,off)
        checks+=1
    assert not accepted(old,new+b'\0',base);checks+=1
    assert not accepted(old,new[:-1],base);checks+=1
    for phase,data in [('candidate',new),('baseline',old)]:
        dest=private/phase/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        assert dest.read_bytes()==data
    rows.append(dict(file=artifact,relative=relative,source_path=str(source),
                     baseline_sha256=sha(old),candidate_sha256=sha(new),bytes=len(new),details=details))
warnings={}
for label,out,parent in [('hal001',r1['cases']['hal']['output'],'hal'),
                         ('loader001',r1['cases']['loader']['output'],'loader'),
                         ('loader002',r2['output'],'loader')]:
    def warning_messages(p):
        return collections.Counter(line.split('warning:',1)[1].strip() for line in p.read_text(errors='replace').splitlines() if 'warning:' in line)
    log=Path(out)/'build.log'
    prior=Path('/home/paul/xbox-windows-native')/('release-readiness403-'+parent+'001/build.log')
    actual=warning_messages(log);expected=warning_messages(prior)
    assert not (set(actual)-set(expected)),(label,set(actual)-set(expected))
    warnings[label]=dict(messages=dict(actual),count=sum(actual.values()),new_messages=[],
                         log_sha256=sha(log.read_bytes()),reference_log_sha256=sha(prior.read_bytes()))
result=dict(passed=True,all_nonmetadata_bytes_exact=True,files=rows,negative_checks=checks,
            warnings=warnings,physical_access=False,guest_launch=False,
            candidate_root='E:/xwn416/candidate',baseline_root='E:/xwn416/baseline',
            original_partial_result_preserved='comparison001.json',
            reconstructed_version_metadata_is_not_new_revision_identity=True,
            source_inputs={str(p.relative_to(W)):sha(p.read_bytes()) for p in [K/'qualify.py',K/'build001.json',K/'build002.json',W/'outputs/baseline-compare415/compare.py']})
with (K/'comparison002.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(passed=True,files=3,negative_checks=checks,warnings={k:v['count'] for k,v in warnings.items()})))
