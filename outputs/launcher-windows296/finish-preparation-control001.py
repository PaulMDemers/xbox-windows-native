"""Change only launcher in a new child of the never-executed combined251 preparation."""
import json,pathlib,subprocess,sys,shutil
K=pathlib.Path(__file__).resolve().parent;ws=K.parents[1];case=sys.argv[1];assert case in ('control001','candidate001')
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,readers,sha,save,hive,scan,m,HIVES
sys.path.insert(0,str(K.parent/'setup-wizard-automation201'));from restore import restore
parent=json.loads((K.parent/'demo-integration251/emu001/fixture.json').read_text());base=pathlib.Path(parent['fixture_path_linux']);assert sha(base)==parent['fixture_sha256']
assert case=='control001'
out=K/case;art=out/'artifacts';assert out.exists() and not (out/'fixture.json').exists()
private=pathlib.Path('/mnt/e/xwn296/fixtures')/case;source=private/'source.qcow2';mode='control004'
review=json.loads((K.parent/'launcher-relocation293/binary-review004.json').read_text());assert review['passed']
launcher=pathlib.Path('/mnt/e/xwn293')/mode/'default.xbe';assert sha(launcher)==review['rows'][mode]['xbe_sha256']
files=dict(parent['files']);protected=dict(parent['protected']);name='E/Applications/XWNFBoot/default.xbe';files[name]=sha(launcher);protected[name]=sha(launcher)
with ColdIO(source) as io:
 rr=readers(io,source)
 for n,h in files.items():v,p=n.split('/',1);assert m.sha(rr[v].read(p))==h,n
 for n in HIVES:
  p=art/('before-'+n);data=rr['F'].read('winnt/system32/config/'+n)
  if p.exists():assert p.read_bytes()==data
  else:p.write_bytes(data)
  hive(p)
scan(source,out/'before/artifacts');a=json.loads((out/'before/allocation.json').read_text());assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==parent['fixture_sha256']
f=dict(parent);f.update(parent=str(base),parent_sha256=parent['fixture_sha256'],fixture_path_linux=str(source),fixture_path_windows='E:'+str(source)[6:],fixture_sha256=sha(source),files=files,protected=protected,case=case,launcher_sha256=sha(launcher),launcher_source=str(launcher),physical_access=False,guest_launch=False,limits='Only launcher replaced in unused combined251 preparation; unchanged audio004/video118/shared158, 4MiB/composite fixture, no HD qualification')
save(out/'fixture.json',f);print('Prepared',case,'with only launcher replacement')
