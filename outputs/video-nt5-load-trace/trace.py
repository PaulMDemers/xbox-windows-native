"""Owned emulator load-path exploration; breakpoints change timing, no guest data edits."""
import datetime,ftplib,hashlib,json,os,re,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path[:0]=[str(ws/'work/python-packages'),str(k.parent/'native-windows-prebuild'),str(k.parent/'native-windows-physical-bootvideo')]
from monitor_capture import command,acquire_monitor_lock
from debug_remote import Remote
import pefile
case=sys.argv[1];assert case.isdigit() and len(case)==3
run=ws/('work/runs/nt5-video-load-trace-'+case);out=k/case;out.mkdir(exist_ok=True)
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
report=out/'trace.json';assert not report.exists()
kernel=k.parent/'native-windows-physical-f/package/F/winnt/system32/ntoskrnl.exe'
assert hashlib.sha256(kernel.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
pe=pefile.PE(str(kernel));pub=json.loads((k.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
fields=json.loads((k.parent/'native-windows-nt5-kernel/pnp-layouts.json').read_text())['_DEVICE_NODE']['fields']
r=dict(scope=__doc__,run=run.name,physical_access=False,events=[],data_or_register_writes=False)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():report.write_text(json.dumps(r,indent=2)+'\n')
g=None;active=set();targets={};returns={}
def arm(addr):
    if addr not in active:g.bp(addr);active.add(addr)
def disarm(addr):
    if addr in active:g.bp(addr,False);active.remove(addr)
def u32(addr):return struct.unpack('<I',g.read(addr,4))[0]
def uni(addr):
    n,m,b=struct.unpack('<HHI',g.read(addr,8));assert n<=m and n<=2048
    return g.read(b,n).decode('utf-16le') if n else ''
def device(n):
    return {f:(uni(n+fields[f]['offset']) if f in ['InstancePath','ServiceName'] else hex(u32(n+fields[f]['offset']))) for f in ['InstancePath','ServiceName','Flags','Problem','FailureStatus','PhysicalDeviceObject']}
with acquire_monitor_lock(4594):
 try:
    deadline=time.monotonic()+60
    while True:
        f=ftplib.FTP()
        try:f.connect('127.0.0.1',4596,timeout=3);f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);break
        except ftplib.all_errors:
            f.close();assert time.monotonic()<deadline;time.sleep(1)
    r['launch_requested_utc']=utc();save()
    try:r['launch_reply']=f.sendcmd('SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe')
    except ftplib.all_errors as e:r['launch_reply_uncertain']=repr(e)
    finally:f.close()
    save();deadline=time.monotonic()+120
    # Discover the actual mapped kernel before arming its verified entry bytes.
    scans=0
    while time.monotonic()<deadline:
        command(4594,'stop');registers=command(4594,'info registers');raw=run/'load-scan.ram'
        command(4594,'pmemsave 0 0x3c00000 '+json.dumps(raw.as_posix()));data=raw.read_bytes();raw.unlink()
        cr3=int(re.search(r'CR3=([0-9a-fA-F]+)',registers)[1],16)&~4095
        def p32(a):return struct.unpack_from('<I',data,a)[0]
        def pa(va):
            de=p32(cr3+(va>>22)*4);assert de&1
            if de&128:return (de&0xffc00000)+(va&0x3fffff)
            te=p32((de&~4095)+((va>>12)&1023)*4);assert te&1
            return (te&~4095)+(va&4095)
        def read(va,n):return bytes(data[pa(va+i)] for i in range(n))
        candidates=[]
        for pos in range(0,len(data)-4096,4096):
            if data[pos:pos+2]!=b'MZ':continue
            off=p32(pos+60)
            if off>3500 or data[pos+off:pos+off+4]!=b'PE\0\0' or p32(pos+off+8)!=0x4b7a1bd5:continue
            base=0x80000000+pos
            try:
                if pa(base)==pos and read(base+pub['_MmLoadSystemImage@24']['rva'],16)==pe.get_data(pub['_MmLoadSystemImage@24']['rva'],16):candidates.append(base)
            except (AssertionError,IndexError,struct.error):pass
        scans+=1
        if len(candidates)==1:base=candidates[0];break
        command(4594,'cont');time.sleep(.15)
    else:raise RuntimeError('Kernel mapping not discovered')
    r.update(kernel_base=hex(base),attach_utc=utc(),attach_registers=registers,discovery_scans=scans)
    g=Remote(4595);g.ask('qSupported');g.ask('?');g.s.settimeout(15)
    names={'_MmLoadSystemImage@24':6,'_IopLoadDriver@8':2,'_IopCallDriverAddDevice@12':3,'_IopInitializeSystemDrivers@0':0,'_KeBugCheckEx@20':5}
    if case=='003':names['_LdrVerifyMappedImageMatchesChecksum@8']=2
    r['verified_entries']={}
    for name,argc in names.items():
        addr=base+pub[name]['rva'];actual=g.read(addr,16);expected=pe.get_data(pub[name]['rva'],16)
        assert actual==expected,(name,actual.hex(),expected.hex())
        r['verified_entries'][name]=dict(address=hex(addr),bytes=actual.hex());targets[addr]=(name,argc);arm(addr)
    if case!='001':
        addr=base+0xce701;expected=bytes.fromhex('bb6c0200c0eb41')
        assert g.read(addr,len(expected))==expected
        targets[addr]=('MiLoadSystemImage_error_conversion',-1);arm(addr)
        r['verified_entries']['MiLoadSystemImage_error_conversion']=dict(address=hex(addr),bytes=expected.hex())
    save();deadline=time.monotonic()+300
    while time.monotonic()<deadline and len(r['events'])<2000:
        g.send('c')
        try:reply=g.recv()
        except TimeoutError:
            g.s.sendall(b'\x03');reply=g.recv()
            r['timeout_registers']=g.regs();r['outcome']='breakpoint_wait_timeout';break
        regs=g.regs();ip=regs['eip'];esp=regs['esp'];row=dict(utc=utc(),registers=regs)
        match=next((v for v in reversed(returns.get(ip,[])) if v['expected_esp']==esp),None)
        if match:
            row.update(kind='return',call_event=match['event'],name=match['name'],eax=hex(regs['eax']))
            returns[ip].remove(match)
            if not returns[ip] and ip not in targets:disarm(ip)
            entry=r['events'][match['event']]
            if match['name']=='_LdrVerifyMappedImageMatchesChecksum@8' and 'xboxvnt5' in entry.get('checking_image','').lower():
                address,length=match['args'];assert length<1024*1024
                mapped=b''.join(g.read(address+i,min(512,length+64-i)) for i in range(0,length+64,512))
                dest=out/('mapped-'+str(match['event'])+'.bin');dest.write_bytes(mapped)
                row.update(mapped_bytes_file=dest.name,mapped_file_sha256=hashlib.sha256(mapped[:length]).hexdigest(),file_length=length,tail_after_eof=mapped[length:].hex())
            if match['name']=='_MmLoadSystemImage@24' and regs['eax']==0 and 'xboxvnt5' in entry.get('image_name','').lower():
                mb=u32(match['args'][5]);off=u32(mb+60);ep=u32(mb+off+40);addr=mb+ep
                row['loaded_miniport_base']=hex(mb);targets[addr]=('XboxVnt5DriverEntry',2);arm(addr)
            if match['name']=='XboxVnt5DriverEntry':
                driver=match['args'][0];extension=u32(driver+0x18);add=u32(extension+4)
                row['driver_object']=hex(driver);row['add_device']=hex(add)
                if add:targets[add]=('XboxVnt5AddDevice',2);arm(add)
        elif ip in targets:
            name,argc=targets[ip]
            if argc==-1:
                row.update(kind='internal',name=name,original_status=hex(regs['ebx']),image_name=uni(u32(regs['ebp']+8)))
                r['events'].append(row);save();disarm(ip);g.ask('s');arm(ip);continue
            words=struct.unpack('<'+'I'*(argc+1),g.read(esp,4*(argc+1)))
            row.update(kind='entry',name=name,args=[hex(v) for v in words[1:]],caller=hex(words[0]))
            if name=='_MmLoadSystemImage@24':row['image_name']=uni(words[1])
            if name=='_LdrVerifyMappedImageMatchesChecksum@8':
                row['checking_image']=next((e['image_name'] for e in reversed(r['events']) if e.get('kind')=='entry' and e.get('name')=='_MmLoadSystemImage@24'),'unknown')
            if name=='_IopCallDriverAddDevice@12':
                try:row['device']=device(words[1])
                except Exception as e:row['device_read_error']=repr(e)
            if name=='_KeBugCheckEx@20':
                r['events'].append(row);r['outcome']='bugcheck';save();break
            returns.setdefault(words[0],[]).append(dict(name=name,args=list(words[1:]),event=len(r['events']),expected_esp=esp+4*(argc+1)))
            arm(words[0])
        else:row.update(kind='unexpected_stop',reply=reply);r['outcome']='unexpected_stop';r['events'].append(row);break
        r['events'].append(row);save()
        if ip in active:
            disarm(ip);step=g.ask('s');assert step.startswith(('S','T')),step
            if ip in targets or returns.get(ip):arm(ip)
    else:r['outcome']='trace_limit'
    command(4594,'pmemsave 0 0x4000000 '+json.dumps((run/'load-trace-final.ram').as_posix()))
 except Exception as e:r['error']=repr(e);raise
 finally:
    try:
        command(4594,'stop')
        if g:
            for addr in list(active):disarm(addr)
        r['breakpoints_removed']=not active
    finally:
        if g:g.s.close()
        r['ended_utc']=utc();r['left_paused']=True;save()
        (run/'capture-complete.signal').touch(exist_ok=False)
print(json.dumps(dict(outcome=r.get('outcome'),events=len(r['events']),kernel=r.get('kernel_base'))))
