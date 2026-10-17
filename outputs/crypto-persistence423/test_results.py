"""Synthetic structural negatives, distinct from actual NT5 API evidence."""
import json
from pathlib import Path
from results import decode
K=Path(__file__).resolve().parent
def model(phase):
 r=[('probe.schema',423),('probe.create_phase',int(phase==1)),('probe.tick',1000)]
 def add(prefix,keys):r.extend((prefix+'.'+k,0) for k in keys)
 add('probe',['token_open','token_user','sid_valid','sid_bounded']+(['sid_save'] if phase==1 else ['sid_load','same_sid']))
 r += [('probe.volume_info',0),('probe.max_component',255),('probe.filesystem_flags',0),('probe.is_ntfs',1),('probe.is_fatx',0),('probe.memory_context',0)]
 for n in [41,42,43,69]:r += [(f'names.n{n}_open_error',0),(f'names.n{n}_exact',0)]
 for prefix in ['rsa_user','rsa_machine']:
  add(prefix,['acquire']+(['generate','export_public','save_public'] if phase==1 else ['get_existing_key','load_public'])+['import_public','hash_create','hash_data']+(['sign','save_signature'] if phase==1 else ['load_signature'])+['verify_persisted','fresh_hash_create','fresh_hash_data','fresh_sign','fresh_verify'])
 for prefix in ['dpapi_user','dpapi_machine']:
  add(prefix,['protect','bounded_blob'] if phase==1 else ['load_blob']);r.append((prefix+'.blob_bytes',128))
  if phase==1:add(prefix,['save_blob'])
  add(prefix,['unprotect','exact_plaintext'])
 r += [('probe.api_failures',0),('probe.complete',423),('probe.restart_privilege',1),('probe.restart_request',1)]
 return r
def wire(rows):return ''.join(f'{k}={v}\r\n' for k,v in rows).encode()
count=0
for phase in [1,2]:
 rows=model(phase);assert decode(wire(rows),phase)['all_api_operations_passed'];count+=1
 bad=[wire(rows)+b'probe.schema=423\r\n',wire(rows)[:-1],wire(rows)+b'x.y=0\r\n']
 bad += [wire(rows[:i]+rows[i+1:]) for i in range(len(rows))]
 for i,(k,v) in enumerate(rows):
  if k in ['probe.schema','probe.complete','probe.create_phase','probe.api_failures','probe.restart_privilege','probe.restart_request'] or k.endswith('blob_bytes'):
   bad.append(wire(rows[:i]+[(k,0xffffffff)]+rows[i+1:]))
 for b in bad:
  try:decode(b,phase)
  except (AssertionError,KeyError,ValueError):count+=1
  else:raise AssertionError('bad wire accepted')
 # Realistic early API failure: no downstream success invented; counted explicitly.
 failed=[]
 for key,value in rows:
  if key.startswith('rsa_user.'):
   if key=='rsa_user.acquire':failed.append((key,0x80090016))
  else:failed.append((key,1 if key=='probe.api_failures' else value))
 d=decode(wire(failed),phase);assert not d['all_api_operations_passed'] and len(d['api_errors'])==1;count+=1
dest=K/'parser-tests001.json';assert not dest.exists();dest.write_text(json.dumps({'checks':count,'passed':True,'scope':'Synthetic wire/schema and truncated/error flows, not Windows API execution'},indent=2)+'\n');print(count)
