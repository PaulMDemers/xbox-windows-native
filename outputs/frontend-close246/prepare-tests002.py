"""Preserve incomplete001 adapters; prepare corrected test inputs only."""
import json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent
p=k/'test-frontend002.c';assert not p.exists()
p.write_text((k/'test-frontend.c').read_text().replace('#include "qemu/atomic.h"','#define qemu_build_assert(c) _Static_assert(c,"atomic width")\n#include "qemu/atomic.h"'))
p=k/'test-frontend002.py';assert not p.exists();p.write_text((k/'test-frontend.py').read_text().replace('frontend-test001','frontend-test002').replace('test-frontend.c','test-frontend002.c'))
shutil.copytree(k.parent/'gpu-lifecycle245/source',k/'source')
(k/'guard-setup-failure001.json').write_text(json.dumps(dict(passed=False,guest_launch=False,physical_access=False,checks_incomplete=True,reason='Missing primary GDB source capsule after finite host checks; no guard result written; source copied for new completed invocation'),indent=2)+'\n')
print('001 failed adapter and incomplete guard attempt retained;002 test prepared')
