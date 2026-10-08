"""Recheck ordinary cold evidence, preserving incomplete and failed cases."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['candidate001'];out=k/case
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
dest=out/'verification.json';assert not dest.exists();audit=read(out/'audit.json');closure=read(out/'closure.json')
for n,h in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/n)==h
assert sha(Path(closure['private_disk']))==closure['private_disk_sha256']
before=read(out/'before-pagefile-map.json');after=read(out/'after-pagefile-map.json');pagefile=all(before[n]==after[n] for n in ['file_size','clusters','first_cluster','requested_65536','whole_file'])
v=(out/'artifacts/video-trace.bin').read_bytes();count,dropped=struct.unpack_from('<II',v,16);assert count<=254
shared=[list(struct.unpack_from('<4I',v,32+i*16)) for i in range(count) if struct.unpack_from('<I',v,32+i*16)[0] in [0x30,0x31,0x32]]
mapped=any(e==[0x30,0,0xfced6000,0x03c00000] for e in shared) and all(e[1]==0 for e in shared)
from protocol import validate_log,fnv,expected_bytes
log=out/'artifacts/result.log';protocol=validate_log(log.read_bytes() if log.exists() else None,case=='candidate001')
assert protocol==audit['protocol_details']
references=[]
for index,row in enumerate(audit['files']):
 p=out/'artifacts'/('ref%02d.rgb'%index)
 if not p.exists():
  assert row['sha256'] is None and not row['matched'];references.append(dict(index=index,present=False));continue
 assert sha(p)==row['sha256']
 match=p.read_bytes()==expected_bytes(index) and index<len(protocol['cases']) and fnv(p.read_bytes())==protocol['cases'][index]['reference_hash']
 assert match==row['matched'];references.append(dict(index=index,present=True,matched=match,sha256=sha(p)))
observed=[]
for row in audit['observed']:
 p=out/'artifacts'/row['name'];data=p.read_bytes() if p.exists() else None;expected=expected_bytes(int(row['name'][3:5]))
 match=data is not None and len(data)==len(expected) and all(data[c::4]==expected[c::4] for c in range(3))
 assert match==row['matched'] and (sha(p) if data is not None else None)==row['sha256'];observed.append(row)
passed=audit['strict_qualification_passed'] and read(out/'after-configuration.json')['expected_configuration'] and pagefile and mapped and dropped==0
r=dict(passed=bool(passed),ordinary_qualified=False,debugger=True,physical_qualified=False,cases=protocol['cases'],references=references,compared_pixels=protocol.get('compared_pixels',0),callback_totals=protocol.get('callback_totals',{}),unobserved_hooks=protocol.get('unobserved_hooks',[]),pagefile_unchanged=pagefile,shared_events=shared,trace_records=count,dropped=dropped,cold_qualification=audit['strict_qualification_passed'],
 pins={n:sha(out/n) for n in ['audit.json','closure.json','preflight.json','allocation.json','after-configuration.json','before-pagefile-map.json','after-pagefile-map.json']},verifier_sha256=sha(Path(__file__)),limits='Real GDI DIB reference and primary readback; own-driver coherence is not independent physical scanout proof. Unobserved callbacks remain unqualified. No physical or speed claim.')
r['profile_attribution_passed']=bool(passed and protocol.get('profile_attribution_passed',False));r['lifecycle_qualified']=False;r['observed_readbacks']=observed;r['clock']=protocol.get('clock');r['timer_protocol_passed']=protocol.get('timing_passed',False)
r['exclusive_xemu']=closure['instance']['mode']=='exclusive'
r['timing_qualified']=False; r['timing_exclusion']='Debugger diagnostic; no timing qualification even if clock gates pass'
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['passed','compared_pixels','callback_totals','unobserved_hooks','cold_qualification','profile_attribution_passed']},indent=2))
