"""Exploratory emulator breakpoints around rename CcPinRead; no data/register patching."""
import argparse,datetime,json,pathlib,re,struct,sys,time
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
sys.path[:0]=[str(k.parent/'native-windows-prebuild'),str(k.parent/'native-windows-physical-bootvideo')]
from monitor_capture import command,acquire_monitor_lock
from debug_remote import Remote
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert a.run.startswith('nt5-physical-f-high-allocation-') and a.run.replace('-','').isalnum()
run=ws/'work/runs'/a.run;out=run/'rename-pin-trace.json';assert not out.exists()
r={'scope':__doc__,'run':a.run,'events':[]};pub=json.loads((k.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
def save():out.write_text(json.dumps(r,indent=2)+'\n')
deadline=time.monotonic()+480
g=None;active=set();keep_stopped=False
with acquire_monitor_lock(4594):
 try:
    while True:
        assert time.monotonic()<deadline
        command(4594,'stop');regs=command(4594,'info registers')
        raw=run/'pin-module-scan.ram';assert not raw.exists()
        try:
            command(4594,'pmemsave 0 62914560 '+json.dumps(raw.resolve().as_posix()))
            data=raw.read_bytes();cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',regs)[1],16)
            def u32(at):return struct.unpack_from('<I',data,at)[0]
            def pa(va):
                pde=u32((cr3&~4095)+(va>>22)*4);assert pde&1
                if pde&128:return (pde&0xffc00000)+(va&0x3fffff)
                pte=u32((pde&~4095)+((va>>12)&1023)*4);assert pte&1
                return (pte&~4095)+(va&4095)
            def read(va,n):return bytes(data[pa(va+i)] for i in range(n))
            def vu(va):return struct.unpack('<I',read(va,4))[0]
            bases=[]
            for pos in range(0,len(data)-4096,4096):
                if data[pos:pos+2]!=b'MZ':continue
                off=u32(pos+60)
                if off>3500 or data[pos+off:pos+off+4]!=b'PE\0\0' or u32(pos+off+8)!=0x4b7a1bd5:continue
                va=0x80000000+pos
                try:
                    if pa(va)==pos and vu(vu(va+pub['_PsLoadedModuleList']['rva'])+24)==va:bases.append(va)
                except (AssertionError,IndexError,struct.error):continue
            assert len(bases)==1
            base=bases[0];head=base+pub['_PsLoadedModuleList']['rva'];link=vu(head);modules=[]
            while link!=head and len(modules)<128:
                mb,entry,size=struct.unpack('<III',read(link+24,12));n,m,b=struct.unpack('<HHI',read(link+44,8));assert n<=m and n<512
                modules.append(dict(name=read(b,n).decode('utf-16-le'),base=mb,size=size));link=vu(link)
            driver=next(m for m in modules if 'xwnfatx' in m['name'].lower())
            assert read(driver['base']+0x7c7e,3)==bytes.fromhex('83ec18')
            r.update(kernel_base=hex(base),driver=driver,modules=modules);save();break
        except (AssertionError,StopIteration,IndexError,struct.error):
            command(4594,'cont');time.sleep(5)
        finally:raw.unlink(missing_ok=True)
    g=Remote(4595);g.ask('qSupported');g.ask('?');g.s.settimeout(60)
    before=driver['base']+0x7c78;after=driver['base']+0x7c7e
    g.bp(before);active.add(before);g.send('c')
    while time.monotonic()<deadline and len(r['events'])<100:
        try:reply=g.recv()
        except TimeoutError:continue
        regs=g.regs();assert regs['eip']==before,regs
        g.bp(before,False);active.remove(before)
        args=struct.unpack('<6I',g.read(regs['esp'],24))
        row=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),before_registers=regs,
                 call_arguments=[hex(v) for v in args],output_words_before=g.read(args[4],8).hex())
        nameptr=struct.unpack('<I',g.read(regs['ebp']+16,4))[0]
        n,m,b=struct.unpack('<HHI',g.read(nameptr,8));assert n<=m and n<=84
        row['rename_name']=g.read(b,n).decode('utf-16-le')
        g.bp(after);active.add(after);g.send('c');g.recv();post=g.regs();assert post['eip']==after
        g.bp(after,False);active.remove(after)
        bcb=struct.unpack('<I',g.read(args[4],4))[0];buffer=struct.unpack('<I',g.read(args[5],4))[0]
        row.update(after_registers=post,returned_boolean=bool(post['eax']&255),bcb=hex(bcb),buffer=hex(buffer))
        if bcb>=0x80000000:
            try:row['bcb_words']=[hex(v) for v in struct.unpack('<24I',g.read(bcb,96))]
            except (ValueError,AssertionError):pass
        r['events'].append(row);save();print(json.dumps(row),flush=True)
        if not row['returned_boolean'] or buffer<0x80000000 or buffer&4095:
            keep_stopped=True;r['stopped_on_invalid_pin']=True
            dump=run/'rename-pin-memory.ram';command(4594,'pmemsave 0 62914560 '+json.dumps(dump.resolve().as_posix()))
            r['memory_bytes']=dump.stat().st_size;break
        g.bp(before);active.add(before);g.send('c')
 except Exception as e:
    r['error']=repr(e);raise
 finally:
    try:
        command(4594,'stop')
        if g:
            g.s.settimeout(20)
            for bp in list(active):
                # HMP stop may leave an asynchronous GDB stop packet ahead
                # of this command's reply after a timed-out continue.
                g.send(f'z0,{bp:x},1')
                for _ in range(4):
                    reply=g.recv()
                    if reply=='OK':break
                    assert reply.startswith(('S','T')),reply
                else:raise RuntimeError('No breakpoint-removal acknowledgement')
                active.remove(bp)
        r['breakpoints_removed']=not active
        if not keep_stopped:command(4594,'cont')
    except Exception as e:
        r['cleanup_error']=repr(e);keep_stopped=True
        r['breakpoints_removed']=not active
        raise
    finally:
        if g:g.s.close()
        r['left_paused']=keep_stopped;save()
