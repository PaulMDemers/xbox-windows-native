"""Admission and single-request tests with modeled FTP, no console access."""
import importlib.util,json,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('control532',K/'controller.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
P=Path('C:/xwn532/host001');assert not P.exists();P.mkdir(parents=True)
ready=dict(ready=True,cold_power_cycle_reported=True);prev=dict(completed=True)
obs=dict(at_dashboard=True,user_report_received=True,manual_reset=False)
audit=dict(closed=True,hives_clean=True,ordinary_code_exact=True)
cases=[]
for ordinal in [1,2]:m.admit(ordinal,ready,prev,obs,audit);cases.append('admit'+str(ordinal))
for index,key in [(0,'ready'),(0,'cold_power_cycle_reported'),(1,'completed'),(2,'at_dashboard'),(2,'user_report_received'),(3,'closed'),(3,'hives_clean'),(3,'ordinary_code_exact')]:
    args=[dict(x) for x in [ready,prev,obs,audit]];args[index][key]=False
    try:m.admit(2,*args)
    except AssertionError:cases.append('reject_'+key)
    else:raise AssertionError(key)
bad=dict(obs,manual_reset=True)
try:m.admit(2,ready,prev,bad,audit)
except AssertionError:cases.append('reject_manual_reset')
else:raise AssertionError('reset admitted')
for uncertain in [False,True]:
    out=P/('uncertain.json' if uncertain else 'accepted.json')
    class Socket:
        def settimeout(self,n):assert n==20
    class FTP:
        sock=Socket();calls=0
        def sendcmd(self,command):
            self.calls+=1;assert command==m.COMMAND and json.loads(out.read_text())['requested']
            if uncertain:raise TimeoutError('modeled')
            return '200 modeled'
    f=FTP();m.request_once(f,out,dict(ordinal=1));assert f.calls==1
    try:m.request_once(f,out,{})
    except FileExistsError:pass
    else:raise AssertionError('duplicate request')
    assert f.calls==1;cases.append('uncertain_one_request' if uncertain else 'accepted_one_request')
r=dict(passed=True,cases=cases,scope='Actual admission and request code, modeled evidence and FTP; no physical execution',controller_sha256=hashlib.sha256((K/'controller.py').read_bytes()).hexdigest())
out=K/'host001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
