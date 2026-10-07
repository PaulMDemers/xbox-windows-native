"""Observe a candidate SetupAPI mapped-append lifecycle without modifying guest data."""
import datetime,hashlib,json,socket,struct,sys,time
from pathlib import Path
from atomic_json import write_json
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case=='001'
out=k/case;art=out/'artifacts';art.mkdir(parents=True,exist_ok=True)
run=ws/('work/runs/nt5-fatx-mapped-lifecycle-'+case)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={}
exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
review=json.loads((k/'sites.json').read_text());sites={v['address']:v for v in review['sites']}
fields=json.loads((k.parent/'native-windows-nt5-kernel/process-layouts.json').read_text())['_EPROCESS']['fields']
owner=json.loads((k.parent/'shutdown-popup-workload/site-review.json').read_text())['thread_owner_offset']
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,case=case,physical_access=False,ordinary_qualified=False,started_utc=utc(),source_sha256=sha(Path(__file__).read_bytes()),sites_sha256=sha((k/'sites.json').read_bytes()),atomic_json_source_sha256=sha((k/'atomic_json.py').read_bytes()),records=[],other_paths={},hit_counts={},unpaired_hit_counts={})
g=None;armed=set();active={};stopped=False;lock=acquire_monitor_lock(4594)
def save():write_json(out/'trace.json',r)
def u32(p):return struct.unpack('<I',g.read(p,4))[0]
def string(p,width=1,limit=8192):
    if not p:return b''
    assert 0x10000<=p<0x80000000
    data=bytearray()
    for offset in range(0,limit,2 if width==2 else 1):
        # Read only the actual page-resident chunk, rather than faulting the guest.
        if offset==len(data):
            n=min(64,limit-offset,4096-((p+offset)%4096));data.extend(g.read(p+offset,n))
        if data[offset:offset+width]==bytes(width):return bytes(data[:offset])
    raise ValueError('Unterminated bounded string')
def store(row,label,data):
    digest=sha(data);p=art/('buffer-'+digest+'.bin')
    if not p.exists():p.write_bytes(data)
    row[label]=dict(file=p.name,sha256=digest,bytes=len(data))
def who(thread):
    process=u32(thread+owner)
    return dict(thread=hex(thread),process=hex(process),pid=u32(process+fields['UniqueProcessId']['offset']),image=g.read(process+fields['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='replace'))
try:
    command(4594,'stop');stopped=True;g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
    for address in sites:g.bp(address);armed.add(address)
    r['status']='armed_before_launch';save();(out/'trace-armed.signal').touch(exist_ok=False)
    deadline=time.monotonic()+600
    for hit in range(20000):
        g.send('c');stopped=False
        while True:
            g.s.settimeout(2)
            try:reply=g.recv();break
            except TimeoutError:
                launch=out/'launch.json';returned=launch.exists() and any(v.get('dashboard_return') for v in json.loads(launch.read_text()).get('cycles',[]))
                if returned or time.monotonic()>=deadline:
                    g.s.settimeout(5);reply=g.interrupt();r['status']='dashboard_observed' if returned else 'capture_deadline';break
        stopped=True;g.s.settimeout(5)
        if r['status'] in ['dashboard_observed','capture_deadline']:break
        regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
        address=regs['EIP'];assert address in sites,(reply,regs)
        site=sites[address];name=site['name'];assert g.read(address,len(bytes.fromhex(site['bytes']))).hex()==site['bytes']
        base=review['base'];assert g.read(base,2)==b'MZ';pe=base+u32(base+60)
        assert g.read(pe,4)==b'PE\0\0' and u32(pe+8)==review['timestamp']
        r['hit_counts'][name]=r['hit_counts'].get(name,0)+1
        thread=u32(0xffdff124)
        if name=='outer_entry':
            args=struct.unpack('<4I',g.read(regs['ESP']+4,16))
            path=string(args[0],2,2048).decode('utf-16le')
            if path.lower().endswith('setupapi.log'):
                assert thread not in active,'Nested target logger call needs explicit pairing'
                row=dict(index=len(r['records']),**who(thread),path=path,outer_frame=hex(regs['ESP']-4),flag=args[3],started_utc=utc(),events=[])
                for label,p in [('first_string',args[1]),('second_string',args[2])]:
                    try:store(row,label,string(p))
                    except Exception as exc:row[label+'_error']=repr(exc)
                r['records'].append(row);active[thread]=row
            else:r['other_paths'][path]=r['other_paths'].get(path,0)+1
        elif thread in active:
            row=active[thread];frame=regs['EBP'];outer=int(row['outer_frame'],16)
            e=dict(site=name,utc=utc(),frame=hex(frame))
            if name in ['helper_return','seek_call','seek_return','cleanup_call','outer_return']:
                assert frame==outer
            elif name in ['mapping_call','mapping_return','view_call','view_return']:
                if name=='mapping_call':row['helper_frame']=hex(frame)
                assert hex(frame)==row['helper_frame']
            else:assert hex(frame)==row['cleanup_frame']
            if name=='mapping_call':e['arguments']=list(struct.unpack('<6I',g.read(regs['ESP'],24)))
            elif name=='view_call':e['arguments']=list(struct.unpack('<5I',g.read(regs['ESP'],20)))
            elif name=='helper_return':
                e.update(status=regs['EAX'],view=hex(u32(frame-60)),old_size=u32(frame-84),file_handle=hex(u32(frame-32)),mapping_handle=hex(u32(frame-40)))
                row.update(view=e['view'],old_size=e['old_size'],helper_status=e['status'])
            elif name=='seek_call':
                args=list(struct.unpack('<4I',g.read(regs['ESP'],16)));e['arguments']=args
                old=row['old_size'];end=args[1];view=int(row['view'],16);e.update(old_size=old,new_size=end)
                if row['helper_status']==0 and args[2:]==[0,0] and 0<=end-old<=8192:
                    try:
                        data=b''.join(g.read(view+old+i,min(512,end-old-i)) for i in range(0,end-old,512))
                        store(e,'mapped_append',data)
                        if old<=270225 and end>=270445:
                            store(e,'target_warning',data[270225-old:270445-old])
                    except Exception as exc:e['mapped_read_error']=repr(exc)
            elif name=='cleanup_call':
                e['arguments']=list(struct.unpack('<5I',g.read(regs['ESP'],20)));row['cleanup_frame']=hex(regs['ESP']-8)
            elif name.endswith('_call'):e['argument']=u32(regs['ESP'])
            else:e['return_value']=regs['EAX']
            row['events'].append(e)
            if name=='outer_return':row.update(ended_utc=utc(),return_status=regs['EAX']);active.pop(thread)
        else:r['unpaired_hit_counts'][name]=r['unpaired_hit_counts'].get(name,0)+1
        save()
        g.bp(address,False);armed.remove(address);assert g.ask('s').startswith(('T','S'));g.bp(address);armed.add(address)
        if time.monotonic()>=deadline:r['status']='capture_deadline';break
    else:r['status']='hit_limit'
except Exception as exc:r.update(status='capture_incomplete',error=repr(exc))
finally:
    if g:
        try:
            if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
            for address in list(armed):g.bp(address,False);armed.remove(address)
            g.send('c');r['guest_resumed']=True
        except Exception as exc:r['resume_error']=repr(exc)
        g.s.close()
    elif stopped:command(4594,'cont')
    r.update(ended_utc=utc(),active_records_remaining=[v['index'] for v in active.values()],armed_breakpoints_remaining=list(armed))
    try:save()
    finally:lock.close()
print(json.dumps({n:r[n] for n in ['status','error','hit_counts','guest_resumed'] if n in r}))
