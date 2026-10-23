"""Pin675 host evidence and audit scope; no console or build execution."""
import datetime,hashlib,json,re,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn675/host001');out=K/'review001.json'
assert not out.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,new_XBE=False,checks=[])
def check(name,condition):assert condition,name;r['checks'].append(name)
try:
 h=json.loads((K/'host001.json').read_text());linked=json.loads((K/'linked001.json').read_text());dark=json.loads((K/'dark-paths001.json').read_text())
 check('sanitizer2039 groups',h['passed'] and h['tests']['assertion_groups']==2039)
 check('19 linked native fixtures',linked['passed'] and len(linked['cases'])==19)
 check('8 old-code dark-path fixtures',dark['passed'] and len(dark['cases'])==8)
 for n,pin in h['source_pins'].items():
  p=Path(n.replace('/mnt/c/','C:/'));check('pinned input '+p.name,sha(p)==pin)
 for n,v in h['artifacts'].items():check('artifact '+n,sha(B/n)==v['sha256'])
 for file,receipt in [('linked.py',linked),('dark_paths.py',dark)]:check('test source '+file,sha(K/file)==receipt['source_sha256'])
 check('exact linked binary',sha(B/'probe.bin')==linked['binary_sha256'])
 check('exact retained674 binary',sha(Path('C:/xwn674/build001/image-crom.bin'))==dark['binary_sha256'])
 for n,root in [('nic.c','drivers/diag656'),('nic.h','drivers/diag656'),('indication.c','drivers/diag657'),('indication.h','drivers/diag657')]:
  check('unchanged original '+n,(B/'source'/n).read_bytes()==(Path('C:/xwn674/source001')/root/n).read_bytes())
 check('no undefined link dependencies',not (B/'undefined.stdout').read_bytes())
 check('no XBE or firmware image produced',not list(Path('C:/xwn675').rglob('*.xbe')))
 dis=(B/'disassembly.stdout').read_text()
 def fn(n):return dis.split('<'+n+'>:',1)[1].split('\n\n',1)[0]
 check('terminal adapter has no return',not re.search(r'\tret\b',fn('terminal675')))
 check('terminal ends at retained hold','<irq_hold669>' in fn('terminal675'))
 check('retained hold CLI and HLT','\tcli' in fn('irq_hold669') and '\thlt' in fn('irq_hold669'))
 for n in ['terminal675','probe675','delay656','write658']:
  check(n+' no IF enable/reset/allocator/NIC call',not re.search(r'\t(?:sti|popf\w*)\b|<(?:malloc|free|BootResetAction|send656|NativeSend656)>',fn(n)))
 check('timerless SMC delay refusal contains no call or I/O',not re.search(r'\t(?:call|in\w*|out\w*)\b',fn('refuse_wait')))
 check('native clock exact port input', '\tin' in fn('ticks') and '$0x8008' in fn('ticks'))
 check('all linked fixtures terminal/reentry-safe',all(v['held'] and v['repeat_no_io'] for v in linked['cases']))
 check('no indicator dark-mask request',all([8,0] not in v['commands'] for v in linked['cases']))
 check('old successful marker also ends dark',next(v for v in dark['cases'] if v['name']=='entry-complete')['latched_mask_model']==0)
 check('old dark errors are modeled only',all(not v['actual_hardware_cause_established'] for v in dark['cases']))
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['checks']),'provenance/scope checks')
