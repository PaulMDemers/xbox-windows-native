"""Bounded two-epoch host observation; never sends guest GPU commands."""
import json,re,time,hashlib
from pathlib import Path
def numbers(s):return {k:int(v) for k,v in re.findall(r'(?<![\w])(\w+)=(\d+)',s)}
def qpath(tree):
    stack=[];found=[]
    for line in tree.splitlines():
        m=re.match(r'^(\s*)/([^ ]*) \(([^)]+)\)',line)
        if not m:continue
        level=len(m[1]);name=m[2]
        while stack and stack[-1][0]>=level:stack.pop()
        if name:stack.append((level,name))
        if m[3]=='nv2a':found.append('/'+'/'.join(n for _,n in stack))
    assert len(found)==1;return found[0]
def validate_report(s,epoch):
    n=numbers(s);assert n['version']==265 and n['epoch']==epoch and n['state']==5
    for key in ['reason','overflow','accounting','shader_jobs_unknown','pending','reuse269_error','native_grant','retirement','cpu0_reason','cpu1_reason','cpu0_count','cpu1_count']:assert n[key]==0,(key,n[key])
    assert n['cpu0_done']==n['cpu1_done']==n['render_fenced']==n['display_fenced']==1
    assert 0<n['worker'] and 0<n['cpu0_thread']==n['cpu1_thread']!=n['worker']
    assert n['cpu0_epoch']==epoch*2-1 and n['cpu1_epoch']==epoch*2
    assert n['started']<=n['cpu0_when']<=n['cpu1_when']<=n['finished']<n['deadline']
    assert n['pages']==(n['rows']+255)//256 and 0<n['rows']<=180000
    assert n['sealed']==n['context_match']==(1 if epoch==2 else 0)
    return n
class Backend:
    def __init__(self,cmd,out,root,result,save):
        self.cmd=cmd;self.out=out;self.root=root;self.r=result;self.save=save
        self.path=None;self.closed=False;self.reopened=False;self.completed=False
    def get(self,prop):return self.cmd('qom-get '+self.path+' '+prop)
    def set(self,prop,value):
        reply=self.cmd('qom-set -j '+self.path+' '+prop+' '+json.dumps(value));assert 'Error' not in reply;return reply
    def wait(self,prop,states,seconds):
        end=time.monotonic()+seconds
        while True:
            s=self.get(prop);n=numbers(s)
            if n['state'] in states:return s
            assert time.monotonic()<end,(prop,s);time.sleep(.03)
    def pages(self,kind,report,epoch):
        n=numbers(report);assert 0<n['pages']<=704
        folder=self.out/(kind+'-pages');folder.mkdir(exist_ok=False);manifest=[]
        prop='xwn-ui265-page' if kind=='ui' else 'xwn-ledger265-page';prefix='end274,' if epoch==2 else ''
        end=time.monotonic()+120
        for i in range(n['pages']):
            assert time.monotonic()<end
            self.set(prop,prefix+str(i));s=self.get(prop);v=numbers(s)
            assert v['epoch']==epoch and v['page']==i and v['pages']==n['pages']
            p=folder/(str(i).zfill(4)+'.txt');p.write_bytes(s.encode());manifest.append(dict(file=p.relative_to(self.out).as_posix(),sha256=hashlib.sha256(s.encode()).hexdigest()))
            self.r[kind+'_pages']=list(manifest);self.save()
        self.r[kind+'_pages']=manifest;self.save()
        self.set(prop,prefix+'0');assert self.get(prop).encode()==(self.out/manifest[0]['file']).read_bytes()
    def begin(self):
        self.path=qpath(self.cmd('info qom-tree'));self.r['nv2a_path']=self.path
        assert numbers(self.get('xwn-ledger265-report'))['state']==0
        self.closed=True;self.r['frontend_close_requested']=True;self.save()
        reply=self.cmd('qom-set '+self.path+' xwn-frontend246-close true');assert 'Error' not in reply
        s=self.wait('xwn-frontend246-report',[2,3],8);v=numbers(s)
        self.r['frontend_initial']=s;self.save();assert v['state']==2 and all(v[n]==0 for n in ['loan','bql','error'])
        ui=self.get('xwn-ui265-report');v=numbers(ui);self.r['ui_report']=ui;self.save()
        assert v['ready']==v['epoch']==1 and v['error']==v['overflow']==0
        self.pages('ui',ui,1)
        self.r['initial_request_may_be_accepted']=True;self.save();self.set('xwn-ledger265','observe276')
        s=self.wait('xwn-ledger265-report',[5,6],12);self.r['initial_report']=s;self.save()
        inventory=self.get('xwn-callbacks276');self.r['callback_inventory_report']=inventory;self.save()
        if numbers(s).get('pages'):self.pages('initial',s,1)
        assert self.get('xwn-ledger265-report')==s
        self.r['inventory_collection_completed']=True;self.save()
        raise RuntimeError('Observation-only276 closed after initial refusal; no guest resume or observer arm')
    def end(self):
        self.r['terminal_request_may_be_accepted']=True;self.save();self.set('xwn-ledger265','finish274')
        s=self.wait('xwn-ledger265-report',[5,6],12);self.r['terminal_report']=s;self.save()
        if numbers(s).get('pages'):self.pages('terminal',s,2)
        n=validate_report(s,2);first=validate_report(self.r['initial_report'],1)
        assert n['worker']==first['worker'] and n['cpu0_thread']==first['cpu0_thread']
        assert n['started']>first['finished'];assert self.get('xwn-ledger265-report')==s
        assert (self.root/'watch/terminal273.bin').is_file()
        self.completed=True;self.r['owner_boundaries_completed']=True;self.save()
    def cleanup(self):
        if self.closed and not self.reopened:
            reply=self.cmd('qom-set '+self.path+' xwn-frontend246-close false');assert 'Error' not in reply
            s=self.wait('xwn-frontend246-report',[5],8);self.r['frontend_reopened_report']=s;self.reopened=True;self.save()
