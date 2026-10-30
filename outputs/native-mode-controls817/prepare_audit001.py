"""Adapt preparation integrity audit to817's qualified40KiB layout; fresh optical contract."""
from pathlib import Path
K=Path(__file__).resolve().parent;A=K.parent/'native-linecompare-low813'
s=(A/'audit_collection002.py').read_text().split('    photo=read')[0]
s=s.replace('813','817').replace("out = K / 'audit002.json'","out = K / 'audit001.json'")
s=s.replace('len(a) == 31','len(a) == 35').replace('32768','40960')
for old,new in [('a[28]','a[32]'),('a[29]','a[33]'),('a[30]','a[34]'),('a[12:20]','a[12:22]'),('a[20:28]','a[22:32]'),('len(set(starts)) == 8','len(set(starts)) == 10')]:s=s.replace(old,new)
s+='''    photo=read(K/'photo001.json');o=read(K/'observation001.json');schema=read(K/'optical-schema001.json');review=read(K/'photo-review001.json')
    assert photo['passed'] and review['passed']
    values=[int(v,16) for v in photo['decoded_rows']]
    assert values==schema['expected_success_rows']==[0x8170000d,0x817]+[0]*8+[56,60,60]
    assert schema['total_masks_required_for_success']==34 and len(schema['omitted_aggregate_masks'])==27
    assert review['fields']==dict(zip(schema['names'],values))
    assert review['bits']==416 and review['adjacent_row_cross_checks']==352
    assert review['offset_samples_per_bit']==5 and review['thresholds_per_sample']==3
    for key,name in [('decoder_sha256','photo_decode001.py'),('decode_sha256','photo001.json'),('schema_sha256','optical-schema001.json'),('reviewer_sha256','photo_review001.py')]:assert review[key]==sha(K/name)
    assert photo['photo_sha256']==review['photo_sha256']==sha(P/'photo001.jpg')
    assert o['user_observation']=='Green, ready'
    ready=read(K/'collection-ready001.json');assert ready['dashboard_confirmed'] and ready['manual_power_cycle_reported_by_standing_workflow']
    assert read(K/'dashboard002.json')['authenticated']
    r.update(passed=True,report_count=9,last_persisted_phase='handoff_armed',private_sources_binaries_reports_exact=True,independent_alias_overlap_check=True,allocation_bytes=40960,alias_pages=10,native_result_persisted=False,native_optical_values=values,native_final_success_code=values[1],native_seven_displayed_cleanup_masks_zero=True,native_mode_controls_forward_mask_zero=True,CR1A_before=56,CR1A_after=60,CR1A_after_CR2D_undo_before_own_undo=60,CR1A_final_restoration_raw_exposed=False,native_other27_cleanup_masks_aggregate_only=schema['omitted_aggregate_masks'],same_value_controls_effective_write_proved=False,pre_arm_cpu=d['pre_arm_cpu'],normal_Windows_shutdown=False,manual_power_cycle=True,reset_basis=ready['basis'])
    r['pins']={n:sha(K/n) for n in ['collection001.json','photo001.json','photo-review001.json','observation001.json','optical-schema001.json','review001.json']}
except BaseException as e:r['failure']=repr(e);raise
finally:
    r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\\n')
print('PASS817 preparation integrity and independent optical evidence; no desktop claim')
'''
with (K/'audit_collection001.py').open('x',encoding='utf-8',newline='\n') as f:f.write(s)
