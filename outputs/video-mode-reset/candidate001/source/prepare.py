"""Fresh shared-UC children; select a project-owned display DLL only in candidate."""
import subprocess,sys
from common import *
from allocation import scan
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
case=sys.argv[1];assert case in ['candidate001'];out=k/case
out.mkdir(exist_ok=True);assert not (out/'before').exists()
parent=k.parent/'video-shared-framebuffer';f=read(parent/'fixture-candidate001.json')
assert read(parent/'pair-review.json')['passed']
source=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert sha(source)==f['fixture_sha256']
target=source.parent/('video-mode-reset-'+case+'.qcow2');seed=ws/('work/video-mode-reset-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
review=read(k/'pe-review.json');assert review['passed'] and sha(k/'build-report.json')==review['build_sha256']
assert sha(k/'probe.c')==review['probe_source_sha256'] and sha(k/'artifacts/probe.exe')==review['probe_sha256']
driver=k/'candidate001/artifacts/xwnown.dll';assert sha(driver)==review['display_sha256']
control=k.parent/'video-ram-primary/candidate001/artifacts/xwnram.dll';assert sha(control)=='51d98cf9ee2d2f42c360d96152877491b32773471ef8a0680d40264b49f6efc5'
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
with ColdIO(source) as io:
 rr=readers(io,source)
 for dll,digest in next(v for v in review['files'] if v['name']=='probe.exe')['targets'].items():
  assert m.sha(rr['F'].read('winnt/system32/'+dll))==digest,('Guest API dependency differs',dll)
 for row in f['protected']:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 protected=[dict(volume=v,path=p,sha256=m.sha(rr[v].read(p))) for v,p in PROTECTED+[('F','winnt/system32/framebuf.dll'),('F','winnt/system32/hidserv.exe')]]
 hives=[dict(path='winnt/system32/config/'+n,sha256=m.sha(rr['F'].read('winnt/system32/config/'+n))) for n in HIVES]
 original_system=rr['F'].read('winnt/system32/config/system')
 for path in ['xwnmode124/ref%02d.rgb'%i for i in range(26)]+['winnt/system32/xwnown.dll','winnt/system32/xwnram.dll','xwnmode124/result.log','xwnmode124/probe.exe','xwnmode124/expected.bin']:
  try:rr['F'].read(path)
  except KeyError:pass
  else:raise AssertionError('New output/input path already exists: '+path)
art=out/'artifacts';art.mkdir(exist_ok=True)
system=art/'prepared-system';system.write_bytes(original_system)
h=hivex.Hivex(str(system),write=True)
def node(path):
 n=h.root()
 for part in path.split('\\'):
  n=h.node_get_child(n,part)
  if not n:return 0
 return n
def val(n,key):return h.value_value(h.node_get_value(n,key))
def flatten():
 result={};todo=[('',h.root())]
 while todo:
  path,n=todo.pop();result[(path,'<node>')]=None
  for v in h.node_values(n):
   t,b=h.value_value(v);result[(path,h.value_key(v))]=(t,b.hex())
  todo.extend((path+'\\'+h.node_name(c),c) for c in h.node_children(n))
 return result
before=flatten();cs='ControlSet%03d'%int.from_bytes(val(node('Select'),'Current')[1],'little')
pci=node(cs+r'\Enum\PCI');gpu=[]
for dev in h.node_children(pci):
 if h.node_name(dev).startswith('VEN_10DE&DEV_02A0&'):
  gpu.extend(h.node_children(dev))
assert len(gpu)==1
driver_key=val(gpu[0],'Driver')[1].decode('utf-16le').rstrip('\0')
paths=[cs+'\\Control\\Class\\'+driver_key+r'\Settings',cs+r'\Services\xboxvnt5\Device0']
edits=[]
for path in paths:
 n=node(path)
 if not n:continue
 v=next((v for v in h.node_values(n) if h.value_key(v)=='InstalledDisplayDrivers'),0)
 if not v:continue
 t,b=h.value_value(v);assert t in [1,7] and b.decode('utf-16le').rstrip('\0')=='framebuf'
 after=('xwnown' if case=='candidate001' else 'xwnram').encode('utf-16le')+b'\0\0'*(2 if t==7 else 1)
 h.node_set_value(n,dict(key='InstalledDisplayDrivers',t=t,value=after))
 edits.append(dict(path=path,type=t,before=b.hex(),after=after.hex()))
assert len(edits)==2
h.commit(None)
del h
h=hivex.Hivex(str(system));after=flatten();changed=[key for key in set(before)|set(after) if before.get(key)!=after.get(key)]
expected=[('\\'+r['path'],'InstalledDisplayDrivers') for r in edits]
assert sorted((p.casefold(),n.casefold()) for p,n in changed)==sorted((p.casefold(),n.casefold()) for p,n in expected),(changed,expected)
del h
system_bytes=system.read_bytes()
assert system_bytes!=original_system
save(out/'registry-selection.json',dict(case=case,physical_access=False,control_set=cs,driver_key=driver_key,
 original_sha256=m.sha(original_system),prepared_sha256=m.sha(system_bytes),edits=edits,
 changed_values=[list(v) for v in changed],all_other_logical_nodes_values_unchanged=True,
 note='Each child changes exactly the same two selectors to its authored display. No INF wizard, signing/protection/device policy/service changes. Microsoft framebuf bytes preserved.'))
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
startup=b'@echo off\r\nC:\\xwnmode124\\probe.exe\r\nexit\r\n';m.replace(w,STARTUP,startup)
payloads=[w.write('xwnmode124/probe.exe',(k/'artifacts/probe.exe').read_bytes()),
 w.write('xwnmode124/expected.bin',bytes([int(case=='candidate001')])),
 w.write('winnt/system32/xwnram.dll',control.read_bytes()),
 w.write('winnt/system32/xwnown.dll',driver.read_bytes())]
trace=b'XWN-VID-TRACE01\n'+bytes(4080);m.replace(w,'winnt/system32/xwn-video-trace.bin',trace)
m.replace(w,'winnt/system32/config/system',system_bytes)
w.flush()
for row in hives:
 if row['path']=='winnt/system32/config/system':row['sha256']=m.sha(system_bytes)
with ColdIO(target) as io:
 rr=readers(io,target)
 assert rr['F'].read(STARTUP)==startup and rr['F'].read('winnt/system32/xwn-video-trace.bin')==trace
 for row in protected:assert m.sha(rr[row['volume']].read(row['path']))==row['sha256']
 for row in hives+payloads:assert m.sha(rr['F'].read(row['path']))==row['sha256']
scan(target,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
save(k/('fixture-'+case+'.json'),dict(case=case,physical_access=False,debugger=False,parents=parents,
 fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),protected=protected,preserved_hives=hives,payloads=payloads,
 startup_sha256=m.sha(startup),initial_trace_sha256=m.sha(trace),readback_verified=True,result_absent=True,
 pe_review_sha256=sha(k/'pe-review.json'),registry_selection_sha256=sha(out/'registry-selection.json'),
 parent_manifest='video-shared-framebuffer/fixture-candidate001.json',parent_manifest_sha256=sha(parent/'fixture-candidate001.json'),
 inherited_configuration='SharedUC0106 miniport/bootvid; FATX0103/HAL0102/NVNet0104/ATAPI0105/HidServ fixed. Existing synthetic QEMU null and01B0/01B4 FAILEDINSTALL retained. Microsoft framebuf unchanged; Both xwnram and xwnown payloads present in both. RAM0108 control, ownership0109 candidate. No cache/mode/physical change.'))
print('Prepared unique '+case+'; not launched')
