"""Cold repeated append audit with independent per-byte oracle and normal shutdown."""
import contextlib,importlib,json,re,struct,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'fatx-mapped-eof'))
from coldio import ColdIO
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
case=sys.argv[1];assert case in ['001','002']
out=k/case;art=out/'artifacts';art.mkdir(parents=True,exist_ok=True)
assert not (out/'audit.json').exists(), 'Preserve completed audit'
fixture=json.loads((k/('fixture-'+case+'.json')).read_text())
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/fixture.get('fixture_name','fatx0098-soak-'+case+'.qcow2')
run=ws/('work/runs/nt5-fatx-draw-append-'+case)
assert (run/'cleanup.json').exists() and m.filehash(base)==fixture['fixture_sha256']
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
r=dict(scope=__doc__,case=case,physical_access=False,payloads=[],hives=[],new_events={})
with contextlib.ExitStack() as stack:
    readers=[]
    for disk in [base,run/'hdd.qcow2']:
        io=stack.enter_context(ColdIO(disk));readers.append({v:m.Writer(io,m.fatx.open_partition(io,disk,v)) for v in ['E','F']})
    before,after=readers
    for row in fixture['payloads']+fixture['preserved_payloads']:
        if row['path']=='winnt/system32/xwn-video-trace.bin':continue
        actual=m.sha(after['F'].read(row['path']))
        r['payloads'].append(dict(path=row['path'],sha256=actual,matched=actual==row['sha256']))
    r['runtime_binary_checks']=[]
    identities=json.loads((k.parent/'shutdown-popup-workload/site-review.json').read_text())
    identities['binaries'].update(json.loads((k.parent/'shutdown-popup-workload/caller-review.json').read_text())['binaries'])
    pairs=[('winnt/system32/'+n,v['sha256']) for n,v in identities['binaries'].items()]+[('winnt/system32/ntoskrnl.exe',identities['kernel_sha256'])]
    for path,sha in pairs:
        first=m.sha(before['F'].read(path));last=m.sha(after['F'].read(path))
        r['runtime_binary_checks'].append(dict(path=path,before_sha256=first,after_sha256=last,matched=first==last==sha))
    r['baseline_checks']={}
    for letter,path in [('F','winnt/system32/drivers/xwnfatx.sys'),('E','Applications/XWNFBoot/loader/halxboxnt5.dll'),('E','Applications/XWNFBoot/default.xbe'),('E','Applications/XWNFBoot/freeldr.sys')]:
        r['baseline_checks'][letter+'/'+path]=before[letter].read(path)==after[letter].read(path)
    r['fatx_exact']=m.sha(after['F'].read('winnt/system32/drivers/xwnfatx.sys'))==fixture['fatx_sha256']
    r['storage_workload_not_run']=True
    for path in ['xwns98/result.log','xwns98/matched.log']:
        for reader in [before,after]:
            try:reader['F'].read(path)
            except KeyError:pass
            else:r['storage_workload_not_run']=False
    for name in ['system','software','default','sam','security']:
        data=after['F'].read('winnt/system32/config/'+name);path=art/('after-'+name);path.write_bytes(data)
        h=hivex.Hivex(str(path));todo=[h.root()];seen=set();values=0
        while todo:
            node=todo.pop();assert node not in seen;seen.add(node)
            for v in h.node_values(node):h.value_key(v);h.value_value(v);values+=1
            todo.extend(h.node_children(node))
        r['hives'].append(dict(name=name,sha256=m.sha(data),keys=len(seen),values=values,parsed=True))
    known=[]
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        decoded=[]
        for prefix,readers in [('before',before),('after',after)]:
            path=art/(prefix+'-'+name);path.write_bytes(readers['F'].read('winnt/system32/config/'+name))
            dest=out/(prefix+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(path),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
            decoded.append(json.loads(dest.read_text())['records'])
        a,b=decoded;by={v['record']:v for v in b};assert all(by.get(v['record'])==v for v in a)
        known.extend(a);boundary=max((v['record'] for v in a),default=0)
        r['new_events'][label]=[v for v in b if v['record']>boundary]
    try:log=after['F'].read('xwnda01/probe.log').decode('ascii')
    except KeyError:log=''
    r['log']=log
    def fnv(data):
        h=2166136261
        for b in data:h=((h^b)*16777619)&0xffffffff
        return h
    mode=1 if case=='002' else 0
    expected=['ATTEMPT_ONCE 16 512 4 2 2 %d'%mode]
    r['append_files']=[]
    offsets=[401,3985,65425,270225];sizes=[219,110,111,112,221,4097]
    for policy in range(2):
        for reopen in range(2):
            for key,offset in enumerate(offsets):
                i=len(r['append_files']);name='t%03d.bin'%i
                seed=bytes(33+(j*13+key*3)%90 for j in range(offset))
                chunks=[]
                for step in range(512):
                    size=sizes[step%6]
                    chunks.append(bytes(32+(j*7+key*11+step*17)%95 for j in range(size-2))+b'\r\n')
                append=b''.join(chunks);correct=seed+append
                try:data=after['F'].read('xwnda01/'+name)
                except KeyError:data=b''
                r['append_files'].append(dict(id=i,policy=policy,reopen=reopen,offset=offset,append_operations=512,append_bytes=len(append),
                    bytes=len(data),sha256=m.sha(data),expected_sha256=m.sha(correct),exact=data==correct))
                expected.extend(['SEED %d %d %d %d %d 0'%(i,offset,offset,fnv(seed),fnv(seed)),
                    'SOURCE %d 512 %d %d %d %d'%(i,len(append),fnv(append),fnv(append),512 if policy==0 else 1),
                    'CASE %d %d %d %d %d %d'%(i,policy,reopen,offset,len(correct),fnv(correct))])
    raw_lines=log.splitlines();drawing=[];draw_end=[]
    for line in raw_lines:
        if line.startswith('DRAW '):
            match=re.fullmatch(r'DRAW ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)',line)
            if match:drawing.append(list(map(int,match.groups())))
        if line.startswith('DRAW_END '):
            match=re.fullmatch(r'DRAW_END ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)',line)
            if match:draw_end.append(list(map(int,match.groups())))
    lines=[line for line in raw_lines if not line.startswith(('DRAW ','DRAW_END '))]
    r['drawing_records']=drawing;r['drawing_end']=draw_end;r['drawing_mode']=mode
    draw_ok=len(drawing)==16 and len(draw_end)==1 and len(raw_lines)==len(lines)+17
    previous=0
    for i,row in enumerate(drawing):
        ident,drawmode,before_frame,after_frame,delta,error=row
        draw_ok=draw_ok and ident==i and drawmode==mode and after_frame>=before_frame>=previous and delta==after_frame-before_frame and error==0 and (delta>0 if mode else after_frame==0)
        previous=after_frame
    if len(draw_end)==1:
        drawmode,frames,during,error,exitcode,reserved=draw_end[0]
        draw_ok=draw_ok and drawmode==mode and frames>=during>=previous and error==exitcode==reserved==0 and (during>0 if mode else frames==during==0)
    r['drawing_checks_passed']=bool(draw_ok)
    last=re.fullmatch(r'COMPLETE 16 ([0-9]+) 0 0 0 0',lines[-2]) if len(lines)>=2 else None
    r['workload_completed']=r['drawing_checks_passed'] and bool(last) and lines[:-2]==expected and lines[-1]=='NORMAL_RESTART_REQUEST 0 0 0 0 0 0'
    r['elapsed_ms']=int(last.group(1)) if last else None
    try:
        entry=after['F'].directory(1)['entries']['xwnda01'][2]
        cluster=struct.unpack_from('<I',entry,44)[0]
        names=set(after['F'].directory(cluster)['entries'])
    except KeyError:names=set()
    r['directory_exact']=names=={'probe.log'}|{'t%03d.bin'%i for i in range(16)}
    r['setup_log']={}
    for label,reader in [('before',before),('after',after)]:
        data=reader['F'].read('winnt/setupapi.log');(art/(label+'-setupapi.log')).write_bytes(data)
        r['setup_log'][label]=dict(bytes=len(data),sha256=m.sha(data),non_ascii_bytes=sum(b>127 for b in data))
        if label=='before':old_setup=data
        else:
            r['setup_log']['prefix_preserved']=data.startswith(old_setup)
            r['setup_log']['new_non_ascii_bytes']=sum(b>127 for b in data[len(old_setup):])

def recurring(v):
    return (v['source'],v['event_id']) in {('Service Control Manager',7000),('Ftdisk',49)} and any(all(v[n]==old[n] for n in ['source','event_id','type','strings','data_hex']) for old in known)
r['unexpected_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2] and not recurring(v)]
r['popup_records']=[v for v in r['new_events']['system'] if v['source']=='Application Popup']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
launch=json.loads((out/'launch.json').read_text());r['dashboard_return']=len(launch['cycles'])==1 and launch['cycles'][0].get('dashboard_return') is True
r['diagnostic_checks_passed']=all([r['workload_completed'] and r['directory_exact'] and all(v['exact'] for v in r['append_files']),r['storage_workload_not_run'],r['dashboard_return'],r['normal_shutdown_count']==1,not r['unexpected_errors'],not r['popup_records'],not r['new_events']['application'],all(v['matched'] for v in r['payloads']),all(r['baseline_checks'].values()),r['fatx_exact'],all(v['matched'] for v in r['runtime_binary_checks'])])
completion=json.loads((run/'completion.json').read_text()) if (run/'completion.json').exists() else {}
r['ordinary_run_valid']=completion.get('reason')=='external_capture_complete' and (run/'capture-complete.signal').exists()
r['completion']=completion
r['debugger_observation_before_deadline']=False
r['post_deadline_snapshot']=(out/'timeout-memory.json').exists()
r['debugger_observation']=r['post_deadline_snapshot']
r['host_recorder_enabled']=False
r['limits']='Paired paced append/GDI diagnostic with candidate0101 and unchanged video0093. No debugger or raw disk writes. A pass does not reproduce first-install activity or rule out intermittent corruption. Historical emulator setup flags differ from physical hardware.'
(out/'audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['diagnostic_checks_passed','workload_completed','elapsed_ms','dashboard_return','unexpected_errors','popup_records','directory_exact','drawing_checks_passed','drawing_end']},indent=2))
