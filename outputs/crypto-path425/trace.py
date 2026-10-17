"""One bounded read-only GDB diagnostic. No guest register/data writes or API substitution."""
import datetime,hashlib,json,socket,struct,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu001';run=Path('E:/xwn425/runs/nt5-crypto425-emu001')
sys.path.insert(0,str(W/'outputs/native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
sys.path.insert(0,str(W/'outputs/surface-bridge260'));from atomic_json import write_json
from parsing import words,object_name,pair_key
code=(W/'outputs/native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
assert (run/'startup-ready.json').exists() and not (run/'cleanup.json').exists() and not (out/'trace.json').exists()
reviewed=json.loads((out/'submit-reviewed.json').read_text());assert reviewed['path']==r'C:\XWN425BIN\trace.exe' and reviewed['visually_verified']
plan=json.loads((K/'sites003.json').read_text());base=plan['image_base'];cp=base+plan['checkpoint']['rva'];nb=plan['ntdll_base']
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r={'started_utc':utc(),'debugger':True,'ordinary_qualified':False,'physical_access':False,'guest_data_or_register_writes':False,
   'events':[],'checkpoints':[],'unpaired_returns':[],'status':'starting','pins':[],'phase':None}
g=None;stopped=False;armed=set();active={};owner=None;phase=None;sites={};lock=acquire_monitor_lock(5456)
def save():write_json(out/'trace.json',r)
def u32(p):return struct.unpack('<I',g.read(p,4))[0]
def pin(address,raw,label):
    got=g.read(address,len(raw));r['pins'].append({'address':address,'label':label,'bytes':got.hex(),'expected':raw.hex()});assert got==raw
def identity():
    t=u32(0xffdff124);assert 0x80000000<=t<=0xfffff000
    p=u32(t+plan['thread_owner_offset']);assert 0x80000000<=p<=0xfffff000
    fields=plan['process_fields'];cid=struct.unpack('<II',g.read(t+plan['thread_fields']['Cid']['offset'],8))
    pid=u32(p+fields['UniqueProcessId']['offset']);assert cid[0]==pid
    name=g.read(p+fields['ImageFileName']['offset'],16).split(b'\0')[0].decode('ascii',errors='strict')
    return {'thread':t,'process':p,'pid':pid,'tid':cid[1],'image':name}
def add(address):g.bp(address);armed.add(address)
try:
    command(5456,'stop');stopped=True;g=Remote(5457);r['initial_stop']=g.ask('?');r['physical_mode']=g.ask('qqemu.PhyMemMode');assert r['physical_mode']=='0'
    add(cp);r['status']='checkpoint_armed';save();(out/'trace-armed.signal').touch(exist_ok=False)
    r['submit_requested']=True;save();command(5456,'sendkey ret');r['submit_sent']=True;save()
    deadline=time.monotonic()+360
    for hit in range(4096):
        assert time.monotonic()<deadline,'Trace deadline'
        g.s.settimeout(max(.1,deadline-time.monotonic()));g.send('c');stopped=False
        reply=g.recv();stopped=True;g.s.settimeout(5)
        raw=bytes.fromhex(g.ask('g'));vals=struct.unpack('<11I',raw[:44]);eax,esp,eip,cs=vals[0],vals[4],vals[8],vals[10]
        assert cs&3==3 and eip in armed,(reply,eip,cs)
        ident=identity()
        if eip==cp:
            pin(cp,bytes.fromhex(plan['checkpoint']['bytes']),'checkpoint')
            args=words(g.read,esp,2);newphase=args[1];assert newphase==len(r['checkpoints']) and 0<=newphase<=6
            state=words(g.read,plan['record_address'],10)
            row={'utc':utc(),'phase':newphase,'identity':ident,'state':state,'stack':esp,'return_address':args[0]};r['checkpoints'].append(row);save()
            assert state[0]==0x42504250 and state[2]==ident['pid'] and state[3]==ident['tid']
            assert ident['image'].lower()=='trace.exe' and state[4]==nb and state[9]==base
            assert not any(v['identity']['process']==ident['process'] for v in active.values()),'Owned API still active at checkpoint'
            if owner is None:
                owner=ident;r['owner']=owner
                for module,addr,stamp in [('probe',base,plan['native_timestamp']),('ntdll',nb,plan['ntdll_timestamp'])]:
                    header=g.read(addr,64);assert header[:2]==b'MZ';off=struct.unpack_from('<I',header,60)[0];assert 64<=off<4096
                    head=g.read(addr+off,24);assert head[:4]==b'PE\0\0' and struct.unpack_from('<I',head,8)[0]==stamp
                    r['pins'].append({'label':module+'-header','address':addr,'dos':header.hex(),'pe':head.hex()})
                for i,api in enumerate(plan['apis']):
                    a=nb+api['rva'];ret=nb+api['return_rva'];assert state[5+i]==a
                    pin(a,bytes.fromhex(api['bytes']),api['name'])
                    sites[a]=(api,'entry');sites[ret]=(api,'return');add(a);add(ret)
            else:assert ident==owner
            phase=newphase;r['phase']=phase
            if phase==6:r['status']='all_checkpoints_complete';save();break
        else:
            api,kind=sites[eip];key=pair_key(ident['thread'],ident['process'],esp,api['name'])
            # Exact unmodified resident stub bytes are checked on every hit.
            assert g.read(nb+api['rva'],len(bytes.fromhex(api['bytes']))).hex()==api['bytes']
            if kind=='entry':
                assert key not in active
                row={'index':len(r['events']),'utc':utc(),'phase':phase,'api':api['name'],'identity':ident,'stack':esp,'owned_probe_thread':ident==owner}
                r['events'].append(row);save()  # retain partial evidence before a potentially failing read
                args=words(g.read,esp+4,api['argc']);row['arguments']=args
                row['object_name']=object_name(g.read,args[api['oa_index']]);active[key]=row
            elif key not in active:
                r['unpaired_returns'].append({'api':api['name'],'identity':ident,'stack':esp,'status':eax,'phase':phase})
            else:
                row=active.pop(key);row.update(return_utc=utc(),status=eax,status_hex=f'{eax:08x}',pending=eax==0x103,paired=True)
                if api['name'] in ['NtCreateFile','NtOpenFile'] and eax<0x80000000 and eax!=0x103:
                    row['returned_handle']=words(g.read,row['arguments'][0],1)[0]
                    row['io_status']=words(g.read,row['arguments'][3],2)
            save()
        g.bp(eip,False);armed.remove(eip);assert g.ask('s').startswith(('T','S'));add(eip)
    else:r['status']='hit_limit'
except Exception as exc:r.update(status='incomplete',error=repr(exc));save()
finally:
    if g:
        try:
            if not stopped:g.s.settimeout(5);g.interrupt();stopped=True
            for a in list(armed):g.bp(a,False);armed.remove(a)
            r['physical_mode_after']=g.ask('qqemu.PhyMemMode');assert r['physical_mode_after']=='0'
            g.send('c');r['guest_resumed']=True
        except Exception as exc:r['teardown_error']=repr(exc)
        g.s.close()
    elif stopped:command(5456,'cont')
    r.update(ended_utc=utc(),armed_remaining=sorted(armed),incomplete_indices=[v['index'] for v in active.values()]);save();lock.close()
print(json.dumps({k:r[k] for k in ['status','error','guest_resumed','armed_remaining'] if k in r}))
