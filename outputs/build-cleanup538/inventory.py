"""Read-only inventory of six obsolete negative-test fixture copies."""
import datetime,importlib.util,json,os,pathlib,shutil,struct,subprocess
K=pathlib.Path(__file__).resolve().parent;W=K.parents[1]
s=importlib.util.spec_from_file_location('meta523',W/'outputs/portable-compression523/common002.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
out=K/'inventory001.json';assert not out.exists()
rows=[];pins={}
for stage in ['bootvideo','mmcomplete','processinit']:
 for variant in ['bad-hal','bad-kernel']:
  p=W/f'work/physical-{stage}-{variant}.qcow2'
  assert p.resolve()==p and p.is_file() and p.stat().st_nlink==1
  for parent in [p,*p.parents]:assert not parent.lstat().st_file_attributes&0x400
  meta=m.metadata(p);kit=W/f'outputs/native-windows-physical-{stage}'
  record=kit/f'fixture-{variant}.json';assert m.js(record)['sha256']==meta['sha256']
  closures=list((W/'work/runs').glob(f'physical-{stage}-{variant}-*/cleanup.json'))
  assert closures
  for c in closures:
   j=m.js(c);assert j['completedUtc'] and not j['retained'];pins[str(c)]=m.sha(c)
  for c in [record,kit/'prepare-fixture.py']:pins[str(c)]=m.sha(c)
  rows.append(dict(path=str(p),metadata=meta,retained_fixture_record=str(record),closure_records=[str(c) for c in closures]))
names={pathlib.Path(r['path']).name for r in rows};scanned=[];dependencies=[];seen=set()
roots=[W,*pathlib.Path('C:/').glob('xwn*'),*pathlib.Path('E:/').glob('xwn*')]
roots += [pathlib.Path('E:/'+n) for n in ['Codex-private-artifacts','Codex-archive','Codex-build']]
def inspect(p):
 p=p.resolve()
 if str(p).lower() in seen:return
 seen.add(str(p).lower())
 with p.open('rb') as f:
  h=f.read(20)
  if h[:4]!=b'QFI\xfb':return
  offset,length=struct.unpack_from('>QI',h,8)
  assert length<=4096
  backing=''
  if length:f.seek(offset);backing=f.read(length).decode('utf-8')
 scanned.append(dict(path=str(p),backing=backing))
 if backing and backing.replace('\\','/').split('/')[-1] in names:dependencies.append(scanned[-1])
for root in roots:
 if not root.exists():continue
 for d,ds,fs in os.walk(root):
  ds[:]=[n for n in ds if n!='.git' and not (pathlib.Path(d)/n).is_junction() and not (pathlib.Path(d)/n).is_symlink()]
  for name in fs:
   if name.endswith(('.qcow2','.qcow')):inspect(pathlib.Path(d)/name)
# Inventory prepared independently inside WSL; inspect through its UNC path.
q=subprocess.run(['wsl','-d','Ubuntu','--','cat','/tmp/xwn538-qcow-paths.txt'],capture_output=True,text=True,timeout=20)
assert q.returncode==0
for line in q.stdout.splitlines():
 if line:inspect(pathlib.Path('//wsl.localhost/Ubuntu'+line))
assert not dependencies,dependencies
active=json.loads((W/'outputs/context-pair536/package001.json').read_bytes())
for p,h in active['pins'].items():assert m.sha(pathlib.Path(p))==h
for row in rows:assert row['path'] not in active['pins']
processes=m.processes()
result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),authorization='User explicitly authorized clearing old builds and resuming.',selected=rows,retained_record_pins=pins,active536_pins_verified=len(active['pins']),qcow_headers=scanned,dependent_active_disks=dependencies,processes=processes,free_c=shutil.disk_usage('C:/').free,free_e=shutil.disk_usage('E:/').free,scope='Only six obsolete generated negative fixtures; no run evidence, good fixture, source, package, media, recovery, or backing volume selected.')
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(selected=len(rows),allocated=sum(r['metadata']['allocated_bytes'] for r in rows),scanned=len(scanned),dependents=dependencies,free_c=result['free_c'])))
