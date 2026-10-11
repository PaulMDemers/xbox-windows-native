"""Strict parser for the NT5 read-only probe. Raw bytes retained, no inferred ID repair."""
import hashlib,json,struct,sys
from pathlib import Path

def configuration(data):
    if len(data)<9 or data[:2]!=b'\x09\x02':raise ValueError('configuration header')
    total=struct.unpack_from('<H',data,2)[0]
    if total!=len(data):raise ValueError('configuration total length')
    result={'raw':data.hex(),'value':data[5],'interfaces':[]};at=0;current=None
    while at<total:
        if at+2>total:raise ValueError('descriptor header truncated')
        size,kind=data[at:at+2]
        if size<2 or at+size>total:raise ValueError('descriptor length')
        d=data[at:at+size]
        if kind==4:
            if size!=9:raise ValueError('interface length')
            current=dict(number=d[2],alternate=d[3],expected_endpoints=d[4],class_code=d[5],subclass=d[6],protocol=d[7],endpoints=[])
            result['interfaces'].append(current)
        elif kind==5:
            if size<7 or current is None:raise ValueError('endpoint without interface/short')
            current['endpoints'].append(dict(address=d[2],attributes=d[3],max_packet=struct.unpack_from('<H',d,4)[0],interval=d[6]))
        at+=size
    if len({i['number'] for i in result['interfaces']})!=data[4]:raise ValueError('interface count')
    for i in result['interfaces']:
        if len(i['endpoints'])!=i['expected_endpoints']:raise ValueError('endpoint count')
        i['classification']='xid_interface' if (i['class_code'],i['subclass'],i['protocol'])==(0x58,0x42,0) else 'hid_interface' if i['class_code']==3 else 'other'
    return result

def parse(data):
    text=data.decode('ascii');lines=text.splitlines()
    if not text.endswith('\r\n') or not lines or not lines[0].startswith('USB_PROBE_BEGIN 1 '):raise ValueError('missing start/framing')
    if not lines[-1].startswith('USB_PROBE_END '):raise ValueError('incomplete probe')
    rows=[];ports=[];configs=[];devices={};requests={};issues=[];hubs=[]
    blob_labels={'DEVICE_ID','PROPERTY','HUB_PATH','HUB_RAW','PORT_RAW','CONFIG_HEADER_RAW','CONFIG_RAW','DRIVERKEY_RAW','CHILD_HUB_RAW'}
    for line in lines:
        parts=line.split(' ',4);label=parts[0]
        if len(parts)<4:raise ValueError('short record')
        a,b,c=map(int,parts[1:4]);row=dict(label=label,a=a,b=b,c=c)
        if label in blob_labels:
            raw=bytes.fromhex(parts[4] if len(parts)>4 else '')
            if len(raw)!=c or c>8192:raise ValueError('blob length')
            row['hex']=raw.hex()
            if label=='DEVICE_ID':devices[a]={'instance':raw.decode('ascii'),'properties':{}}
            elif label=='PROPERTY':devices[a]['properties'][b]=raw.hex()
            elif label=='HUB_RAW':hubs.append(row)
            elif label=='PORT_RAW':
                if len(raw)<35:raise ValueError('short connection information')
                index=struct.unpack_from('<I',raw)[0];status=struct.unpack_from('<I',raw,31)[0]
                if index!=b:raise ValueError('port index changed')
                port=dict(hub=a,port=b,status=status,raw=raw.hex(),configured=raw[22],low_speed=raw[23],is_hub=raw[24],address=struct.unpack_from('<H',raw,25)[0],open_pipes=struct.unpack_from('<I',raw,27)[0])
                if status==1:
                    if raw[4:6]!=b'\x12\x01':raise ValueError('bad device descriptor')
                    port.update(vendor=struct.unpack_from('<H',raw,12)[0],product=struct.unpack_from('<H',raw,14)[0],revision=struct.unpack_from('<H',raw,16)[0],device_class=raw[8],configurations=raw[21])
                ports.append(port)
            elif label=='CONFIG_RAW':
                if len(raw)<12 or struct.unpack_from('<I',raw)[0]!=b:raise ValueError('descriptor request header')
                configs.append(dict(hub=a,port=b,configuration=configuration(raw[12:])))
        elif label=='DEVICE_PARENT':devices[a]['parent_query']=b;devices[a]['parent']=c
        elif label=='DEVICE_STATUS':devices[a]['status']=b;devices[a]['problem']=c
        elif label=='IOCTL':
            if a in requests:raise ValueError('duplicate request')
            requests[a]={'code':b,'error':c}
        elif label=='IOCTL_RESULT':requests[a].update(success=b,bytes=c)
        if any(word in label for word in ['ERROR','BUDGET','CANCEL','INVALID']):issues.append(row)
        rows.append(row)
    end=list(map(int,lines[-1].split()[1:]));assert len(end)==3
    if sorted(requests)!=list(range(1,end[0]+1)) or any('success' not in v for v in requests.values()):raise ValueError('request sequence')
    if sum(not r['success'] for r in requests.values())>end[1]:raise ValueError('failure accounting')
    return dict(complete=True,sha256=hashlib.sha256(data).hexdigest(),elapsed_ms=end[2],reported_failures=end[1],devices=devices,hubs=hubs,ports=ports,configurations=configs,requests=requests,issues=issues,
                physical_qualified=False,input_qualified=False,limits='Descriptor/topology evidence only. No XID vendor request or input report is issued; the hub API forces standard GET_DESCRIPTOR.')

if __name__=='__main__':
    source,dest=map(Path,sys.argv[1:]);assert not dest.exists()
    r=parse(source.read_bytes());dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['complete','elapsed_ms','reported_failures']}))
