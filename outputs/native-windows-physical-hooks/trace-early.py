"""Observe exact early entry in an owned xemu snapshot; never target the Xbox."""
import argparse, ftplib, json, pathlib, socket, struct, sys, time
kit=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(kit.parents[1]/'work/python-packages'))
sys.path.insert(0,str(kit.parent/'native-windows-prebuild'))
import pefile
from monitor_capture import command, acquire_monitor_lock

class Remote:
    def __init__(self,port):
        self.s=socket.create_connection(('127.0.0.1',port),timeout=20)
        self.s.settimeout(20)
    def recv(self):
        while True:
            c=self.s.recv(1)
            if not c:raise EOFError('Debugger disconnected')
            if c!=b'$':continue
            b=bytearray()
            while True:
                c=self.s.recv(1)
                if not c:raise EOFError('Incomplete debugger packet')
                if c==b'#':break
                b+=c
            checksum=self.s.recv(2)
            assert int(checksum,16)==sum(b)%256
            self.s.sendall(b'+')
            if b.startswith(b'O') and b!=b'OK':continue
            return b.decode()
    def send(self,s):
        b=s.encode();self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode())
    def ask(self,s):self.send(s);return self.recv()
    def bp(self,addr,on=True):assert self.ask(f'{"Z" if on else "z"}0,{addr:x},1')=='OK'
    def regs(self):
        raw=bytes.fromhex(self.ask('g'))
        values=struct.unpack_from('<10I',raw)
        return {k:values[i] for i,k in enumerate(['eax','ecx','edx','ebx','esp','ebp','esi','edi','eip','eflags'])}
    def read(self,addr,size):return bytes.fromhex(self.ask(f'm{addr:x},{size:x}'))

p=argparse.ArgumentParser()
for flag in ['gdb','monitor','ftp']:p.add_argument('--'+flag,type=int,required=True)
p.add_argument('--reference',type=pathlib.Path,required=True)
p.add_argument('--output',type=pathlib.Path,required=True)
a=p.parse_args();reference=json.loads(a.reference.read_text())
assert reference['status']=='partition_hooks_boundary_verified'
e=reference['entry_record']['words']
pe=pefile.PE(str(kit/'package/loader/halxboxnt5.dll'))
exports={x.name.decode():e[8]+x.address for x in pe.DIRECTORY_ENTRY_EXPORT.symbols if x.name}
points={e[5]:'KernelEntry',exports['HalInitializeProcessor']:'HalInitializeProcessor',exports['HalInitSystem']:'HalInitSystem'}
boundary=json.loads((kit/'hal-boundary-audit.json').read_text())
for symbol in ['_HalInitializeBios@8','@HalpXboxExamineMBR@16','@HalpXboxIoReadPartitionTable@16','@HalpXboxIoSetPartitionInformation@16','@HalpXboxIoWritePartitionTable@20']:
    points[e[8]+int(boundary['symbols_rva'][symbol],16)]='FORBIDDEN_'+symbol
points[e[8]+int(boundary['symbols_rva']['_HalpXwnBaseReady'],16)]='BaseHalReady'
for symbol,name in [('_HalpCalibrateStallExecution@0','CalibrationEntry'),('OnlyOnePersonCanWriteHalCode','FirstRtcInterrupt'),('ComputeStall','SecondRtcInterrupt'),('_HalpXwnTimerReady','TimerReady')]:
    points[e[8]+int(boundary['symbols_rva'][symbol],16)]=name
for symbol,name in [('_HalpInitializeClock@0','ClockInitialize'),('_HalStopProfileInterrupt@4','ProfileStop'),('_HalpXwnClockReady','ClockReady'),('_HalpInitPhase0','XboxPhase0'),('_HalpXboxInitPartIo','PartitionRegistration'),('_HalpXwnHooksReady','HooksReady')]:
    points[e[8]+int(boundary['symbols_rva'][symbol],16)]=name
for instruction,name in zip(boundary['inlined_pit_writes'],['PitModeWrite','PitLowWrite','PitHighWrite']):
    points[e[8]+int(instruction['rva'],16)]=name
kpe=pefile.PE(str(kit/'package/WINNT/system32/ntoskrnl.exe'))
points[e[6]+next(s.address for s in kpe.DIRECTORY_ENTRY_EXPORT.symbols if s.name==b'KeSetTimeIncrement')]='KernelSetTimeIncrement'
for m in reference['modules']:
    if m['name'].lower().endswith('.sys'):points[int(m['entry'],16)]='FORBIDDEN_DriverEntry_'+m['name']
