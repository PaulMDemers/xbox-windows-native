"""Model bounded progressive-mode transactions and compare compiled profile facts."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn633/host001')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held' and not P.exists()
sys.path.insert(0,str(K.parents[1]/'tools'));from build_space import require_space
space=require_space(P,minimum_gib=20.02);P.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,hardware_io='modeled',space=space)
def save():(K/'host001.json').write_text(json.dumps(r,indent=2)+'\n')
assert not (K/'host001.json').exists();save()
try:
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 for p in K.glob('*.c'):(P/p.name).write_bytes(p.read_bytes())
 for p in K.glob('*.h'):(P/p.name).write_bytes(p.read_bytes())
 r['sources']={p.name:sha(p) for p in P.iterdir()}
 for name,sources in [('profile',['xwn_hd_profile.c','profile-host.c']),('adapter',['xwn_hd_profile.c','xwn_hd_adapter.c','adapter-host.c'])]:
  args=[str(cc),'-DXWN_HD_TIMING_720P=1','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-pie','-no-pie',*[str(P/n) for n in sources],'-o',str(P/name)]
  x=subprocess.run(args,capture_output=True,timeout=40);(P/(name+'-compile.log')).write_bytes(x.stdout+x.stderr);assert x.returncode==0,x.stderr.decode()
  x=subprocess.run([str(P/name)],capture_output=True,timeout=20);(P/(name+'-result.txt')).write_bytes(x.stdout);(P/(name+'-stderr.txt')).write_bytes(x.stderr)
  assert x.returncode==0 and not x.stderr,(x.returncode,x.stderr.decode())
  r[name+'_checks']=int(x.stdout.decode().splitlines()[-1].split()[1]);r[name+'_binary_sha256']=sha(P/name)
 actual={}
 for line in (P/'profile-result.txt').read_text().splitlines():
  a=line.split()
  if a[0]=='PROFILE':actual[int(a[1])]=dict(geometry=list(map(int,a[2:])),CR={},MM={},EN={})
  elif a[0] in ('CR','MM','EN'):actual[int(a[1])][a[0]][int(a[2],16)]=int(a[3],16)
 old=json.loads((K.parent/'hd-profile310/profile-facts.json').read_text())
 for mode,p in enumerate(old['profiles'],1):
  assert actual[mode]['geometry']==[p[n] for n in ('width','height','stride','visible_bytes','interlaced')]
  for group,index,key in [('CR','crtc_indices','crtc'),('MM','mmio_offsets','mmio'),('EN','encoder_indices','encoder')]:assert actual[mode][group]==dict(zip(old[index],p[key]))
 facts=json.loads((K/'profile-facts.json').read_text());assert actual[3]['geometry']==[720,480,2880,1382400,0]
 for group in ('CR','MM','EN'):assert actual[3][group]=={int(n):v for n,v in facts['groups'][group].items()}
 r.update(passed=True,existing_profiles_identical=True,compiled480p_matches_physical632_programming_facts=True,physical_windows_boot=False,scope='ASan/UBSan pure profile and modeled transaction tests; no hardware timing/interrupt proof')
except BaseException as e:r['failure']=repr(e);raise
finally:save()
print(json.dumps({n:r[n] for n in ('passed','profile_checks','adapter_checks')}))
