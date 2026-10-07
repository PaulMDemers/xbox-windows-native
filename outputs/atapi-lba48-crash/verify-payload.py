"""Compare every runtime dump payload with high-LBA cold bytes and wire writes."""
import hashlib
import json
import re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash006'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');a=read(out/'audit.json');by={v['kind']:v for v in t['events']}
assert t['status']=='dump_return_observed' and t['guest_resumed'] and not t['armed_breakpoints_remaining']
assert by['selector_entry']['flags']&0x400000 and by['selector_entry']['extended_command']==0x39
assert by['extended_decoded_lba']['lba']==289922160 and by['extended_high_byte']['al']==0x11
assert by['extended_command_call']['port']==0x1f7 and by['extended_command_call']['command_argument']&255==0x39
assert sum(len(bytes.fromhex(t['runtime_pins'][i]['resident'])) for i in by['selector_entry']['full_selector_pins'])==105
calls=[v for v in t['events'] if v['kind']=='write_payload_entry']
returns=[v for v in t['events'] if v['kind']=='write_payload_return']
assert len(calls)==len(returns)>0
payload=bytearray();volume=140436013056
for index,(en,ex) in enumerate(zip(calls,returns)):
    assert en['write_index']==ex['write_index']==index and en['index']<ex['index']
    assert en['thread']==ex['thread'] and int(ex['registers']['ESP'],16)==int(en['registers']['ESP'],16)+12 and ex['status']=='0x0'
    assert en['volume_offset']==volume+len(payload)
    p=out/'artifacts'/en['payload_file'];assert sha(p)==en['payload_sha256'] and p.stat().st_size==en['byte_count']
    payload.extend(p.read_bytes())
assert len(payload)==65536 and bytes(payload)==(out/'artifacts/after-pagefile-prefix.bin').read_bytes()
assert a['dump_write_evidence_passed'] and a['integrity_passed'] and a['alias_unchanged']
path=ws/'work/runs/nt5-atapi-lba48-crash-crash006/cpu-trace.log'
history={};commands=[];writes=[];active=False
for number,line in enumerate(path.read_text(errors='replace').splitlines(),1):
    m=re.match(r'ide_ioport_write .* @ 0x([0-9a-f]+) .*; val 0x([0-9a-f]+);',line)
    if m:
        port,value=int(m[1],16),int(m[2],16)
        history.setdefault(port,[]).append(value)
        if port==0x1f7:
            if value==0x39:
                assert all(len(history.get(p,[]))>=2 for p in range(0x1f2,0x1f6))
                high={p:history[p][-2] for p in range(0x1f2,0x1f6)};low={p:history[p][-1] for p in range(0x1f2,0x1f6)}
                lba=(high[0x1f5]<<40)|(high[0x1f4]<<32)|(high[0x1f3]<<24)|(low[0x1f5]<<16)|(low[0x1f4]<<8)|low[0x1f3]
                sectors=(high[0x1f2]<<8)|low[0x1f2];assert sectors
                commands.append(dict(line=number,lba=lba,sectors=sectors,command='0x39'));active=True
            history={}
    m=re.match(r'blk_co_pwritev .* offset (\d+) bytes (\d+) flags (\S+)',line)
    if active and m:writes.append(dict(offset=int(m[1]),bytes=int(m[2])))
absolute=a['pagefile_disk_offset'];cursor=absolute
for row in commands:
    assert row['lba']*512==cursor;cursor+=row['sectors']*512
assert cursor==absolute+65536
cursor=absolute
for row in writes:
    assert row['offset']==cursor;cursor+=row['bytes']
assert cursor==absolute+65536
r=dict(passed=True,physical_access=False,ordinary_qualified=False,recovery_qualified=False,
    high_lba_dump_write_qualified=True,total_payload_bytes=len(payload),all_payloads_exact=True,
    intended_disk_offset=absolute,low_alias_unchanged=True,actual_commands=commands,
    dump_block_writes=writes,all_post_command_writes_contained=True,
    trace_sha256=sha(out/'trace.json'),wire_sha256=sha(path),audit_sha256=sha(out/'audit.json'),
    limits='Successful observed controlled crash write and bounded write containment. Requires separate recovery boot and dump parser validation; does not qualify hardware.')
(k/'payload-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
