"""Verify frozen recovery evidence and the independent Microsoft dump-reader result."""
import hashlib,json,re,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'recovery003'
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def host(s):return Path(s.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
a=read(out/'audit.json');c=read(out/'closure.json');pre=read(out/'preflight.json');f=read(k/'fixture-recovery003.json')
for n,h in pre['sources'].items():assert sha(out/'source'/n)==h,(n,'source changed')
assert a['recovery_qualified'] and not a['ordinary_qualified'] and not a['physical_access']
assert c['never_relaunch'] and sha(Path(c['private_disk']))==c['private_disk_sha256']
for row in f['parents']:assert sha(host(row['path']))==row['sha256']
for row in a['hives']:assert sha(out/'artifacts'/('after-'+row['name']))==row['sha256'] and row['parsed']
assert sha(out/'allocation.json')==a['allocation_sha256']
assert len(a['saved_dumps'])==1
saved=out/'artifacts'/a['saved_dumps'][0]['artifact'];data=saved.read_bytes()
assert sha(saved)==f['crash_payload_sha256']==a['saved_dumps'][0]['sha256']
assert data==(k.parent/'atapi-lba48-crash/crash006/artifacts/after-pagefile-prefix.bin').read_bytes()
assert len(data)==65536 and data[:8]==b'PAGEDUMP'
assert struct.unpack_from('<5I',data,40)==(0xe058d103,0x44554d50,0x103,0x10000,1)
parser=read(out/'dump-reader.json');assert parser['exit_code']==0 and parser['authenticode']=='Valid'
assert sha(saved)==parser['dump_sha256']
log=out/'artifacts/cdb-recovered.txt';assert sha(log)==parser['log_sha256'];text=log.read_text()
for snippet in ['Mini Kernel Dump File','Windows 2000 Kernel Version 2195','Bugcheck code E058D103','Arguments 44554d50 00000103 00010000 00000001','DUMP_HEADER32:','TRIAGE_DUMP32:','dump_atapi','trigger']:
    assert snippet in text,snippet
for label,value in [('MachineImageType','0000014c'),('NumberProcessors','00000001'),('SizeOfDump','00010000'),('ValidOffset','0000fffc'),('DriverCount','0000004d')]:
    assert re.search(r'\b'+label+r'\s+'+value+r'\b',text),(label,value)
assert re.search(r'\beip=[0-9a-f]{8}\b',text)
for phase in ['before','after']:assert read(out/(phase+'-configuration.json'))['expected_configuration']
before,after=[read(out/(phase+'-pagefile-map.json')) for phase in ['before','after']]
assert before['clusters']==after['clusters'] and before['requested_65536']==after['requested_65536']
r=dict(passed=True,physical_qualified=False,ordinary_qualified=False,controlled_recovery_qualified=True,
       original_crash_unchanged=True,exact_saved_bytes=len(data),dump_sha256=sha(saved),
       saved_path=a['saved_dumps'][0]['path'],frozen_sources=len(pre['sources']),
       expected_prior_crash_events=a['expected_prior_crash_events'],
       unexpected_warning_error_count=len(a['unexpected_warnings_errors']),
       normal_shutdown_count=a['normal_shutdown_count'],independent_reader=parser,
       audit_sha256=sha(out/'audit.json'),closure_sha256=sha(out/'closure.json'),
       limits='One controlled emulator crash and separate recovery. Reader validates header, crash identity, context and module list; no fully symbolized stack-unwind claim. No physical test or general >2TiB claim.')
p=k/'verification.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
