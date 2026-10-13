"""New paired runtime from reviewed339 controller; no launch or fixture mutation."""
import ast,difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'stock-repeat339';changes={}
for name in ['Invoke.ps1','close-host.py','analyze-allocation002.py','stock_io002.py','analyze-capture.py','typed-state.py','installed-binding.py','supervise002.py','audit002.py']:
    target={'supervise002.py':'supervise.py','audit002.py':'audit.py'}.get(name,name);old=(P/name).read_text();s=old
    s=s.replace('xwn336','xwn346').replace('xwn339','xwn346').replace('stock339','phase346').replace('5126','5166').replace('5127','5167').replace('5128','5168')
    s=s.replace("case in ['emu001']","case in ['control001','candidate001']").replace("case=='emu001'","case in ['control001','candidate001']")
    if target=='supervise.py':s=s.replace('time.monotonic()+660','time.monotonic()+1260')
    if target=='audit.py':
        s=s.replace("case=sys.argv[1];", "case=sys.argv[1];mode=int(case=='candidate001');")
        s=s.replace('[timing(v,0) for v in texts]','[timing(v,mode) for v in texts]').replace('[window(v,0) for v in texts]','[window(v,mode) for v in texts]')
        needle="subprocess.run([sys.executable,str(k/'typed-state.py'),case],check=True);"
        assert s.count(needle)==1
        s=s.replace(needle,"sys.path.insert(0,str(k.parent/'hd-phase344'))\nfrom phase_analysis import analyze as large_phase\nr['large_phase_samples']=[large_phase(v,mode) for v in texts]\nr['display_workload_passed'] &= all(v['passed'] for v in r['large_phase_samples'])\n"+needle)
    assert not (K/target).exists();(K/target).write_text(s)
    if target.endswith('.py'):ast.parse(s)
    changes[target]=dict(parent=name,before_sha256=hashlib.sha256((P/name).read_bytes()).hexdigest(),after_sha256=hashlib.sha256((K/target).read_bytes()).hexdigest())
    (K/(target+'.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='339/'+name,tofile='346/'+target)))
s=(P/'Run.ps1').read_text();s=s.replace("$ErrorActionPreference='Stop'","param([ValidateSet('control001','candidate001')][string]$Case)\n$ErrorActionPreference='Stop'",1)
s=s.replace('Join-Path $PSScriptRoot emu001','Join-Path $PSScriptRoot $Case').replace('nt5-stock339-emu001','("nt5-phase346-"+$Case)').replace('windows-native-stock339-emu001','("windows-native-phase346-"+$Case)')
s=s.replace('5126','5166').replace('5127','5167').replace('5128','5168').replace('-Seconds 600','-Seconds 1200')
s=s.replace("$pins=Get-Content (Join-Path $PSScriptRoot emulator-frozen.json)","$pins=Get-Content (Join-Path $out emulator-frozen.json)")
(K/'Run.ps1').write_text(s)
(K/'controller-source-review.json').write_text(json.dumps(dict(passed=True,source_changes=changes,physical_access=False,gate_changes='Expected clock mode per case plus required344 large interval decoder; original event/audio/integrity/shutdown gates retained.',runtime=False),indent=2)+'\n')
(K/'.gitignore').write_text('**/artifacts/\n')
