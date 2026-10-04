"""Capture the first shutdown bugcheck without modifying native results."""
import argparse,json,pathlib,struct,sys,time,subprocess
out=pathlib.Path(__file__).resolve().parent
sys.path[:0]=[str(out.parent/'native-windows-prebuild'),str(out.parent/'native-windows-physical-bootvideo')]
from monitor_capture import command,acquire_monitor_lock
from debug_remote import Remote
p=argparse.ArgumentParser();p.add_argument('--run',type=pathlib.Path,required=True);a=p.parse_args()
deadline=time.monotonic()+360
while not (a.run/'state-210.json').exists():
    assert time.monotonic()<deadline
    assert not (a.run/'cleanup.json').exists(),'VM ended before shutdown request'
    time.sleep(2)
state=json.loads((a.run/'state-210.json').read_text());K=int(state['kernel_base'],16)
pubs=json.loads((out.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
for cmd in ('sendkey ctrl-esc','sendkey u'):
    command(4594,cmd);time.sleep(2)
subprocess.run([sys.executable,str(out.parent/'native-windows-prebuild/monitor_capture.py'),'--port','4594','--output',str(a.run/'shutdown-dialog.png')],check=True)
r={'scope':'Read-only execution breakpoint on first native bugcheck after UI shutdown; no patched code results', 'kernel_base':hex(K)}
with acquire_monitor_lock(4594):
    command(4594,'stop');g=Remote(4595);g.s.settimeout(45);g.ask('qSupported');g.ask('?')
    at=K+pubs['_KeBugCheckEx@20']['rva'];g.bp(at)
    try:
        g.send('c');command(4594,'sendkey ret');g.recv();regs=g.regs();assert regs['eip']==at
        r['registers']={k:hex(v) for k,v in regs.items()}
        args=struct.unpack('<6I',g.read(regs['esp'],24));r['caller']=hex(args[0]);r['bugcheck']=[hex(v) for v in args[1:]]
        modules=[(int(m['base'],16),m['size'],m['name']) for m in state['modules']]
        def describe(v):
            for base,size,name in modules:
                if base<=v<base+size:
                    d={'address':hex(v),'module':name,'rva':hex(v-base)}
                    if base==K:
                        near=max(((x['rva'],n) for n,x in pubs.items() if x['rva']<=v-K),default=(0,'?'))
                        d['nearest_public']=near[1];d['offset']=hex(v-K-near[0])
                    return d
        n=4096-(regs['esp']&4095);data=g.read(regs['esp'],n);r['stack_candidates']=[]
        for i in range(0,len(data)-3,4):
            v=struct.unpack_from('<I',data,i)[0];d=describe(v)
            if d:r['stack_candidates'].append({'stack':hex(regs['esp']+i),**d})
        r['note']='Stack candidates are address scans, not a validated unwind. Guest remains stopped for inspection.'
    except Exception as ex:
        r['error']=repr(ex);g.s.sendall(b'\x03')
        try:g.recv()
        except Exception:pass
    finally:
        try:g.bp(at,False)
        except Exception:pass
        g.s.close();command(4594,'stop')
        (a.run/'first-shutdown-fault.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))

