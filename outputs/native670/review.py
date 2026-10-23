"""Independent artifact/source and qualification-boundary review."""
import datetime,hashlib,json,re,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn670/host003');out=K/'review001.json'
assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,new_XBE=False,checks=[])
def check(n,v):assert v,n;r['checks'].append(n)
def local(s):return Path(s.replace('/mnt/c/','C:/',1))
try:
 b=json.loads((K/'host003.json').read_text());e=json.loads((K/'execute003.json').read_text())
 check('leased host build',b['passed'] and b['space']['minimum_free_gib']==20.05)
 check('40 actual integration model cases',e['passed'] and len(e['cases'])==40)
 check('exercised exact code',e['binary_sha256']==b['artifacts']['integration.bin']['sha256']==sha(B/'integration.bin'))
 check('exact test source',e['source_sha256']==sha(K/'execute_v3.py'))
 for n,v in b['inputs'].items():check('input '+n,sha(local(v['path']))==v['sha256']==sha(B/'source'/n))
 for n,v in b['artifacts'].items():check('artifact '+n,sha(B/n)==v['sha256'])
 check('legacy header inputs unchanged',all(sha(Path('C:/xwn667/source001')/n)==h for n,h in b['legacy_headers'].items()))
 for n in ['native.c','admission.c','admission.h','nic.c','nic.h']:
  check('original656 '+n,sha(W/'outputs/net656'/n)==b['inputs'][n]['sha256'])
 check('667 source tracked diff empty',not subprocess.check_output(['git','-C','C:/xwn667/source001','diff','--name-only'],timeout=25))
 check('no XBE',not any(p.suffix.lower()=='.xbe' for p in B.rglob('*')))
 check('all terminal repeats no IO',all(v['repeat_terminal_no_io'] and v['held'] and v['IF_at_hold']==0 for v in e['cases']))
 cases={v['name']:v for v in e['cases']}
 for n in ['success-if-set','success-if-clear']:
  v=cases[n];check(n+' packet/flags/three frames',v['original_packet_sha256']==v['transport_packet_sha256'] and len(v['frames'])==3 and len(set(v['frames']))==1 and v['transport_flags']==(v['original_flags']&~512) and v['result'][5:7]==[3,1])
 for n,v in cases.items():
  if v['admission']:check(n+' no native NIC activity',v['mmio_reads']==v['mmio_writes']==0 and not v['pci_writes'])
 check('all admission classes',set(v['admission'] for v in e['cases'])==set(range(6)))
 dis=(B/'disassembly.stdout').read_text()
 check('no IF restore or privileged context writes',not re.search(r'\t(?:sti|popf\w*|wrmsr|invlpg)\b|\tmov[^\n]*,%cr',dis))
 check('actual native cache instructions retained','\twbinvd' in dis)
 text=(K/'integration.c').read_text()
 check('single direct sender call',text.count('e=NativeSend656(')==1)
 check('no boot reset continuation',not re.search(r'Boot|Reboot|Reset|malloc|free\(',text))
 check('terminal noreturn declaration','__attribute__((noreturn))' in (K/'integration.h').read_text())
 check('encode before sealing',text.index('xwn655_encode(')<text.index('return seal669('))
 check('finite indication uses existing bounded helper',text.count('=write658(')==2 and 'irq_hold669();' in text)
 check('compile failures retained',all(not json.loads((K/n).read_text())['passed'] for n in ['host001.json','host002.json']))
 check('harness failure retained',not json.loads((K/'execute001.json').read_text())['passed'])
 check('prior 39 case pass retained',json.loads((K/'execute002.json').read_text())['passed'])
 r['passed']=True
except BaseException as ex:r['failure']=repr(ex);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'artifact/scope checks')
