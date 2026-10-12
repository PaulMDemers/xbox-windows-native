"""Change only launcher in a new child of the never-executed combined251 preparation."""
import json,pathlib,subprocess,sys,shutil
K=pathlib.Path(__file__).resolve().parent;ws=K.parents[1];case=sys.argv[1];assert case in ('control001','candidate001')
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,readers,sha,save,hive,scan,m,HIVES
sys.path.insert(0,str(K.parent/'setup-wizard-automation201'));from restore import restore
parent=json.loads((K.parent/'hd-reservation301/candidate001/fixture.json').read_text());base=pathlib.Path(parent['fixture_path_linux']);assert sha(base)==parent['fixture_sha256']
assert case=='control001'
out=K/case;assert out.exists() and not (out/'fixture.json').exists();art=out/'artifacts'
private=pathlib.Path('/mnt/d/xwn304/fixtures')/case;assert private.exists()
target=private/'preparation.qcow2';source=private/'source.qcow2';mode=case
review=json.loads((K.parent/'hd-surface303/binary-review003.json').read_text());assert review['passed']
build=PathBuild=pathlib.Path('/mnt/d/xwn303/build003')/case
mapping={'F/winnt/system32/xwnown.dll':'xwnown.dll'}
assert sha(build/'xwnown.dll')==review['cases'][case]['sha256']
files=dict(parent['files']);protected=dict(parent['protected'])
with ColdIO(base) as io:
 rr=readers(io,base)
 for n,h in files.items():v,p=n.split('/',1);assert m.sha(rr[v].read(p))==h,n
 # A never-executed seed must not contain output from its staged runner.
 try:rr['F'].read(parent['namespace']+'/attempt.log')
 except KeyError:pass
 else:raise AssertionError('Seed contains consumed workload')
assert source.exists() and target.exists()
for name,binary in mapping.items():files[name]=sha(build/binary);protected[name]=sha(build/binary)
source_before=sha(source)
with ColdIO(source) as io:
 rr=readers(io,source)
 for n,h in files.items():v,p=n.split('/',1);assert m.sha(rr[v].read(p))==h,n
 for n in HIVES:
  p=art/('before-'+n);data=rr['F'].read('winnt/system32/config/'+n)
  if p.exists():assert p.read_bytes()==data
  else:p.write_bytes(data)
  hive(p)
scan(source,out/'before/artifacts');a=json.loads((out/'before/allocation.json').read_text());assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==parent['fixture_sha256'] and sha(source)==source_before
f=dict(parent);f.update(parent=str(base),parent_sha256=parent['fixture_sha256'],fixture_path_linux=str(source),fixture_path_windows='D:'+str(source)[6:],fixture_sha256=sha(source),files=files,protected=protected,case=case,replacement_files={n:sha(build/b) for n,b in mapping.items()},avpack='hdtv',eeprom_source='E:/xwn289/fixture001/hd.bin',physical_access=False,guest_launch=False,limits='Matched303 software bounds on unused301 candidate preparation; same300 nine-MiB chain/audio004/FATX0101. HDTV profile, unchanged low-resolution timings. No physical or Windows1080 qualification')
save(out/'fixture.json',f);print('Prepared',case,'with one matched software display override')
