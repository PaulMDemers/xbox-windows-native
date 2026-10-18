# SPDX-License-Identifier: MIT
"""One-shot host transformation/negative test. No CPU or kernel model execution."""
import hashlib,json,shutil,struct,traceback
from datetime import datetime,timezone
from pathlib import Path
import candidate
from candidate import layout
K=Path(__file__).resolve().parent;OUT=K/'host001.json';R=Path('C:/xwn516/host001')
assert not OUT.exists() and not R.exists();assert shutil.disk_usage('C:/').free-32*1024**2>=20*1024**3
R.mkdir(parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
paths=[K/'candidate.py',K/'host001.py',K.parent/'data-layout515/elf32.py',K.parent/'data-layout515/layout.py',K.parent/'data-layout515/final-review.json',Path('C:/xwn510/build001/default.xbe'),Path('C:/xwn510/build001/xbeboot.o')]
pins={str(p):sha(p.read_bytes()) for p in paths}
r=dict(passed=False,closed=False,started_utc=datetime.now(timezone.utc).isoformat(),inputs=pins,scope='actual Python byte transformation and validator; no instruction/CPU/API execution',physical_access=False)
try:
    old=paths[-2].read_bytes();obj=paths[-1].read_bytes()
    assert sha(old)=='fe9d78fa2f07d4804d0a82a66188e45293ac45a212575613369815c766c7f83f'
    expected,ledger,t,d,offsets=candidate.prepare(old,obj);candidate.validate(expected,old,ledger,t,d,offsets)
    assert expected.count(candidate.NEW_NAME)==5 and expected.count(candidate.OLD_NAME)==1
    assert expected[layout.OLD-layout.BASE:]==old[layout.OLD-layout.BASE:]
    failures=[]
    def reject(b,label):
        try:candidate.validate(b,old,ledger,t,d,offsets)
        except ValueError:failures.append(label);return
        raise AssertionError('accepted '+label)
    def repaired(b):b[0x36c:0x380]=layout.digest(b);return bytes(b)
    for x in ledger:
        if x['symbol_section']!=d:continue
        off=x['address']-layout.BASE if x['section']==t else layout.NEW-layout.BASE+x['offset']
        b=bytearray(expected);struct.pack_into('<I',b,off,x['value']);reject(repaired(b),'old-data-reference-'+hex(off))
    for off in offsets:
        b=bytearray(expected);b[off:off+len(candidate.OLD_NAME)]=candidate.OLD_NAME;reject(repaired(b),'stale-path-'+hex(off))
    b=bytearray(expected.replace(candidate.OLD_NAME,candidate.NEW_NAME));reject(repaired(b),'changed-retained-tail-path')
    positions=set(range(0,0x36c))|set(range(0x380,4096))|set(range(0x1000,0x102c))|set(range(0x1100,0x1107))
    positions.update(range(layout.CODE-layout.BASE,layout.OLD+layout.SIZE-layout.BASE))
    for off in offsets:positions.update(range(off,off+len(candidate.NEW_NAME)))
    for off in sorted(positions):
        b=bytearray(expected);b[off]^=1;reject(repaired(b),'byte-'+hex(off))
    reject(expected[:-1],'short');reject(expected+b'\0','long')
    # Full truncation to the relinked raw extent would drop the old tail.
    reject(expected[:layout.NEW+layout.SIZE-layout.BASE],'shrunk-to-linked-length')
    for p in paths:assert sha(p.read_bytes())==pins[str(p)]
    r.update(passed=True,expected_sha256=sha(expected),bytes=len(expected),new_data=[layout.NEW,layout.NEW+layout.SIZE],namespace_offsets=offsets,negative_controls=len(failures),old_tail_unchanged=True,synthetic_image_saved=False)
    (R/'negative-labels.json').write_bytes((json.dumps(failures,indent=2)+'\n').encode())
except Exception:r['failure']=traceback.format_exc()
finally:
    r.update(closed=True,finished_utc=datetime.now(timezone.utc).isoformat(),private_files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in R.iterdir() if p.is_file()})
    OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({k:r[k] for k in ['passed','negative_controls','failure'] if k in r}))
if not r['passed']:raise SystemExit(1)
