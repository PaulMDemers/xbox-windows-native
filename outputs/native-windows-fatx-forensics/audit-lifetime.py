"""Read-only lifetime probe payload audit after emulator closure; no physical access."""
import argparse,hashlib,json,pathlib,subprocess,sys
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--expected',choices=['pass','fail'],required=True);p.add_argument('--reboot',action='store_true');a=p.parse_args()
assert a.run.startswith('nt5-physical-f-high-allocation-') and a.run.replace('-','').isalnum()
run=ws/'work/runs'/a.run;assert (run/'cleanup.json').exists()
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures')/(a.run+'-life.raw');assert not raw.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
r=dict(scope=__doc__,run=a.run,files=[])
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
 with raw.open('rb') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  r['log']=w.read('xwn-life.log').decode('ascii');r['probe_sha256']=hashlib.sha256(w.read('xwnlife.exe')).hexdigest()
  r['probe_matches_fixture']=r['probe_sha256']==json.loads((k/'lifetime-fixture.json').read_text())['lifetime_sha256']
  if a.reboot:
   r['reboot_log']=w.read('xwn-life-reboot.log').decode('ascii')
   fixture=json.loads((k/'lifetime-long-fixture.json').read_text())
   r['reboot_verifier_matches']=hashlib.sha256(w.read('xwnlifeverify.exe')).hexdigest()==fixture['reboot_verifier_sha256']
   r['long_helper_matches']=hashlib.sha256(w.read('xwnphys2.exe')).hexdigest()==fixture['long_soak_sha256']
   r['long_soak_completed']=b'fifteen minute background soak completed' in w.read('xwn-report-v2.txt')
   r['reboot_verified']=r['reboot_log']=='LIFE-REBOOT-BEGIN\r\nLIFE-REBOOT-VERIFY-PASS\r\n' and r['reboot_verifier_matches'] and r['long_helper_matches'] and r['long_soak_completed']
  r['probe_passed']=all(marker+'\r\n' in r['log'] for marker in ['LOCKED-PASS','PENDING-PASS','MAPPING-PASS','REPLACEMENT-PASS','LIFE-PASS']) and 'FAIL:' not in r['log']
  r['reuse_counts']=[int(line.split('=')[1]) for line in r['log'].splitlines() if line.startswith('reuse=')]
  for name,seed in [('pending.bin',32),('mapped.bin',42)]+[(f'{kind}{i:02}.bin',seed+i) for kind,seed in [('target',100),('reuse',300)] for i in range(32)]:
   try:data=w.read('xwnlife/'+name)
   except KeyError:data=None
   expected=bytes(((at*37)^(at>>8)^seed)&255 for at in range(131073))
   r['files'].append(dict(name=name,present=data is not None,match=data==expected,sha256=hashlib.sha256(data).hexdigest() if data is not None else None))
finally:raw.unlink(missing_ok=True)
r['passed']=r['probe_matches_fixture'] and (not a.reboot or r['reboot_verified']) and r['probe_passed'] and all(x['match'] for x in r['files']) and len(r['reuse_counts'])==1 and r['reuse_counts'][0]>0
(k/(a.run+'-lifetime-audit.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({key:r[key] for key in ['run','log','reuse_counts','passed']}))
assert r['passed']==(a.expected=='pass')
