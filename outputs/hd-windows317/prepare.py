"""Change only default.xbe in a never-executed313 preparation."""
import json,pathlib,subprocess,sys,shutil
K=pathlib.Path(__file__).resolve().parent;ws=K.parents[1];case=sys.argv[1];assert case=='candidate001'
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,readers,sha,save,hive,scan,m,HIVES
sys.path.insert(0,str(K.parent/'setup-wizard-automation201'));from restore import restore
parent=json.loads((K.parent/'hd-ui313/candidate001/fixture.json').read_text());base=pathlib.Path(parent['fixture_path_linux']);assert sha(base)==parent['fixture_sha256']
out=K/case;assert not out.exists();out.mkdir();art=out/'artifacts';art.mkdir()
private=pathlib.Path('/mnt/d/xwn317/fixtures')/case;private.mkdir(parents=True,exist_ok=False)
target=private/'preparation.qcow2';source=private/'source.qcow2';mode=case
review=json.loads((K.parent/'hd-interlace316/binary-review002.json').read_text());assert review['passed']
build=pathlib.Path('/mnt/d/xwn316/build001/candidate001')
mapping={'E/Applications/XWNFBoot/default.xbe':'default.xbe'}
assert sha(build/'default.xbe')==review['rows']['candidate001']['files']['default.xbe']['sha256']
files=dict(parent['files']);protected=dict(parent['protected'])
with ColdIO(base) as io:
 rr=readers(io,base)
 for n,h in files.items():v,p=n.split('/',1);assert m.sha(rr[v].read(p))==h,n
 # A never-executed seed must not contain output from its staged runner.
 try:rr['F'].read(parent['namespace']+'/attempt.log')
 except KeyError:pass
 else:raise AssertionError('Seed contains consumed workload')
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
for name,binary in mapping.items():
 v,p=name.split('/',1);restore(rr[v],p,(build/binary).read_bytes());files[name]=sha(build/binary);protected[name]=sha(build/binary)
for r in rr.values():r.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
assert not json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)])).get('backing-filename')
with ColdIO(source) as io:
 rr=readers(io,source)
 for n,h in files.items():v,p=n.split('/',1);assert m.sha(rr[v].read(p))==h,n
 for n in HIVES:p=art/('before-'+n);p.write_bytes(rr['F'].read('winnt/system32/config/'+n));hive(p)
scan(source,out/'before/artifacts');a=json.loads((out/'before/allocation.json').read_text());assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==parent['fixture_sha256']
f=dict(parent);f.update(parent=str(base),parent_sha256=parent['fixture_sha256'],fixture_path_linux=str(source),fixture_path_windows='D:'+str(source)[6:],fixture_sha256=sha(source),files=files,protected=protected,case=case,replacement_files={n:sha(build/b) for n,b in mapping.items()},avpack='hdtv',eeprom_source='E:/xwn289/fixture001/hd.bin',physical_access=False,guest_launch=False,limits='Only3161080i launcher differs from unused313 preparation; same helper/303/300/audio004/FATX0101. No physical qualification.')
f['helpers']=dict(parent['helpers'])
if 'payload' in f:f['inherited_payload_description_not_current']=f.pop('payload')
f['current_payload_authority']='files/protected readback hashes, not historical inherited payload description'
save(out/'fixture.json',f);print('Prepared',case,'with one1080i launcher override')
