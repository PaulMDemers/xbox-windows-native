"""Actual observer sequencing with modeled stops/transport, before runtime."""
import copy, hashlib, json
from pathlib import Path
from trampoline import observe_trampoline, FIELDS, ENTRY, TARGET, GUARD
K=Path(__file__).resolve().parent;out=K/'host003.json';assert not out.exists()
image=Path('C:/xwn520/build001/default.xbe').read_bytes()
assert hashlib.sha256(image).hexdigest()=='73b3623af2694d3c803f70f49fc9c8c072df54a7010d3238358cf6576589ca13'
prior=json.loads((K.parent/'entry-observer517/emu001/trace.json').read_text())
hr=next(r for r in prior['reads'] if r['label']=='trampoline-loaded-header')
loaded=Path(hr['private_file']).read_bytes();assert hashlib.sha256(loaded).hexdigest()==hr['sha256']
import struct
loaded=bytearray(loaded)
for offset,length in [(0x10c,4),(0x350,4),(0x358,4),(0x36c,20)]:loaded[offset:offset+length]=image[offset:offset+length]
loaded=bytes(loaded)
base=dict(registers={**{n:0x100+i for i,n in enumerate(FIELDS)},'EIP':ENTRY})

class Model:
    def __init__(self, fail=None, mutation=None):
        self.events=[];self.active=set();self.fail=fail;self.mutation=mutation
        self.after=copy.deepcopy(base);self.after['registers']['EIP']=TARGET
    def event(self, name):
        self.events.append(name)
        if len(self.events)==self.fail:raise OSError('modeled transport failure')
    def capture(self, address, length, label):
        self.event(label)
        raw=loaded if label=='trampoline-loaded-header' else image[address-0x10000:address-0x10000+length]
        if self.mutation and self.mutation[0]==label:
            b=bytearray(raw);b[self.mutation[1]]^=1;raw=bytes(b)
        return raw
    def bp(self,address,add):
        assert add and address==GUARD;self.active.add(address);self.event('guard')
    def advance(self,address,label):
        assert address==TARGET and label=='early-entry';self.active.add(address)
        self.event('advance');self.active.remove(address);return self.after
    def run(self, low=None):
        try:return observe_trampoline(base if low is None else low,image,self.capture,self.advance,self.bp)
        finally:self.active.clear() # Models caller cleanup; actual trace cleanup checked below.

m=Model();row,proof=m.run();assert proof['passed'] and not m.active
assert m.events==['trampoline-loaded-header','trampoline-five-bytes','guard','advance']
failures=0;negatives=0
for i in range(1,5):
    m=Model(fail=i)
    try:m.run()
    except OSError:failures+=1
    else:raise AssertionError(i)
    assert not m.active
for label,indices in [('trampoline-loaded-header',range(0x128,0x12c)),('trampoline-five-bytes',range(5))]:
    for i in indices:
        m=Model(mutation=(label,i))
        try:m.run()
        except ValueError:negatives+=1
        else:raise AssertionError((label,i))
        assert not m.active
for side in ['before','after']:
    for name in FIELDS+('EIP',):
        for mode in ['missing','changed','boolean','oversize']:
            m=Model();low=copy.deepcopy(base);r=low['registers'] if side=='before' else m.after['registers']
            if mode=='missing':del r[name]
            elif mode=='changed':r[name]^=1
            elif mode=='boolean':r[name]=True
            else:r[name]=2**32
            try:m.run(low)
            except ValueError:negatives+=1
            else:raise AssertionError((side,name,mode))
            assert not m.active
# Execute the actual trace's finally body with modeled transport, without executing its main.
import ast
tree=ast.parse((K/'trace001.py').read_text(encoding='utf-8'))
transaction=next(n for n in tree.body if isinstance(n,ast.Try))
cleanup=compile(ast.fix_missing_locations(ast.Module(body=transaction.finalbody,type_ignores=[])),'trace-finally','exec')
cleanup_cases=0
for stopped in [False,True]:
    for physical in [False,True]:
        for points in [set(),{GUARD},{GUARD,TARGET}]:
            events=[];active=set(points);result={}
            class Socket:
                def close(self):events.append('close')
            class Remote:
                s=Socket()
                def ask(self,c):
                    events.append(c)
                    return '0' if c=='qqemu.PhyMemMode' else 'OK'
            def bp(a,add):assert not add;active.remove(a);events.append(('remove',a))
            class NoRun:
                def exists(self):return False
            env=dict(g=Remote(),stopped=stopped,physical_mode=physical,active=active,r=result,
                     mon=lambda c:events.append(c),bp=bp,save=lambda:None,utc=lambda:'modeled',RUN=NoRun())
            exec(cleanup,env)
            assert not active and result['remaining_breakpoints']==[] and result['physical_mode_remaining'] is False
            assert result['physical_mode_restored'] and 'close' in events
            assert ('stop' in events)==(not stopped)
            cleanup_cases+=1
r=dict(passed=True,actual_observer_paths=1,transport_failure_boundaries=failures,
       invalid_state_and_stub_cases=negatives,actual_trace_cleanup_paths=cleanup_cases,
       CPU_and_transport_modeled=True,physical_access=False,
       sources={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['trampoline.py','host003.py','trace001.py']})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
