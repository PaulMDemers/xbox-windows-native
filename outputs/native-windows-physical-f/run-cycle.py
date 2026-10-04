"""Wait for verified upload, launch once, and retrieve the bounded native test."""
import argparse,pathlib,json,subprocess,sys,time,datetime
k=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--wait-upload-seconds',type=int,default=2400);a=p.parse_args()
assert 0<=a.wait_upload_seconds<=3600
record=k/'physical-supervisor.json';assert not record.exists(),'Inspect the prior supervisor before starting another'
assert not (k/'physical-cycle-001.json').exists(),'Do not repeat a prior launch'
r={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'waiting_for_verified_upload','launch_retries':0}
def save():
 tmp=record.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(record)
save();deadline=time.monotonic()+a.wait_upload_seconds
while True:
 try:ready=json.loads((k/'upload.json').read_text()).get('all_files_verified',False)
 except (FileNotFoundError,json.JSONDecodeError):ready=False
 if ready:break
 if time.monotonic()>=deadline:r['status']='upload_wait_expired';save();sys.exit(2)
 time.sleep(10)
r['status']='activating_once';save();print('Upload verified; enabling and launching the physical test once.',flush=True)
result=subprocess.run([sys.executable,str(k/'activate-launch.py')])
if result.returncode:
 r.update(status='activation_failed_inspect_record',returncode=result.returncode);save();sys.exit(result.returncode)
r['status']='waiting_for_normal_restart';save();print('Physical launch sent; waiting for normal restart and fresh native result.',flush=True)
time.sleep(60)
for attempt in range(1,13):
 result=subprocess.run([sys.executable,str(k/'collect-physical.py')],capture_output=True,text=True)
 r.update(collection_attempts=attempt,last_collection_output=(result.stdout+result.stderr)[-3000:])
 if result.returncode==0:
  r.update(status='physical_native_probe_passed',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save();print(result.stdout,flush=True);sys.exit(0)
 proof=json.loads((k/'physical-cycle-001.json').read_text())
 if proof.get('dashboard_available'):
  r['status']='dashboard_available_without_report' if proof.get('report_missing') else 'native_report_failed_validation';save();print(r['last_collection_output'],flush=True);sys.exit(3)
 save()
 if attempt<12:time.sleep(15)
r['status']='manual_screen_check_required';save();print('Fresh native result unavailable; no relaunch attempted. Inspect the console screen.',flush=True);sys.exit(4)
