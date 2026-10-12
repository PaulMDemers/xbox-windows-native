"""Independent binary bounds, exact parent reconstruction and physical field facts."""
import hashlib,importlib.util,json,pathlib,re,struct,subprocess
K=pathlib.Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
spec=importlib.util.spec_from_file_location('elf',K.parent/'launcher-relocation293/review.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=pathlib.Path('D:/xwn316/build001');dest=K/'binary-review002.json';assert not dest.exists()
b=read(K/'build001.json');assert b['status']=='compiled';r=dict(passed=False,guest_launched=False,physical_access=False,rows={});warnings=[]
try:
 for case in ['control001','candidate001']:
  p=out/case
  for n,v in b['cases'][case]['files'].items():assert sha(p/n)==v['sha256']
  raw,s,y=m.elf(p/'image-crom.elf');assert s['.text']['va']==0x2600000
  end=max(v['va']+v['size'] for v in s.values() if v['flags']&2);assert end==y['BSS_END']['va'] and 0x2800000-end>=262144
  assert (p/'image-crom.bin').stat().st_size<=0x100000
  text=raw[s['.text']['offset']:s['.text']['offset']+s['.text']['size']];assert b'\xbc'+struct.pack('<I',0x2800000) in text
  bb,ss,yy=m.elf(p/'xbeboot.elf');assert b'\xbf'+struct.pack('<I',0x2600000)+b'\xb9\x00\x00\x10\x00\xf3\xa4\xfa\xea'+struct.pack('<I',0x2600000)+b'\x08\x00' in bb
  names=['XwnHdTry720','XwnHdState311'] if case=='control001' else ['XwnHdTry1080','XwnHdState316']
  assert all(n in y for n in names+['xwn_hd_apply','xwn_hd_smb_write','xwn_hd_get_profile'])
  rows=[re.sub(r'/home/paul/xbox-windows-native/build/hd-interlace316-build001/[^/]+','SOURCE',a) for a in (out/(case+'.log')).read_text().splitlines() if 'warning:' in a.lower()]
  assert not any('clock skew' in a.lower() for a in rows);warnings.append(rows)
  r['rows'][case]=dict(files=b['cases'][case]['files'],text_sha256=hashlib.sha256(text).hexdigest(),text_size=len(text),bss_end=end,stack_headroom=0x2800000-end,symbols={n:y[n] for n in names+['BootVgaInitializationKernelNG','xwn_hd_apply','BSS_END']},warnings=len(rows))
 old,s,y=m.elf(pathlib.Path('D:/xwn311/build001/candidate001/image-crom.elf'));oldtext=old[s['.text']['offset']:s['.text']['offset']+s['.text']['size']]
 assert hashlib.sha256(oldtext).hexdigest()==r['rows']['control001']['text_sha256'];assert warnings[0]==warnings[1]
 source='/home/paul/xbox-windows-native/build/hd-interlace316-build001/source';parent='/home/paul/xbox-windows-native/build/hd-loader311-build001/source'
 def cat(p):return subprocess.check_output(['wsl','-d','Ubuntu','--','cat',p])
 changed=b['source_changes'];patch=[];q=K/'integrated002';q.mkdir()
 for n,pin in changed.items():
  original=cat(parent+'/'+n);actual=cat(source+'/'+n);assert hashlib.sha256(original).hexdigest()==pin['before'] and hashlib.sha256(actual).hexdigest()==pin['after']
  (q/pathlib.Path(n).name).write_bytes(actual)
  x=subprocess.run(['wsl','-d','Ubuntu','--','git','diff','--no-index','--',parent+'/'+n,source+'/'+n],capture_output=True);assert x.returncode==1
  patch.append(x.stdout.decode().replace(parent+'/','a/').replace(source+'/','b/'))
 # Every other tracked parent byte remains identical, not just selected functions.
 script="from pathlib import Path;import subprocess,json; p=Path("+repr(parent)+");s=Path("+repr(source)+");c=set("+repr(list(changed))+");names=subprocess.check_output(['git','-C',str(p),'ls-files'],text=True).splitlines();assert all((p/n).read_bytes()==(s/n).read_bytes() for n in names if n not in c);print(len(names))"
 r['parent_files_checked']=int(subprocess.check_output(['wsl','-d','Ubuntu','--','python3','-c',script]))
 (K/'integration002.patch').write_bytes(''.join(patch).encode())
 for n in ['adapter.c','adapter.h','native.c']:
  t=(q/('xwn_hd_'+n)).read_text().replace('"xwn_hd_adapter.h"','"adapter.h"').replace('"xwn_hd_profile.h"','"profile.h"')
  if n=='adapter.c':t=t[len('#ifdef XWN_HD_TIMING_1080I\n'):-len('\n#endif\n')]
  assert ((q/('xwn_hd_'+n)).read_bytes()==(K/n).read_bytes()) if n=='native.c' else t==(K/n).read_text()
 assert (q/'xwn_hd_profile.c').read_bytes().replace(b'XWN_HD_TIMING_1080I',b'XWN_HD_TIMING_720P')==cat(parent+'/drivers/video/xwn_hd_profile.c')
 assert (q/'BootVgaInitialization.c').read_bytes().replace(b'XWN_HD_TIMING_1080I',b'XWN_HD_TIMING_720P').replace(b'XwnHdTry1080',b'XwnHdTry720')==cat(parent+'/drivers/video/BootVgaInitialization.c')
 # Exact known capability definition and independent hardware fields, not new guesses.
 hdr=pathlib.Path('C:/nxdk/lib/hal/video.h');assert re.search(r'#define\s+VIDEO_MODE_1080I\s+0x40000',hdr.read_text())
 facts=read(K.parent/'hd-matrix309/physical001/trial.json')['independent_log_review'];fields=[]
 for i in [0,1]:
  tm=facts['timings'][i];fp=facts['pixels']['rows'][i]['fp'];assert tm['crtc']['0x39']==[255,16][i] and tm['crtc']['0x2d']&1==i
  assert [fp[j] for j in [1,2,3,4,9]]==[[749,719,724,729,1649],[1124,1083,1083,1093,2199]][i]
  fields.append(dict(mode=i+1,interlace=tm['crtc']['0x39'],overflow_bit=tm['crtc']['0x2d']&1,totals=[fp[j] for j in [1,2,3,4,9]]))
 r.update(passed=True,control_text_byte_identical_311=True,matched_warnings=True,source_closure_reconstructed=True,changed_files=list(changed),capability_header_sha256=sha(hdr),physical_timing_evidence=fields,limits='Static/modeled preparation only. No1080i Windows/emulator/physical success, no persistence of failure state,314 cause unresolved.')
except Exception as e:r['failure']=repr(e);raise
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print({n:r[n] for n in ['passed','control_text_byte_identical_311','matched_warnings','source_closure_reconstructed']})
