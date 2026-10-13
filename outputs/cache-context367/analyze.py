import hashlib,json
from pathlib import Path
from paired_decode import paired
K=Path(__file__).resolve().parent;dest=K/'analysis001.json';assert not dest.exists();root=K.parent/'bandwidth-runtime365/candidate001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=json.loads((root/'audit.json').read_text());oldfinal=sha(root.parent/'final-review.json');pins={};states=[]
assert a['bandwidth_passed'] and not a['memory_state_passed'] and not a['scoped_combined_passed']
assert json.loads((root/'joined-review.json').read_text())['passed']
assert [v['error'] for v in a['memory_states'] if not v['passed']]==['cold/warm CPU state changed']
for i in range(5):
 for phase in ['before','after']:
  base=root/'artifacts'/('sample%d/memory-%s.bin'%(i,phase));cold=base.with_name(base.name+'.cold')
  r=paired(cold.read_bytes(),base.read_bytes());rows=r.pop('rows');sc=[v for v in rows if v['role']==1]
  assert r['bytes']==8294400 and len(sc)==2025 and all(v['physical']==0x03700000+4096*j for j,v in enumerate(sc))
  assert all(v['physical']<0x03700000 for v in rows if v['role']==0)
  pins[str(base)]=sha(base);pins[str(cold)]=sha(cold);states.append(dict(sample=i,phase=phase,**r))
fields=['setup_gate_passed','display_workload_passed','integrity_passed','measurement_events_passed','dashboard_return','audio_children_joined','audio_probe_passed','audio_state_passed','orderly_host_exit','bandwidth_passed']
scoped=all(a[n] for n in fields) and a['normal_shutdown_count']==1 and a['installed_audio_binding']['passed'] and a['audio_capture']['passed'] and not a['new_events']['application'] and not any(v['source']=='Application Popup' for v in a['new_events']['system'])
r=dict(supplemental_scoped_combined_passed=scoped,corrected_memory_policy_passed=all(v['passed'] for v in states),strict_qualification_passed=scoped and a['strict_events_passed'],original_audit_unchanged=sha(root/'audit.json'),original_final_unchanged=oldfinal,original_result_remains_false=True,states=states,raw_packets=pins,original_nonmemory_gates={n:a[n] for n in fields},warnings_errors=a['warnings_errors'],physical_access=False,performance_qualified=False,release_qualified=False)
assert sha(root.parent/'final-review.json')==oldfinal
r['inputs']={n:sha(K/n) for n in ['analyze.py','decode.py','paired_decode.py','test.py','tests001.json','DESIGN.md']};dest.write_text(json.dumps(r,indent=2)+'\n');print(scoped,r['strict_qualification_passed'])
