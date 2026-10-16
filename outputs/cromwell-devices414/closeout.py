"""Read-only final evidence closure for both consumed diagnostic attempts."""
import datetime
import hashlib
import json
from pathlib import Path

W=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def host_path(p):
    p=str(p)
    return Path(p.replace('/mnt/e/','E:/').replace('/mnt/c/','C:/'))


for number,folder in [(413,'cromwell-init413'),(414,'cromwell-devices414')]:
    k=W/'outputs'/folder
    dest=k/'final-review.json'
    assert not dest.exists()
    run=Path(f'E:/xwn{number}/runs/nt5-cromwell{number}-emu001')
    trace=json.loads((k/'emu001/trace.json').read_text(encoding='utf-8'))
    audit=json.loads((k/'emu001/audit.json').read_text(encoding='utf-8'))
    ns=json.loads((k/'emu001/namespace-summary.json').read_text(encoding='utf-8'))
    pins=json.loads((k/'emu001/frozen.json').read_text(encoding='utf-8'))
    for p,h in pins.items():
        assert sha(W/p)==h,p
    assert (run/'cleanup.json').exists() and audit['host_exit']['passed']
    assert not trace['remaining_breakpoints'] and trace['physical_mode_restored'] and not trace.get('cleanup_error')
    for row in trace['reads']:
        assert sha(Path(row['private_file']))==row['sha256']
    for p,h in audit['private_cold_files'].items():
        assert sha(host_path(p))==h,p
    for p,h in ns['private_manifest_sha256'].items():
        assert sha(host_path(p))==h,p
    assert sha(Path(f'E:/xwn{number}/cold001/namespace-review.json'))==ns['private_raw_sha256']
    source=json.loads((k/'source-review.json').read_text(encoding='utf-8'))
    for p,h in source['source_files'].items():
        assert sha(Path(f'E:/xwn{number}/source')/p)==h
    for row in json.loads((run/'input-hashes.json').read_text(encoding='utf-8-sig')):
        assert sha(Path(row['Path'])).lower()==row['Hash'].lower()
    assert ns['E_file_contents_and_names_exact'] and ns['file_counts']==[6552,6552]
    assert audit['allocation']['allocation_consistent'] and audit['eeprom_unchanged']
    assert audit['source_unchanged'] and audit['changed_bytes']==55 and not audit['strict_whole_disk_equal']
    private={str(p):sha(p) for p in Path(f'E:/xwn{number}/trace001').iterdir() if p.is_file()}
    runtime={p.name:sha(p) for p in run.iterdir() if p.is_file() and p.suffix=='.json'}
    r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_owned_processes_closed=True,
           original_trace_passed=trace['passed'],physical_access=False,ordinary_or_physical_qualification=False,
           physical_failure_reproduced=False,strict_whole_disk_equal=False,changed_disk_bytes=55,
           E_file_names_and_contents_exact=True,E_files=6552,allocation_consistent=True,eeprom_unchanged=True,
           source_seed_unchanged=True,frozen_inputs_verified=len(pins),private_trace_files=private,
           runtime_metadata_sha256=runtime,original_failures_preserved=True,public_release_ready=False)
    with dest.open('x',encoding='utf-8') as f:
        json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(dict(case=number,closed=True,original_trace_passed=trace['passed'],frozen_inputs=len(pins))))
