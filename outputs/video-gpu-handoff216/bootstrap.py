"""Freeze reviewed214 adapters into a NEW216 read-only diagnostic kit once.
No compilation, guest launch, physical IO or source-cache mutation.
"""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-gpu-state214'
dest=k/'adapter-provenance.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['common.py','boundary_analysis.py','upload_analysis.py','runner_analysis.py','sample_analysis.py',
 'dib_analysis.py','timing_analysis.py','window_analysis.py','text_analysis.py','interval_policy.py','typed-state.py',
 'prepare-emulator.py','audit-emulator.py','supervise-emulator.py','run-emulator.py','compare-pair.py',
 'build001.py','review-build.py','review-native-inputs.py','Build001.ps1','Prepare.ps1','Run.ps1',
 'Invoke-214.ps1','gpu_snapshot.c','inventory-model.py','host-test002.c','test-host002.py','test-parser002.py',
 'snapshot_trace.py','host-shim/ntddk.h']
pins={}
for name in names:
 p=old/name;target=name.replace('Invoke-214','Invoke-216').replace('host-test002.c','host-test.c').replace('test-host002.py','test-host.py').replace('test-parser002.py','test-parser.py')
 q=k/target;assert not q.exists();q.parent.mkdir(parents=True,exist_ok=True)
 t=p.read_text(encoding='utf-8').replace('video-gpu-state214','video-gpu-handoff216').replace('gstate214','gstate216').replace('xwng214','xwng216').replace('Invoke-214','Invoke-216')
 # Unique trace namespace; every inherited214 case remains untouched.
 for n in ['21400','21401','21402','21403']:t=t.replace(n,str(int(n)+200))
 t=t.replace('Fresh214','Fresh216').replace('native214','native216').replace('new214','new216').replace('fresh214','fresh216').replace('narrow214','narrow216')
 if name=='inventory-model.py':
  t=t.replace("'pcrtc.c','pgraph/pgraph.c'","'pcrtc.c','pfb.c','pgraph/pgraph.c'")
  t=t.replace("(0x400000,'PGRAPH',['INTR','INTR_EN','CTX_USER','FIFO'])","(0x100000,'PFB',['CFG0','CSTATUS']),\n (0x400000,'PGRAPH',['INTR','INTR_EN','CTX_USER','FIFO','DEBUG_3','CTX_CONTROL'])")
  t=t.replace('len(rows)==22','len(rows)==26').replace('XGN_REGISTER_COUNT 22u','XGN_REGISTER_COUNT 26u')
 if name=='host-test002.c':
  t=t.replace('allowed[22]','allowed[26]').replace('0x600100,0x600140,0x600800','0x100200,0x10020c,0x40008c,0x400144,0x600100,0x600140,0x600800')
  # Mirror the approved register order, independently of generated header.
  t=t.replace('0x400100,0x400140,0x400148,0x400720,\n 0x100200,0x10020c,0x40008c,0x400144,','0x100200,0x10020c,0x400100,0x400140,0x400148,0x400720,0x40008c,0x400144,\n ')
  for a,b in [('i<22','i<26'),('?44u','?52u'),('?48u','?56u'),('?24u','?28u'),('?22u','?26u'),('at+23','at+27'),('==22','==26')]:t=t.replace(a,b)
 if name=='snapshot_trace.py':
  t=t.replace('0x3250,0x400100','0x3250,0x100200,0x10020c,0x400100').replace('0x400720,0x600100','0x400720,0x40008c,0x400144,0x600100')
  for a,b in [('21400<=','21600<='),('<21500','<21700'),('len(rows)!=48','len(rows)!=56'),('phase*24:(phase+1)*24','phase*28:(phase+1)*28'),('part[1:23]','part[1:27]'),('part[23]','part[27]'),('phase,22,checksum','phase,26,checksum'),('actual_new_reads=44','actual_new_reads=52')]:t=t.replace(a,b)
 if name=='test-parser002.py':t=t.replace('phase,22,sum','phase,26,sum')
 if name in ['test-host002.py','build001.py','review-build.py','review-native-inputs.py']:
  t=t.replace('host-tests002.json','host-tests001.json').replace('host-test002.c','host-test.c').replace('artifacts/host002','artifacts/host001')
 if name=='test-host002.py':t=t.replace("k/'artifacts/host002'","k/'artifacts/host001'")
 q.write_text(t,encoding='utf-8');pins[target]=dict(parent_path=str(p.relative_to(k.parents[1])).replace('\\','/'),parent_sha256=sha(p),derived_sha256=sha(q))
dest.write_text(json.dumps(dict(passed=True,source_sha256=sha(Path(__file__)),files=pins,
 limits='One-time exact parent/derived adapter provenance. New216 source reviewed separately before any launch; closed214 cases not rerun.'),indent=2)+'\n',encoding='utf-8')
