"""Actual admission/request code, modeled FTP; no console access."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

K=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('second531',K/'second-launch.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
P=Path('C:/xwn531/second-host001');assert not P.exists();P.mkdir(parents=True)
out=K/'second-host001.json';assert not out.exists()
paths=[m.m.NORMAL,m.m.TARGET]+m.m.MUTABLE+[m.m.REMOTE+'/owner.json',m.m.REMOTE+'/default.xbe']
row=dict(path='MODELED',bytes=1,sha256='a'*64)
stage=dict(completed=True,temporary_startup_added=False,remote=m.m.REMOTE,
           staged={n:copy.deepcopy(row) for n in paths[-2:]})
collection=dict(completed=True,temporary_hook_installed=False,remote_writes=[],
                protected_code_exact=True,files={n:copy.deepcopy(row) for n in paths})
collection['files'].update({m.m.REMOTE+'/'+n:None for n in m.m.RECEIPTS})
closure=dict(closed=True,physical_launches=1,no_next_launch_queued=True)
observer=dict(user_report_received=True,at_dashboard=True,manual_reset_between_launches=False)
base=[stage,collection,closure,observer];cases=[]
assert len(m.admit(*base))==len(paths);cases.append('first_receipts_absent_allowed')
b=copy.deepcopy(base)
for name in m.m.RECEIPTS:b[1]['files'][m.m.REMOTE+'/'+name]=copy.deepcopy(row)
assert len(m.admit(*b))==len(paths)+2;cases.append('first_receipts_retained_allowed')
mutations=[(0,'completed',False),(0,'temporary_startup_added',True),(0,'remote','/E/wrong'),
           (1,'completed',False),(1,'temporary_hook_installed',True),(1,'remote_writes',['unexpected']),
           (1,'protected_code_exact',False),(2,'closed',False),(2,'physical_launches',2),
           (2,'no_next_launch_queued',False),(3,'user_report_received',False),(3,'at_dashboard',False),
           (3,'manual_reset_between_launches',True)]
def refuse(values,label):
    try:m.admit(*values)
    except (AssertionError,KeyError):cases.append(label)
    else:raise AssertionError('invalid admission accepted: '+label)
for i,key,value in mutations:
    b=copy.deepcopy(base);b[i][key]=value;refuse(b,f'refuse_{i}_{key}')
b=copy.deepcopy(base);b[1]['files'][paths[-1]]['sha256']='b'*64;refuse(b,'changed_candidate')
b=copy.deepcopy(base);del b[1]['files'][paths[0]];refuse(b,'missing_protected_file')
b=copy.deepcopy(base);b[1]['files']['/E/unexpected']=row;refuse(b,'unexpected_collected_file')
requests=[]
for name,uncertain in [('accepted',False),('uncertain',True)]:
    target=P/(name+'.json');calls=[]
    class F:
        def __init__(self):self.sock=self
        def settimeout(self,value):assert value==20;calls.append('bound20')
        def sendcmd(self,cmd):
            saved=json.loads(target.read_text(encoding='utf-8'))
            assert saved['requested'] and saved['ordinal']==2 and saved['command']==cmd
            assert cmd==r'SITE EXEC E:\Applications\XWNDispatch528\default.xbe'
            calls.append('SITE')
            if uncertain:raise TimeoutError('MODELED reply loss')
            return '200 MODELED acceptance'
    f=F();r=m.request_once(f,target,{})
    try:m.request_once(f,target,{})
    except AssertionError:pass
    else:raise AssertionError('duplicate second request allowed')
    assert calls==['bound20','SITE']
    assert ('reply_uncertain' in r)==uncertain
    requests.append(dict(case=name,exactly_one_request=True,intent_saved_before_request=True,
                         duplicate_refused=True,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
r=dict(passed=True,scope='Actual admission/request code, modeled FTP and first-run evidence',
       physical_access=False,source_sha256=hashlib.sha256((K/'second-launch.py').read_bytes()).hexdigest(),
       cases=cases,request_cases=requests,all_processes_closed=True)
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print('PASS',len(cases),'admission cases and2 modeled one-request cases')
