"""Cross-check named callback PCs, relocated code pins and stop chronology."""
import hashlib,json,struct,sys,copy
from pathlib import Path
from validate_mode import validate
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'candidate001'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
trace=read(out/'trace.json');dest=k/'transition-verification.json';assert not dest.exists()
v=read(k/'verification.json');assert v['passed'] and validate(trace)['passed']
p=out/'artifacts/xwnown.dll';data=p.read_bytes();pe=pefile.PE(data=data)
pos=pe.FILE_HEADER.PointerToSymbolTable;count=pe.FILE_HEADER.NumberOfSymbols;strings=pos+18*count;size=struct.unpack_from('<I',data,strings)[0]
assert strings+size<=len(data);symbols={};i=0
while i<count:
 name,value,sec,typ,storage,aux=struct.unpack_from('<8sIhHBB',data,pos+i*18);i+=1+aux
 if name[:4]==bytes(4):
  off=struct.unpack_from('<I',name,4)[0];assert 4<=off<size;name=data[strings+off:strings+size].split(b'\0')[0]
 else:name=name.split(b'\0')[0]
 if sec>0:symbols[name.decode().lstrip('_').split('@')[0]]=pe.sections[sec-1].VirtualAddress+value
stages=trace['mode_stages'];stops=trace['stop_sequence'];before=stages[0]['stop_index'];after=stages[1]['stop_index']
for row in stages:
 s=stops[row['stop_index']];assert s['owner']==row['owner'] and s['registers']==row['registers']
for row in trace['mode_calls']:
 base=row['module']['base'];pc=row['entry_registers']['EIP'];assert pc==base+symbols[row['name']]
 assert any(x['module']=='xwnown.dll' and x['base']==base and x['rva']==pc-base and x['sha256']==sha(p) for x in trace['pins'])
 ret=row['return'];m=row['return_module'];pc=ret['registers']['EIP']
 assert any(x['module']==m['name'] and x['base']==m['base'] and x['rva']==pc-m['base'] for x in trace['pins'])
 assert before<row['entry_stop_index']<ret['stop_index']<after
 for index,regs,owner in [(row['entry_stop_index'],row['entry_registers'],row['owner']),(ret['stop_index'],ret['registers'],ret['owner'])]:
  s=stops[index];assert s['registers']==regs and s['owner']==owner
tests=[]
def reject(name,mutate):
 t=copy.deepcopy(trace);mutate(t);assert not validate(t)['passed'],name;tests.append(dict(name=name,rejected=True))
reject('missing_return',lambda t:t['mode_calls'][0].pop('return'))
reject('wrong_return_thread',lambda t:t['mode_calls'][0]['return']['owner'].update(thread=0))
reject('wrong_return_stack',lambda t:t['mode_calls'][0]['return']['registers'].update(ESP=0))
reject('missing_end_marker',lambda t:t['mode_stages'].pop())
reject('module_change',lambda t:t['mode_stages'][1]['module'].update(base=0))
reject('no_callbacks',lambda t:t.update(mode_calls=[]))
reject('API_failure',lambda t:t['mode_stages'][1]['args'].__setitem__(2,1))
enables=[c for c in trace['mode_calls'] if c['name']=='DrvEnableSurface']
if enables:
 n=enables[0]['index'];reject('failed_surface_creation',lambda t:t['mode_calls'][n]['return']['registers'].update(EAX=0))
r=dict(passed=True,mode=validate(trace),actual_mutation_tests=tests,pins={str(p.relative_to(k)):sha(p), 'candidate001/trace.json':sha(out/'trace.json'),'verification.json':sha(k/'verification.json'),'verifier':sha(Path(__file__))},scope='Actual named lifecycle PCs/return sites, chronological stop records, live PDEV fields and strict oracle/cold result; no hardware or new-resolution claim.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['mode'],indent=2))
