"""Close native attempts with calibrated outcomes and immutable evidence hashes."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for case in ('native001','native002'):
    out=k/case;dest=out/'closure.json';assert not dest.exists()
    run=read(out/'run.json');audit=read(out/'audit.json');telemetry=read(out/'telemetry.json')
    assert run['closed'] and run['source_unchanged'] and audit['integrity_passed'] and telemetry['telemetry_passed'] and telemetry['binding_valid']
    r=dict(closed=True,never_relaunch_this_disk=True,physical_access=False,hardware_ready=False,
           normal_shutdown_qualified=False,persistence_qualified=False,whole_boot_passed=False,
           pins={p.name:sha(p) for p in (out/'run.json',out/'fixture.json',out/'audit.json',out/'telemetry.json')})
    if case=='native002':
        records=(out/'artifacts/before/directories.bin').read_bytes();assert len(records)%80==0
        names=[]
        for offset in range(0,len(records),80):
            rec=records[offset:offset+80]
            if struct.unpack_from('<I',rec)[0]==2:
                entry=rec[16:];names.append(entry[2:2+entry[0]].decode('cp1252').lower())
        assert 'cycle-00.log' not in names and 'cycle.exe' in names
        log=audit['logs']['cycle-00.log'];assert 'telemetry_valid=1\r\n' in log and 'restart_blocked_pending_install=258\r\n' in log and 'normal_restart_request' not in log
        delta=(out/'setupapi-delta.txt').read_text();assert 'DEV_01B0' in delta and 'DEV_01B4' not in delta
        prior=read(k/'native001/audit.json')
        assert audit['logs']['install.log']==prior['logs']['install.log'] and audit['logs']['probe-00.log']==prior['logs']['probe-00.log']
        assert audit['pci_targets']==prior['pci_targets']
        r.update(outcome='Persisted binding and fresh telemetry PASS; normal restart HELD by genuine pending installation.',fresh_cycle_log=True,
                 source_directory_sha256=sha(out/'artifacts/before/directories.bin'),binding_unchanged=True,old_logs_unchanged=True,
                 no_reinstallation_observed=True,no_smbus_install_in_new_setupapi=True,pending_install_state=258,
                 unresolved_setupapi_device='PCI\\VEN_10DE&DEV_01B0&SUBSYS_00000000&REV_B1\\2&ebb567f&0&28',
                 limits='One cold relaunch from installed host-stopped state, not two normal-shutdown cycles. Global pending state does not identify every pending device. No wizard cancellation.')
    else:r.update(outcome='Actual installation and live telemetry PASS; host-stopped diagnostic only.')
    dest.write_text(json.dumps(r,indent=2)+'\n')
print('Both native attempts closed; no ordinary shutdown/persistence/hardware promotion')
