"""Independent binary/layout/source-closure review; no guest execution."""
import hashlib,importlib.util,json,pathlib,re,struct,subprocess
K=pathlib.Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
spec=importlib.util.spec_from_file_location('oldelf',K.parent/'launcher-relocation293/review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=pathlib.Path('D:/xwn311/build001');dest=K/'binary-review001.json';assert not dest.exists()
b=read(K/'build001.json');assert b['status']=='compiled'
r=dict(passed=False,guest_launched=False,rows={});warnings=[]
try:
 for case in ['control001','candidate001']:
  p=out/case
  for n,v in b['cases'][case]['files'].items():assert sha(p/n)==v['sha256']
  raw,s,y=m.elf(p/'image-crom.elf');assert s['.text']['va']==0x2600000
  end=max(v['va']+v['size'] for v in s.values() if v['flags']&2);assert end==y['BSS_END']['va'] and 0x2800000-end>=262144
  assert (p/'image-crom.bin').stat().st_size<=0x100000
  text=raw[s['.text']['offset']:s['.text']['offset']+s['.text']['size']]
  assert b'\xbc'+struct.pack('<I',0x2800000) in text
  bb,ss,yy=m.elf(p/'xbeboot.elf');assert b'\xbf'+struct.pack('<I',0x2600000)+b'\xb9\x00\x00\x10\x00\xf3\xa4\xfa\xea'+struct.pack('<I',0x2600000)+b'\x08\x00' in bb
  names=['XwnHdTry720','XwnHdState311','xwn_hd_apply','xwn_hd_smb_write','xwn_hd_get_profile']
  if case=='candidate001':assert all(n in y for n in names)
  else:assert all(n not in y for n in names)
  rows=[re.sub(r'/home/paul/xbox-windows-native/build/hd-loader311-build001/[^/]+','SOURCE',a) for a in (out/(case+'.log')).read_text().splitlines() if 'warning:' in a.lower()]
  assert not any('clock skew' in a.lower() for a in rows);warnings.append(rows)
  r['rows'][case]=dict(files=b['cases'][case]['files'],text_sha256=hashlib.sha256(text).hexdigest(),text_size=len(text),bss_end=end,stack_headroom=0x2800000-end,sections=s,symbols={n:y[n] for n in ['BootVgaInitializationKernelNG','BSS_END']+names if n in y},warnings=len(rows))
 old,s,y=m.elf(pathlib.Path('E:/xwn300/build001/candidate001/image-crom.elf'))
 oldtext=old[s['.text']['offset']:s['.text']['offset']+s['.text']['size']]
 assert hashlib.sha256(oldtext).hexdigest()==r['rows']['control001']['text_sha256']
 assert warnings[0]==warnings[1]
 # Export the prepared authored diff and all new sources, never private firmware.
 source='/home/paul/xbox-windows-native/build/hd-loader311-build001/source'
 parent='/home/paul/xbox-windows-native/build/hd-reservation300-build001/cromwell'
 changes=read(K/'source-review001.json');patch=[]
 for n,v in changes['changes'].items():
  cmd=['wsl','-d','Ubuntu','--','git','diff','--no-index','--',parent+'/'+n,source+'/'+n]
  x=subprocess.run(cmd,capture_output=True);assert x.returncode==1
  patch.append(x.stdout.decode().replace(parent+'/', 'a/').replace(source+'/', 'b/'))
 (K/'integration.patch').write_text(''.join(patch))
 for n,h in changes['additions'].items():
  blob=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',source+'/'+n]);assert hashlib.sha256(blob).hexdigest()==h
  target=K/'integrated'/pathlib.Path(n).name;target.parent.mkdir(exist_ok=True);assert not target.exists();target.write_bytes(blob)
 # Undo only declared transformations and compare authored exact logical text.
 q=K/'integrated'
 for n in ['adapter.c','adapter.h']:
  t=(q/('xwn_hd_'+n)).read_text().replace('"xwn_hd_adapter.h"','"adapter.h"').replace('"xwn_hd_profile.h"','"profile.h"')
  if n.endswith('.c'):assert t.startswith('#ifdef XWN_HD_TIMING_720P\n');t=t[len('#ifdef XWN_HD_TIMING_720P\n'):-len('\n#endif\n')]
  assert t==(K/n).read_text()
 for n in ['profile.c','profile.h']:
  t=(q/('xwn_hd_'+n)).read_text().replace('"xwn_hd_profile.h"','"profile.h"')
  if n.endswith('.c'):t=t[len('#ifdef XWN_HD_TIMING_720P\n'):-len('\n#endif\n')];t=t.replace('#include "profile.h"\n','#include "profile.h"\n#include <stddef.h>\n',1)
  assert t==(K.parent/'hd-profile310'/n).read_text()
 assert (q/'xwn_hd_native.c').read_bytes()==(K/'native.c').read_bytes()
 r.update(passed=True,control_text_byte_identical_300=True,matched_warnings=True,source_closure_reconstructed=True,limitations='Static and modeled I/O only. No hardware reset/SMBus/720p runtime proof. No 1080i enablement or release qualification.')
except Exception as e:r['failure']=repr(e);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print({n:r[n] for n in ['passed','control_text_byte_identical_300','matched_warnings','source_closure_reconstructed']})
