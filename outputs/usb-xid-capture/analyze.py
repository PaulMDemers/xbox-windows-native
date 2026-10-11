"""Strict native XID log decoding; distinguish raw reports from mapped input."""
import hashlib,importlib.util,json,struct,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('usb207_parser',Path(__file__).resolve().parent.parent/'usb-identification207/analyze.py')
usb207=importlib.util.module_from_spec(spec);spec.loader.exec_module(usb207)
configuration=usb207.configuration

def parse(data):
    if len(data)>1024*1024:raise ValueError('log size')
    text=data.decode('ascii');lines=text.splitlines()
    if not text.endswith('\r\n') or not lines or lines[0] not in ['XWN_XID_CAPTURE 1 emulator','XWN_XID_CAPTURE 1 physical']:raise ValueError('framing')
    if not lines[-1].startswith('CAPTURE_END '):raise ValueError('incomplete capture')
    result=dict(mode=lines[0].split()[-1],sha256=hashlib.sha256(data).hexdigest(),reports=[],issues=[],endpoints=[],transport_events=[])
    seen=set(); ready=False
    for line in lines[1:-1]:
        parts=line.split(' ',4);tag=parts[0]
        if tag in ['DEVICE','CONFIG','XID','INPUT']:
            if len(parts)!=5:raise ValueError('blob framing')
            ms,status,size=map(int,parts[1:4]);raw=bytes.fromhex(parts[4])
            if ms<0 or size!=len(raw) or size>4096:raise ValueError('blob length')
            if tag!='INPUT':
                if tag in seen:raise ValueError('duplicate descriptor')
                seen.add(tag)
            if status:result['issues'].append(dict(tag=tag,status=status))
            if tag=='DEVICE':
                if len(raw)!=18 or raw[:2]!=b'\x12\x01':raise ValueError('device descriptor')
                result['device']=dict(vendor=struct.unpack_from('<H',raw,8)[0],product=struct.unpack_from('<H',raw,10)[0],revision=struct.unpack_from('<H',raw,12)[0],raw=raw.hex())
            elif tag=='CONFIG':result['configuration']=configuration(raw)
            elif tag=='XID':
                result['xid_raw']=raw.hex()
                if not status:
                    if len(raw)!=16 or raw[:2]!=b'\x10\x42':raise ValueError('XID descriptor')
                    result['xid']=dict(version=struct.unpack_from('<H',raw,2)[0],type=raw[4],subtype=raw[5],input_size=raw[6],output_size=raw[7],alternate_ids=list(struct.unpack_from('<4H',raw,8)))
            else:
                if not ready or size>32 or len(result['reports'])>=2250:raise ValueError('input state/length')
                if result['reports'] and ms<result['reports'][-1]['ms']:raise ValueError('time order')
                row=dict(ms=ms,status=status,raw=raw.hex())
                if status==0 and len(raw)==20 and raw[:2]==b'\0\x14':
                    row['decoded']=dict(buttons=struct.unpack_from('<H',raw,2)[0],analog=dict(zip(['a','b','x','y','black','white','left_trigger','right_trigger'],raw[4:12])),sticks=list(struct.unpack_from('<4h',raw,12)))
                else:result['issues'].append(dict(tag='INPUT',issue='nonstandard or failed report',ms=ms))
                result['reports'].append(row)
        elif tag=='ENDPOINT':
            if len(parts)!=5:raise ValueError('endpoint framing')
            result['endpoints'].append(list(map(int,parts[1:])))
        elif tag=='READY':
            if len(parts)!=5 or ready or not {'DEVICE','CONFIG','XID'}<=seen or 'xid' not in result:raise ValueError('ready state')
            result['ready']=list(map(int,parts[1:]));ready=True
            d=result['device'];ids=(d['vendor'],d['product'])
            if ids!=(65535,65535) and not(result['mode']=='emulator' and ids==(0x045e,0x0202)):raise ValueError('device allowlist')
            interfaces=result['configuration']['interfaces']
            if len(interfaces)!=1:raise ValueError('interface count')
            interface=interfaces[0]
            if (interface['class_code'],interface['subclass'],interface['protocol'],interface['alternate'])!=(0x58,0x42,0,0):raise ValueError('interface profile')
            eps=[[ep[n] for n in ['address','attributes','max_packet','interval']] for ep in interface['endpoints']]
            if eps!=result['endpoints'] or len(eps)!=2 or any(e[1:]!=[3,32,4] for e in eps):raise ValueError('endpoint mismatch')
            if sorted(e[0] for e in eps) not in [[2,0x81],[2,0x82]] or result['ready'][3]!=max(e[0] for e in eps):raise ValueError('endpoint address')
        elif tag in ['CAPTURE_DEADLINE','CANCEL','DRAINED']:
            result['transport_events'].append(dict(tag=tag,values=list(map(int,parts[1:]))))
        elif tag in ['READ_TIMEOUT','SUBMIT_FAILED','NO_READY_DEVICE','GUARD_UNDRAINED']:
            result['issues'].append(dict(tag=tag,values=list(map(int,parts[1:]))))
        else:raise ValueError('unknown record '+tag)
    end=lines[-1].split()
    if len(end)!=3:raise ValueError('end framing')
    count,failures=map(int,end[1:])
    if count!=len(result['reports']) or failures<0:raise ValueError('end accounting')
    tags=[e['tag'] for e in result['transport_events']]
    if tags not in [[],['CAPTURE_DEADLINE','CANCEL','DRAINED']]:raise ValueError('cancel sequence')
    result.update(complete=True,reported_failures=failures,distinct_reports=len({r['raw'] for r in result['reports'] if not r['status']}),native_capture_passed=ready and count>0 and failures==0 and not result['issues'],windows_input_qualified=False,physical_input_mapping_qualified=False)
    return result

if __name__=='__main__':
    source,dest=map(Path,sys.argv[1:]);result=parse(source.read_bytes())
    with dest.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps({n:result[n] for n in ['complete','mode','reported_failures','distinct_reports','native_capture_passed']}))
