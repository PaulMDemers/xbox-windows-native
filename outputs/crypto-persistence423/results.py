"""Independent exact-schema decoder; API failure is an observation, never a PASS."""
import re
def decode(data,phase):
 assert phase in (1,2) and len(data)<=16384 and data.endswith(b'\r\n')
 rows=[]
 for line in data.decode('ascii').splitlines():
  assert re.fullmatch(r'[a-z0-9_]+\.[a-z0-9_]+=[0-9]{1,10}',line),line
  key,value=line.split('=');value=int(value);assert value<=0xffffffff;rows.append((key,value))
 values=dict(rows);assert len(values)==len(rows),'duplicate key'
 assert values['probe.schema']==423 and values['probe.complete']==423
 assert values['probe.create_phase']==(phase==1)
 assert values['probe.restart_privilege']==1 and values['probe.restart_request']==1
 expected=['probe.schema','probe.create_phase','probe.tick'];errors=[]
 def error(key):
  expected.append(key);v=values[key]
  if v:errors.append((key,v))
  return v
 def chain(prefix,keys):
  for key in keys:
   if error(prefix+'.'+key):return False
  return True
 assert chain('probe',['token_open','token_user','sid_valid','sid_bounded']+(['sid_save'] if phase==1 else ['sid_load','same_sid']))
 if not error('probe.volume_info'):
  expected+=['probe.max_component','probe.filesystem_flags','probe.is_ntfs','probe.is_fatx']
  assert values['probe.is_ntfs'] in (0,1) and values['probe.is_fatx'] in (0,1)
 error('probe.memory_context')
 for n in [41,42,43,69]:
  key=f'names.n{n}_open_error';expected.append(key)
  if not values[key]:error(f'names.n{n}_exact')
 for prefix in ['rsa_user','rsa_machine']:
  chain(prefix,['acquire']+(['generate','export_public','save_public'] if phase==1 else ['get_existing_key','load_public'])+['import_public','hash_create','hash_data']+(['sign','save_signature'] if phase==1 else ['load_signature'])+['verify_persisted','fresh_hash_create','fresh_hash_data','fresh_sign','fresh_verify'])
 for prefix in ['dpapi_user','dpapi_machine']:
  if not chain(prefix,['protect','bounded_blob'] if phase==1 else ['load_blob']):continue
  key=prefix+'.blob_bytes';expected.append(key);assert 0<values[key]<=16384
  if phase==1 and error(prefix+'.save_blob'):continue
  chain(prefix,['unprotect','exact_plaintext'])
 expected+=['probe.api_failures','probe.complete','probe.restart_privilege','probe.restart_request']
 assert [k for k,v in rows]==expected,'missing, extra, reordered or post-failure fields'
 assert values['probe.api_failures']==len(errors),'failure counter mismatch'
 name_errors={str(n):values[f'names.n{n}_open_error'] for n in [41,42,43,69]}
 return {'complete':True,'phase':phase,'api_errors':errors,'name_errors':name_errors,'all_api_operations_passed':not errors,'all_names_passed':not any(name_errors.values()),'values':values}
