"""Prepare distinct312 harness; never edit304 or launch a guest."""
from pathlib import Path
import hashlib,json
k=Path(__file__).resolve().parent;old=k.parent/'hd-regression304';new=k.parent/'hd-boot312'
assert not new.exists();new.mkdir()
names=['Run.ps1','Invoke.ps1','Prepare.ps1','supervise.py','audit.py','typed-state.py','installed-binding.py','analyze-capture.py','review-combined.py','close-host.py','freeze.py']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
provenance={}
for n in names:
 p=old/n;t=p.read_text();provenance[n]=dict(parent_sha256=sha(p))
 t=t.replace('xwn304','xwn312').replace('hd304','hd312').replace('hd-regression304','hd-boot312').replace('XWN304_CASE','XWN312_CASE').replace('304 preparation','312 preparation')
 if n=='Run.ps1':t=t.replace('-CaptureAudio -Seconds 540','-CaptureAudio -CaptureWidth 1280 -CaptureHeight 720 -CapturePitch 5120 -Seconds 540')
 if n=='freeze.py':t=t.replace("files += [k/'profile.json']", "files += list((ws/'outputs/hd-loader311').glob('*.json'))+list((ws/'outputs/hd-loader311').glob('*.c'))+list((ws/'outputs/hd-loader311').glob('*.h'))\nfiles += [k/'profile.json']")
 (new/n).write_text(t);provenance[n]['new_sha256']=sha(new/n)
t=(old/'prepare.py').read_text()
t=t.replace("hd-reservation301/candidate001/fixture.json","hd-regression304/candidate001/fixture.json").replace('xwn304','xwn312')
t=t.replace("hd-surface303/binary-review003.json","hd-loader311/binary-review001.json").replace("/mnt/d/xwn303/build003","/mnt/d/xwn311/build001")
t=t.replace("mapping={'F/winnt/system32/xwnown.dll':'xwnown.dll'}","mapping={'E/Applications/XWNFBoot/default.xbe':'default.xbe'}")
t=t.replace("assert sha(build/'xwnown.dll')==review['cases'][case]['sha256']","assert sha(build/'default.xbe')==review['rows'][case]['files']['default.xbe']['sha256']")
t=t.replace('Matched303 software bounds on unused301 candidate preparation; same300 nine-MiB chain/audio004/FATX0101. HDTV profile, unchanged low-resolution timings. No physical or Windows1080 qualification','Matched311 loader on unused304 candidate preparation; same303 software bounds/300 nine-MiB chain/audio004/FATX0101. Control720x480 versus candidate1280x720. No physical/1080i qualification')
t=t.replace('with one matched software display override','with one matched launcher override')
(new/'prepare.py').write_text(t);provenance['prepare.py']=dict(parent_sha256=sha(old/'prepare.py'),new_sha256=sha(new/'prepare.py'))
(new/'harness-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
(new/'profile.json').write_text(json.dumps(dict(avpack='hdtv',eeprom_source='E:/xwn289/fixture001/hd.bin',guest_parent='never-executed304 candidate preparation',expected={'control001':[720,480,2880],'candidate001':[1280,720,5120]},scope='311 bounded720p Cromwell handoff with same303/300 Windows chain'),indent=2)+'\n')
print('Prepared new312 harness; no guest preparation or launch')
