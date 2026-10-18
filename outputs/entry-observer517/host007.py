# SPDX-License-Identifier: MIT
"""Actual stopped transaction/verification callbacks with a modeled513 replay.

Retained captures supply an explicitly synthetic516 memory/CPU fixture. This is
not a rerun of513, nor evidence of new kernel execution or physical mapping.
"""
import ast,copy,hashlib,json,re,struct,traceback
from datetime import datetime,timezone
from pathlib import Path
from contracts import plan
from trampoline import observe_trampoline
from entry_decode import decode as decode_entry
K=Path(__file__).resolve().parent;OUT=K/'host007.json';assert not OUT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((K.parent/'entry-colocated516/build001.json').read_bytes());sym=build['wrapper_symbols']
xbe=Path('C:/xwn516/build001/default.xbe').read_bytes();assert sha(xbe)==build['sha256']
prior=json.loads((K.parent/'entry-contract513/emu001/trace.json').read_bytes());assert prior['passed']
raw=[]
for row in prior['reads']:
    b=Path(row['private_file']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256'];raw.append(b)
bylabel={row['label']:(row,b) for row,b in zip(prior['reads'],raw)}
tree=ast.parse((K/'trace001.py').read_text(encoding='utf-8'))
main=next(n for n in tree.body if isinstance(n,ast.Try))
start=next(i for i,n in enumerate(main.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='low' for t in n.targets))
end=next(i for i,n in enumerate(main.body) if isinstance(n,ast.ImportFrom) and n.module=='waiter')
body=compile(ast.fix_missing_locations(ast.Module(body=main.body[start:end],type_ignores=[])),'actual517-stopped-transaction','exec')
definitions=compile(ast.fix_missing_locations(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['ActualCalls','translate']],type_ignores=[])),'actual517-verifiers','exec')
cleanup=compile(ast.fix_missing_locations(ast.Module(body=main.finalbody,type_ignores=[])),'actual517-cleanup','exec')
def shift(v):return v-0x3e0 if 0x95000<=v<0x95140 else v
def fixture(row,data):
    label=row['label'];address=shift(row['address']);b=data
    if label in ['trampoline-loaded-header','loaded-xbe-header']:
        b=bytearray(xbe[:4096]);struct.pack_into('<I',b,0x128,0x11100);b=bytes(b)
    if label in ['trampoline-five-bytes','entry-code','entry-data','original-start-code','object','name','path','code-virtual','data-virtual']:
        b=xbe[address-0x10000:address-0x10000+row['bytes']]
    if label=='data-pde':b=bylabel['code-pde'][1]
    if label=='data-pte':address-=4;b=bylabel['code-pte'][1]
    if label=='code-physical':b=xbe[0x84877:0x84877+row['bytes']]
    if label=='data-physical':
        address=(bylabel['code-physical'][0]['address']&~4095)+(sym['entry498_record']&4095)
        b=xbe[sym['entry498_record']-0x10000:sym['entry498_record']-0x10000+row['bytes']]
    if label.endswith('-stack'):
        words=struct.unpack('<'+'I'*(len(b)//4),b);b=struct.pack('<'+'I'*len(words),*(shift(v) for v in words))
    return address,b
fixtures=[fixture(row,b) for row,b in zip(prior['reads'],raw)]

class Model:
    def __init__(self,fail=None,mutation=None,old_symbols=False):
        self.fail=fail;self.mutation=mutation;self.events=[];self.read_index=0;self.stop_index=0;self.active={0x11100};self.closed=False
        owner=self
        class Socket:
            def close(self):owner.event('close');owner.closed=True
        class Remote:
            s=Socket()
            def ask(self,c):owner.event('ask:'+c);assert c in ('qqemu.PhyMemMode','?');return '0' if c=='qqemu.PhyMemMode' else 'S05'
            def send(self,c):owner.event('send:'+c);assert c=='c'
        class NoRun:
            def exists(self):return False
        ss=copy.deepcopy(sym)
        if old_symbols:
            for n,v in ss.items():
                if 0x94c20<=v<0x94d60:ss[n]=v+0x3e0
        self.env=dict(r={'checkpoints':[],'reads':[]},sym=ss,xbe=xbe,calls=plan(xbe,ss),struct=struct,re=re,decode_entry=decode_entry,observe_trampoline=observe_trampoline,
            capture=self.capture,advance=self.advance,await_stop=self.advance,bp=self.bp,save=lambda:None,utc=lambda:'modeled',g=Remote(),active=self.active,
            stopped=True,physical_mode=False,RUN=NoRun(),mon=lambda c:self.event('mon:'+c))
        exec(definitions,self.env)
    def event(self,label):
        self.events.append(label)
        if len(self.events)==self.fail:raise OSError('modeled transport failure')
    def bp(self,address,add):
        self.event(('add:' if add else 'remove:')+hex(address))
        if add:self.active.add(address)
        else:self.active.remove(address)
    def advance(self,address,label):
        self.event('stop:'+label)
        row=copy.deepcopy(prior['checkpoints'][self.stop_index]);self.stop_index+=1
        assert row['label']==label and row['registers']['EIP']==address
        if address in self.active:self.active.remove(address)
        if self.mutation==('stop',label):row['registers']['EAX']^=1
        self.env['r']['checkpoints'].append(row)
        return row
    def capture(self,address,length,label,physical=False):
        self.event('read:'+label)
        row=prior['reads'][self.read_index];expected,b=fixtures[self.read_index];self.read_index+=1
        assert (label,address,length,physical)==(row['label'],expected,row['bytes'],row['physical']),('wrong request',label,hex(address),hex(expected))
        if self.mutation==('raw',label):b=bytes([b[0]^1])+b[1:]
        if self.mutation==('old',label):b=raw[self.read_index-1]
        self.env['r']['reads'].append(dict(label=label,address=address,bytes=length,physical=physical))
        assert len(b)==length;return b
    def run(self):
        try:exec(body,self.env)
        finally:exec(cleanup,self.env)
        assert self.read_index==len(raw) and self.stop_index==len(prior['checkpoints'])
        assert self.env['r']['actual_completed_kernel_calls']==12 and self.env['r']['terminal_status']==[0]*6
        assert not self.active and self.closed and self.env['r']['remaining_breakpoints']==[]
        assert self.env['r']['physical_mode_restored']
        return self.env['r']

r=dict(passed=False,started_utc=datetime.now(timezone.utc).isoformat(),scope='Actual trace stopped-body, pagewalk, kernel/export verification, ActualCalls callbacks and cleanup; transport/CPU/API/memory fixtures explicitly modeled from retained513 captures plus516 bytes',physical_access=False)
try:
    m=Model();result=m.run();failures=0
    for i in range(1,len(m.events)+1):
        q=Model(fail=i)
        try:q.run()
        except (OSError,AssertionError):
            assert q.closed and not q.active and not q.env['r'].get('cleanup_error');failures+=1
        else:raise AssertionError(('failure accepted',i))
    mutations=[('old',n) for n in ['entry-code','entry-data','object','name','path','wait-amber-stack','wait-green-stack']]
    mutations += [('raw',n) for n in ['trampoline-loaded-header','trampoline-five-bytes','entry-code','entry-data','resolved-thunks','kernel-exports','kernel-export-functions','code-pde','code-pte','data-pde','data-pte','code-physical','data-physical','object','name','path','entry-memory-receipt','initial-indicator-status','final-state','terminal-indicator-status','terminal-indicator-state','terminal-return-state','terminal-restored-registers']]
    # Header byte0 is intentionally not an entry invariant; use disk-vs-loaded
    # representation tests separately (host003), not an invented header gate.
    mutations.remove(('raw','trampoline-loaded-header'))
    mutations += [('stop',n) for n in ['early-entry','file-gate-entry','file-complete-before-indicator']]
    rejected=0
    for mutation in mutations:
        q=Model(mutation=mutation)
        try:q.run()
        except (AssertionError,ValueError,struct.error):
            assert q.closed and not q.active;rejected+=1
        else:raise AssertionError(('mutation accepted',mutation))
    q=Model(old_symbols=True)
    try:q.run()
    except (AssertionError,ValueError):assert q.closed and not q.active;rejected+=1
    else:raise AssertionError('old data symbols accepted')
    r.update(passed=True,actual_stops=m.stop_index,actual_captures=m.read_index,transport_events=len(m.events),injected_transport_failures=failures,mutation_rejections=rejected,actual_verification_callbacks_executed=True,new_runtime_or_physical_proof=False,source_sha256={n:sha((K/n).read_bytes()) for n in ['trace001.py','trampoline.py','indicator_calls.py','kernel_calls.py','contracts.py','entry_decode.py','host007.py']},retained_capture_pins={row['private_file']:row['sha256'] for row in prior['reads']})
except Exception:r['failure']=traceback.format_exc()
r['finished_utc']=datetime.now(timezone.utc).isoformat();OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['passed','failure','actual_stops','actual_captures','injected_transport_failures','mutation_rejections'] if n in r}))
if not r['passed']:raise SystemExit(1)
