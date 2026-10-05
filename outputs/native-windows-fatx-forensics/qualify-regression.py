"""Combine API, cold-disk, current-boot event and explicit visual evidence without hiding warnings."""
import argparse,json,pathlib
ws=pathlib.Path(__file__).resolve().parents[2];k=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--events',type=pathlib.Path,required=True)
p.add_argument('--visual',choices=['delayed-write','no-warning-observed'],required=True)
p.add_argument('--expected',choices=['pass','fail'],required=True);p.add_argument('--rotation-boots',type=int);p.add_argument('--lifetime',action='store_true');a=p.parse_args()
assert a.run.startswith('nt5-physical-f-high-allocation-') and a.run.replace('-','').isalnum()
assert (ws/'work/runs'/a.run/'cleanup.json').exists()
probe=json.loads((ws/'outputs/native-windows-physical-f'/(a.run+'-audit.json')).read_text())
cold=json.loads((ws/'outputs/native-windows-extended-storage'/(a.run+'-cold-audit.json')).read_text())
events=json.loads(a.events.read_text())['records']
start=max(e['record'] for e in events if e['source']=='EventLog' and e['event_id']==6005)
boot=[e for e in events if e['record']>=start]
warnings=[e for e in boot if (e['source']=='Ftdisk' and e['event_id']==50) or any('Delayed Write Failed' in s for s in e['strings'])]
shutdown=any(e['source']=='EventLog' and e['event_id']==6006 for e in boot)
rename=probe['rename_regression'];files=probe['files']
payloads=all(f.get('pattern_match',True) and f.get('truncated_to_zero',True) for f in files) and all(f['present'] for f in files)
passed=all([cold['passed'],probe['probe_passed'],rename['passed'],rename['test_directory_removed'],payloads,shutdown,not warnings,a.visual=='no-warning-observed'])
rotation=None
if a.rotation_boots:
    rotation=json.loads((k/(a.run+'-rotate-audit.json')).read_text())
    passed=passed and rotation['passed'] and rotation['state']==a.rotation_boots
r=dict(scope=__doc__,run=a.run,filesystem_sha256=cold['expected_filesystem_driver_sha256'],
       api_regression_passed=rename['passed'],test_directory_removed=rename['test_directory_removed'],
       cache_soak_passed=probe['probe_passed'],payloads_match=payloads,cold_audit_passed=cold['passed'],
       immutable_files_checked=cold['immutable_files_checked'],hives_checked=len(cold['hives']),
       event_start_record=start,current_boot_events=boot,delayed_write_records=warnings,
       normal_eventlog_shutdown=shutdown,visual_observation=a.visual,passed=passed,
       caveat='Bounded emulator evidence; does not establish the cause of physical013 corruption or long-term hardware stability.')
if rotation:r['rotation']={key:rotation[key] for key in ['passed','state','reuse_counts','no_temporary_files','probe_sha256']}
if a.lifetime:
    life=json.loads((k/(a.run+'-lifetime-audit.json')).read_text())
    r['lifetime']={key:life[key] for key in ['probe_passed','reuse_counts','passed','probe_sha256']}
    if 'reboot_verified' in life:r['lifetime'].update(reboot_verified=life['reboot_verified'],long_soak_completed=life['long_soak_completed'])
    passed=passed and life['passed']
    r['passed']=passed
(k/(a.run+'-qualification.json')).write_text(json.dumps(r,indent=2)+'\n')
print(a.run,'PASS' if passed else 'FAIL','delayed-write records:',len(warnings))
assert passed==(a.expected=='pass')
