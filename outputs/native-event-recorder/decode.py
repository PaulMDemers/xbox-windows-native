"""Decode bounded host records; never interpret unverified/nonresident fields."""
import argparse, json, struct
from pathlib import Path

RECORD = struct.Struct('<19I8s16s512s64s576s512s')

def utf16(raw):
    end = next((i for i in range(0,len(raw),2) if raw[i:i+2] == b'\0\0'),len(raw))
    return raw[:end].decode('utf-16le')

def decode(raw, sites):
    assert len(raw) >= 12 and raw[:8] == b'XWNEVT01', 'Invalid header'
    size = struct.unpack_from('<I',raw,8)[0]
    assert size == RECORD.size and (len(raw)-12)%size == 0, 'Partial/mismatched record'
    count = (len(raw)-12)//size
    assert count < 4096, 'Capture capacity reached; completeness unknown'
    result=[]
    for index in range(count):
        v=RECORD.unpack_from(raw,12+index*size)
        seq,site,pc,tick,cr3=v[:5];valid=v[18]
        assert seq == index and site < len(sites)
        s=sites[site]
        e=dict(index=index,site=s['name'],pc=hex(pc),valid_mask=hex(valid),cr3=hex(cr3),
               code=v[19].hex(),registers=dict(zip(['eax','ecx','edx','ebx','esp','ebp','esi','edi'],map(hex,v[5:13]))))
        verified=bool(valid&1) and pc==s['pc'] and v[19].startswith(bytes.fromhex(s['bytes']))
        e['site_verified']=verified
        if not verified:
            result.append(e);continue
        if valid&2:e['tick']=tick
        if valid&4:e['stack']=[hex(n) for n in struct.unpack('<16I',v[22])]
        if valid&8:e.update(thread=hex(v[13]),owner=hex(v[14]),pid=v[15],image=v[20].split(b'\0')[0].decode('ascii',errors='replace'))
        if valid&16:e['command']=utf16(v[21])
        if valid&64:e.update(target=hex(v[16]),target_pid=v[17])
        if valid&128:e['target_command']=utf16(v[24])
        if s['capture_kind']==1 and valid&32:
            e['process_information']=[hex(n) for n in struct.unpack_from('<4I',v[23])]
            e['installer_command']=utf16(v[23][16:528])
        if valid&256:e['saved_token']=hex(struct.unpack_from('<I',v[23],568)[0])
        if valid&512:e['last_error']=struct.unpack_from('<I',v[23],572)[0]
        if s['capture_kind']==2 and valid&32:
            e['termination_arguments']=[hex(n) for n in struct.unpack_from('<2I',v[23])]
        result.append(e)
    return dict(scope=__doc__,record_size=size,record_count=count,capacity=4096,
                debugger_stops=False,guest_writes=False,ordinary_run_valid=False,
                invalid_site_records=sum(not e['site_verified'] for e in result),events=result,
                kernel_shutdown_observed=any(e['site_verified'] and e['site']=='_NtShutdownSystem@4' for e in result),
                limits='Fixed reviewed addresses; recorded code and CR3 must match the pinned fixture. Recording overhead can alter timing. No general stability qualification.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();k=Path(__file__).resolve().parent
    r=decode(a.input.read_bytes(),json.loads((k/'sites.json').read_text())['sites'])
    a.output.write_text(json.dumps(r,indent=2)+'\n')
    print({n:r[n] for n in ['record_count','invalid_site_records','kernel_shutdown_observed']})
