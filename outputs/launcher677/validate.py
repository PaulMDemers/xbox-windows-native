"""Review the four source-pin changes against retained 633 evidence, then build.
Fresh source trees and host tests only; never launches or stages a console.
"""
import copy, datetime, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; B=Path('/mnt/c/xwn677')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not (K/'validation001.json').exists()
sys.path.insert(0,str(W/'tools'));import xwn
from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,source_changed=False,manifest_promoted=False,commands=[])
def save():(K/'validation001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 r['space']=require_space(B,20.25); B.mkdir(); (B/'tmp').mkdir()
 m=json.loads((W/'upstream/components.json').read_text());old=next(p for p in m['profiles'] if p['name']=='launcher')
 prior=json.loads((W/'outputs/native480p633/build001.json').read_text())
 assert prior['status']=='compiled' and old['reference_tree']==prior['parent_tree']
 r['historical_record_sha256']=sha(W/'outputs/native480p633/build001.json')
 try:xwn.verify(old)
 except ValueError as e:r['original_verification_failure']=str(e)
 else:raise AssertionError('Expected the retained four-pin mismatch')
 candidate=copy.deepcopy(old);candidate['reference_tree']=prior['tree'];changes=[]
 for entry in candidate['files']:
  p=W/candidate['overlay']/entry['path']
  if entry['action']=='write' and sha(p)!=entry['sha256']:
   hist=prior['changes'][entry['path']]
   assert entry['sha256']==hist['before'] and sha(p)==hist['after']
   assert p.read_bytes()==(W/'outputs/native480p633'/p.name).read_bytes()
   changes.append(dict(path=entry['path'],before=entry['sha256'],after=hist['after']))
   entry['sha256']=hist['after']
 assert len(changes)==4 and not xwn.verify(candidate)
 r['changes']=changes;r['old_tree']=old['reference_tree'];r['candidate_tree']=candidate['reference_tree']
 (K/'candidate-profile.json').write_text(json.dumps(candidate,indent=2)+'\n')
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)==old['build']['compiler_sha256']
 r['compiler_sha256']=sha(cc)
 def run(name,args,timeout=120,cwd=None):
  r['commands'].append([str(a) for a in args]);save()
  v=subprocess.run(args,capture_output=True,timeout=timeout,cwd=cwd)
  (B/(name+'.stdout')).write_bytes(v.stdout);(B/(name+'.stderr')).write_bytes(v.stderr)
  assert v.returncode==0,(name,v.returncode,v.stderr[-1500:]);return v.stdout
 # Fresh host fixtures use the exact current maintained files, not a closed run.
 H=B/'host001';H.mkdir()
 for name in ['xwn_hd_profile.c','xwn_hd_profile.h','xwn_hd_adapter.c','xwn_hd_adapter.h']:
  shutil.copyfile(W/old['overlay']/'drivers/video'/name,H/name)
 for name in ['profile-host.c','adapter-host.c']:
  shutil.copyfile(W/'outputs/native480p633'/name,H/name)
 r['host_source_pins']={p.name:sha(p) for p in H.iterdir()}
 for name,files in [('profile',['xwn_hd_profile.c','profile-host.c']),('adapter',['xwn_hd_profile.c','xwn_hd_adapter.c','adapter-host.c'])]:
  run(name+'-compile',[str(cc),'-DXWN_HD_TIMING_720P=1','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-pie','-no-pie',*[str(H/f) for f in files],'-o',str(H/name)])
  output=run(name+'-test',[str(H/name)])
  assert not (B/(name+'-test.stderr')).read_bytes()
  r[name+'_checks']=int(output.decode().splitlines()[-1].split()[1])
 assert r['profile_checks']==129 and r['adapter_checks']==235552
 actual={}
 for line in (B/'profile-test.stdout').read_text().splitlines():
  a=line.split()
  if a[0]=='PROFILE':actual[int(a[1])]=dict(geometry=list(map(int,a[2:])),CR={},MM={},EN={})
  elif a[0] in ('CR','MM','EN'):actual[int(a[1])][a[0]][int(a[2],16)]=int(a[3],16)
 facts=json.loads((W/'outputs/hd-profile310/profile-facts.json').read_text())
 for mode,p in enumerate(facts['profiles'],1):
  assert actual[mode]['geometry']==[p[n] for n in ('width','height','stride','visible_bytes','interlaced')]
  for group,index,key in [('CR','crtc_indices','crtc'),('MM','mmio_offsets','mmio'),('EN','encoder_indices','encoder')]:assert actual[mode][group]==dict(zip(facts[index],p[key]))
 facts=json.loads((W/'outputs/native480p633/profile-facts.json').read_text())
 for group in ('CR','MM','EN'):assert actual[3][group]=={int(k):v for k,v in facts['groups'][group].items()}
 r['old_profiles_identical']=True;r['compiled_480p_facts_match']=True
 cache=Path('/home/paul/xbox-windows-native/release-readiness403-dependencies002/cromwell')
 # Independent full reconstruction must match the existing 633 tree, with no waiver.
 r['builds']={}
 for name,profile in [('default720',candidate),('explicit480',copy.deepcopy(candidate))]:
  if name=='explicit480':profile['build']['flags']+=' -DXWN_HD_BOOT_MODE=3'
  output=B/name
  source,record=xwn.materialize(profile,cache,output)
  assert record['reference_match'] and not record['changed_sources']
  result=xwn.build(profile,source,output,None,cc,m,2)
  r['builds'][name]=result
  run(name+'-symbols',['nm','-n',str(source/'obj/image-crom.elf')])
  run(name+'-disassembly',['objdump','-d',str(source/'obj/image-crom.elf')])
  save()
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({'passed':r['passed'],'profile_checks':r.get('profile_checks'),'adapter_checks':r.get('adapter_checks'),'builds':list(r.get('builds',{}))}))
