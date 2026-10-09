"""Strict counted-field parser. Query errors/budgets retained, never converted to success."""
import json,sys
from pathlib import Path
BLOBS={'COMMAND_UTF16','PROCESS_IMAGE','WINDOW_CLASS','WINDOW_TEXT','DEVICE_ID','PROPERTY_BYTES','DRIVE_TARGET'}
def analyze(raw):
    assert len(raw)<=4*1024*1024
    lines=raw.decode('ascii').splitlines();assert lines and lines[0]=='XWN_DEVICE_OBSERVER 188 5 30000'
    samples=[];sample=None;complete=None
    for line in lines[1:]:
        fields=line.split(' ');label=fields[0]
        if label=='SAMPLE':
            assert sample is None or sample['complete'];assert int(fields[1])==len(samples)
            sample=dict(index=int(fields[1]),elapsed_ms=int(fields[2]),pid=int(fields[3]),complete=False,records=[],processes=[],windows=[],devices=[],volumes=[],query_failures=[])
            samples.append(sample);devices={};procs={};windows={};volumes={}
        elif label=='COMPLETE':
            assert sample is not None and sample['complete'];complete=[int(v) for v in fields[1:]]
        elif label=='NO_RESTART_OR_DEVICE_ACTION':assert fields[1:]==['0','0','0']
        else:
            assert sample is not None and not sample['complete']
            sample['records'].append(line)
            if label in BLOBS:
                assert len(fields)==5
                owner,typ,length=map(int,fields[1:4]);assert length<=4096
                data=bytes.fromhex(fields[4]);assert len(data)==length
                text=data.decode('utf-16le' if label=='COMMAND_UTF16' else 'cp1252',errors='strict').rstrip('\0') if label!='PROPERTY_BYTES' else None
                if label in ['COMMAND_UTF16','PROCESS_IMAGE']:assert owner in procs;procs[owner][label.lower()]=text
                elif label in ['WINDOW_CLASS','WINDOW_TEXT']:assert owner in windows;windows[owner][label.lower()]=text
                elif label=='DEVICE_ID':
                    devices[owner]=dict(index=owner,devinst=typ,instance=text,properties={});sample['devices'].append(devices[owner])
                elif label=='PROPERTY_BYTES':
                    assert owner in devices
                    devices[owner]['properties'][str(typ)]=dict(bytes=length,hex=data.hex())
                elif label=='DRIVE_TARGET':assert owner in volumes;volumes[owner]['target']=text
            elif label=='PROCESS':
                p=dict(pid=int(fields[1]),parent=int(fields[2]));assert p['pid'] not in procs
                procs[p['pid']]=p;sample['processes'].append(p)
            elif label in ['TOP','CHILD']:
                assert len(fields)==9
                pid,hwnd,parent,control,visible,enabled,text_ok,error=map(int,fields[1:9])
                w=dict(kind=label,pid=pid,hwnd=hwnd,parent_hwnd=parent,control_id=control,visible=visible,enabled=enabled,text_query_ok=text_ok,text_error=error)
                assert pid in procs and hwnd not in windows
                windows[hwnd]=w;sample['windows'].append(w)
            elif label=='DEVICE_STATUS':
                owner,status,problem=map(int,fields[1:]);assert owner in devices
                devices[owner].update(status=status,problem=problem)
            elif label=='DEVICE_STATUS_RESULT':
                owner,result,devinst=map(int,fields[1:]);assert owner in devices and devices[owner]['devinst']==devinst
                devices[owner]['status_query_result']=result
                if result:sample['query_failures'].append(line)
            elif label=='DEVICE_ENUM_END':
                sample['device_enum_end']=list(map(int,fields[1:]))
            elif label=='DRIVE':
                owner,kind,unused=map(int,fields[1:]);assert owner not in volumes
                volumes[owner]=dict(letter=chr(65+owner),type=kind);sample['volumes'].append(volumes[owner])
            elif label=='BYTES':
                owner=int(fields[1]);assert owner in volumes
                volumes[owner].update(available=int(fields[2],16),total=int(fields[3],16),free=int(fields[4],16))
            elif label=='CLUSTERS':
                owner,spc,bps,freec,totalc=map(int,fields[1:]);assert owner in volumes
                volumes[owner].update(sectors_per_cluster=spc,bytes_per_sector=bps,free_clusters=freec,total_clusters=totalc)
            elif label in ['INSTALL_STATE_BEGIN','INSTALL_STATE_END']:
                index,status,unused=map(int,fields[1:]);assert index==sample['index']
                sample[label.lower()]=status
            elif label=='SAMPLE_COMPLETE':
                index,elapsed,zero=map(int,fields[1:]);assert index==sample['index'] and zero==0
                sample.update(complete=True,completed_ms=elapsed)
            if label.endswith('_FAILED') or label.endswith('_UNREADABLE') or label.endswith('_UNAVAILABLE') or 'BUDGET_EXHAUSTED' in label or label=='PROPERTY_OVERSIZE':sample['query_failures'].append(line)
    assert len(samples)==5 and all(s['complete'] for s in samples)
    assert complete and complete[0]==5 and complete[1]>=120000 and complete[2]==0
    assert lines[-1]=='NO_RESTART_OR_DEVICE_ACTION 0 0 0'
    for s in samples:
        assert s['elapsed_ms']>=s['index']*30000
        assert s['devices'] and s['volumes'] and 'install_state_begin' in s and 'install_state_end' in s
        assert s.get('device_enum_end')==[len(s['devices']),259,0]
        for v in s['volumes']:
            if 'free' in v and 'free_clusters' in v:v['free_apis_agree']=v['free']==v['free_clusters']*v['sectors_per_cluster']*v['bytes_per_sector']
        s.pop('records')
    return dict(completed=True,samples=samples,elapsed_ms=complete[1],no_restart_or_device_action=True,physical_qualified=False,
                limits='Live API observations. Shared filesystem implementations are not independent allocation proof; emulated devices/partition free space do not establish physical values.')
if __name__=='__main__':
    p=Path(sys.argv[1]);dest=Path(sys.argv[2]);assert not dest.exists()
    dest.write_text(json.dumps(analyze(p.read_bytes()),indent=2)+'\n',encoding='utf-8')
