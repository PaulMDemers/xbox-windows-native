"""Failure-injection checks against the preserved real NT5 inventory; no guest/network."""
import hashlib,importlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;sys.path.insert(0,str(k));analyze=importlib.import_module('analyze-inventory').analyze
data=(k/'emulator001/artifacts/audit/inventory.log').read_bytes()
r=analyze(data);assert r['completed'] and r['device_count']==12
assert not r['all_resource_payloads_available'] and len(r['unavailable_resource_payloads'])==1
assert 'DEV_02A0' in r['unavailable_resource_payloads'][0]['device']
cases={
    'truncated_completion':data[:-10],
    'duplicate_device_identity':data.replace(b'DEV_01B4',b'DEV_01B1').replace(b'&0&09\r\n',b'&0&30\r\n'),
    'bad_enumeration_terminal':data.replace(b'enumeration_end_error=259',b'enumeration_end_error=5'),
    'missing_resource_free':data.replace(b'free_resource_handle=0\r\n',b'',1),
    'configuration_query_failure':data.replace(b'first_configuration_result=14',b'first_configuration_result=5',1),
    'missing_resource_blob':data.replace(b'resource_data_result=0\r\nhex=',b'resource_data_result=0\r\nignored_hex=',1),
    'device_bound':data.replace(b'devices=12',b'device_bound_reached=1\r\ndevices=12'),
    'missing_property_payload':data.replace(b'property_error=',b'ignored_error=',1),
}
results=[]
for name,bad in cases.items():
    try:analyze(bad)
    except (AssertionError,KeyError,ValueError,TypeError,AttributeError):results.append(dict(case=name,rejected=True))
    else:raise AssertionError('Accepted malformed evidence: '+name)
out=k/'parser001-tests.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,source_sha256=hashlib.sha256((k/'analyze-inventory.py').read_bytes()).hexdigest(),fixture_sha256=hashlib.sha256(data).hexdigest(),valid_real_inventory_passed=True,missing_nv2a_payload_remains_unavailable=True,cases=results),indent=2)+'\n')
print('PASS real NT5 inventory and',len(results),'malformed/truncated evidence cases')
