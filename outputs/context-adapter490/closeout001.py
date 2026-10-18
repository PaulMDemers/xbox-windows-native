"""Read-only rehash/closure; writes only a new receipt and continuation prefix."""
import ast,datetime,hashlib,json,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'final-review.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=['host-build001.json','host-run001.json','build001.json','validation001.json','full-source001.json','full-host001.json','decoder-source001.json','full-transport001.json']
private={};inputs={}
for name in records:
 r=json.loads((K/name).read_text());assert r.get('passed',r.get('status') in ('compiled','passed'))
 for n,v in r.get('files',{}).items():
  p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes'];private[n]=v
 for n,h in r.get('inputs',{}).items():inputs[n]=h
local={n:h for n,h in inputs.items() if n.startswith('/mnt/c/')}
for n,h in local.items():assert sha(Path(n.replace('/mnt/c/','C:/')))==h
remote={n:h for n,h in inputs.items() if not n.startswith('/mnt/c/')}
code="import pathlib,json,hashlib,sys; d=json.load(sys.stdin); assert all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==h for p,h in d.items()); active=[]\nfor p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):\n try:\n  a=p.read_bytes().split(b'\\0'); active += [str(p)] if a and pathlib.PurePath(a[0].decode(errors='replace')).name.startswith('qemu-system') and b'xwn-context-adapter490-host001' in a else []\n except (FileNotFoundError,PermissionError):pass\nassert not active,active\nprint(json.dumps({'remote_pins':len(d),'owned_VM_processes':active}))"
v=subprocess.run(['wsl','-d','Ubuntu','--','python3','-B','-c',code],input=json.dumps(remote),text=True,capture_output=True,timeout=30,check=True)
for p in K.glob('*.py'):ast.parse(p.read_text())
free={n:shutil.disk_usage(n+':/').free for n in ['C','E']}
assert free['C']-128*1024**2>=20*1024**3
b=json.loads((K/'build001.json').read_text())
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,console_prepared=False,console_launched=False,ordinary_launcher_startup_720p_changed=False,all_owned_processes_closed=True,process_check=json.loads(v.stdout),private_files_rehashed=len(private),input_pins_rehashed=len(inputs),free_bytes=free,compiled_XBE=dict(path='C:/xwn490/build001/default.xbe',sha256=b['sha256'],bytes=b['bytes']),actual_privileged_fixture_cases=46,modeled_full_wrapper_cases=150,fixture_negative_controls=4067,full_transport_negative_controls=5241,full_admission_cleanup_20_21_pending=True,page_walk_implemented=False,physical_boot_qualified=False,records={n:sha(K/n) for n in records})
out.write_text(json.dumps(r,indent=2)+'\n')
head='''# Current: CPU-context adapter490 compiled and host-qualified; no console launch

Read outputs/context-adapter490 REPORT/DESIGN/NEXT/final-review and actual records.
New exact487 diagnostic adds BYTE-IDENTICAL489 capture before witness IO and after
its successfulclose.400-bytecontext packet cannotproveitsownclose/laterPG.
Diskless privilegedhost001 actualadapter/capture/originalwitness/helper46cases
PASS (2contextpairs44refusals), originalregisters/flags exact; CPU/allocations/IO
synthetic and refusalendpointmodeled. VMclosedexit33,noexceptions/deadline/fallback.
Full001 actualassembledwrapper150cases PASS withoriginalrefusalcleanup, CPUcapture
substitutedbydebuggertrap/model; distinctfromactualprivilegedfixture.18newfile
failurepaths22..25 covered. Newadmissionreasons20/21 stillneedfullcleanuppaths in
NEWfull002 beforephysicalpackage;46fixturecoversadmissionwithmodeledendpoint.
4067fixturetransport+5241fulltransport negativesreject;28modeledCPUcontextpackets,
129refusalrecordsdecode. Original1024loader/payload/font/imports unchanged;313byte
captureexact. OnefixtureRWXLOADwarningreviewed;XBEbuildlogempty. No490failure.

PrivateC:/xwn490/{host001,build001,full001}; allclosed, neverrerunconsumedIDs.
Next NEWfull002 admissioncleanup tests thennamespace490physicalrunner/controller
usingexisting490XBE andunchanged486sample/oracle, boundedFTPreadreconnect andcontext
collection/identitychecks; seeNEXT preciseimports/boundaries. No490consolefiles,
startuphook/deployment/launch, sharedSDK/driver/720pchange orpagewalkprovider.
Nohardwaretestqueued/useractionneededyet. Lastverifiedconsolestate remains487
dashboardreturn/hookremoved; do notclaimfreshaccess. Bootcauseunresolved.

Continueauthorizedworkuntil2026-10-18 14:00UTC, closeoutonlyafter13:50UTC; actual
clockfirst/betweenstages. HeartbeatACTIVE. Preserveoldresults/failures andstrict
Ft49/shutdownlimits; noidenticalfailedbootretry orfunctionaldriverpatch. Enear
20GiBguard; smallC/WSLonly, projectedguardrequired. No backingmoves/deletions.

'''
for n in ['CONTINUATION.md','STATUS.md']:
 p=W/'outputs/engineering-notes'/n;old=p.read_bytes();p.write_bytes(head.replace('\n','\r\n').encode()+old)
print(json.dumps(dict(passed=True,private_files=len(private),pins=len(inputs),free=free)))
