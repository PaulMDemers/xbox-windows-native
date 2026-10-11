"""Correct adapter clock signature, retain failed001 unchanged."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent;assert not (k/'test-worker002.py').exists()
assert not json.loads((k/'worker-test001.json').read_text())['passed']
(k/'test-worker002.c').write_text((k/'test-worker.c').read_text().replace('static uint64_t qemu_clock_get_ns','static int64_t qemu_clock_get_ns'))
s=(k/'test-worker.py').read_text().replace('worker-test001','worker-test002').replace("k/'test-worker.c'","k/'test-worker002.c'")
(k/'test-worker002.py').write_text(s)
print('002 uses primary signed clock signature; product helper unchanged')
