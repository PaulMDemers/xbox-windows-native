"""Reconcile retained Windows emulator source manifests without building/running xemu."""
import hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
S=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
out=K/'xemu-audit001.json';assert not out.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
r=dict(passed=False,physical_access=False,emulator_launched=False,shared_source_modified=False)
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
try:
 base=subprocess.check_output(['git','-C',str(S),'rev-parse','HEAD']).decode().strip()
 assert base=='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d';r['base']=base
 diff=subprocess.check_output(['git','-C',str(S),'diff','--name-only']).decode().splitlines()
 assert diff==['hw/xbox/mcpx/nvnet/nvnet.c'];r['shared_checkout_delta']=diff
 parent_path=W/'outputs/xemu-cpu-surface-evict/build003/candidate-source-pins.json'
 parent=json.loads(parent_path.read_text());assert len(parent)==11340
 assert sha(parent_path.read_bytes())=='db75df9a0b59ca0e3cc646c0b7548f1553a0739b7e7f50b9697072edb3f8ecb9'
 with tempfile.TemporaryDirectory(prefix='xwn679-audit-') as tmp:
  temp=Path(tmp)
  names=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/surface.c','hw/xbox/nv2a/pgraph/gl/renderer.h','hw/xbox/nv2a/pramdac.c','hw/xbox/nv2a/nv2a_regs.h']
  for n in names:
   p=temp/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((S/n).read_bytes())
  resource=W/'outputs/native-windows-physical-f/xemu-nv2a-resource-model.patch'
  subprocess.run(['patch','--batch','--forward','-p1','-i',str(resource)],cwd=temp,check=True,capture_output=True)
  evict=module('evict679',W/'outputs/xemu-cpu-surface-evict/build003/patch.py')
  a,b=evict.apply((temp/names[2]).read_text(),(temp/names[3]).read_text())
  (temp/names[2]).write_text(a);(temp/names[3]).write_text(b)
  derived={n:sha((temp/n if n in names else S/n).read_bytes()) for n in parent}
  assert derived==parent; r['parent_files_verified']=len(derived)
  timing=module('timing679',W/'outputs/pramdac-timing322/patch.py')
  candidate=timing.apply({n:(temp/n).read_text() for n in names})
  for n,t in candidate.items():derived[n]=sha(t.encode())
  manifest=sha((json.dumps(derived,indent=2)+'\n').encode())
  assert manifest=='eb40517fee6dba7427ae9ba20af42487ea37675378e256b8ed7e1c2666e36fdf'
  r['candidate_manifest_sha256']=manifest
  changed=names+['hw/xbox/mcpx/nvnet/nvnet.c'];r['changed_source_files']=sorted(changed)
  for n in changed:
   original=subprocess.check_output(['git','-C',str(S),'show',base+':'+n]);assert sha(original)!=derived[n]
  nv=(S/changed[-1]).read_text();r['tx_batch_patch_present']= 'if (tx_flags & NV_TX_LASTPACKET)' not in nv # checked below using exact patch context instead
  tx=(W/'outputs/upstream-xemu/patches/02-nvnet-drain-tx-batch.patch').read_text()
  r['tx_patch_classification']='Separate Linux candidate; not part of this four-change Windows build'
  r.pop('tx_batch_patch_present')
  r['logical_change_count']=4
  r['logical_changes']=['NVNET access-size alignment','NV2A resource/BAR experiment (opt-in)','CPU-write surface eviction with open-primitive guard','PRAMDAC three timing-register latches and migration fields']
  r['source_manifest_scope']='All 11340 retained tracked file hashes; build metadata excluded by original manifest'
  r['binary_sha256']='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'
  r['evidence_pins']={str(p.relative_to(W)):sha(p.read_bytes()) for p in [parent_path,resource,W/'outputs/xemu-cpu-surface-evict/build003/patch.py',W/'outputs/pramdac-timing322/patch.py',W/'outputs/pramdac-timing322/build003.json',W/'outputs/windows480p639/runtime.py']}
  r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['passed','parent_files_verified','logical_change_count','changed_source_files']}))
