"""Prepare a single-run controller from the closed536 protocol, without running it."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'context-pair536'
sha=lambda b:hashlib.sha256(b).hexdigest()
rows={}
def write(name,text,source):
    p=K/name
    if p.exists():assert p.read_text(encoding='utf-8')==text
    else:p.write_text(text,encoding='utf-8',newline='\n')
    rows[name]=dict(source=str(source),source_sha256=sha(source.read_bytes()),sha256=sha(p.read_bytes()))
def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b)
s=(S/'controller.py').read_text(encoding='utf-8').replace('context-pair536','entry-footprint539').replace('xwn536','xwn539')
s=replace(s,'"""Finite matched context pair. No startup hook or ordinary launcher changes."""','"""One post-stack-marker ablation launch; no startup hook or ordinary changes."""')
a=s.index('def admit(');b=s.index('\ndef verify()',a)
s=s[:a]+'''def admit(i,ready,audit=None,observer=None):
    assert i==1 and ready['ordinal']==1 and ready['ready']
    assert ready['unchanged_dashboard_since536'] and not ready['intervening_launch_or_power_cycle']

'''+s[b:]
s=replace(s,'for i in (1,2):','for i in (1,):')
s=replace(s,"('before1','after1','before2','after2')","('before1','after1')")
s=replace(s,"else:assert read(K/f'launch{i}.json')['requested']","else:\n        assert read(K/f'launch{i}.json')['requested']\n        obs=read(K/'observer1.json');assert obs['at_dashboard'] and obs['user_report_received']")
a=s.index('def launch_command(');b=s.index('\ndef launch(i)',a)
s=s[:a]+'''def launch_command(i):
    assert i==1
    return r'SITE EXEC E:\\Applications\\XWNBoot539b\\default.xbe'

'''+s[b:]
s=replace(s,"K.parent/'cold-pair534/after2.json' if i==1 else K/'after1.json'","K.parent/'context-pair536/after2.json'")
s=replace(s,"('launch1','launch2')","('launch1',)")
write('controller.py',s,S/'controller.py')
s=(S/'supervise.py').read_text().replace('536','539')
s=replace(s,'dict(stage=240,before1=240,before2=240,launch1=120,launch2=120,after1=240,after2=240)','dict(stage=240,before1=240,launch1=120,after1=240)')
write('supervise.py',s,S/'supervise.py')
s=(S/'host001.py').read_text().replace('536','539').replace('unchanged_dashboard_since534','unchanged_dashboard_since536')
s=replace(s,"q=read(K/'prepared001.json');cases=[]","q=dict(images={'1':read(K/'prepared001.json')['images']['b']});cases=[]")
a=s.index('ready2=');b=s.index('\nclass FTP:',a)
s=s[:a]+'''audit=dict(closed=True,hives_clean=True,ordinary_code_exact=True)
observer=dict(at_dashboard=True,user_report_received=True)
c.admit(1,ready1);cases.append('admit1')
for key in ready1:
    v=copy.deepcopy(ready1);v[key]=9 if key=='ordinal' else not v[key]
    try:c.admit(1,v)
    except AssertionError:cases.append('reject-'+key)
    else:raise AssertionError(key)
try:c.admit(2,ready1)
except AssertionError:cases.append('reject-second-launch')
else:raise AssertionError('second launch allowed')
'''+s[b:]
s=replace(s,"'success1','success2','timeout'","'success1','timeout'")
s=replace(s,"case.parent/'cold-pair534/after2.json'","case.parent/'context-pair536/after2.json'")
write('host001.py',s,S/'host001.py')
s=(S/'stage-host001.py').read_text().replace('536','539').replace('unchanged_dashboard_since534','unchanged_dashboard_since536')
s=replace(s,"q=c.read(K/'prepared001.json');out=", "q=dict(images={'1':c.read(K/'prepared001.json')['images']['b']});out=")
s=replace(s,"'XWNBoot539a'","'XWNBoot539b'")
s=replace(s,"(6 if mode=='success'","(3 if mode=='success'")
s=replace(s,"'launch1.json':{'requested':True},","'launch1.json':{'requested':True},'observer1.json':{'at_dashboard':True,'user_report_received':True},")
write('stage-host001.py',s,S/'stage-host001.py')
for name in ['audit.py','decode_actual.py']:
    s=(S/name).read_text().replace('536','539')
    s=replace(s,"('1','2')","('1',)")
    if name=='decode_actual.py':s=replace(s,"read(K/'prepared001.json')['wrapper_symbols']","read(K.parent/'context-adapter490/build001.json')['wrapper_symbols']")
    write(name,s,S/name)
for name in ['primary_decode.py','witness_decode.py','decode.py','receipts.py','legacy_refusal_decode.py','failure_marker.py']:
    write(name,(S/name).read_text(),S/name)
(K/'workflow-copy001.json').write_text(json.dumps(dict(files=rows,physical_access=False),indent=2)+'\n',encoding='utf-8')
