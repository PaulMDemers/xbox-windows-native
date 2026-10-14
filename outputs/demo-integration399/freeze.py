import ast,hashlib,json,shutil,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
paths=list(K.glob('*.py'))+[K/'DESIGN.md',K/'QUICKSTART.md',K/'adoption-host001.json']
paths += [W/'docs'/(n+'.md') for n in ['DEMO','DEMO-SETUP','DISPLAY','RECOVERY','BUILD','PUBLIC-RELEASE']]
paths += [W/'tools'/n for n in ['configure-e-display.py','e-display-policy.json']]
T=K.parent/'setup-candidate398'
paths += [T/n for n in ['frozen.json','final-review.json','final-review002.json','corrected-analysis002.py','package.json','REPORT.md']]
paths += [T/'candidate001'/n for n in ['audit.json','collection.json','final-state.json','corrected-analysis002.json']]
paths += [K.parent/'demo-settings376'/n for n in ['package001.json','settings.c']]
paths += [K.parent/'demo-runtime377/control001/audit.json',K.parent/'resolution-e374/cromwell.patch']
paths += [K.parent/'fatx-enumeration390'/n for n in ['0390-vfat-cached-fatx-logical-indices.patch','manifest.json','build-report.json','binary-review.json','final-review.json']]
pkg=read(K.parent/'demo-settings376/package001.json');P=Path(pkg['package_root'])
for n,v in pkg['files'].items():assert sha(P/n)==v['sha256']
assert sha(P/'demo-startup.cmd')==pkg['startup']['sha256']
base=Path('E:/xwn343/bundle002/stock-e-1080i-001.zip')
with base.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='e79771fbf5eaf10c3e30e80e0d04e622dfd443448e24fa4eb76deac01d1b3e83'
assert shutil.disk_usage('C:/').free-base.stat().st_size-256*1024**2>=20*1024**3
# Preflight the reconstructed protected files before producing an archive.
before=read(T/'candidate001/final-state.json')['files'];policy=read(W/'tools/e-display-policy.json')
changes={'/E/Applications/XWNEBoot/default.xbe':Path('E:/xwn374/build001/default.xbe'),
 '/E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd':P/'demo-startup.cmd',
 '/E/winnt/system32/drivers/xwnfatx.sys':Path('E:/xwn390/build001/xwnfatx.sys')}
checked=[]
with zipfile.ZipFile(base) as z:
 for p,v in before.items():
  if not p.startswith('/E/') or '/XWNFBoot/' in p or '/system32/config/' in p:continue
  b=changes[p].read_bytes() if p in changes else z.read('payload'+p)
  expected='41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126' if p.endswith('/xwnfatx.sys') else v['sha256']
  assert hashlib.sha256(b).hexdigest()==expected,p;checked.append(p)
for mode,p in [('720p',Path('E:/xwn374/build001/default.xbe')),('1080i',Path('E:/xwn334/build001/default.xbe'))]:assert sha(p)==policy['profiles'][mode]['sha256']
pins={}
for p in paths:
 if p.suffix=='.py':ast.parse(p.read_bytes())
 pins[p.relative_to(W).as_posix()]=sha(p)
dest=K/'frozen.json';assert not dest.exists();dest.write_text(json.dumps(pins,indent=2)+'\n')
dest=K/'preflight001.json';assert not dest.exists();dest.write_text(json.dumps(dict(frozen_inputs=len(pins),base_verified=True,reconstructed_protected_files_checked=checked,output_on_host_C=True,no_console_writes=True),indent=2)+'\n')
print('Frozen',len(pins),'inputs; verified reconstruction of',len(checked),'protected E files')
