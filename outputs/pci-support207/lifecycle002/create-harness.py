"""Fresh diagnostic trial preserves Code10 control and records resource IRPs."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'lifecycle001'
names=['prepare-emulator.py','run-emulator.py','audit-emulator.py','review-pnp.py','Prepare-Emulator001.ps1','Run-Emulator001.ps1','Audit-Pnp001.ps1','Wait-Audit001.ps1']
for name in names:
    p=k/name;assert not p.exists()
    s=(old/name).read_text(encoding='utf-8').replace('lifecycle001','lifecycle002').replace('xwnpcilife1','xwnpcilife2').replace('build001','build003').replace('build-review001','build-review003').replace('4744','4754').replace('4746','4756')
    if name=='review-pnp.py':
        marker="log=audit['logs'].get('lifecycle.log','');r['log']=log"
        extra='''    try:
        data=rr['F'].read('xwnpcilife2/resource-trace.bin')
        (out/'artifacts/audit/resource-trace.bin').write_bytes(data)
        import struct
        records=[];offset=0
        while offset<len(data):
            assert len(data)-offset>=28
            magic,stage,profile,status,a,b,sequence=struct.unpack_from('<7I',data,offset)
            assert magic==0x52574e58 and a<=1024 and b<=1024 and offset+28+a+b<=len(data)
            offset+=28
            records.append(dict(stage=stage,profile=profile,status=hex(status),sequence=sequence,first_hex=data[offset:offset+a].hex(),second_hex=data[offset+a:offset+a+b].hex()))
            offset+=a+b
        save(out/'resource-trace.json',dict(sha256=__import__('hashlib').sha256(data).hexdigest(),records=records))
        r['resource_trace_records']=len(records)
    except KeyError:r['resource_trace_records']=0
'''
        s=s.replace(marker,extra+marker)
    p.write_text(s,encoding='utf-8',newline='\n')
