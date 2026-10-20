"""MIT. Exercise exact cleanup transaction paths without network access."""
import hashlib,importlib.util,json,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('cleanup_test',K/'apply_cleanup002.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
c=a.c;m=a.m;read=c.read;sha=m.sha;cases=[]
class FTP:
    def __init__(self,mode):self.mode=mode;self.files={a.TARGET:b'old'};self.calls=[]
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def rename(self,src,dst):
        self.calls.append(('rename',src,dst));assert src in self.files and dst not in self.files
        if self.mode=='uncertain-before-rename':raise TimeoutError()
        self.files[dst]=self.files.pop(src)
        if self.mode=='uncertain-after-rename':raise TimeoutError()
def get(f,n,optional=False):return f.files.get(n) if optional else f.files[n]
def put(f,n,b):
    assert n not in f.files;f.calls.append(('put',n));f.files[n]=b+(b'bad' if f.mode=='corrupt-stage' else b'')
with tempfile.TemporaryDirectory(prefix='xwn596-cleanup-model-') as tmp:
    for mode in ['pass','foreign-source','existing-temp','existing-backup','hook-present','corrupt-stage','uncertain-before-rename','uncertain-after-rename']:
        a.K=Path(tmp)/mode;a.K.mkdir();p=a.K/'candidate';p.write_bytes(b'new');f=FTP(mode)
        prep=dict(passed=True,all_other_key_names_and_raw_values_unchanged=True,source=dict(sha256=sha(b'old')),candidate=dict(path=str(p),bytes=3,sha256=sha(b'new')))
        (a.K/'cleanup-preparation002.json').write_text(json.dumps(prep));(a.K/'collection001.json').write_text(json.dumps(dict(completed=True,hook_removed=True)))
        c.verify=lambda:None;c.budget=lambda:None;c.startup=lambda *args:None
        m.connect=lambda **kwargs:f;m.baseline=lambda *args:None;m.get=get;m.put=put;m.cold_pair=lambda n,r,o:get(f,n)
        if mode=='foreign-source':f.files[a.TARGET]=b'other'
        if mode=='existing-temp':f.files[a.TEMP]=b'existing'
        if mode=='existing-backup':f.files[a.BACKUP]=b'existing'
        if mode=='hook-present':f.files[c.HOOK]=b'hook'
        try:a.run();passed=True
        except (AssertionError,TimeoutError):passed=False
        assert passed==(mode=='pass'),mode
        if passed:
            assert f.files=={a.TARGET:b'new',a.BACKUP:b'old'}
            count=len(f.calls)
            try:a.run()
            except AssertionError:pass
            else:raise AssertionError('Repeated cleanup admitted')
            assert len(f.calls)==count
        elif mode=='uncertain-after-rename':assert f.files[a.BACKUP]==b'old' and a.TARGET not in f.files
        elif mode!='foreign-source':assert f.files[a.TARGET]==b'old'
        if mode in ['foreign-source','existing-temp','existing-backup','hook-present']:assert not f.calls
        assert sum(x[0]=='rename' for x in f.calls)<=2
        cases.append(dict(case=mode,expected_outcome=True,no_launch=True,no_write_retry=True))
out=K/'cleanup-host001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,cases=cases,pins={n:sha((K/n).read_bytes()) for n in ['apply_cleanup002.py','cleanup_host001.py','prepare_cleanup002.py']},limits='Transport model, not physical persistence proof.'),indent=2)+'\n');print('Passed',len(cases),'cleanup transaction cases')
