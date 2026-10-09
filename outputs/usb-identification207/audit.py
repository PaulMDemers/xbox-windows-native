"""Cold read-only audit of the owned diagnostic run. Host stop is never a normal boot pass."""
import hashlib,importlib,json,struct,sys,re
from pathlib import Path
sys.dont_write_bytecode=True
k=Path(__file__).resolve().parent;repo=k.parents[1]
case=sys.argv[1];assert re.fullmatch(r'emu[0-9]{3}',case);run=repo/('work/runs/usb207-'+case)
canonical=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path[:0]=[str(canonical/'outputs/fatx-mapped-eof'),str(canonical/'outputs/native-windows-paint-save'),'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages']
from coldio import ColdIO
from allocation import scan
from analyze import parse
import hivex
m=importlib.import_module('prepare-fixture');m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert (run/'cleanup.json').exists();disk=run/'hdd.qcow2';out=k/'artifacts'/case
out.mkdir(exist_ok=True);(k/case).mkdir(exist_ok=True)
f=read(k/'fixture-emu001.json');checks={};hives={}
with ColdIO(disk) as io:
    rr={v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']}
    log=rr['F'].read('xwnusb207/usb.log');(out/'usb.log').write_bytes(log)
    parsed=parse(log);(k/case/'observation.json').write_text(json.dumps(parsed,indent=2)+'\n')
    for name,digest in f['protected'].items():v,p=name.split('/',1);checks[name]=dict(expected=digest,actual=sha(rr[v].read(p)))
    checks['F/xwnusb207/usbprobe.exe']=dict(expected=f['files']['F/xwnusb207/usbprobe.exe'],actual=sha(rr['F'].read('xwnusb207/usbprobe.exe')))
    for name in ['system','software','default','sam','security','sysevent.evt','appevent.evt']:
        b=rr['F'].read('winnt/system32/config/'+name);p=out/('after-'+name);p.write_bytes(b)
        if name.endswith('.evt'):continue
        h=hivex.Hivex(str(p));todo=[h.root()];seen=set();values=0
        while todo:
            n=todo.pop();assert n not in seen;seen.add(n);h.node_name(n)
            for v in h.node_values(n):h.value_key(v);h.value_value(v);values+=1
            todo.extend(h.node_children(n))
        a,c=struct.unpack_from('<II',b,4);checksum=0
        for at in range(0,508,4):checksum^=struct.unpack_from('<I',b,at)[0]
        checksum=0xfffffffe if checksum==0xffffffff else 1 if checksum==0 else checksum
        hives[name]=dict(sha256=sha(b),keys=len(seen),values=values,sequences_equal=a==c,checksum_valid=checksum==struct.unpack_from('<I',b,508)[0])
    setup=rr['F'].read('winnt/setupapi.log');(out/'after-setupapi.log').write_bytes(setup)
scan(disk,k/case/'after/artifacts');allocation=read(k/case/'after/allocation.json')
r=dict(probe_complete=parsed['complete'],probe_failures=parsed['reported_failures'],protected=checks,protected_exact=all(c['expected']==c['actual'] for c in checks.values()),hives=hives,
 allocation_consistent=allocation['allocation_consistent'],allocation_errors=allocation['errors'],orphan_cluster_count=allocation['orphan_cluster_count'],
 setup_history_prefix=setup.startswith((k/'artifacts/emu001/before-setupapi.log').read_bytes()),normal_shutdown=False,ordinary_boot_qualified=False,physical_qualified=False,
 limits='Read-only descriptor diagnostic and cold structural audit after owned host stop. No functional XID input, normal shutdown, persistent binding or physical qualification.')
r['xid_model_ports']=[p for p in parsed['ports'] if (p.get('vendor'),p.get('product'))==(0x045e,0x0202)]
r['captured_interfaces']=[dict(hub=c['hub'],port=c['port'],**i) for c in parsed['configurations'] for i in c['configuration']['interfaces']]
r['xid_configuration_captured']=any((i['class_code'],i['subclass'],i['protocol'])==(0x58,0x42,0) for i in r['captured_interfaces'])
r['keyboard_configuration_captured']=any((i['class_code'],i['subclass'],i['protocol'])==(3,1,1) for i in r['captured_interfaces'])
r['mouse_configuration_captured']=any((i['class_code'],i['subclass'],i['protocol'])==(3,1,2) for i in r['captured_interfaces'])
r['descriptor_scope_observed']=bool(r['xid_model_ports']) and all(r[n] for n in ['probe_complete','xid_configuration_captured','keyboard_configuration_captured','mouse_configuration_captured','protected_exact'])
failed={n:v for n,v in parsed['requests'].items() if not v['success']}
r['failed_requests']=failed
# This fixture's unbound XID child has no driver key. Preserve the failure;
# permit only this exact reviewed omission, never arbitrary failed queries.
r['only_expected_driver_key_absence']=(failed=={34:dict(code=2229280,error=2,success=0,bytes=0)} and parsed['reported_failures']==1 and not parsed['issues'])
r['descriptor_scope_observed'] &= r['only_expected_driver_key_absence']
r['input_qualified']=False
r['screenshots_qualify_input']=False
(k/case/'audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['protected','hives','captured_interfaces','xid_model_ports']}))
