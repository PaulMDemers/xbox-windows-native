"""Fresh Linux-filesystem strict reconstruction after retained DrvFS mode failure."""
import copy,datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
B=Path('/home/paul/xbox-windows-native/launcher677-validation002')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not (K/'validation002.json').exists()
sys.path.insert(0,str(W/'tools'));import xwn
from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,changed_sources=[],builds={})
def save():(K/'validation002.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 first=json.loads((K/'validation001.json').read_text());delta=json.loads((K/'tree-difference001.json').read_text())
 assert first['profile_checks']==129 and first['adapter_checks']==235552 and first['old_profiles_identical'] and first['compiled_480p_facts_match']
 assert delta and all(v['historical'].split()[1:]==v['new'].split()[1:] for v in delta)
 assert all(v['historical'].split()[0]=='100644' and v['new'].split()[0]=='100755' for v in delta)
 r['preserved_first_failure']=first['failure'];r['mode_only_differences']=len(delta)
 r['space']=require_space(B,20.25);B.mkdir()
 m=json.loads((W/'upstream/components.json').read_text());candidate=json.loads((K/'candidate-profile.json').read_text())
 assert not xwn.verify(candidate)
 r['candidate_sha256']=sha(K/'candidate-profile.json')
 r['source_pins']={entry['path']:sha(W/candidate['overlay']/entry['path']) for entry in candidate['files'] if entry['action']=='write'}
 cache=Path('/home/paul/xbox-windows-native/release-readiness403-dependencies002/cromwell');cc=Path('/usr/bin/gcc-12').resolve()
 for name,profile in [('default720',candidate),('explicit480',copy.deepcopy(candidate))]:
  if name=='explicit480':profile['build']['flags']+=' -DXWN_HD_BOOT_MODE=3'
  output=B/name;source,record=xwn.materialize(profile,cache,output)
  assert record['reference_match'] and not record['changed_sources']
  result=xwn.build(profile,source,output,None,cc,m,2)
  r['builds'][name]=result
  for tool,flags,filename in [('nm',['-n'],'symbols.txt'),('objdump',['-d'],'disassembly.txt')]:
   (output/filename).write_bytes(subprocess.check_output([tool,*flags,str(source/'obj/image-crom.elf')],timeout=30))
  save()
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({'passed':r['passed'],'builds':list(r['builds'])}))
