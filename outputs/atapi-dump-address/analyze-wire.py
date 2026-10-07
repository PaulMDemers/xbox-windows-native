"""Compare pinned kernel dump input with captured ATA register/address evidence."""
import hashlib,json,re,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash005';run=ws/'work/runs/nt5-atapi-dump-address-crash005'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');a=read(out/'audit.json');by={v['kind']:v for v in t['events']};first=by['first_write_call'];last=by['dump_return']
assert first['volume_offset']==140436013056 and first['byte_count']==4096
prefix=bytes.fromhex(first['source_prefix']);assert prefix[:8]==b'PAGEDUMP' and list(struct.unpack_from('<5I',prefix,40))==[0xe058d103,0x44554d50,0x103,0x10000,1]
assert by['first_write_return']['status']=='0x0' and last['returned_boolean']==1 and last['final_status']=='0x0'
regs={};commands=[];path=run/'cpu-trace.log'
for number,line in enumerate(path.read_text(errors='replace').splitlines(),1):
    match=re.match(r'ide_ioport_write .* @ 0x([0-9a-f]+) .*; val 0x([0-9a-f]+);',line)
    if match:
        port,val=int(match[1],16),int(match[2],16);regs[port]=val
        if port==0x1f7 and val==0xc5:
            lba=((regs[0x1f6]&15)<<24)|(regs[0x1f5]<<16)|(regs[0x1f4]<<8)|regs[0x1f3]
            if a['lba28_alias_offset']<=lba*512<a['lba28_alias_offset']+65536:commands.append(dict(line=number,command=hex(val),registers={hex(p):hex(regs[p]) for p in range(0x1f2,0x1f8)},lba28=lba,disk_offset=lba*512,sectors=regs[0x1f2] or 256))
assert commands and commands[0]['disk_offset']==a['lba28_alias_offset'] and sum(v['sectors']*512 for v in commands)==65536
alias=(out/'artifacts/after-alias.bin').read_bytes();assert alias[:64]==prefix and not a['alias_unchanged'] and not a['dump_header_matches']
r=dict(scope=__doc__,physical_access=False,kernel_volume_offset=first['volume_offset'],kernel_header_exact=True,writer=first['writer'],writer_pin=t['runtime_pins'][first['writer_pin']],first_write_status='0x0',dump_return=True,final_status='0x0',actual_wire_commands=commands,intended_disk_offset=a['pagefile_disk_offset'],alias_offset=a['lba28_alias_offset'],lost_address_bit_bytes=1<<37,wire_trace_sha256=sha(path),source_header_matches_cold_alias=True,dump_qualified=False,recovery_allowed=False,limits='Correct upper dump offset and header, successful returns, but low ATA address and wrong cold destination. The exact lower mask and bypass are separately proven by address-verification.json. This unchanged diagnostic still fails dump qualification.')
(k/'wire-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
