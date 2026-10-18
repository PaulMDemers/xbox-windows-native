"""Independent review of closed records/bytes; no build, launch or console IO."""
import copy,hashlib,json,re,struct
from pathlib import Path
K=Path(__file__).resolve().parent
out=K/'final-review.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={}
def read(p):
 p=Path(p);pins[str(p)]=sha(p);return p.read_bytes()
def js(p):return json.loads(read(p))
def wp(s):
 if s.startswith('/mnt/c/'):return Path('C:/'+s[7:])
 return Path(s)
def actual(number,folder,collection,review):
 root=K.parent/folder;c=js(root/collection);r=js(root/review)
 result={}
 for name in ['report.bin','handoff.bin']:
  row=c['files'][f'/E/Applications/XWNBoot{number}a/{name}'];p=Path(row['path'])
  b=read(p);assert sha(p)==row['sha256'];result[name]=b
 result['parsed']=r['actual_witness'];return result
a=actual(483,'handoff-witness483','physical001-collection.json','actual-witness001.json')
b=actual(487,'blend-precision487','collection-completed002.json','actual-witness002.json')
assert a['parsed']['preparation']==b['parsed']['preparation']
ap=a['report.bin'];bp=b['report.bin'];aw=a['handoff.bin'];bw=b['handoff.bin']
pdiff=[i for i in range(176) if ap[i]!=bp[i]]
wdiff=[i for i in range(256) if aw[i]!=bw[i]]
assert set(pdiff)<=set([3,14,170])
# Witness difference set: identity/cookie plus marker timing and poll count only.
allowed=set([3,14,250])|set(range(100,120))|set(range(148,152))
assert set(wdiff)<=allowed,(wdiff,sorted(allowed))
source483=read('C:/xwn483/build001/xbeboot.S')
source487=read('C:/xwn487/build001/xbeboot.S')
assert source483.replace(b'483',b'487')==source487
assert read('C:/xwn483/build001/witness.S').replace(b'483',b'487')==read('C:/xwn487/build001/witness.S')
build=js(K/'build003.json');runs=js(K/'run003.json')
assert build['passed'] and runs['closed'] and runs['passed'] and len(runs['cases'])==10
for p,v in build['files'].items():assert sha(wp(p))==v['sha256'];read(wp(p))
elf=read('C:/xwn488/lab003/dual_copy.elf');loader=read('C:/xwn488/lab003/loader.bin')
sy=build['symbols'];data=read('C:/xwn487/build001/default.xbe')
assert data[sy['blentry']-65536:sy['blentry']-65536+1024]==loader
assert elf.count(loader)==1
# Decode actual opcode immediates independently; no instruction substitution.
assert loader[:17]==bytes.fromhex('fa0f20c025ffffff7f0f22c031c00f22d8')
assert loader[73:80]==bytes.fromhex('ea000000000800')
assert loader[80:100]==bytes.fromhex('bf00006002b900001000f3a4faea000060020800')
assert struct.unpack_from('<H',loader,218)[0]==0x8000
# Verify original source reconstruction of the two harness-only corrections.
assert read(K/'boot.S').replace(b'flat',b'fixture_flat')==read(K/'boot002.S')
assert read(K/'payload.S').replace(b'    ud2',b'    cli\n1:  hlt\n    jmp 1b')==read(K/'payload003.S')
def qualify(i,c,debug,cpu):
 if not c['closed'] or c['deadline'] or c.get('fallback_kill'):raise ValueError('lifecycle')
 if c['name']!=build['cases'][i]:raise ValueError('case identity')
 faults=re.findall(r'^\s*\d+: v=([0-9a-f]+).*?IP=([0-9a-f]+):([0-9a-f]+)',cpu,re.M)
 if i in (0,1,9):
  if debug!=(b'BEF' if i==9 else b'BEP') or c['exit_code']!=(35 if i==9 else 33) or faults or 'Triple fault' in cpu:raise ValueError('terminal oracle')
 else:
  expected={2:('0e','0008','02000000'),3:('06','0008','0200000c'),4:('06','0008','02000000'),5:('06','0008','00000000'),6:('06','0008','02600000')}
  if debug!=b'B' or c['exit_code']!=0 or 'Triple fault' not in cpu or not faults:raise ValueError('negative fault')
  if i in expected and faults[0]!=expected[i]:raise ValueError('wrong fault boundary')
 return faults[:1]
neg=0;details=[]
for i,c in enumerate(runs['cases']):
 files={Path(p).name:(wp(p),v) for p,v in c['files'].items()}
 for p,v in files.values():assert sha(p)==v['sha256'];read(p)
 debug=read(files['debug.bin'][0]);cpu=read(files['cpu.log'][0]).decode()
 first=qualify(i,c,debug,cpu);details.append(dict(name=c['name'],exit_code=c['exit_code'],debug=debug.decode(),first_fault=first))
 tests=[]
 for field,value in [('closed',False),('deadline',True),('fallback_kill',True),('name','wrong'),('exit_code',99)]:
  t=copy.deepcopy(c);t[field]=value;tests.append((t,debug,cpu))
 for size in range(len(debug)):tests.append((c,debug[:size],cpu))
 tests.extend([(c,debug+b'P',cpu),(c,b'BEP' if i>=2 else b'B',cpu)])
 if i not in (0,1,9):tests.append((c,debug,cpu.replace('Triple fault','fault')))
 else:tests.append((c,debug,cpu+'\nTriple fault\n'))
 for args in tests:
  try:qualify(i,*args)
  except ValueError:neg+=1;continue
  raise AssertionError(('negative accepted',i))
assert all(sha(Path(p))==h for p,h in pins.items())
out.write_text(json.dumps(dict(passed=True,physical_access=False,actual_preparation_equal=True,actual_primary_diff_offsets=pdiff,actual_witness_diff_offsets=wdiff,namespace_normalized_source_exact=True,actual_loader_bytes=1024,loader_sha256=hashlib.sha256(loader).hexdigest(),cpu_fixture_cases=details,negative_controls=neg,inputs=pins,originals_unchanged=True,root_cause_established=False,xbox_boot_qualified=False,scope='actual old record/source comparison plus synthetic PC QEMU privileged execution; no physical CPU/context/interrupt qualification'),indent=2)+'\n')
