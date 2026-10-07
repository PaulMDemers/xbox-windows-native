"""Compare each physical GPU setup boot's event and SetupAPI deltas without erasing first-boot anomalies."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
for case in ['001','002']:
 target=k if case=='001' else k/'002';r=json.loads((target/'physical.json').read_text());assert r.get('collected_utc')
 afterdir=target/'artifacts';beforedir=k/'artifacts';beforeprefix='before-' if case=='001' else 'after-';events={};known=[]
 for label in ['system','application']:
  decoded=[]
  for phase in ['before','after']:
   source=(beforedir/(beforeprefix+label+'.evt')) if phase=='before' else afterdir/('after-'+label+'.evt')
   assert sha(source.read_bytes())==r[phase][label+'.evt']['sha256']
   dest=target/(phase+'-'+label+'-events.json');subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(source),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL);decoded.append(json.loads(dest.read_text())['records'])
  before,after=decoded;by={v['record']:v for v in after};assert all(by.get(v['record'])==v for v in before),'Event prefix changed or rolled over'
  known.extend(before);boundary=max((v['record'] for v in before),default=0);events[label]=[v for v in after if v['record']>boundary]
 def recurring(v):return (v['source'],v['event_id']) in {('Service Control Manager',7000),('Ftdisk',49)} and any(all(v[n]==old[n] for n in ['source','event_id','type','strings','data_hex']) for old in known)
 errors=[v for group in events.values() for v in group if v['type'] in (1,2) and not recurring(v)];popups=[v for v in events['system'] if v['source']=='Application Popup'];starts=[v for v in events['system'] if v['source']=='EventLog' and v['event_id']==6005];stops=[v for v in events['system'] if v['source']=='EventLog' and v['event_id']==6006]
 old=(beforedir/(beforeprefix+'setupapi.log')).read_bytes();new=(afterdir/'after-setupapi.log').read_bytes();assert sha(old)==r['before']['setupapi.log']['sha256'] and sha(new)==r['after']['setupapi.log']['sha256'];prefix=new.startswith(old);delta=new[len(old):] if prefix else b'';odd=[i for i,b in enumerate(delta) if b not in (9,10,13) and not 32<=b<127]
 result=dict(scope=__doc__,case=case,new_events=events,unexpected_errors=errors,popups=popups,normal_shutdown_event=len(starts)==len(stops)==1 and starts[0]['record']<stops[0]['record'],strict_event_gate=not errors and not popups and not events['application'],setupapi_exact_prior_prefix=prefix,setupapi_new_bytes=len(delta),setupapi_new_non_ascii_bytes=len(odd),setupapi_new_non_ascii_range=[min(odd),max(odd)] if odd else None,setupapi_new_gpu_install=b'newdev.dll,DevInstall PCI\\VEN_10DE&DEV_02A0' in delta,limits='Manual setup boots; event shutdown evidence does not establish unattended protocol. First-boot malformed SetupAPI bytes remain unresolved, even if no new malformed bytes appear.')
 (target/'events-and-log-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
