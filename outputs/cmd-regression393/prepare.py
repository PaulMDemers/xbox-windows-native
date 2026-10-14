"""Fresh unused391 source with additional CMD workload; no executed runtime parent."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];case=sys.argv[1]
assert case=='candidate001' and os.environ.get('XWN_BUILD_LEASE')=='held'
old=K.parent/'file-enumeration391'/case;out=K/case;P=Path('/mnt/c/xwn393')/case
assert not out.exists() and not P.exists()
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
from stock_io002 import readers,scan
f=json.loads((old/'fixture.json').read_text());source=Path(f['fixture_path_linux']);assert sha(source)==f['fixture_sha256']
assert json.loads((old/'closure.json').read_text())['guest_started'] is False
assert not Path('/mnt/c/xwn391/runs/nt5-enumeration391-candidate001/instance.json').exists()
reserve=10000000000+source.stat().st_size+512*1024**2
assert shutil.disk_usage('/mnt/c').free-reserve>=20*1024**3
out.mkdir();(out/'artifacts').mkdir();P.mkdir(parents=True);raw=P/'staging.raw';target=P/'source.qcow2'
r=dict(prepared=False,physical_access=False,parent=str(source),parent_sha256=sha(source),registry_edited=False,changes=[],source_is_never_executed_preparation=True)
def save():(out/'preparation.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('r+b') as fp:
  wr=m.Writer(fp,m.fatx.open_partition(fp,raw,'E'));assert 'xwncmd393' not in wr.directory(1)['entries']
  for name,data in [('commands.cmd',(K/'commands.cmd').read_bytes()),('input.bmp',wr.read(f['namespace']+'/input.bmp'))]:r['changes'].append(wr.write('xwncmd393/'+name,data))
  before=wr.read(STARTUP);assert before==(K.parent/'file-enumeration391/startup.cmd').read_bytes()
  after=(K/'startup.cmd').read_bytes();m.replace(wr,STARTUP,after);wr.flush();fp.flush()
  r['changes'].append(dict(path=STARTUP,sha256=m.sha(after),before_sha256=m.sha(before)))
  assert m.sha(wr.read('winnt/system32/drivers/xwnfatx.sys'))=='41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126'
  assert m.sha(wr.read('winnt/system32/cmd.exe'))=='4b04da85216ddbd98fa194d71f3c3acf311ac69fbe93444d9bc4c5464177762e'
  for n in ['system','software','default','sam','security']:(out/'artifacts'/('before-'+n)).write_bytes(wr.read('winnt/system32/config/'+n))
 subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
 subprocess.run(['qemu-img','compare','-f','raw','-F','qcow2',str(raw),str(target)],check=True);subprocess.run(['qemu-img','check',str(target)],check=True)
 assert sha(source)==r['parent_sha256']
 with ColdIO(source) as a,ColdIO(target) as b:
  aa,bb=readers(a,source)['E'],readers(b,target)['E']
  for n in ['system','software','default','sam','security']:assert aa.read('winnt/system32/config/'+n)==bb.read('winnt/system32/config/'+n)
  for v in r['changes']:assert m.sha(bb.read(v['path']))==v['sha256']
 f.update(fixture_path_linux=str(target),fixture_path_windows='C:/xwn393/candidate001/source.qcow2',fixture_sha256=sha(target),parent=str(source),parent_sha256=r['parent_sha256'])
 for field in ['files','protected']:
  f[field]=dict(f[field])
  for v in r['changes']:
   keys=[n for n in f[field] if n.lower()==('E/'+v['path']).lower()]
   for n in keys:f[field][n]=v['sha256']
   if not keys:f[field]['E/'+v['path']]=v['sha256']
 (out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n');scan(target,out/'before-allocation/artifacts')
 assert json.loads((out/'before-allocation/allocation.json').read_text())['allocation_consistent']
 assert raw.resolve().parent==P.resolve() and raw.name=='staging.raw';raw.unlink()
 r.update(prepared=True,source_sha256=sha(target),raw_staging_removed_after_virtual_equality=True,hives_unchanged=True);save()
except BaseException as e:r['error']=repr(e);save();raise
print('393 prepared with unchanged candidate390 and additional exact CMD regression')
