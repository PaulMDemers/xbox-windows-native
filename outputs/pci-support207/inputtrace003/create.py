"""Fresh debugger-only input ownership case using unchanged veto-arm payloads."""
from pathlib import Path
import json, shutil
k=Path(__file__).resolve().parent;old=k.parent/'rebalance002'
assert not (k/'run.py').exists()
for name in ('audit-emulator002.py','review-pnp002.py','e_allocation.py','xwnrsc.inf'):
    shutil.copy2(old/name,k/name)
(k/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
s=(old/'run-emulator002.py').read_text().replace("('skip','allow','veto')","('veto',)").replace('4814','4824').replace('4816','4826')
s=s.replace('for port in (4824,4826):','for port in (4824,4825,4826):')
s=s.replace("'debugger':False", "'debugger':True").replace("'host_bound_seconds_after_launch':180", "'host_bound_seconds_after_launch':300")
s=s.replace("'-device','usb-kbd'", "'-gdb','tcp:127.0.0.1:4825','-device','usb-kbd'")
s=s.replace('vm=None;stdout=', 'observer=None;observer_log=None;vm=None;stdout=')
s=s.replace("    r.update(launch_requested=True", """    observer_log=(out/'observer-console.txt').open('xb')
    observer=subprocess.Popen([sys.executable,str(k/'trace.py')],cwd=k,stdout=observer_log,stderr=subprocess.STDOUT,startupinfo=si)
    arm_deadline=time.monotonic()+30
    while not (case/'trace-armed.signal').exists():
        if observer.poll() is not None:raise RuntimeError('Observer exited before arming')
        if time.monotonic()>arm_deadline:raise TimeoutError('Observer arm bound')
        time.sleep(.1)
    r['observer_pid']=observer.pid
    r.update(launch_requested=True""")
s=s.replace('deadline=time.monotonic()+180','deadline=time.monotonic()+300').replace('deadline-145','deadline-265')
s=s.replace('finally:\n    if vm:', """finally:
    if observer:
        try:observer.wait(timeout=10)
        except subprocess.TimeoutExpired:
            observer.terminate();observer.wait(timeout=10);r['observer_host_terminated']=True
        r['observer_exit_code']=observer.returncode
    if observer_log:observer_log.close()
    if vm:""")
(k/'run.py').write_text(s)
s=(old/'Continue-001.ps1').read_text().replace('/rebalance002/','/inputtrace003/').replace("@('skip','allow','veto')","@('veto')")
start=s.index("Stage 'build'");end=s.index('foreach($variant',start)
s=s[:start]+"Stage 'preflight' { & C:/Python314/python.exe (Join-Path $PSScriptRoot 'preflight.py');if($LASTEXITCODE){throw 'Preflight failed'} }\n"+s[end:]
s=s.replace("'prepare-emulator002.py'","'prepare.py'").replace("'run-emulator002.py'","'run.py'")
(k/'Continue-001.ps1').write_text(s)
