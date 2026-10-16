"""Mutation controls for actual captured byte classification; no device access."""
import hashlib
import json
import struct
from pathlib import Path
from compare import pe, pe_compare, xbe_compare

K=Path(__file__).resolve().parent
root=Path('E:/xwn415')
checks=[]

def check(name, predicate):
    assert predicate,name
    checks.append(name)

def rejected(a,b):
    try:
        xbe_compare(a,b)
    except (AssertionError,ValueError,struct.error):
        return True
    return False

def digest(data):
    base=struct.unpack_from('<I',data,0x104)[0]
    count,table=struct.unpack_from('<II',data,0x11c)
    for i in range(count):
        s=table-base+i*56
        off,size=struct.unpack_from('<II',data,s+12)
        data[s+36:s+56]=hashlib.sha1(struct.pack('<I',size)+data[off:off+size]).digest()

records=json.loads((K/'comparison001.json').read_text(encoding='utf-8'))['comparison']
for row in records:
    if row['classification']!='PE timestamps/checksum only':continue
    name=row['path'];a=(root/'demo'/name).read_bytes();b=(root/'fresh'/name).read_bytes()
    check(name+' actual metadata',pe_compare(a,b)['timestamp_checksum_only'])
    layout=pe(b)
    for section in layout['sections']:
        if not section['bytes']:continue
        mutated=bytearray(b);mutated[section['raw']]^=1
        check(name+' rejects '+section['name'],not pe_compare(a,mutated)['timestamp_checksum_only'])
    check(name+' rejects appended data',not pe_compare(a,b+b'\0')['timestamp_checksum_only'])
    at=b.index(b'PE\0\0')+24+16
    mutated=bytearray(b);mutated[at]^=1
    check(name+' rejects entrypoint',not pe_compare(a,mutated)['timestamp_checksum_only'])

name='Applications/XWNEBoot/default.xbe'
a=(root/'demo'/name).read_bytes();b=(root/'fresh'/name).read_bytes()
check('actual date-only XBE',xbe_compare(a,b)['only_display_date_and_valid_section_digest'])
for name,offset in [('wrapper',0x1100),('Cromwell code',0x3100),('header',0x130),('date',247105)]:
    mutated=bytearray(b);mutated[offset]^=1
    check('XBE rejects '+name,rejected(a,mutated))
    digest(mutated)
    check('XBE rejects digest-valid '+name,rejected(a,mutated))
check('XBE rejects tail',rejected(a,b+b'\0'))
out=dict(passed=True,checks=len(checks),cases=checks,physical_access=False,
         scope='Actual binary mutations; classification does not prove runtime equivalence')
with (K/'classifier-tests001.json').open('x',encoding='utf-8') as f:
    json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(dict(passed=True,checks=len(checks))))
