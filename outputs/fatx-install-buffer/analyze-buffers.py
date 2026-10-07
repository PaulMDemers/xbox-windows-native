"""Compare immutable source snapshots, syscall returns and cold warning bytes."""
import hashlib,importlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002','003'];out=k/case
dest=out/'buffer-analysis.json';assert not dest.exists()
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text())
t=read(out/'trace.json');sites=read(k/'sites.json');f=read(k/('fixture-'+case+'.json'))
source=out/'trace-source.py' if (out/'trace-source.py').exists() else k/'trace.py'
assert sha(source.read_bytes())==t['source_sha256'] and sha((k/'sites.json').read_bytes())==t['sites_sha256']
assert t['guest_resumed'] and not t['armed_breakpoints_remaining']
run=ws/('work/runs/nt5-fatx-install-buffer-'+case);assert (run/'cleanup.json').exists()
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(ws/'outputs/fatx-mapped-eof'));from coldio import ColdIO
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];assert m.filehash(base)==f['fixture_sha256']
module_checks=[]
for disk in [base,run/'hdd.qcow2']:
 with ColdIO(disk) as io:data=m.Writer(io,m.fatx.open_partition(io,disk,'F')).read('winnt/system32/ntdll.dll')
 module_checks.append(dict(disk=disk.name,sha256=sha(data),matched=sha(data)==sites['ntdll_sha256']))
assert all(v['matched'] for v in module_checks)
al=read(out/'alignment.json');cold=(out/'artifacts/after-setupapi.log').read_bytes();assert sha(cold)==al['after_sha256']
marker=b'An unsigned or incorrectly signed driver (c:\\xwninf99\\xwnvideo.inf) was installed'
expected=cold[al['desired_offset']:al['desired_offset']+al['expected_warning_bytes']]
returns={e['entry_index']:e for e in t['events'] if e['function']=='NtWriteFile_return'}
buffers=0;warnings=[];errors=[]
for e in t['events']:
 if e['function']!='NtWriteFile':continue
 if 'buffer_error' in e:errors.append(dict(index=e['index'],error=e['buffer_error']))
 if not e.get('buffer_captured'):continue
 data=(out/'artifacts'/e['buffer_file']).read_bytes();assert sha(data)==e['buffer_sha256'] and len(data)==e['length'];buffers+=1
 if marker not in data:continue
 ret=returns.get(e['index']);positions=[];at=0
 while (at:=data.find(marker,at))>=0:positions.append(at);at+=len(marker)
 row=dict(entry_index=e['index'],pid=e['pid'],image=e['image'],handle=e['handle'],buffer=e['buffer'],length=e['length'],byteoffset=e.get('byteoffset'),source_sha256=e['buffer_sha256'],warning_positions_in_request=positions,request_is_exact_warning=data==expected,first111_exact=data[:111]==expected[:111],return_event_index=ret['index'] if ret else None,eax=ret.get('eax') if ret else None,iosb_status=ret.get('iosb_status') if ret else None,iosb_information=ret.get('iosb_information') if ret else None)
 row['full_synchronous_success']=bool(ret and ret.get('eax')=='0x0' and ret.get('iosb_status')==0 and ret.get('iosb_information')==e['length'])
 row['explicit_offset_cold_match']=bool(e.get('byteoffset') is not None and e['byteoffset']>=0 and cold[e['byteoffset']:e['byteoffset']+e['length']]==data)
 warnings.append(row)
a=read(out/'audit.json');v=read(out/'allocation.json');p=read(out/'package-audit.json')
r=dict(scope=__doc__,case=case,debugger_observation=True,physical_qualified=False,ordinary_qualified=False,trace_status=t['status'],ntdll_checks=module_checks,captured_buffers_verified=buffers,buffer_read_errors=errors,warning_requests=warnings,target_coverage=bool(warnings),all_warning_requests_full_success=bool(warnings) and all(v['full_synchronous_success'] for v in warnings),cold_target_intact=al['target_warning_intact'],actual_target_offset=al['actual_after_copy_offsets'],cold_checks_passed=all([a['diagnostic_checks_passed'],p['installation_checks_passed'],v['allocation_consistent'],not v['errors'],not v['orphan_cluster_count'],al['actual_alignment_verified'],al['prefix_preserved'],al['target_warning_intact']]),trace_sha256=sha((out/'trace.json').read_bytes()),evidence_sha256={name:sha((out/name).read_bytes()) for name in ['audit.json','allocation.json','package-audit.json','alignment.json','collection.json','launch.json']},limits='Debugger perturbs timing. Readable request bytes and synchronous success do not identify cache or DMA contents. Null or negative offset is not an explicit file position. Identical warning text occurs several times; do not assign a request to a specific cold occurrence without independent offset evidence. Flush/close events are entry observations, not success results.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