result={'scope':'Native kernel entry observed using emulator breakpoints; all disk writes isolated in snapshot.','events':[],'forbidden_breakpoints':{hex(k):v for k,v in points.items() if v.startswith('FORBIDDEN')},'passed':False}
lock=acquire_monitor_lock(a.monitor);g=None
def save():a.output.write_text(json.dumps(result,indent=2)+'\n')
try:
    command(a.monitor,'stop')
    g=Remote(a.gdb);g.ask('qSupported');g.ask('?')
    for addr in points:g.bp(addr)
    g.send('c')
    with ftplib.FTP() as ftp:
        ftp.connect('127.0.0.1',a.ftp,timeout=8);ftp.login('xbox','xbox')
        result['launch_response']=ftp.sendcmd(r'SITE EXEC E:\Applications\XWNLoader\default.xbe')
    for expected in ['KernelEntry','HalInitializeProcessor','ProcessorReturned','HalInitSystem','BaseHalReady','CalibrationEntry','FirstRtcInterrupt','SecondRtcInterrupt','CalibrationReturned','TimerReady','ClockInitialize','KernelSetTimeIncrement','PitModeWrite','PitLowWrite','PitHighWrite','ClockReturned','ProfileStop','ProfileReturned','ClockReady','XboxPhase0','PartitionRegistration','HooksReady','LoaderCheckpoint']:
        stop=g.recv();r=g.regs();name=points.get(r['eip'],'unexpected')
        event={'name':name,'stop':stop,'registers':{k:hex(v) for k,v in r.items()},'stack':list(struct.unpack('<4I',g.read(r['esp'],16)))}
        result['events'].append(event);save()
        assert name==expected,event
        g.bp(r['eip'],False)
        if name=='HalInitializeProcessor':
            assert event['stack'][1:3]==[0,e[4]]
            assert e[6]<=event['stack'][0]<e[6]+e[7]
            points[event['stack'][0]]='ProcessorReturned';g.bp(event['stack'][0])
        if name=='HalInitSystem':
            assert event['stack'][1:3]==[0,e[4]]
        if name=='CalibrationEntry':
            points[event['stack'][0]]='CalibrationReturned';g.bp(event['stack'][0])
        if name=='FirstRtcInterrupt':
            event['rtc_interrupt_count_before_increment']=struct.unpack('<I',g.read(r['ebp']-12,4))[0]
            assert event['rtc_interrupt_count_before_increment']==0
        if name=='SecondRtcInterrupt':
            event['rtc_interrupt_count']=struct.unpack('<I',g.read(r['ebp']-12,4))[0]
            assert event['rtc_interrupt_count']==2
        if name=='KernelSetTimeIncrement':assert event['stack'][1:3]==[150000,10000]
        if name in ['PitModeWrite','PitLowWrite','PitHighWrite']:
            assert r['eax']&255=={'PitModeWrite':0x34,'PitLowWrite':16875&255,'PitHighWrite':16875>>8}[name]
        if name=='ProfileStop':assert event['stack'][1]==0
        if name in ['ClockInitialize','ProfileStop']:
            returned={'ClockInitialize':'ClockReturned','ProfileStop':'ProfileReturned'}[name]
            points[event['stack'][0]]=returned;g.bp(event['stack'][0])
        if name=='PartitionRegistration':
            dispatch=e[6]+next(s.address for s in kpe.DIRECTORY_ENTRY_EXPORT.symbols if s.name==b'HalDispatchTable')
            originals=[struct.unpack('<I',g.read(dispatch+off,4))[0] for off in [0x14,0x1c,0x20,0x24]]
            event['original_partition_handlers']=[hex(x) for x in originals]
            assert all(e[6]<=x<e[6]+e[7] for x in originals)
        if name=='HooksReady':
            installed=[struct.unpack('<I',g.read(dispatch+off,4))[0] for off in [0x14,0x1c,0x20,0x24]]
            symbols=['@HalpXboxExamineMBR@16','@HalpXboxIoReadPartitionTable@16','@HalpXboxIoSetPartitionInformation@16','@HalpXboxIoWritePartitionTable@20']
            assert installed==[e[8]+int(boundary['symbols_rva'][s],16) for s in symbols]
            saved=[struct.unpack('<I',g.read(e[8]+int(v,16),4))[0] for v in boundary['saved_handler_globals_rva'].values()]
            assert saved==originals
            event['installed_partition_handlers']=[hex(x) for x in installed]
            event['saved_originals_equal_pre_registration']=True
            points[e[10]]='LoaderCheckpoint';g.bp(e[10])
        if name=='LoaderCheckpoint':assert event['stack'][1:3]==[70,e[4]]
        g.send('c')
    time.sleep(1)
    regs=command(a.monitor,'info registers')
    assert 'HLT=1' in regs
    result['final_registers']=regs
    result['passed']=True;save()
finally:
    if g:g.s.close()
    lock.close()
print('RTC calibration, native time-increment call, PIT programming and profile stop observed; partition hooks registered, no BIOS/partition-handler/driver entry.')
