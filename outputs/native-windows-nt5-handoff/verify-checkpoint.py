"""Verify saved handoff package and evidence; no new emulator run."""
import hashlib,json,pathlib,re
out=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads((out/p).read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 return h.hexdigest()
for name,rec in read('manifest.json')['files'].items():
 p=out/name;assert p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256'],name
iso=read('artifacts/handoff-002.json')
assert sha(out/'artifacts/handoff-002.iso')==iso['iso_sha256']
for name in ['freeldr.sys','rosload.exe','halxboxnt5.dll','xboxbvid.dll']:
 assert sha(out/'artifacts'/name)==iso['files']['/LOADER/'+name.upper()+';1']
state=read('evidence/nt5-handoff-006/state-030.json')
assert state['status']=='pre_entry_halt_verified'
assert 'HLT=1' in state['registers']
assert int(state['cr0'],16)&0x80000000
assert state['extension']['size']==40 and state['extension']['version']==[5,0]
assert len(state['modules'])==21 and len(state['boot_drivers'])==15
assert state['mapped_import_entries_verified']==1673
assert state['lists_have_valid_backlinks']
assert all(c['relocated_executable_sections_equal_after_expected_import_binding'] for c in state['mapped_code_integrity'])
assert state['mapped_code_integrity'][0]['source_sha256']==sha(out/'artifacts/halxboxnt5.dll')
inputs=read('evidence/nt5-handoff-006/input-hashes.json')
assert any(p['Hash'].lower()==iso['iso_sha256'] for p in inputs)
for run in read('checkpoint.json')['runs']:
 assert read('evidence/'+run['id']+'/cleanup.json')['retained'] is False
 assert read('evidence/'+run['id']+'/disk-retention.json')['retained'] is False
assert read('patch-check.json')['complete_chain_matches_working_tree']
assert read('checkpoint.json')['windows_kernel_entered'] is False
print('PASS: package hashes; final ISO; 21 modules, 15 drivers, 1673 import entries; executable-section checks; paging and pre-entry halt; patch-chain and cleanup evidence.')
