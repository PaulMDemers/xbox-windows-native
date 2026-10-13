"""Create new 330 controller from pinned closed 323; never edit old evidence."""
import ast
import hashlib
import json
from pathlib import Path
K=Path(__file__).resolve().parent
W=K.parents[1]
old=W/'outputs/hd-emulator323'
new=W/'outputs/hd-large-runtime330'
assert not new.exists()
new.mkdir()
names=['Invoke.ps1','Run.ps1','supervise.py','close-host.py','audit.py','typed-state.py','installed-binding.py','analyze-capture.py','review-combined.py']
rows={}
for name in names:
    original=(old/name).read_bytes()
    text=original.decode('utf-8-sig')
    text=text.replace('D:/xwn323','E:/xwn330').replace('/mnt/d/xwn323','/mnt/e/xwn330').replace('nt5-hd323-','nt5-hd330-').replace('windows-native-hd323-','windows-native-hd330-')
    text=text.replace("('control001','candidate001')","('emu001',)").replace("['control001','candidate001']","['emu001']").replace("ValidateSet('control001','candidate001')","ValidateSet('emu001')")
    text=text.replace('5094','5104').replace('5095','5105').replace('5096','5106')
    if name=='Run.ps1':
        begin=text.index('$label=$Case.Replace')
        end=text.index('if((Get-FileHash $exe)',begin)
        text=text[:begin]+"$exe='E:/xwn329/retained-builds001/xemu-hd322.exe'\n$digest='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'\n"+text[end:]
        text=text.replace('(Get-PSDrive D).Free','(Get-PSDrive E).Free').replace('-Seconds 540','-Seconds 1200')
    if name=='supervise.py':
        assert 'deadline=time.monotonic()+600' in text
        text=text.replace('deadline=time.monotonic()+600','deadline=time.monotonic()+1260')
    if name=='audit.py':
        marker="r['actual_caps']=r['samples'][0]['actual_caps']"
        assert marker in text
        text=text.replace(marker,"sys.path.insert(0,str(k.parent/'hd-large327'))\nfrom large_analysis import analyze as large_analysis\nr['large_samples']=[large_analysis(v) for v in texts]\n"+marker)
        marker="subprocess.run([sys.executable,str(k/'typed-state.py'),case],check=True)"
        assert marker in text
        text=text.replace(marker,"r['display_workload_passed'] &= all(v['passed'] for v in r['large_samples'])\n"+marker)
    if name.endswith('.py'):
        ast.parse(text)
    (new/name).write_bytes(text.encode())
    rows[name]=dict(parent_sha256=hashlib.sha256(original).hexdigest(),current_sha256=hashlib.sha256(text.encode()).hexdigest())
(new/'source-review.json').write_text(json.dumps(dict(parent='hd-emulator323',files=rows,
    changes=['C/E paths and unique case/ports','exact recovered candidate emulator','1200s overall host watchdog and1260s observer; guest180s per replay unchanged','all five327 extension verdicts additionally required'],
    physical_access=False,guest_launched=False),indent=2)+'\n')
