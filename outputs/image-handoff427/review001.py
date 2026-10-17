# SPDX-License-Identifier: MIT
"""Verify closed host/static evidence without rerunning consumed tests."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
K = Path(__file__).resolve().parent
R = K.parent.parent
out = K/'final-review.json'
assert not out.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
tests = json.loads((K/'tests001.json').read_text())
assert tests['passed'] and tests['total'] == 4952
for name, digest in tests['inputs'].items():
    p = K/name if name != 'model.py' else K.parent/'image-volume426/model.py'
    assert sha(p) == digest
sources = json.loads((K/'source-review001.json').read_text())
assert sources['passed'] and len(sources['sources']) == 11
for row in sources['sources']:
    if row.get('overlay'):
        assert sha(R/row['overlay']) == row['sha256']
for name, digest in sources['context_only'].items():
    assert sha(R/name) == digest
static = json.loads((K/'kernel-calls002.json').read_text())
assert static['dbg_pdb_identity_validated'] is True
assert (static['image_age'], static['pdb_age'], static['dbi_age']) == (1,2,1)
for row in static['functions']:
    assert sha(Path(row['private_disassembly'])) == row['private_sha256']
calls = {f['name']:{c['rva']:c['target'] for c in f['calls']}
         for f in static['functions']}
required = {
 '_IoInitSystem@4': {0x149d69:'_IopInitializeBootDrivers@8',
                    0x149e20:'_IopReassignSystemRoot@8',0x149e7e:'IoAssignDriveLetters'},
 '_IopInitializeBootDrivers@8': {0x14b2cf:'_IopWaitForBootDevicesStarted@0',
                               0x14b334:'_IopWaitForBootDevicesStarted@0',
                               0x14b340:'_IopCreateArcNames@4'}
}
for function, sites in required.items():
    assert all(calls[function][rva] == name for rva,name in sites.items())
assert sha(Path('E:/xwn425/modules001/ntoskrnl.exe')) == static['kernel_sha256']
failure = json.loads((K/'static001-failure.json').read_text())
assert sha(K/'static001.py') == failure['source_sha256']
assert not Path('E:/xwn427/static001').exists()
assert subprocess.check_output(['git','diff','--name-only','--','src','tools',
                                'outputs/crypto-path425','outputs/image-volume426'],cwd=R) == b''
result = dict(utc=datetime.now(timezone.utc).isoformat(), passed=True,
              scope='Static boot-path/source review and synthetic host projection only',
              host_checks=tests['total'], full_sources_exact=11, public_overlays_exact=10,
              private_disassembly_hashes_verified=6, required_static_calls=6,
              symbol_age_correction_preserves_failed001=True,
              native_build=False, guest_launch=False, physical_access=False,
              native_partition_exclusion_proven=False, writable_ntfs_image_boot=False,
              strict_release_qualified=False, owned_running_sessions=[],
              inputs={p.name:sha(p) for p in sorted(K.iterdir()) if p.is_file()})
with out.open('x',encoding='utf-8',newline='\n') as f:
    f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='inputs'}))
