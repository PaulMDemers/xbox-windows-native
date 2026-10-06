"""Ensure malformed or unreadable observations cannot become decoded evidence."""
import importlib.util,struct
from pathlib import Path
spec=importlib.util.spec_from_file_location('decoder',Path(__file__).with_name('decode.py'))
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
site=dict(name='test',pc=0x82400000,bytes='558bec',capture_kind=0)
fields=[0,0,site['pc'],100,0x1000]+[0]*8+[0x80010000,0x80020000,42,0,0,31]
payload=d.RECORD.pack(*fields,b'\x55\x8b\xec'+b'\0'*5,b'rundll32.exe',
                      'rundll32 test'.encode('utf-16le'),b'\0'*64,b'\0'*576,b'\0'*512)
header=b'XWNEVT01'+struct.pack('<I',d.RECORD.size)
assert d.decode(header+payload,[site])['events'][0]['command']=='rundll32 test'
for data in [b'',header+payload[:-1],b'BADHDR00'+header[8:]+payload]:
    try:d.decode(data,[site])
    except AssertionError:pass
    else:raise AssertionError('Malformed capture accepted')
fields[18]=8  # Image readable but code/command unverified: do not interpret either.
bad=d.RECORD.pack(*fields,b'\0'*8,b'rundll32.exe',b'X'*512,b'\0'*64,b'\0'*576,b'\0'*512)
e=d.decode(header+bad,[site])['events'][0]
assert not e['site_verified'] and 'command' not in e and 'image' not in e
fields[18]=1|8
unknown=d.RECORD.pack(*fields,b'\x55\x8b\xec'+b'\0'*5,b'rundll32.exe',b'X'*512,b'\0'*64,b'\0'*576,b'\0'*512)
e=d.decode(header+unknown,[site])['events'][0]
assert e['site_verified'] and e['image']=='rundll32.exe' and 'command' not in e
print('Decoder rejects partial/malformed records and preserves unknown fields.')
