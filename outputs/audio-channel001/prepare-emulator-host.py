"""Adapt the exercised installed-driver emulator harness to a fresh channel case."""
import ast,hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;old=k.parent/'audio207'
assert not (k/'prepare.py').exists()
origin={}
def get(name):
 p=old/name;origin[name]=hashlib.sha256(p.read_bytes()).hexdigest();return p.read_text()
s=get('prepare-installed002.py')
s=s.replace('k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]','k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1];old=k.parent/"audio207"')
s=s.replace("['installed002']","['emu001']").replace("namespace='xwnpost207b'","namespace='xwnchan001'")
for ref in ['install001/audit.json','install001/closure.json','installed001/audit.json','installed001/closure.json','installed001/fixture.json','artifacts/build004/ac97xnt5.sys','xwnaci207.inf','state-provider001.json','artifacts/state001/installed-runner.exe','artifacts/state001/state.exe']:
 s=s.replace("k/'"+ref+"'","old/'"+ref+"'")
s=s.replace("k/'artifacts/state001/probe-installed.exe'","k/'artifacts/build002/probe.exe'")
s=s.replace("root/(case+'-","root/('channel001-'+case+'-")
ast.parse(s);(k/'prepare.py').write_text(s)
s=get('Prepare-Installed002.ps1').replace('/audio207/prepare-installed002.py installed002','/audio-channel001/prepare.py emu001')
(k/'Prepare.ps1').write_text(s)
for before,after in [('typed-state-installed002.py','typed-state.py'),('installed-binding002.py','installed-binding.py'),('supervise-installed002.py','supervise.py')]:
 s=get(before).replace("['installed002']","['emu001']").replace('nt5-audio207-','nt5-audio-channel001-')
 ast.parse(s);(k/after).write_text(s)
s=get('audit-installed002.py').replace("['installed002']","['emu001']").replace('frozen-installed002.json','frozen.json').replace('nt5-audio207-','nt5-audio-channel001-')
s=s.replace('typed-state-installed002.py','typed-state.py').replace('installed-binding002.py','installed-binding.py')
s=s.replace("['AUDIO207_END','12','0']","['CHANNEL001_END','6','0']").replace("['AUDIO207_BEGIN','1','1']","['CHANNEL001_BEGIN','1','1']").replace('range(12)','range(6)').replace('if i%3!=1:','if True:').replace("('POSITION_SAMPLES','96000')","('POSITION_SAMPLES','144000')")
s=s.replace("    r['probe_passed'] &= rows.count(['DONE_AFTER_RESET',str(i),'1'])==1","    r['probe_passed'] &= rows.count(['DONE_AFTER_RESET',str(i),'1'])==1\n    r['probe_passed'] &= rows.count(['PHASE_MASK',str(i),str(i%3+1)])==1 and rows.count(['CYCLE',str(i),'0'])==1")
ast.parse(s);(k/'audit.py').write_text(s)
s=get('Audit-Installed002.ps1').replace("'installed002'","'emu001'").replace('/audio207/audit-installed002.py','/audio-channel001/audit.py')
(k/'Audit.ps1').write_text(s)
s=get('Run-Installed002.ps1').replace("'installed002'","'emu001'").replace("$PSScriptRoot host-dependencies002.json","$PSScriptRoot ../audio207/host-dependencies002.json").replace('frozen-installed002.json','frozen.json').replace("'Invoke-Audio.ps1'","'../audio207/Invoke-Audio.ps1'").replace('nt5-audio207-','nt5-audio-channel001-').replace('windows-native-audio207','windows-native-audio-channel001')
(k/'Run.ps1').write_text(s)
s=get('Wait-Installed002.ps1').replace("'installed002'","'emu001'").replace('Run-Installed002.ps1','Run.ps1')
(k/'Wait.ps1').write_text(s)
(k/'emulator-controller-origin.json').write_text(json.dumps(origin,indent=2)+'\n')
print('Fresh emulator controllers prepared; no fixture write or guest launch')
